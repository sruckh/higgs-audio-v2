#!/bin/bash

# Bootstrap script for Higgs Audio RunPod Serverless
# Handles runtime dependency installation and model setup

set -e

echo "🚀 Higgs Audio V2 RunPod Serverless Bootstrap"
echo "============================================="

# Set up logging
exec > /app/logs/bootstrap.log 2>&1

# Environment variables with defaults
export PYTHONPATH=/app
export HF_HOME=/app/hf_cache
export TORCH_HOME=/app/torch_cache
export MODEL_PATH=${MODEL_PATH:-/runpod-volume/bosonai/higgs-audio-v2-generation-3B-base}
export TOKENIZER_PATH=${TOKENIZER_PATH:-/runpod-volume/bosonai/higgs-audio-v2-tokenizer}

echo "📋 Bootstrap Configuration:"
echo "  Model Path: $MODEL_PATH"
echo "  Tokenizer Path: $TOKENIZER_PATH"
echo "  HF Cache: $HF_HOME"
echo "  Torch Cache: $TORCH_HOME"

# Step 1: Install runtime dependencies
echo ""
echo "📦 Installing runtime dependencies..."

pip install --no-cache-dir \
    soundfile==0.12.1 \
    loguru==0.7.2 \
    click==8.1.7 \
    langid==1.1.6 \
    jieba==0.42.1 \
    tqdm==4.66.1 \
    pyyaml==6.0.1 \
    boto3==1.34.0 \
    s3fs==2023.12.2 \
    numpy==1.24.3 \
    scipy==1.10.1 \
    librosa==0.10.1

echo "✅ Runtime dependencies installed successfully"

# Step 2: Verify S3 environment variables (if configured)
echo ""
echo "🔍 Checking S3 configuration..."

if [[ -n "$AWS_ACCESS_KEY_ID" && -n "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "✅ S3 credentials found"
    echo "  Region: ${AWS_DEFAULT_REGION:-us-east-1}"
    echo "  Bucket: ${AWS_S3_BUCKET:-not specified}"
else
    echo "ℹ️  S3 credentials not configured - S3 upload disabled"
fi

# Step 3: Prepare network volume structure
echo ""
echo "📁 Preparing network volume structure..."

# Create base directories
mkdir -p /runpod-volume/bosonai
mkdir -p /runpod-volume/logs
mkdir -p /runpod-volume/cache

# Create model directories if they don't exist
if [[ ! -d "$MODEL_PATH" ]]; then
    echo "📥 Model directory not found - will download on first inference request"
    echo "  Target: $MODEL_PATH"
    mkdir -p "$(dirname "$MODEL_PATH")"
else
    echo "✅ Model directory exists: $MODEL_PATH"
fi

if [[ ! -d "$TOKENIZER_PATH" ]]; then
    echo "📥 Tokenizer directory not found - will download on first inference request"
    echo "  Target: $TOKENIZER_PATH"
    mkdir -p "$(dirname "$TOKENIZER_PATH")"
else
    echo "✅ Tokenizer directory exists: $TOKENIZER_PATH"
fi

# Step 4: Download HuggingFace models if they don't exist (optional preload)
if [[ "$PRELOAD_MODELS" == "true" ]]; then
    echo ""
    echo "🔄 Preloading models (may take several minutes)..."
    
    if [[ ! -d "$MODEL_PATH" ]]; then
        echo "  Downloading generation model..."
        python -c "
from huggingface_hub import snapshot_download
import os
os.environ['HF_HOME'] = '$HF_HOME'
snapshot_download(
    repo_id='bosonai/higgs-audio-v2-generation-3B-base',
    local_dir='$MODEL_PATH',
    local_dir_use_symlinks=False
)
print('✅ Generation model downloaded')
"
    fi
    
    if [[ ! -d "$TOKENIZER_PATH" ]]; then
        echo "  Downloading audio tokenizer..."
        python -c "
from huggingface_hub import snapshot_download
import os
os.environ['HF_HOME'] = '$HF_HOME'
snapshot_download(
    repo_id='bosonai/higgs-audio-v2-tokenizer',
    local_dir='$TOKENIZER_PATH',
    local_dir_use_symlinks=False
)
print('✅ Audio tokenizer downloaded')
"
    fi
else
    echo ""
    echo "ℹ️  Model preload disabled - models will download on first inference"
fi

# Step 5: Verify CUDA availability
echo ""
echo "🔍 Checking CUDA availability..."

python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA device count: {torch.cuda.device_count()}')
    print(f'Current CUDA device: {torch.cuda.current_device()}')
    print(f'Device name: {torch.cuda.get_device_name()}')
else:
    print('⚠️  CUDA not available - fallback to CPU')
"

# Step 6: Start the serverless handler
echo ""
echo "🎯 Starting Higgs Audio serverless handler..."
echo "   Container is ready to accept inference requests"
echo "   Log file: /app/logs/bootstrap.log"
echo "   Server log: /app/logs/server.log"

# Redirect server output to log file
exec python serverless_handler.py > /app/logs/server.log 2>&1