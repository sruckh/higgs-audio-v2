# RunPod Serverless Deployment Guide - Higgs Audio V2

## Overview

This guide explains the correct deployment process for Higgs Audio V2 on RunPod serverless. The key insight is that **RunPod serverless does not build containers** - it runs pre-built containers from a registry.

## Architecture

### Container Structure
```
Ultra-thin base container (<2GB) - Built on GitHub Actions
│
├── Runtime Dependencies (installed at bootstrap)
│   ├── Audio processing (librosa, soundfile)
│   ├── HuggingFace libraries
│   ├── AWS S3 client (boto3)
│   └── Additional utilities
│
├── Model Storage (Network Volume)
│   ├── /runpod-volume/bosonai/higgs-audio-v2-generation-3B-base
│   └── /runpod-volume/bosonai/higgs-audio-v2-tokenizer
│
└── Bootstrap Process (Runtime)
    ├── Install additional dependencies
    ├── Download models on first request
    └── Start serverless handler
```

## Step 1: GitHub Actions Setup

### 1.1 Enable GitHub Container Registry
Your repository must be configured to push containers to GitHub Container Registry (ghcr.io).

### 1.2 Verify Actions Workflow
The workflow `.github/workflows/build-runpod-container.yml` should:
- Build ultra-thin container on push to main
- Push to `ghcr.io/your-repo/higgs-audio-runpod:latest`
- Create deployment artifacts

### 1.3 Manually Trigger Build
 trigger the workflow:
```bash
# Go to GitHub Actions → Build and Push RunPod Container → Run workflow
# Wait for build to complete
```

## Step 2: RunPod Network Volume Setup

### 2.1 Create Network Volume
In RunPod dashboard:
1. Go to Network Volumes
2. Create new volume (100GB recommended)
3. Note the volume ID (e.g., `vol-xxxxxxxx`)

### 2.2 Optional: Pre-load Models
Skip this step if you want models to download automatically on first inference.

```bash
# SSH into a GPU instance with the network volume attached
# Install git-lfs and huggingface-hub
git lfs install
pip install huggingface-hub

# Download models to network volume
huggingface-cli download bosonai/higgs-audio-v2-generation-3B-base --local-dir /runpod-volume/bosonai/higgs-audio-v2-generation-3B-base
huggingface-cli download bosonai/higgs-audio-v2-tokenizer --local-dir /runpod-volume/bosonai/higgs-audio-v2-tokenizer
```

## Step 3: RunPod Serverless Endpoint Configuration

### 3.1 Create Serverless Endpoint
In RunPod dashboard:
1. Go to Serverless → Create Endpoint
2. Configure as follows:

```json
{
  "name": "higgs-audio-v2-serverless",
  "image": "ghcr.io/your-username/higgs-audio:latest",  // From GitHub build
  "gpu": "NVIDIA RTX 4090",
  "gpu_count": 1,
  "container_disk_size_gb": 5,
  "network_volume_id": "vol-your-volume-id",  // From Step 2.1
  "network_volume_mount_path": "/runpod-volume",
  "ports": "8080/http",
  "env": {
    "MODEL_PATH": "/runpod-volume/bosonai/higgs-audio-v2-generation-3B-base",
    "TOKENIZER_PATH": "/runpod-volume/bosonai/higgs-audio-v2-tokenizer",
    "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
    "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
    "AWS_DEFAULT_REGION": "${AWS_DEFAULT_REGION:-us-east-1}",
    "PRELOAD_MODELS": "false"  // Set to "true" if you pre-loaded models
  },
  "request_timeout_ms": 600000,  // 10 minutes
  "idle_timeout_ms": 300000,   // 5 minutes
  "startup_timeout_ms": 600000  // 10 minutes for bootstrap
}
```

### 3.2 Environment Variables
Configure these in RunPod endpoint settings:

```bash
# Required for S3 upload (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Model configuration (optional overrides)
MODEL_PATH=/runpod-volume/bosonai/higgs-audio-v2-generation-3B-base
TOKENIZER_PATH=/runpod-volume/bosonai/higgs-audio-v2-tokenizer

# Runtime options
PRELOAD_MODELS=false  # Set to true if you pre-loaded models in Step 2.2
```

