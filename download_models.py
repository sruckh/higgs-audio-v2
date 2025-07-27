#!/usr/bin/env python3
"""
Model download script for Higgs Audio V2.
Downloads models at runtime to avoid including them in Docker images.
"""

import os
import sys
from loguru import logger
from huggingface_hub import snapshot_download
from transformers import AutoConfig, AutoTokenizer


def download_models(model_name_or_path="sruckh/higgs-audio-v2", cache_dir=None):
    """
    Download all required models for Higgs Audio V2.

    Args:
        model_name_or_path: HuggingFace model identifier
        cache_dir: Directory to cache models (default: ~/.cache/huggingface)
    """
    try:
        logger.info(f"Downloading models from {model_name_or_path}...")
        
        # Download main model and tokenizer
        snapshot_download(
            repo_id=model_name_or_path,
            cache_dir=cache_dir,
            resume_download=True,
            local_files_only=False
        )
        
        # Verify the download by loading config
        config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)
        logger.info(f"Model config loaded successfully: {type(config).__name__}")
        
        # Download tokenizer if separate
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
            logger.info("Tokenizer downloaded successfully")
        except Exception as e:
            logger.warning(f"Could not download tokenizer: {e}")
        
        logger.info("All models downloaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Higgs Audio V2 models")
    parser.add_argument(
        "--model",
        default="sruckh/higgs-audio-v2",
        help="Model name or path (default: sruckh/higgs-audio-v2)",
    )
    parser.add_argument(
        "--cache-dir",
        help="Directory to cache models (default: ~/.cache/huggingface)",
    )
    
    args = parser.parse_args()
    
    success = download_models(args.model, args.cache_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()