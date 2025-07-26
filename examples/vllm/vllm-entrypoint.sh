#!/bin/bash
set -e

# Initialize CUDA if available
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
    export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
    
    # Check GPU memory
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    echo "GPU Memory: ${GPU_MEMORY} MiB"
    
    # Warn if less than 24GB
    if [ "$GPU_MEMORY" -lt 24000 ]; then
        echo "WARNING: GPU has less than 24GB memory. Performance may be degraded."
    fi
else
    echo "ERROR: No CUDA detected. vLLM requires CUDA-enabled GPU."
    exit 1
fi

# Set default model paths if not provided
export MODEL_PATH=${MODEL_PATH:-"sruckh/higgs-audio-v2"}
export AUDIO_TOKENIZER_PATH=${AUDIO_TOKENIZER_PATH:-"sruckh/higgs-audio-v2"}

# Create necessary directories
mkdir -p /app/outputs

# Download models at runtime (not during build)
echo "Downloading models at runtime..."
python /app/download_models.py --model ${MODEL_PATH} || {
    echo "Warning: Model download failed, vLLM will attempt to download during startup"
}

# Set default voice presets directory
export VOICE_PRESETS_DIR=${VOICE_PRESETS_DIR:-"/app/voice_presets"}

echo "Starting vLLM server for Higgs Audio v2..."
echo "Model: $MODEL_PATH"
echo "Audio Tokenizer: $AUDIO_TOKENIZER_PATH"
echo "Voice Presets: $VOICE_PRESETS_DIR"

# Start vLLM server with provided arguments
exec python -m vllm.entrypoints.openai.api_server "$@" --voice-presets-dir "$VOICE_PRESETS_DIR"