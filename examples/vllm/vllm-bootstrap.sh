#!/bin/bash
set -euo pipefail

# Bootstrap script for vLLM Higgs Audio V2 Serverless
# Installs all dependencies at runtime on the GPU host
echo "🚀 Starting vLLM Higgs Audio V2 Runtime Bootstrap..."

# Function for logging with timestamps
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to install CUDA toolkit at runtime
install_cuda_toolkit() {
    log "🔧 Installing CUDA Toolkit 12.6 at runtime..."
    
    # Download and install CUDA keyring
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb || { log "❌ Failed to install CUDA keyring"; exit 1; }
    
    # Update apt and install CUDA toolkit
    apt-get update
    apt-get -y install cuda-toolkit-12-6 || { log "❌ Failed to install CUDA toolkit"; exit 1; }
    
    # Install NVIDIA open drivers  
    apt-get install -y nvidia-open || log "⚠️ Warning: nvidia-open installation failed (may not be needed)"
    
    # Set CUDA environment
    export PATH=/usr/local/cuda-12.6/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
    
    log "✅ CUDA Toolkit 12.6 installed successfully"
}

# Function to check GPU and setup environment
setup_gpu_environment() {
    if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
        log "✓ GPU detected, setting up CUDA environment"
        
        # Check CUDA version
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}' | head -1)
        log "✓ CUDA Driver Version: $CUDA_VERSION"
        
        # Install CUDA toolkit at runtime
        install_cuda_toolkit
        
    else
        log "⚠ No GPU detected, skipping CUDA installation"
    fi
}

# Function to install core dependencies
install_core_deps() {
    log "📦 Installing PyTorch 2.7.0 with CUDA 12.6..."
    
    # Install PyTorch 2.7.0 with CUDA 12.6 support
    pip install --no-cache-dir \
        torch==2.7.0 \
        torchvision==0.22.0 \
        torchaudio==2.7.0 \
        --index-url https://download.pytorch.org/whl/cu126 \
        || { log "❌ Failed to install PyTorch"; exit 1; }
    
    # Install transformers and accelerate
    pip install --no-cache-dir \
        transformers>=4.45.1,\<4.47.0 \
        accelerate>=0.26.0 \
        || { log "❌ Failed to install transformers/accelerate"; exit 1; }
}

# Function to install vLLM
install_vllm() {
    log "⚡ Installing vLLM for high-throughput inference..."
    
    pip install --no-cache-dir vllm \
        || { log "❌ Failed to install vLLM"; exit 1; }
}

# Function to install Flash Attention
install_flash_attention() {
    log "⚡ Installing Flash Attention 2.8.0 for optimal performance..."
    
    if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
        # Install the specific wheel you provided
        pip install --no-cache-dir \
            https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.7cxx11abiFALSE-cp311-cp311-linux_x86_64.whl \
            || { 
                log "⚠️ Warning: Flash Attention installation failed"
                log "   Performance may be impacted but system will still work"
            }
    else
        log "⚠️ Skipping Flash Attention (GPU required)"
    fi
}

# Function to install audio processing dependencies
install_audio_deps() {
    log "🎵 Installing audio processing dependencies..."
    
    pip install --no-cache-dir \
        librosa \
        soundfile>=0.12.1 \
        pydub \
        descript-audio-codec \
        || { log "❌ Failed to install audio packages"; exit 1; }
}

# Function to install utility dependencies
install_utility_deps() {
    log "🔧 Installing utility dependencies..."
    
    pip install --no-cache-dir \
        dacite \
        boto3==1.35.36 \
        s3fs \
        json_repair \
        pandas \
        pydantic \
        vector_quantize_pytorch \
        loguru \
        omegaconf \
        click \
        langid \
        jieba \
        requests>=2.31.0 \
        aiohttp>=3.9.0 \
        pyyaml>=6.0 \
        psutil>=5.9.0 \
        openai>=1.0.0 \
        tqdm>=4.65.0 \
        || { log "❌ Failed to install utility packages"; exit 1; }
}

# Function to install the Higgs Audio package
install_higgs_package() {
    log "🎯 Installing Higgs Audio V2 package..."
    
    # Install in development mode
    pip install --no-cache-dir -e . \
        || { log "❌ Failed to install Higgs Audio package"; exit 1; }
}

# Function to download models
download_models() {
    log "📥 Downloading models at runtime..."
    
    # Set model paths from environment or defaults
    MODEL_NAME_OR_PATH="${MODEL_NAME_OR_PATH:-sruckh/higgs-audio-v2}"
    AUDIO_TOKENIZER_NAME_OR_PATH="${AUDIO_TOKENIZER_NAME_OR_PATH:-sruckh/higgs-audio-v2}"
    
    # Download main model
    python -c "
from transformers import AutoModel, AutoTokenizer
import os

print(f'Downloading model: ${MODEL_NAME_OR_PATH}')
try:
    model = AutoModel.from_pretrained('${MODEL_NAME_OR_PATH}', trust_remote_code=True)
    print('✓ Model downloaded successfully')
except Exception as e:
    print(f'⚠ Model download warning: {e}')
    print('Will attempt to download during vLLM server startup')

print('Bootstrap model download completed')
" || log "⚠ Model download failed, will retry during vLLM startup"
}

# Function to verify installation
verify_installation() {
    log "🔍 Verifying vLLM installation..."
    
    python -c "
import torch
import transformers
import librosa
import vllm
import boson_multimodal

print(f'✓ PyTorch: {torch.__version__}')
print(f'✓ Transformers: {transformers.__version__}')
print(f'✓ LibROSA: {librosa.__version__}')
print(f'✓ vLLM: {vllm.__version__}')
print(f'✓ CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✓ GPU: {torch.cuda.get_device_name(0)}')
    print(f'✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
" || { log "❌ Installation verification failed"; exit 1; }
}

# Main bootstrap execution
main() {
    log "🎬 Starting runtime bootstrap for vLLM Higgs Audio V2"
    
    # Show system info
    log "💻 System Information:"
    echo "  Python: $(python --version)"
    echo "  Platform: $(uname -a)"
    echo "  Memory: $(free -h | grep Mem: | awk '{print $2}')"
    echo "  Disk: $(df -h / | tail -1 | awk '{print $4}')"
    
    # Setup and install everything
    setup_gpu_environment
    install_core_deps
    install_flash_attention
    install_vllm
    install_audio_deps  
    install_utility_deps
    install_higgs_package
    download_models
    verify_installation
    
    log "🎉 vLLM Bootstrap completed successfully!"
    log "🔥 vLLM Higgs Audio V2 is ready for high-throughput inference"
}

# Run bootstrap
main "$@"