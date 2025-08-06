"""
RunPod Serverless Handler for Higgs Audio V2 - Optimized Version

Ultra-optimized serverless endpoint for audio generation with voice cloning,
LLM tone control, and S3 output storage. Optimized for <5GB container size.
"""

import gc
import json
import os
import sys
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import boto3
import soundfile as sf
import torch
from loguru import logger

from boson_multimodal.audio_processing.higgs_audio_tokenizer import load_higgs_audio_tokenizer

# Import only what's needed for serverless
from boson_multimodal.model.higgs_audio.modeling_higgs_audio import HiggsAudioModel


# Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-generation-3B-base")
TOKENIZER_PATH = os.getenv("TOKENIZER_PATH", "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-tokenizer")
VOICE_PROMPTS_PATH = os.getenv("VOICE_PROMPTS_PATH", "/runpod-volume/higgs_audio/voice_prompts")

# Global cache for optimized memory usage
_model_cache = None
_audio_tokenizer_cache = None
_voice_prompts_cache = None


@dataclass
class OptimizedGenerationRequest:
    """Optimized request data model"""

    transcript: str
    ref_audio: str | None = None
    scene_prompt: str | None = None
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.95
    max_new_tokens: int = 2048
    s3_bucket: str | None = None
    s3_key: str | None = None


@dataclass
class OptimizedGenerationResponse:
    """Optimized response data model"""

    success: bool
    audio_url: str | None = None
    duration_seconds: float | None = None
    sample_rate: int = 24000
    text_output: str | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None


