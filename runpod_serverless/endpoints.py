"""
Endpoint handlers for different types of audio generation requests.
Each endpoint corresponds to examples in the main codebase.
"""

import os
import yaml
import numpy as np
import soundfile as sf
import tempfile
from typing import Dict, Any, Optional, List
from loguru import logger

from .model_loader import get_serve_engine
from .config import get_config, get_voice_prompt_path, get_voice_text_path, get_scene_prompt_path

from boson_multimodal.data_types import Message, ChatMLSample, AudioContent, TextContent
from boson_multimodal.serve.serve_engine import HiggsAudioResponse


def load_voice_prompt(voice_id: str) -> tuple[Optional[np.ndarray], Optional[str], Optional[int]]:
    """
    Load voice prompt audio and text for voice cloning.

    Args:
        voice_id: Voice identifier

    Returns:
        Tuple of (audio_array, text, sampling_rate)
    """
    try:
        # Get paths
        audio_path = get_voice_prompt_path(voice_id)
        text_path = get_voice_text_path(voice_id)

        if not audio_path:
            logger.warning(f"Voice audio not found for: {voice_id}")
            return None, None, None

        # Load audio
        audio, sr = sf.read(audio_path)

        # Load text if available
        text = None
        if text_path:
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read().strip()

        logger.info(f"Loaded voice prompt: {voice_id} (audio: {audio.shape}, sr: {sr})")
        return audio, text, sr

    except Exception as e:
        logger.error(f"Failed to load voice prompt {voice_id}: {e}")
        return None, None, None