## Step 4: Testing the Deployment

### 4.1 Wait for Endpoint to Start
After deployment, check the endpoint status in RunPod dashboard. Wait for it to show "Ready".

### 4.2 Health Check Test
```bash
# Get your endpoint URL from RunPod dashboard
ENDPOINT_URL="https://your-endpoint-id.runpod.net"

curl -X GET "$ENDPOINT_URL/health"
```

### 4.3 Basic Audio Generation Test
```bash
ENDPOINT_URL="https://your-endpoint-id.runpod.net"

curl -X POST "$ENDPOINT_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "Hello! This is a test of the Higgs Audio RunPod serverless deployment.",
      "ref_audio": "en_woman",
      "scene_prompt": "warm and friendly speaking style",
      "temperature": 0.8,
      "top_p": 0.9
    }
  }' | jq .
```

### 4.4 S3 Upload Test
If S3 credentials are configured:
```bash
ENDPOINT_URL="https://your-endpoint-id.runpod.net"

curl -X POST "$ENDPOINT_URL/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"input\": {
      \"transcript\": \"This audio file will be uploaded to S3 automatically.\",
      \"ref_audio\": \"en_man\",
      \"scene_prompt\": \"professional corporate tone\",
      \"temperature\": 0.7,
      \"s3_bucket\": \"your-s3-bucket\",
      \"s3_key\": \"higgs-audio/test-$(date +%s).wav\"
    }
  }" | jq .
```

## Runtime Process

### First Request (Bootstrap Phase)
1. **Container Start**: Bootstrap script runs automatically
2. **Dependency Installation**: Installs audio processing libraries
3. **Model Download**: Downloads Higgs AI modules to `/runpod-volume/bosonai/`
4. **Server Start**: Serverless handler becomes ready
5. **First Inference**: Processes the request and generates audio

### Subsequent Requests
1. **Immediate Processing**: Models are cached in memory
2. **Fast Response**: No download or installation needed
3. **S3 Upload**: If configured, uploads audio to S3 bucket

## Troubleshooting

### Common Issues

#### Container Stuck in "Starting"
- Check `startup_timeout_ms` - increase to 600000 (10 minutes)
- Model download can take 5-10 minutes on first request
- Check endpoint logs in RunPod dashboard

#### Request Timeouts
- Increase `request_timeout_ms` for long audio generation
- Check if models downloaded successfully
- Verify GPU availability and memory

#### S3 Upload Failures
- Verify AWS credentials in environment variables
- Check S3 bucket permissions
- Ensure region matches bucket location

#### Model Download Failures
- Verify network volume is properly mounted
- Check HuggingFace access permissions
- Ensure sufficient disk space on network volume

### Log Locations
- **Bootstrap Log**: `/app/logs/bootstrap.log` in container
- **Server Log**: `/app/logs/server.log` in container
- **RunPod Dashboard**: Real-time endpoint logs

## Performance Optimization

### Cold Start vs Warm Request
- **Cold Start**: 30-120 seconds (first requests, model download)
- **Warm Request**: 2-5 seconds (subsequent requests)

### Cost Optimization
- **Idle Timeout**: Set `idle_timeout_ms` to balance cost vs responsiveness
- **GPU Choice**: RTX 4090 for best performance, adjust based on workload
- **Network Volume**: 100GB sufficient for 2-3 model variants

### Model Caching
Models persist in network volume, so:
- Container restarts don't require re-download
- Multiple endpoints can share the same network volume
- Model updates require manual volume refresh

## Security Considerations

- **AWS Credentials**: Never hardcode - always use environment variables
- **Network Volume**: Secure access through RunPod volume permissions
- **API Security**: Consider adding authentication headers to requests
- **Input Validation**: Server includes request validation and sanitization

## Migration from Local Development

If you have existing local deployment files:
- **Delete**: `deploy-runpod.sh` (not needed for serverless)
- **Update**: `Dockerfile.runpod` → use `Dockerfile.runpod.ultra`
- **Add**: `bootstrap.sh` for runtime setup
- **Configure**: GitHub Actions workflow for automated builds

This deployment approach ensures optimal performance, cost efficiency, and scalability for Higgs Audio V2 on RunPod serverless.