# Use NVIDIA PyTorch container as base for vLLM
FROM nvcr.io/nvidia/pytorch:25.02-py3

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install vLLM for high-throughput inference
RUN pip install --no-cache-dir vllm

# Copy source code
COPY . .

# Install the package in editable mode
RUN pip install -e .

# Create directory for models, voice samples, and presets
RUN mkdir -p /app/models /app/outputs /app/voice_presets

# Copy vLLM specific files
COPY examples/vllm/ /app/vllm/
COPY examples/voice_prompts/ /app/voice_presets/

# Set up entry point for vLLM server
COPY examples/vllm/vllm-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/vllm-entrypoint.sh

# Expose port for vLLM API server
EXPOSE 8000

# Set default command to start vLLM server
ENTRYPOINT ["vllm-entrypoint.sh"]
CMD ["--served-model-name", "higgs-audio-v2-generation-3B-base", \
     "--model", "bosonai/higgs-audio-v2-generation-3B-base", \
     "--audio-tokenizer-type", "bosonai/higgs-audio-v2-tokenizer", \
     "--limit-mm-per-prompt", "audio=50", \
     "--max-model-len", "8192", \
     "--port", "8000", \
     "--gpu-memory-utilization", "0.8", \
     "--disable-mm-preprocessor-cache"]