def handle_text_to_speech(text: str, voice_id: Optional[str], options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle basic text-to-speech generation.
    Based on examples/generation.py basic TTS functionality.

    Args:
        text: Text to convert to speech
        voice_id: Optional voice identifier for the speaker
        options: Additional generation options

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        serve_engine = get_serve_engine()
        config = get_config()

        # Prepare generation options
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # Create ChatML sample for TTS
        messages = [
            Message(
                role="system",
                content=[TextContent(text="You are an AI assistant designed to convert text into speech.")],
            ),
            Message(role="user", content=[TextContent(text=text)]),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating TTS for text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "voice_id": voice_id,
                "generation_options": generation_options,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise


def handle_voice_cloning(text: str, voice_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle zero-shot voice cloning generation.
    Based on examples/generation.py voice cloning functionality.

    Args:
        text: Text to convert to speech
        voice_id: Voice identifier for cloning
        options: Additional generation options

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        if not voice_id:
            raise ValueError("voice_id is required for voice cloning")

        serve_engine = get_serve_engine()
        config = get_config()

        # Load voice prompt
        voice_audio, voice_text, voice_sr = load_voice_prompt(voice_id)
        if voice_audio is None:
            available_voices = config["voice_prompts"]["available_voices"]
            raise ValueError(f"Voice '{voice_id}' not found. Available voices: {available_voices}")

        # Prepare generation options
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # Create ChatML sample with voice reference
        messages = [
            Message(
                role="system",
                content=[
                    TextContent(
                        text="You are an AI assistant designed to convert text into speech using the provided voice reference."
                    )
                ],
            ),
            Message(
                role="user",
                content=[
                    TextContent(text=f"Please generate speech for: {text}"),
                    AudioContent(audio=voice_audio, sampling_rate=voice_sr),
                ],
            ),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating voice cloning for voice: {voice_id}, text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "voice_id": voice_id,
                "voice_text": voice_text,
                "generation_options": generation_options,
                "reference_audio_shape": voice_audio.shape,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise


def handle_multi_speaker(text: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle multi-speaker dialog generation.
    Based on examples/transcript/multi_speaker/ functionality.

    Args:
        text: Text containing speaker tags (e.g., [SPEAKER1], [SPEAKER2])
        options: Additional generation options

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        serve_engine = get_serve_engine()
        config = get_config()

        # Prepare generation options
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # System message for multi-speaker
        system_message = """You are an AI assistant designed to convert text into speech.
If the user's message includes a [SPEAKER*] tag, do not read out the tag and generate speech for the following text, using the specified voice.
If no speaker tag is present, select a suitable voice on your own."""

        # Create ChatML sample for multi-speaker
        messages = [
            Message(role="system", content=[TextContent(text=system_message)]),
            Message(role="user", content=[TextContent(text=text)]),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating multi-speaker dialog for text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "type": "multi_speaker",
                "generation_options": generation_options,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"Multi-speaker generation failed: {e}")
        raise


def handle_vllm(text: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle vLLM high-throughput generation.
    Based on examples/vllm/ functionality.

    Args:
        text: Text to convert to speech
        options: Additional generation options including vLLM-specific settings

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        # This is a placeholder for vLLM integration
        # In a full implementation, this would use the vLLM OpenAI-compatible API
        # For now, we'll use the regular serve engine

        serve_engine = get_serve_engine()
        config = get_config()

        # Prepare generation options (vLLM may have different parameters)
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # Create ChatML sample
        messages = [
            Message(
                role="system",
                content=[
                    TextContent(
                        text="You are an AI assistant designed to convert text into speech with high throughput."
                    )
                ],
            ),
            Message(role="user", content=[TextContent(text=text)]),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating vLLM high-throughput audio for text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "type": "vllm",
                "generation_options": generation_options,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"vLLM generation failed: {e}")
        raise


def handle_scene_based(text: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle scene-based generation with environmental context.
    Based on examples/scene_prompts/ functionality.

    Args:
        text: Text to convert to speech
        options: Additional generation options including scene_id

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        serve_engine = get_serve_engine()
        config = get_config()

        # Get scene context
        scene_id = options.get("scene_id", "quiet_indoor")
        scene_path = get_scene_prompt_path(scene_id)
        scene_context = ""

        if scene_path:
            with open(scene_path, "r", encoding="utf-8") as f:
                scene_context = f.read().strip()
            logger.info(f"Loaded scene context: {scene_id}")
        else:
            logger.warning(f"Scene context not found: {scene_id}")

        # Prepare generation options
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # Create ChatML sample with scene context
        system_message = f"""You are an AI assistant designed to convert text into speech with environmental awareness.
Scene context: {scene_context}

Generate speech that is appropriate for the given scene and context."""

        messages = [
            Message(role="system", content=[TextContent(text=system_message)]),
            Message(role="user", content=[TextContent(text=text)]),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating scene-based audio for scene: {scene_id}, text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "type": "scene_based",
                "scene_id": scene_id,
                "scene_context": scene_context,
                "generation_options": generation_options,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"Scene-based generation failed: {e}")
        raise


def handle_experimental(text: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle experimental features like BGM and humming.
    Based on examples/transcript/single_speaker/experimental/ functionality.

    Args:
        text: Text to convert to speech (may include special markers)
        options: Additional generation options including experimental_type

    Returns:
        Dictionary containing generated audio and metadata
    """
    try:
        serve_engine = get_serve_engine()
        config = get_config()

        experimental_type = options.get("experimental_type", "bgm")

        # Prepare generation options
        generation_options = {
            "max_new_tokens": options.get("max_new_tokens", config["generation"]["max_new_tokens"]),
            "temperature": options.get("temperature", config["generation"]["temperature"]),
            "do_sample": options.get("do_sample", config["generation"]["do_sample"]),
        }

        # Create system message based on experimental type
        if experimental_type == "bgm":
            system_message = """You are an AI assistant that can generate speech with background music.
Generate speech for the provided text and include appropriate background music where indicated."""
        elif experimental_type == "humming":
            system_message = """You are an AI assistant that can generate speech with humming and musical elements.
Generate speech for the provided text and include humming or musical interludes where appropriate."""
        else:
            system_message = """You are an AI assistant with experimental audio generation capabilities.
Generate creative audio content based on the provided text."""

        # Create ChatML sample
        messages = [
            Message(role="system", content=[TextContent(text=system_message)]),
            Message(role="user", content=[TextContent(text=text)]),
        ]

        sample = ChatMLSample(messages=messages)

        logger.info(f"Generating experimental audio ({experimental_type}) for text length: {len(text)}")

        # Generate audio
        response: HiggsAudioResponse = serve_engine.generate(sample=sample, **generation_options)

        return {
            "audio": response.audio,
            "text": response.generated_text,
            "sampling_rate": response.sampling_rate,
            "metadata": {
                "type": "experimental",
                "experimental_type": experimental_type,
                "generation_options": generation_options,
                "audio_shape": response.audio.shape if response.audio is not None else None,
            },
        }

    except Exception as e:
        logger.error(f"Experimental generation failed: {e}")
        raise
