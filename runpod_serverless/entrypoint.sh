#!/bin/bash

# Entrypoint script for Runpod serverless container
echo "Starting Higgs Audio V2 Runpod Serverless Container..."

# Set environment variables if not already set
export PYTHONPATH="${PYTHONPATH:-/app}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export MODEL_NAME_OR_PATH="${MODEL_NAME_OR_PATH:-sruckh/higgs-audio-v2}"
export AUDIO_TOKENIZER_NAME_OR_PATH="${AUDIO_TOKENIZER_NAME_OR_PATH:-sruckh/higgs-audio-v2}"
export DEVICE="${DEVICE:-cuda}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Check GPU availability
echo "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
    echo "GPU detected"
else
    echo "WARNING: nvidia-smi not found, running in CPU mode"
    export DEVICE="cpu"
fi

# Check disk space
echo "Checking disk space..."
df -h

# Download models at runtime (not during build)
echo "Downloading models at runtime..."
python /app/download_models.py --model ${MODEL_NAME_OR_PATH} || {
    echo "Warning: Model download failed, will attempt to download during model loading"
}

# Pre-load models
echo "Pre-loading models..."
python -c "
from runpod_serverless.model_loader import initialize_models
from runpod_serverless.config import get_config, print_config

print('Loading configuration...')
config = get_config()
print_config(config)

print('Initializing models...')
initialize_models()

print('Model initialization completed!')
"

if [ $? -ne 0 ]; then
    echo "ERROR: Model initialization failed"
    exit 1
fi

echo "Models pre-loaded successfully!"

# Start the runpod serverless handler
echo "Starting Runpod handler..."
python -u -m runpod.serverless.start --handler_file runpod_serverless.handler