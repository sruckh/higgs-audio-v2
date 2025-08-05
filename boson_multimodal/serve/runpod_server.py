"""
RunPod Serverless Handler for Higgs Audio V2

This module provides a RunPod-compatible HTTP API server for Higgs Audio V2
with serverless deployment, S3 integration, and one-shot voice cloning.
"""

import base64
import io
import os
import traceback
from typing import Any

import boto3
import runpod
import soundfile as sf
import torch
from loguru import logger
from runpod.serverless.utils.rp_validator import validate

from boson_multimodal.audio_processing.higgs_audio_tokenizer import load_higgs_audio_tokenizer
from boson_multimodal.data_collator.higgs_audio_collator import HiggsAudioSampleCollator
from boson_multimodal.data_types import ChatMLSample, Message, TextContent
from boson_multimodal.model.higgs_audio import HiggsAudioModel
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
from boson_multimodal.serve.voice_prompts import LLMToneController, VoicePromptManager


class RunPodHiggsAudioServer:
    """
    RunPod serverless handler for Higgs Audio V2 with extreme optimization
    for <5GB container size and network volume model storage.
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.audio_tokenizer = None
        self.collator = None
        self.serve_engine = None
        self.voice_prompts_path = "/app/voice_prompts"
        self.network_volume_path = "/runpod-volume/higgs_audio"
        self.s3_client = None

        # Initialize managers
        self.voice_manager = VoicePromptManager(self.voice_prompts_path)
        self.tone_controller = LLMToneController()

        # Initialize models (lazy loading)
        self._model_loaded = False
        self._init_s3_client()

    def _init_s3_client(self):
        """Initialize S3 client from environment variables."""
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            )
            logger.info("S3 client initialized")
        else:
            logger.warning("S3 credentials not found in environment variables")

    def _load_models_if_needed(self):
        """Lazy load models only when needed."""
        if not self._model_loaded:
            logger.info("Loading Higgs Audio models from network volume...")

            model_path = f"{self.network_volume_path}/bosonai/higgs-audio-v2-generation-3B-base"
            tokenizer_path = f"{self.network_volume_path}/bosonai/higgs-audio-v2-tokenizer"

            # Detect device
            if torch.cuda.is_available():
                device = "cuda:0"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

            logger.info(f"Using device: {device}")

            # Load audio tokenizer (CPU for MPS compatibility)
            audio_tokenizer_device = "cpu" if device == "mps" else device
            self.audio_tokenizer = load_higgs_audio_tokenizer(tokenizer_path, device=audio_tokenizer_device)

            # Load model
            self.model = HiggsAudioModel.from_pretrained(
                model_path,
                device_map=device,
                torch_dtype=torch.bfloat16,
            )
            self.model.eval()

            # Load tokenizer and config
            from transformers import AutoConfig, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            config = AutoConfig.from_pretrained(model_path)

            # Initialize collator
            self.collator = HiggsAudioSampleCollator(
                whisper_processor=None,
                audio_in_token_id=config.audio_in_token_idx,
                audio_out_token_id=config.audio_out_token_idx,
                audio_stream_bos_id=config.audio_stream_bos_id,
                audio_stream_eos_id=config.audio_stream_eos_id,
                encode_whisper_embed=config.encode_whisper_embed,
                pad_token_id=config.pad_token_id,
                return_audio_in_tokens=config.encode_audio_in_tokens,
                use_delay_pattern=config.use_delay_pattern,
                round_to=1,
                audio_num_codebooks=config.audio_num_codebooks,
            )

            # Initialize serve engine
            self.serve_engine = HiggsAudioServeEngine(
                model_path=model_path,
                audio_tokenizer=audio_tokenizer_device,
                max_new_tokens=2048,
                use_static_kv_cache=True,
                kv_cache_lengths=[512, 1024, 2048],
                device=device,
            )

            self._model_loaded = True
            logger.info("Models loaded successfully")

    def _upload_to_s3(self, audio_data: bytes, sample_rate: int, bucket: str, key: str) -> str:
        """Upload audio data to S3 bucket."""
        if not self.s3_client:
            raise ValueError("S3 client not initialized")

        try:
            # Convert to WAV bytes
            audio_buffer = io.BytesIO()

            # Convert numpy array to bytes for soundfile
            import numpy as np

            if isinstance(audio_data, np.ndarray):
                sf.write(audio_buffer, audio_data, sample_rate, format="WAV")
            else:
                audio_buffer.write(audio_data)

            audio_buffer.seek(0)

            # Upload to S3
            self.s3_client.put_object(Bucket=bucket, Key=key, Body=audio_buffer.getvalue(), ContentType="audio/wav")

            s3_url = f"s3://{bucket}/{key}"
            logger.info(f"Audio uploaded to S3: {s3_url}")
            return s3_url

        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise

    def _get_voice_prompt_path(self, ref_audio: str) -> str:
        """Get the voice prompt file path for reference audio."""
        voice_file = f"{self.voice_prompts_path}/{ref_audio}.wav"
        if os.path.exists(voice_file):
            return voice_file

        # Check for text file fallback
        text_file = f"{self.voice_prompts_path}/{ref_audio}.txt"
        if os.path.exists(text_file):
            return text_file

        logger.warning(f"Voice prompt not found for: {ref_audio}")
        return None

    def _prepare_messages(self, transcript: str, ref_audio: str, scene_prompt: str) -> list:
        """Prepare messages for generation."""
        messages = []

        # Add system message with scene prompt for tone control
        system_message = {
            "role": "system",
            "content": f"You are an AI assistant designed to convert text into speech. {scene_prompt}",
        }
        messages.append(system_message)

        # Add reference audio if provided
        if ref_audio:
            voice_path = self._get_voice_prompt_path(ref_audio)
            if voice_path:
                with open(voice_path.replace(".wav", ".txt"), encoding="utf-8") as f:
                    ref_text = f.read().strip()

                ref_message = {"role": "user", "content": f"[SPEAKER:{ref_audio}] {ref_text}"}
                messages.append(ref_message)

        # Add main transcript
        main_message = {"role": "user", "content": transcript}
        messages.append(main_message)

        return messages


# Input validation schema
INPUT_SCHEMA = {
    "transcript": {"type": "string", "required": True, "min": 1, "max": 5000},
    "ref_audio": {"type": "string", "required": False, "default": "en_woman"},
    "scene_prompt": {"type": "string", "required": False, "default": "quiet indoor setting with warm, friendly tone"},
    "temperature": {"type": "number", "required": False, "default": 1.0, "min": 0.1, "max": 2.0},
    "top_p": {"type": "number", "required": False, "default": 0.95, "min": 0.1, "max": 1.0},
    "top_k": {"type": "integer", "required": False, "default": 50, "min": 1, "max": 100},
    "s3_bucket": {"type": "string", "required": False},
    "s3_key": {"type": "string", "required": False},
}


# Global server instance
server = RunPodHiggsAudioServer()


@runpod.serverless.func
def handler(event: dict[str, Any]) -> dict[str, Any]:
    """
    Main RunPod serverless handler function.

    Args:
        event: RunPod event containing input data

    Returns:
        Response dictionary with audio output
    """
    try:
        # Validate input
        validated_input = validate(event["input"], INPUT_SCHEMA)
        if "errors" in validated_input:
            return {"error": "Validation failed", "details": validated_input["errors"]}

        input_data = validated_input["validated_input"]

        # Load models on first request
        server._load_models_if_needed()

        # Enhanced voice selection with suggestions
        ref_audio = input_data["ref_audio"]
        voice_prompt = server.voice_manager.get_voice_prompt(ref_audio)

        # Provide voice suggestions if requested voice not available
        if not voice_prompt:
            suggested_voices = server.voice_manager.suggest_voices_for_prompt(
                input_data["transcript"], input_data["scene_prompt"]
            )
            logger.warning(f"Voice '{ref_audio}' not available. Suggested voices: {suggested_voices}")

            # Use first suggested voice
            if suggested_voices:
                ref_audio = suggested_voices[0]
                logger.info(f"Using suggested voice: {ref_audio}")
            else:
                ref_audio = "en_woman"  # Fallback

        # Prepare messages
        messages = server._prepare_messages(
            transcript=input_data["transcript"], ref_audio=ref_audio, scene_prompt=input_data["scene_prompt"]
        )

        # Add memory management for serverless environment
        if hasattr(server, "_cleanup_memory"):
            server._cleanup_memory()

        # Convert to boson_multimodal format
        boson_messages = []
        for msg in messages:
            boson_messages.append(Message(role=msg["role"], content=TextContent(text=msg["content"])))

        chatml_sample = ChatMLSample(messages=boson_messages)

        # Generate audio
        logger.info(f"Generating audio for transcript: {input_data['transcript'][:50]}...")

        response = server.serve_engine.generate(
            messages=messages,
            temperature=input_data["temperature"],
            top_p=input_data["top_p"],
            top_k=input_data["top_k"],
            max_new_tokens=2048,
        )

        if not response.audio_data or len(response.audio_data) == 0:
            return {"error": "Audio generation failed", "details": "No audio data generated"}

        # Calculate duration
        duration_seconds = len(response.audio_data) / response.sample_rate

        # Handle S3 upload if requested
        audio_url = None
        if input_data.get("s3_bucket") and input_data.get("s3_key"):
            try:
                # Convert to WAV bytes for S3 upload
                audio_buffer = io.BytesIO()
                sf.write(audio_buffer, response.audio_data, response.sample_rate, format="WAV")
                audio_buffer.seek(0)

                audio_url = server._upload_to_s3(
                    audio_data=audio_buffer.getvalue(),
                    sample_rate=response.sample_rate,
                    bucket=input_data["s3_bucket"],
                    key=input_data["s3_key"],
                )
            except Exception as e:
                logger.error(f"S3 upload failed: {str(e)}")
                # Don't fail the request, just return without S3 URL

        # Prepare response
        result = {
            "success": True,
            "audio_url": audio_url,
            "duration_seconds": duration_seconds,
            "sample_rate": response.sample_rate,
            "text_output": input_data["transcript"],
            "metadata": {
                "model_used": "bosonai/higgs-audio-v2-generation-3B-base",
                "voice_clone": input_data["ref_audio"],
                "scene_prompt": input_data["scene_prompt"],
                "generation_parameters": {
                    "temperature": input_data["temperature"],
                    "top_p": input_data["top_p"],
                    "top_k": input_data["top_k"],
                },
            },
        }

        # Add base64 audio data if not using S3
        if not audio_url:
            # Convert to base64 for direct response
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, response.audio_data, response.sample_rate, format="WAV")
            audio_buffer.seek(0)
            result["audio_data_b64"] = base64.b64encode(audio_buffer.getvalue()).decode()

        logger.info(f"Generated {duration_seconds:.2f}s of audio successfully")
        return {"output": result}

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": "Internal server error", "details": str(e)}


if __name__ == "__main__":
    # For local testing
    import uvicorn

    uvicorn.run(handler, host="0.0.0.0", port=8080)
