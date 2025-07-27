# Runpod Serverless Dockerfile for Higgs Audio V2
# Based on NVIDIA PyTorch container for optimal GPU performance

# Super minimal Serverless Dockerfile for GPU Cloud deployment
# Only essential system dependencies - everything else happens at runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ONLY essential system dependencies
# ffmpeg: Audio processing
# libsndfile1: Audio file I/O
# curl/wget: Download tools for bootstrap
# git: For pip installs from git repos
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

# Copy ONLY the serverless application code (not the entire project)
COPY runpod_serverless/ ./runpod_serverless/
COPY boson_multimodal/ ./boson_multimodal/
COPY examples/voice_prompts/ ./examples/voice_prompts/
COPY setup.py ./
COPY README.md ./
COPY download_models.py ./

# Copy bootstrap and entrypoint scripts
COPY runpod_serverless/bootstrap.sh ./
COPY runpod_serverless/entrypoint.sh ./

# Make scripts executable
RUN chmod +x bootstrap.sh entrypoint.sh

# Create temp directory for runtime files
RUN mkdir -p /tmp/higgs_audio

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# No pip installs, no model downloads, no heavy dependencies
# Container should be ~100MB instead of 10GB+

# Expose port for health checks
EXPOSE 8000

# Entry point runs bootstrap then starts service
ENTRYPOINT ["./entrypoint.sh"]