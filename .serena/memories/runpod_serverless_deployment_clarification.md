# RunPod Serverless Deployment Clarification

## Issue with Current Setup
The current deployment script and Dockerfile misunderstand RunPod serverless architecture:

1. **Container Building**: RunPod serverless doesn't build containers - it runs pre-built containers
2. **Local Testing**: Current script tries to test container locally, which is not the serverless workflow
3. **Deployment Process**: The process should be GitHub Actions build → Container registry → RunPod deploy

## Correct RunPod Serverless Workflow

### Phase 1: GitHub Actions Build (Container Creation)
```yaml
name: Build and Push RunPod Container

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and Push Ultra-thin Container
        run: |
          docker build -f Dockerfile.runpod.ultra \
            -t ghcr.io/${{ github.repository }}/higgs-audio-runpod:latest \
            --push .
```

### Phase 2: Container Structure (Ultra-thin Base)
```dockerfile
# Ultra-thin base for GitHub Actions build
FROM python:3.10-slim

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/runpod-volume/bosonai/higgs-audio-v2-generation-3B-base
ENV TOKENIZER_PATH=/runpod-volume/bosonai/higgs-audio-v2-tokenizer

# Install minimal runtime dependencies
RUN pip install --no-cache-dir runpod==0.8.4 torch==2.0.1 transformers==4.35.0

# Copy ONLY essential files for runtime
COPY serverless_handler.py /app/
COPY boson_multimodal/ /app/boson_multimodal/

WORKDIR /app

# Bootstrap script for runtime dependency installation
COPY bootstrap.sh /app/bootstrap.sh
RUN chmod +x /app/bootstrap.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD python -c "import os; print('Container ready')"

EXPOSE 8080
CMD ["/app/bootstrap.sh"]
```

### Phase 3: Runtime Bootstrap Process
```bash
#!/bin/bash
# bootstrap.sh - Runtime installation and initialization

set -e

echo "🚀 Starting Higgs Audio RunPod Serverless Bootstrap..."

# Step 1: Install additional runtime dependencies
echo "📦 Installing runtime dependencies..."
pip install --no-cache-dir \
    soundfile loguru click langid jieba tqdm pyyaml boto3 s3fs \
    librosa numpy scipy

# Step 2: Verify environment
echo "🔍 Verifying environment..."
echo "Model path: $MODEL_PATH"
echo "Tokenizer path: $TOKENIZER_PATH"

# Step 3: Check network volume
if [ ! -d "$MODEL_PATH" ]; then
    echo "⚠️  Model directory not found, setting up..."
    mkdir -p /runpod-volume/bosonai
    # First-time model download will happen on first inference request
fi

# Step 4: Start the server
echo "🎯 Starting serverless handler..."
python serverless_handler.py
```

### Phase 4: Serverless Handler with Runtime Model Download
```python
def download_models_if_needed():
    """Download Higgs AI modules on first inference"""
    model_path = Path(MODEL_PATH)
    tokenizer_path = Path(TOKENIZER_PATH)
    
    if not model_path.exists():
        logger.info("📥 Downloading Higgs Audio model (first time)...")
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="bosonai/higgs-audio-v2-generation-3B-base",
            local_dir=str(model_path.parent),
            local_dir_use_symlinks=False
        )
    
    if not tokenizer_path.exists():
        logger.info("📥 Downloading Higgs Audio tokenizer...")
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="bosonai/higgs-audio-v2-tokenizer",
            local_dir=str(tokenizer_path.parent),
            local_dir_use_symlinks=False
        )
    
    logger.info("✅ Models ready!")

async def handle_inference(request_data):
    """Main inference handler with automatic model setup"""
    try:
        # Ensure models are downloaded
        download_models_if_needed()
        
        # Load models (with caching)
        model_client, audio_tokenizer = await get_cached_models()
        
        # Process generation request
        result = await generate_audio(
            model_client,
            audio_tokenizer,
            request_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return {"success": False, "error": str(e)}
```

### Phase 5: RunPod Serverless Configuration
```json
{
  "name": "higgs-audio-v2-serverless",
  "image": "ghcr.io/your-org/higgs-audio-runpod:latest",
  "gpu": "NVIDIA RTX 4090",
  "gpu_count": 1,
  "container_disk_size_gb": 5,
  "network_volume_id": "your-volume-id",
  "network_volume_mount_path": "/runpod-volume",
  "ports": "8080/http",
  "env": {
    "MODEL_PATH": "/runpod-volume/bosonai/higgs-audio-v2-generation-3B-base",
    "TOKENIZER_PATH": "/runpod-volume/bosonai/higgs-audio-v2-tokenizer",
    "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
    "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
    "AWS_DEFAULT_REGION": "${AWS_DEFAULT_REGION}"
  },
  "request_timeout_ms": 600000,
  "idle_timeout_ms": 300000,
  "startup_timeout_ms": 600000
}
```

## S3 Configuration (Environment Variables Only)
```bash
# RunPod Template Environment Variables
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Correct Deployment Process
1. **GitHub Actions**: Build and push ultra-thin container to registry
2. **RunPod Setup**: Create network volume and configure endpoint
3. **Bootstrap**: Container downloads dependencies and models at runtime
4. **Inference**: First request triggers model download to /runpod-volume/bosonai/

## Key Benefits
- **Container Size**: <2GB ultra-thin base container
- **GitHub Integration**: Automated builds and releases
- **Runtime Efficiency**: Dependencies installed when needed
- **Model Management**: Automatic download on first use
- **S3 Security**: Credentials via environment variables only
- **Network Volume**: Persistent storage for models across container restarts