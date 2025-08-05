"""
RunPod Serverless Handler for Higgs Audio V2

Ultra-thin serverless endpoint for audio generation with voice cloning,
LLM tone control, and S3 output storage.
"""

import gc
import json
import os
import sys
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import boto3
import re
import soundfile as sf
import torch
from loguru import logger

from boson_multimodal.audio_processing.higgs_audio_tokenizer import load_higgs_audio_tokenizer


# Model imports


# Import generation utilities (needs sys.path modification first)
sys.path.append("/app/examples")
from generation import (
    HiggsAudioModelClient,
    normalize_chinese_punctuation,
    prepare_chunk_text,
    prepare_generation_context,
)


# Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-generation-3B-base")
TOKENIZER_PATH = os.getenv("TOKENIZER_PATH", "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-tokenizer")
VOICE_PROMPTS_PATH = os.getenv("VOICE_PROMPTS_PATH", "/runpod-volume/higgs_audio/voice_prompts")

# Global variables for caching
_model_cache = None
_tokenizer_cache = None
_audio_tokenizer_cache = None
_collator_cache = None
_voice_prompts_cache = None
_last_access_time = None
_memory_cleanup_threshold = 300  # 5 minutes


@dataclass
class GenerationRequest:
    """Request data model"""

    transcript: str
    ref_audio: str | None = None
    scene_prompt: str | None = None
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.95
    max_new_tokens: int = 2048
    chunk_method: str | None = None
    chunk_max_word_num: int = 200
    chunk_max_num_turns: int = 1
    ras_win_len: int = 7
    ras_win_max_num_repeat: int = 2
    seed: int | None = None
    s3_bucket: str | None = None
    s3_key: str | None = None


@dataclass
class GenerationResponse:
    """Response data model"""

    success: bool
    audio_url: str | None = None
    duration_seconds: float | None = None
    sample_rate: int = 24000
    text_output: str | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None
    voice_suggestions: list[dict[str, str]] | None = None


class ModelManager:
    """Manages model lifecycle with memory optimization"""

    def __init__(self):
        self.model_path = MODEL_PATH
        self.tokenizer_path = TOKENIZER_PATH
        self.device = self._get_device()
        self.model_client = None
        self.audio_tokenizer = None
        self.last_cleanup = time.time()

    def _get_device(self) -> str:
        """Determine optimal device"""
        if torch.cuda.is_available():
            return "cuda:0"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    async def initialize(self):
        """Initialize models with lazy loading"""
        global _model_cache, _tokenizer_cache, _audio_tokenizer_cache, _collator_cache

        if _model_cache is None:
            logger.info("Loading models...")

            # Load audio tokenizer
            device_for_tokenizer = "cpu" if self.device == "mps" else self.device
            _audio_tokenizer_cache = load_higgs_audio_tokenizer(self.tokenizer_path, device=device_for_tokenizer)
            self.audio_tokenizer = _audio_tokenizer_cache

            # Initialize model client
            _model_cache = HiggsAudioModelClient(
                model_path=self.model_path,
                audio_tokenizer=self.audio_tokenizer,
                device=self.device,
                max_new_tokens=2048,
                use_static_kv_cache="cuda" in self.device,
            )
            self.model_client = _model_cache

            # Cache voice prompts
            self._load_voice_prompts()

            logger.info("Models loaded successfully")

    def _load_voice_prompts(self):
        """Load voice prompts for suggestions"""
        global _voice_prompts_cache

        if _voice_prompts_cache is None:
            voice_prompts_dir = Path(VOICE_PROMPTS_PATH)
            if voice_prompts_dir.exists():
                _voice_prompts_cache = []
                for wav_file in voice_prompts_dir.glob("*.wav"):
                    voice_name = wav_file.stem
                    txt_file = wav_file.with_suffix(".txt")
                    if txt_file.exists():
                        _voice_prompts_cache.append(
                            {
                                "name": voice_name,
                                "description": f"Voice: {voice_name}",
                                "audio_path": str(wav_file),
                                "text_path": str(txt_file),
                            }
                        )

    def get_voice_suggestions(self) -> list[dict[str, str]]:
        """Get available voice suggestions"""
        if _voice_prompts_cache is None:
            self._load_voice_prompts()

        return _voice_prompts_cache or [
            {"name": "belinda", "description": "Female voice with warm tone"},
            {"name": "chadwick", "description": "Male voice with deep tone"},
            {"name": "daffy", "description": "Animated character voice"},
            {"name": "elsa", "description": "Female voice with clear articulation"},
            {"name": "jorts", "description": "Male voice with casual tone"},
        ]

    def cleanup_memory(self):
        """Clean up GPU memory and unused resources"""
        current_time = time.time()
        if current_time - self.last_cleanup < 60:  # Don't cleanup too frequently
            return

        logger.info("Performing memory cleanup...")

        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        # Force garbage collection
        gc.collect()

        self.last_cleanup = current_time
        logger.info("Memory cleanup completed")

    def get_model_info(self) -> dict[str, Any]:
        """Get model status and information"""
        return {
            "model_path": self.model_path,
            "tokenizer_path": self.tokenizer_path,
            "device": self.device,
            "models_loaded": self.model_client is not None,
            "voice_prompts_available": len(self.get_voice_suggestions()) if _voice_prompts_cache else 0,
            "memory_cleanup_threshold": _memory_cleanup_threshold,
        }


