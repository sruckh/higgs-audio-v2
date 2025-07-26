"""
Model loader with pre-initialization for Runpod serverless deployment.
This module handles model loading and caching to minimize cold start times.
"""

import os
import torch
import gc
from typing import Optional, Dict, Any
from loguru import logger

from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
from boson_multimodal.model.higgs_audio import HiggsAudioModel
from boson_multimodal.audio_processing.higgs_audio_tokenizer import load_higgs_audio_tokenizer
from transformers import AutoTokenizer


class ModelLoader:
    """
    Singleton class for managing model pre-loading and caching in serverless environment.
    """

    _instance = None
    _models_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.models = {}
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
            self.initialized = True
            logger.info(f"ModelLoader initialized on device: {self.device}")

    def load_models(self, model_config: Dict[str, Any]) -> None:
        """
        Pre-load all models into GPU memory for fast inference.

        Args:
            model_config: Dictionary containing model paths and configuration
        """
        if self._models_loaded:
            logger.info("Models already loaded, skipping...")
            return

        try:
            logger.info("Starting model pre-loading...")

            # Extract configuration
            model_name_or_path = model_config.get("model_name_or_path", "sruckh/higgs-audio-v2")
            audio_tokenizer_name_or_path = model_config.get("audio_tokenizer_name_or_path", "sruckh/higgs-audio-v2")
            tokenizer_name_or_path = model_config.get("tokenizer_name_or_path")

            # Initialize the serve engine (this loads all required models)
            logger.info(f"Loading HiggsAudioServeEngine with model: {model_name_or_path}")
            self.models["serve_engine"] = HiggsAudioServeEngine(
                model_name_or_path=model_name_or_path,
                audio_tokenizer_name_or_path=audio_tokenizer_name_or_path,
                tokenizer_name_or_path=tokenizer_name_or_path,
                device=self.device,
                torch_dtype=self.torch_dtype,
                kv_cache_lengths=[1024, 4096, 8192],  # Multiple KV cache sizes for optimization
            )

            # Store individual components for easy access
            self.models["model"] = self.models["serve_engine"].model
            self.models["tokenizer"] = self.models["serve_engine"].tokenizer
            self.models["audio_tokenizer"] = self.models["serve_engine"].audio_tokenizer
            self.models["collator"] = self.models["serve_engine"].collator

            # Optimize GPU memory
            if self.device == "cuda":
                torch.cuda.empty_cache()
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
                logger.info(f"GPU memory cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")

            self._models_loaded = True
            logger.info("Model pre-loading completed successfully!")

        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            raise e

    def get_serve_engine(self) -> HiggsAudioServeEngine:
        """Get the pre-loaded serve engine."""
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self.models["serve_engine"]

    def get_model(self) -> HiggsAudioModel:
        """Get the pre-loaded model."""
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self.models["model"]

    def get_tokenizer(self) -> AutoTokenizer:
        """Get the pre-loaded tokenizer."""
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self.models["tokenizer"]

    def get_audio_tokenizer(self):
        """Get the pre-loaded audio tokenizer."""
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self.models["audio_tokenizer"]

    def get_collator(self):
        """Get the pre-loaded collator."""
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self.models["collator"]

    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._models_loaded

    def get_memory_info(self) -> Dict[str, float]:
        """Get current memory usage information."""
        info = {}
        if self.device == "cuda" and torch.cuda.is_available():
            info["gpu_allocated_gb"] = torch.cuda.memory_allocated() / 1e9
            info["gpu_cached_gb"] = torch.cuda.memory_reserved() / 1e9
            info["gpu_max_allocated_gb"] = torch.cuda.max_memory_allocated() / 1e9
        return info

    def cleanup(self):
        """Clean up models and free memory."""
        if self._models_loaded:
            logger.info("Cleaning up models...")
            del self.models
            self.models = {}
            if self.device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            self._models_loaded = False
            logger.info("Model cleanup completed")


# Global model loader instance
model_loader = ModelLoader()


def initialize_models(model_config: Optional[Dict[str, Any]] = None):
    """
    Initialize models with optional configuration.
    This function should be called during container startup.

    Args:
        model_config: Optional model configuration. Uses defaults if None.
    """
    if model_config is None:
        model_config = {
            "model_name_or_path": os.getenv("MODEL_NAME_OR_PATH", "sruckh/higgs-audio-v2"),
            "audio_tokenizer_name_or_path": os.getenv("AUDIO_TOKENIZER_NAME_OR_PATH", "sruckh/higgs-audio-v2"),
            "tokenizer_name_or_path": os.getenv("TOKENIZER_NAME_OR_PATH", None),
        }

    model_loader.load_models(model_config)


def get_serve_engine() -> HiggsAudioServeEngine:
    """Get the global serve engine instance."""
    return model_loader.get_serve_engine()


def get_model() -> HiggsAudioModel:
    """Get the global model instance."""
    return model_loader.get_model()


def is_ready() -> bool:
    """Check if models are ready for inference."""
    return model_loader.is_loaded()


def get_memory_info() -> Dict[str, float]:
    """Get current memory usage."""
    return model_loader.get_memory_info()
