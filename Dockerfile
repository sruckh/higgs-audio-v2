# Use NVIDIA PyTorch container as base
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

# Copy source code
COPY . .

# Install the package in editable mode
RUN pip install -e .

# Create directory for models and voice samples
RUN mkdir -p /app/models /app/outputs

# Set up entry point
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port for serving (if needed)
EXPOSE 8000

# Set default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "examples/generation.py", "--help"]