class S3Uploader:
    """Handles S3 uploads with error handling"""

    def __init__(self):
        self.s3_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize S3 client with credentials from environment"""
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    async def upload_audio(self, audio_data: torch.Tensor, sample_rate: int, bucket: str, key: str) -> str:
        """Upload audio data to S3"""
        try:
            # Convert audio to bytes
            audio_bytes = BytesIO()
            sf.write(audio_bytes, audio_data, sample_rate)
            audio_bytes.seek(0)

            # Upload to S3
            upload_start = time.time()
            self.s3_client.put_object(Bucket=bucket, Key=key, Body=audio_bytes.getvalue(), ContentType="audio/wav")
            upload_time = time.time() - upload_start

            url = f"s3://{bucket}/{key}"
            logger.info(f"Audio uploaded to S3 in {upload_time:.2f}s: {url}")

            return url

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    def validate_bucket_access(self, bucket: str) -> bool:
        """Validate S3 bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=bucket)
            return True
        except Exception as e:
            logger.error(f"Bucket access validation failed: {e}")
            return False


class AudioGenerator:
    """Handles audio generation with voice cloning and tone control"""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.voice_prompts_path = VOICE_PROMPTS_PATH

    async def generate_audio(self, request: GenerationRequest) -> dict[str, Any]:
        """Generate audio with given parameters"""

        # Normalize transcript
        transcript = normalize_chinese_punctuation(request.transcript)

        # Extract speaker tags if present
        import re

        pattern = re.compile(r"\[(SPEAKER\d+)\]")
        speaker_tags = sorted(set(pattern.findall(transcript)))

        # Additional text normalization
        transcript = transcript.replace("(", " ")
        transcript = transcript.replace(")", " ")
        transcript = transcript.replace("°F", " degrees Fahrenheit")
        transcript = transcript.replace("°C", " degrees Celsius")

        # Apply sound effect replacements
        for tag, replacement in [
            ("[laugh]", "<SE>[Laughter]</SE>"),
            ("[humming start]", "<SE_s>[Humming]</SE_s>"),
            ("[humming end]", "<SE_e>[Humming]</SE_e>"),
            ("[music start]", "<SE_s>[Music]</SE_s>"),
            ("[music end]", "<SE_e>[Music]</SE_e>"),
            ("[music]", "<SE>[Music]</SE>"),
            ("[sing start]", "<SE_s>[Singing]</SE_s>"),
            ("[sing end]", "<SE_e>[Singing]</SE_e>"),
            ("[applause]", "<SE>[Applause]</SE>"),
            ("[cheering]", "<SE>[Cheering]</SE>"),
            ("[cough]", "<SE>[Cough]</SE>"),
        ]:
            transcript = transcript.replace(tag, replacement)

        # Clean up lines
        lines = transcript.split("\n")
        transcript = "\n".join([" ".join(line.split()) for line in lines if line.strip()])
        transcript = transcript.strip()

        # Add period if not ending with punctuation
        if not any([transcript.endswith(c) for c in [".", "!", "?", ",", ";", '"', "'", "</SE_e>", "</SE>"]]):
            transcript += "."

        # Prepare generation context
        messages, audio_ids = prepare_generation_context(
            scene_prompt=request.scene_prompt,
            ref_audio=request.ref_audio,
            ref_audio_in_system_message=True,  # Use system message for voice clarity
            audio_tokenizer=self.model_manager.audio_tokenizer,
            speaker_tags=speaker_tags,
        )

        # Prepare text chunking
        chunked_text = prepare_chunk_text(
            transcript,
            chunk_method=request.chunk_method,
            chunk_max_word_num=request.chunk_max_word_num,
            chunk_max_num_turns=request.chunk_max_num_turns,
        )

        logger.info(f"Generating audio with {len(chunked_text)} chunks")

        # Generate audio
        generation_start = time.time()
        concat_wv, sr, text_output = self.model_manager.model_client.generate(
            messages=messages,
            audio_ids=audio_ids,
            chunked_text=chunked_text,
            generation_chunk_buffer_size=None,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            ras_win_len=request.ras_win_len,
            ras_win_max_num_repeat=request.ras_win_max_num_repeat,
            seed=request.seed,
        )
        generation_time = time.time() - generation_start

        # Calculate duration
        duration_seconds = len(concat_wv) / sr

        return {
            "audio_data": concat_wv,
            "sample_rate": sr,
            "text_output": text_output,
            "duration_seconds": duration_seconds,
            "generation_time": generation_time,
            "chunks_processed": len(chunked_text),
        }