class OptimizedModelManager:
    """Optimized model manager with lazy loading"""

    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.audio_tokenizer = None
        self.initialized = False

    async def initialize(self):
        """Initialize models with lazy loading"""
        global _model_cache, _audio_tokenizer_cache

        if not self.initialized:
            # Load audio tokenizer first
            if _audio_tokenizer_cache is None:
                logger.info("Loading audio tokenizer...")
                _audio_tokenizer_cache = load_higgs_audio_tokenizer(TOKENIZER_PATH, device=self.device)
            self.audio_tokenizer = _audio_tokenizer_cache

            # Load model with optimizations
            if _model_cache is None:
                logger.info("Loading model...")
                _model_cache = HiggsAudioModel.from_pretrained(
                    MODEL_PATH,
                    device_map={"": self.device},
                    torch_dtype=torch.bfloat16,
                    low_cpu_mem_usage=True,
                )
                # Enable inference optimizations
                _model_cache.eval()
                if "cuda" in self.device:
                    _model_cache = torch.compile(_model_cache, mode="reduce-overhead")

            self.model = _model_cache
            self.initialized = True
            logger.info("Optimized models loaded successfully")

    def cleanup_memory(self):
        """Aggressive memory cleanup"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        gc.collect()


class OptimizedS3Uploader:
    """Optimized S3 uploader"""

    def __init__(self):
        self.s3_client = None
        self._init_client()

    def _init_client(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            )
        except Exception as e:
            logger.error(f"S3 client init failed: {e}")

    async def upload_audio(self, audio_data, sample_rate: int, bucket: str, key: str) -> str:
        """Upload audio to S3"""
        try:
            audio_bytes = BytesIO()
            sf.write(audio_bytes, audio_data, sample_rate)
            audio_bytes.seek(0)

            self.s3_client.put_object(Bucket=bucket, Key=key, Body=audio_bytes.getvalue(), ContentType="audio/wav")

            return f"s3://{bucket}/{key}"
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise


class OptimizedAudioGenerator:
    """Optimized audio generation"""

    def __init__(self, model_manager: OptimizedModelManager):
        self.model_manager = model_manager

    async def generate_audio(self, request: OptimizedGenerationRequest) -> dict[str, Any]:
        """Generate audio with optimized workflow"""

        if not self.model_manager.initialized:
            await self.model_manager.initialize()

        # Prepare input text with optimizations
        normalized_text = self._normalize_text(request.transcript)

        # Build generation context
        messages = self._build_messages(request.scene_prompt, request.ref_audio)

        # Generate audio with memory optimization
        with torch.no_grad():
            if "cuda" in self.model_manager.device:
                torch.cuda.empty_cache()

            # Use model.generate() directly with bfloat16 precision
            inputs = {
                "messages": messages,
                "temperature": request.temperature,
                "top_k": request.top_k,
                "top_p": request.top_p,
                "max_new_tokens": request.max_new_tokens,
            }

            outputs = self.model_manager.model.generate(**inputs)

            # Process outputs
            audio_data = outputs.get("audio", torch.tensor([]))
            text_output = outputs.get("text", normalized_text)

        return {
            "audio_data": audio_data,
            "sample_rate": 24000,
            "text_output": text_output,
            "duration_seconds": len(audio_data) / 24000 if len(audio_data) > 0 else 0.0,
        }

    def _normalize_text(self, text: str) -> str:
        """Optimized text normalization"""
        # Basic cleaning
        text = text.replace("(", " ").replace(")", " ")
        text = text.replace("°F", " degrees Fahrenheit")
        text = text.replace("°C", " degrees Celsius")

        # Clean up lines
        lines = text.split("\n")
        text = "\n".join([" ".join(line.split()) for line in lines if line.strip()])
        text = text.strip()

        # Add period if needed
        if text and not any([text.endswith(c) for c in [".", "!", "?", ",", ";", '"', "'"]]):
            text += "."

        return text

    def _build_messages(self, scene_prompt: str | None, ref_audio: str | None) -> list[dict]:
        """Build message list"""
        messages = []

        if scene_prompt:
            messages.append({"role": "system", "content": f"Scene: {scene_prompt}. Generate appropriate speech."})

        if ref_audio and ref_audio != "default":
            messages.append({"role": "user", "content": f"Voice reference: {ref_audio}"})

        return messages


class OptimizedValidator:
    """Optimized request validation"""

    def validate_request(self, request_data: dict) -> tuple[bool, list[str]]:
        """Validate request with minimal checks"""
        errors = []

        # Essential checks only
        if "transcript" not in request_data:
            errors.append("Missing required field: transcript")
        elif not isinstance(request_data["transcript"], str) or not request_data["transcript"].strip():
            errors.append("transcript must be a non-empty string")

        # Temperature validation
        if "temperature" in request_data:
            temp = request_data["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                errors.append("temperature must be between 0 and 2")

        return len(errors) == 0, errors


class OptimizedHandler:
    """Main optimized handler"""

    def __init__(self):
        self.model_manager = OptimizedModelManager()
        self.s3_uploader = OptimizedS3Uploader()
        self.audio_generator = OptimizedAudioGenerator(self.model_manager)
        self.validator = OptimizedValidator()

    async def handle_generation(self, event: dict) -> dict:
        """Handle generation request"""
        try:
            input_data = event.get("input", {})

            # Validate input
            is_valid, errors = self.validator.validate_request(input_data)
            if not is_valid:
                return {
                    "output": OptimizedGenerationResponse(
                        success=False, error=f"Validation failed: {'; '.join(errors)}"
                    ).__dict__
                }

            # Create optimized request
            request = OptimizedGenerationRequest(**input_data)

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
                    logger.warning(f"S3 upload failed: {e}")
                    # Continue without S3

            # Prepare response
            response = OptimizedGenerationResponse(
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
                    },
                },
            )

            # Memory cleanup
            self.model_manager.cleanup_memory()

            return {"output": response.__dict__}

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {"output": OptimizedGenerationResponse(success=False, error=f"Generation error: {str(e)}").__dict__}

    async def handle_health(self) -> dict:
        """Handle health check"""
        try:
            # Validate virtual environment setup
            venv_path = "/runpod-volume/higgs"
            venv_python = f"{venv_path}/bin/python"
            
            # Check if virtual environment exists and is accessible
            venv_valid = (
                os.path.exists(venv_path) and 
                os.path.exists(venv_python) and
                sys.path[0].startswith(venv_path) and
                os.environ.get("VIRTUAL_ENV") == venv_path
            )
            
            # Check if Python packages are accessible in virtual environment
            packages_accessible = True
            try:
                import torch
                import soundfile
                import transformers
                import loguru
                logger.info(f"Virtual environment packages accessible - PyTorch: {torch.__version__}")
            except ImportError as e:
                packages_accessible = False
                logger.error(f"Virtual environment package access failed: {e}")
            
            health_status = "healthy" if (venv_valid and packages_accessible) else "unhealthy"
            
            return {
                "status": health_status,
                "timestamp": time.time(),
                "models_loaded": self.model_manager.initialized,
                "device": self.model_manager.device,
                "container_optimized": True,
                "virtual_environment": {
                    "valid": venv_valid,
                    "path": venv_path,
                    "packages_accessible": packages_accessible,
                    "sys_path_prefix": sys.path[0],
                    "virtual_env_var": os.environ.get("VIRTUAL_ENV")
                }
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}


# Global optimized handler
optimized_handler = OptimizedHandler()


async def handler(event: dict) -> dict:
    """Main handler for RunPod serverless - optimized version"""

    # Route request
    if event.get("path") == "/health" or event.get("health_check"):
        return await optimized_handler.handle_health()

    return await optimized_handler.handle_generation(event)


def run_handler(event: dict) -> dict:
    """Synchronous wrapper for RunPod"""
    import asyncio

    try:
        return asyncio.run(handler(event))
    except Exception as e:
        logger.error(f"Handler execution failed: {e}")
        return {"output": OptimizedGenerationResponse(success=False, error=f"Handler error: {str(e)}").__dict__}


if __name__ == "__main__":
    # For local testing
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            test_event = json.load(f)
            result = run_handler(test_event)
            print(json.dumps(result, indent=2))
    else:
        print("RunPod Serverless Handler - Optimized for Higgs Audio V2")
        print("Container size: <5GB")
        print("Usage: python serverless_handler_optimized.py <test_event.json>")
