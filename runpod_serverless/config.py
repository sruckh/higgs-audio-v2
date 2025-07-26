"""
Configuration management for Runpod serverless deployment.
Handles environment variables and default settings.
"""

import os
from typing import Dict, Any, Optional
from loguru import logger


def get_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables with defaults.

    Returns:
        Configuration dictionary
    """
    config = {
        # Model configuration
        "model": {
            "model_name_or_path": os.getenv("MODEL_NAME_OR_PATH", "sruckh/higgs-audio-v2"),
            "audio_tokenizer_name_or_path": os.getenv("AUDIO_TOKENIZER_NAME_OR_PATH", "sruckh/higgs-audio-v2"),
            "tokenizer_name_or_path": os.getenv("TOKENIZER_NAME_OR_PATH", None),
            "device": os.getenv("DEVICE", "cuda"),
            "torch_dtype": os.getenv("TORCH_DTYPE", "auto"),
        },
        # Generation defaults
        "generation": {
            "max_new_tokens": int(os.getenv("MAX_NEW_TOKENS", "1024")),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "do_sample": os.getenv("DO_SAMPLE", "true").lower() == "true",
            "sampling_rate": int(os.getenv("SAMPLING_RATE", "24000")),
        },
        # Performance settings
        "performance": {
            "kv_cache_lengths": [1024, 4096, 8192],  # Multiple KV cache sizes
            "enable_cuda_graphs": os.getenv("ENABLE_CUDA_GRAPHS", "true").lower() == "true",
            "batch_size": int(os.getenv("BATCH_SIZE", "1")),
        },
        # Voice prompts configuration
        "voice_prompts": {
            "voice_prompts_dir": os.getenv("VOICE_PROMPTS_DIR", "/app/examples/voice_prompts"),
            "default_voice": os.getenv("DEFAULT_VOICE", "en_woman"),
            "available_voices": [
                "en_woman",
                "en_man",
                "belinda",
                "bigbang_amy",
                "bigbang_sheldon",
                "broom_salesman",
                "chadwick",
                "fiftyshades_anna",
                "mabaoguo",
                "mabel",
                "shrek_donkey",
                "shrek_fiona",
                "shrek_shrek",
                "vex",
                "zh_man_sichuan",
            ],
        },
        # Scene prompts configuration
        "scene_prompts": {
            "scene_prompts_dir": os.getenv("SCENE_PROMPTS_DIR", "/app/examples/scene_prompts"),
            "available_scenes": ["quiet_indoor", "reading_blog"],
        },
        # Storage configuration
        "storage": {
            "temp_dir": os.getenv("TEMP_DIR", "/tmp"),
            "output_format": os.getenv("OUTPUT_FORMAT", "wav"),
            "max_audio_length_seconds": int(os.getenv("MAX_AUDIO_LENGTH_SECONDS", "300")),  # 5 minutes
        },
        # Logging configuration
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "{time} | {level} | {message}"),
        },
        # Security and limits
        "limits": {
            "max_text_length": int(os.getenv("MAX_TEXT_LENGTH", "10000")),
            "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")),
            "request_timeout_seconds": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "300")),
        },
        # vLLM specific configuration
        "vllm": {
            "enable_vllm": os.getenv("ENABLE_VLLM", "false").lower() == "true",
            "vllm_host": os.getenv("VLLM_HOST", "localhost"),
            "vllm_port": int(os.getenv("VLLM_PORT", "8000")),
            "openai_api_key": os.getenv("OPENAI_API_KEY", "EMPTY"),
            "openai_api_base": os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1"),
        },
    }

    return config


def validate_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the configuration for common issues.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required paths exist if they're local
        voice_prompts_dir = config["voice_prompts"]["voice_prompts_dir"]
        if voice_prompts_dir.startswith("/") and not os.path.exists(voice_prompts_dir):
            return False, f"Voice prompts directory does not exist: {voice_prompts_dir}"

        # Check numeric values are reasonable
        max_tokens = config["generation"]["max_new_tokens"]
        if max_tokens <= 0 or max_tokens > 10000:
            return False, f"max_new_tokens must be between 1 and 10000, got {max_tokens}"

        temperature = config["generation"]["temperature"]
        if temperature < 0 or temperature > 2.0:
            return False, f"temperature must be between 0 and 2.0, got {temperature}"

        sampling_rate = config["generation"]["sampling_rate"]
        if sampling_rate not in [16000, 22050, 24000, 44100, 48000]:
            logger.warning(f"Unusual sampling rate: {sampling_rate}")

        return True, None

    except Exception as e:
        return False, f"Configuration validation error: {str(e)}"


def print_config(config: Optional[Dict[str, Any]] = None):
    """
    Print the current configuration for debugging.

    Args:
        config: Optional config to print. Gets current config if None.
    """
    if config is None:
        config = get_config()

    logger.info("Current configuration:")
    for section, values in config.items():
        logger.info(f"  [{section}]")
        for key, value in values.items():
            # Mask sensitive values
            if "key" in key.lower() or "token" in key.lower():
                display_value = "*" * len(str(value)) if value else "None"
            else:
                display_value = value
            logger.info(f"    {key}: {display_value}")


def get_voice_prompt_path(voice_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get the full path to a voice prompt file.

    Args:
        voice_id: Voice identifier
        config: Optional configuration. Gets current config if None.

    Returns:
        Path to voice prompt file or None if not found
    """
    if config is None:
        config = get_config()

    voice_dir = config["voice_prompts"]["voice_prompts_dir"]

    # Try with .wav extension
    wav_path = os.path.join(voice_dir, f"{voice_id}.wav")
    if os.path.exists(wav_path):
        return wav_path

    # Try without extension (in case it's already included)
    direct_path = os.path.join(voice_dir, voice_id)
    if os.path.exists(direct_path):
        return direct_path

    return None


def get_voice_text_path(voice_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get the full path to a voice text file.

    Args:
        voice_id: Voice identifier
        config: Optional configuration. Gets current config if None.

    Returns:
        Path to voice text file or None if not found
    """
    if config is None:
        config = get_config()

    voice_dir = config["voice_prompts"]["voice_prompts_dir"]

    # Try with .txt extension
    txt_path = os.path.join(voice_dir, f"{voice_id}.txt")
    if os.path.exists(txt_path):
        return txt_path

    return None


def get_scene_prompt_path(scene_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get the full path to a scene prompt file.

    Args:
        scene_id: Scene identifier
        config: Optional configuration. Gets current config if None.

    Returns:
        Path to scene prompt file or None if not found
    """
    if config is None:
        config = get_config()

    scene_dir = config["scene_prompts"]["scene_prompts_dir"]

    # Try with .txt extension
    txt_path = os.path.join(scene_dir, f"{scene_id}.txt")
    if os.path.exists(txt_path):
        return txt_path

    return None


# Initialize logging on module import
def setup_logging():
    """Setup logging configuration based on environment variables."""
    config = get_config()
    log_level = config["logging"]["level"]

    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(sink=lambda msg: print(msg, end=""), level=log_level, format=config["logging"]["format"])


# Setup logging when module is imported
setup_logging()