class RequestValidator:
    """Validates input requests"""

    def __init__(self, max_transcript_length: int = 10000):
        self.max_transcript_length = max_transcript_length

    def validate_generation_request(self, request_data: dict) -> tuple[bool, list[str]]:
        """Validate generation request and return (is_valid, errors)"""
        errors = []

        # Check required fields
        if "transcript" not in request_data:
            errors.append("Missing required field: transcript")
        elif not isinstance(request_data["transcript"], str):
            errors.append("transcript must be a string")
        elif len(request_data["transcript"]) > self.max_transcript_length:
            errors.append(f"transcript too long: max {self.max_transcript_length} characters")
        elif not request_data["transcript"].strip():
            errors.append("transcript cannot be empty")

        # Validate optional fields
        if "temperature" in request_data:
            temp = request_data["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                errors.append("temperature must be between 0 and 2")

        if "top_k" in request_data:
            top_k = request_data["top_k"]
            if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
                errors.append("top_k must be between 1 and 100")

        if "top_p" in request_data:
            top_p = request_data["top_p"]
            if not isinstance(top_p, (int, float)) or top_p <= 0 or top_p > 1:
                errors.append("top_p must be between 0 and 1")

        if "max_new_tokens" in request_data:
            max_tokens = request_data["max_new_tokens"]
            if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4096:
                errors.append("max_new_tokens must be between 1 and 4096")

        return len(errors) == 0, errors


class ServerlessHandler:
    """Main serverless handler"""

    def __init__(self):
        self.model_manager = ModelManager()
        self.s3_uploader = S3Uploader()
        self.audio_generator = AudioGenerator(self.model_manager)
        self.request_validator = RequestValidator()
        self.initialized = False

    async def initialize(self):
        """Initialize the handler"""
        if not self.initialized:
            await self.model_manager.initialize()
            self.initialized = True

    async def handle_request(self, event: dict) -> dict:
        """Handle incoming RunPod serverless request"""
        try:
            # Parse input
            input_data = event.get("input", {})

            # Validate request
            is_valid, validation_errors = self.request_validator.validate_generation_request(input_data)
            if not is_valid:
                return {
                    "output": GenerationResponse(
                        success=False, error=f"Validation failed: {'; '.join(validation_errors)}"
                    ).__dict__
                }

            # Create request object
            request = GenerationRequest(**input_data)

            # Initialize models if needed
            await self.initialize()

            # Generate audio
            generation_result = await self.audio_generator.generate_audio(request)

            # Handle S3 upload if requested
            audio_url = None
            if request.s3_bucket and request.s3_key:
                try:
                    audio_url = await self.s3_uploader.upload_audio(
                        generation_result["audio_data"],
                        generation_result["sample_rate"],
                        request.s3_bucket,
                        request.s3_key,
                    )
                except Exception as e:
                    logger.error(f"S3 upload failed: {e}")
                    # Continue with local result

            # Prepare response
            response = GenerationResponse(
                success=True,
                audio_url=audio_url,
                duration_seconds=generation_result["duration_seconds"],
                sample_rate=generation_result["sample_rate"],
                text_output=generation_result["text_output"],
                metadata={
                    "model_used": MODEL_PATH,
                    "voice_clone": request.ref_audio,
                    "generation_parameters": {
                        "temperature": request.temperature,
                        "top_k": request.top_k,
                        "top_p": request.top_p,
                        "generation_time": generation_result["generation_time"],
                        "chunks_processed": generation_result["chunks_processed"],
                    },
                },
                voice_suggestions=self.model_manager.get_voice_suggestions(),
            )

            # Perform memory cleanup if needed
            self.model_manager.cleanup_memory()

            return {"output": response.__dict__}

        except Exception as e:
            logger.error(f"Request handling failed: {e}")
            return {"output": GenerationResponse(success=False, error=f"Internal error: {str(e)}").__dict__}

    async def handle_health_check(self) -> dict:
        """Handle health check requests"""
        try:
            model_info = self.model_manager.get_model_info()

            return {
                "status": "healthy",
                "timestamp": time.time(),
                "model_info": model_info,
                "voice_suggestions": self.model_manager.get_voice_suggestions(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}


# Initialize global handler
handler = ServerlessHandler()


async def handler_function(event: dict) -> dict:
    """Main handler function for RunPod serverless"""

    # Handle different request types
    if event.get("path") == "/health" or event.get("health_check"):
        return await handler.handle_health_check()

    # Handle generation requests
    return await handler.handle_request(event)


def run_handler(event: dict) -> dict:
    """Synchronous handler wrapper for RunPod"""
    import asyncio

    try:
        return asyncio.run(handler_function(event))
    except Exception as e:
        logger.error(f"Handler execution failed: {e}")
        return {"output": GenerationResponse(success=False, error=f"Handler execution failed: {str(e)}").__dict__}


if __name__ == "__main__":
    # For local testing
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            test_event = json.load(f)
            result = run_handler(test_event)
            print(json.dumps(result, indent=2))
    else:
        print("RunPod Serverless Handler for Higgs Audio V2")
        print("Usage: python serverless_handler.py <test_event.json>")
        print("Available voices:")
        for voice in ModelManager().get_voice_suggestions():
            print(f"  - {voice['name']}: {voice['description']}")
