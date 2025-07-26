#!/bin/bash
set -e

# Initialize CUDA if available
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
    export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
else
    echo "No CUDA detected, using CPU"
    export CUDA_VISIBLE_DEVICES=""
fi

# Set default model paths if not provided
export MODEL_PATH=${MODEL_PATH:-"sruckh/higgs-audio-v2"}
export AUDIO_TOKENIZER_PATH=${AUDIO_TOKENIZER_PATH:-"sruckh/higgs-audio-v2"}

# Create output directory if it doesn't exist
mkdir -p /app/outputs

# Download models at runtime (not during build)
echo "Downloading models at runtime..."
python /app/download_models.py --model ${MODEL_PATH} || {
    echo "Warning: Model download failed, will attempt to download during inference"
}

# If no command provided, show help
if [ $# -eq 0 ]; then
    echo "Higgs Audio v2 Docker Container"
    echo "Available commands:"
    echo "  generation - Run audio generation"
    echo "  serve - Start serving engine"
    echo "  bash - Interactive shell"
    echo ""
    echo "Example usage:"
    echo "  docker run gemneye/higgs-audio-v2 generation --transcript 'Hello world' --out_path /app/outputs/test.wav"
    exit 0
fi

# Handle different commands
case "$1" in
    generation)
        shift
        exec python examples/generation.py "$@"
        ;;
    serve)
        shift
        exec python examples/serve_engine/run_hf_example.py "$@"
        ;;
    vllm)
        shift
        exec python examples/vllm/run_chat_completion.py "$@"
        ;;
    bash)
        exec /bin/bash
        ;;
    *)
        # Default: execute the command as-is
        exec "$@"
        ;;
esac