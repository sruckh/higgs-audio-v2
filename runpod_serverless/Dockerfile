# Runpod Serverless Dockerfile for Higgs Audio V2
# Based on NVIDIA PyTorch container for optimal GPU performance

FROM nvcr.io/nvidia/pytorch:25.02-py3

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/runpod_serverless/requirements.txt
COPY ../requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/runpod_serverless/requirements.txt

# Copy the entire project
COPY . /app/

# Install the package in development mode
# Prevent model downloads during build
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
RUN pip install -e .

# Copy voice prompts and examples
COPY examples/ /app/examples/

# Create directories for temporary files
RUN mkdir -p /tmp/higgs_audio

# Unset offline mode for runtime (models will be downloaded when container runs)
ENV HF_HUB_OFFLINE=
ENV TRANSFORMERS_OFFLINE=

# Set up proper permissions
RUN chmod +x /app/runpod_serverless/entrypoint.sh

# Expose port for health checks (optional)
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/runpod_serverless/entrypoint.sh"]