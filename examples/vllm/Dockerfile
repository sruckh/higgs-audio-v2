# Minimal vLLM Dockerfile for GPU Cloud deployment
# Only essential system dependencies - everything else happens at runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ONLY essential system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install only pip (no packages yet - happens at runtime)
RUN pip install --no-cache-dir --upgrade pip

# Copy ONLY the application code
COPY boson_multimodal/ ./boson_multimodal/
COPY examples/vllm/ ./vllm/
COPY examples/voice_prompts/ ./voice_presets/
COPY setup.py ./
COPY README.md ./
COPY download_models.py ./

# Copy bootstrap and entrypoint scripts
COPY examples/vllm/vllm-bootstrap.sh ./
COPY examples/vllm/vllm-entrypoint.sh ./

# Make scripts executable
RUN chmod +x vllm-bootstrap.sh vllm-entrypoint.sh

# Create temp directories
RUN mkdir -p /tmp/higgs_audio /app/models /app/outputs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# No pip installs, no model downloads, no heavy dependencies
# Container should be ~100MB instead of 10GB+

# Expose port for vLLM API server
EXPOSE 8000

# Entry point runs bootstrap then starts vLLM server
ENTRYPOINT ["./vllm-entrypoint.sh"]