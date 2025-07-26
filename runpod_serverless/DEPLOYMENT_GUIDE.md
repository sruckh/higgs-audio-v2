# Comprehensive Deployment Guide for Higgs Audio V2 Runpod Serverless

This guide provides step-by-step instructions for deploying Higgs Audio V2 on Runpod serverless platform.

## 📋 Prerequisites

### System Requirements
- **Docker** installed and configured
- **Git** for cloning the repository
- **Runpod account** with serverless access
- **Docker registry access** (Docker Hub, AWS ECR, etc.)

### Hardware Requirements (Runpod GPU)
- **Minimum**: 16GB GPU memory (RTX 4090, A10G)
- **Recommended**: 24GB+ GPU memory (A100, H100)
- **CPU**: 8+ cores
- **RAM**: 32GB+ system memory
- **Storage**: 50GB+ for model and container

## 🚀 Step-by-Step Deployment

### Step 1: Prepare the Codebase

```bash
# Clone the repository
git clone <your-higgs-audio-repo>
cd higgs-audio

# Ensure all files are in place
ls runpod_serverless/
# Should show: handler.py, model_loader.py, endpoints.py, config.py, etc.
```

### Step 2: Build the Docker Image

```bash
# Set your Docker registry and image name
export DOCKER_REGISTRY="your-registry.com"  # e.g., "docker.io", "your-account"
export IMAGE_NAME="higgs-audio-serverless"
export IMAGE_TAG="v1.0.0"

# Build the image
python runpod_serverless/deploy.py \
    --image-name "${DOCKER_REGISTRY}/${IMAGE_NAME}" \
    --tag "${IMAGE_TAG}" \
    --test

# Expected output:
# ✅ Docker build completed
# ✅ Local test passed
# Image ready: your-registry.com/higgs-audio-serverless:v1.0.0
```

### Step 3: Push to Registry

```bash
# Login to your Docker registry
docker login ${DOCKER_REGISTRY}

# Push the image
python runpod_serverless/deploy.py \
    --image-name "${DOCKER_REGISTRY}/${IMAGE_NAME}" \
    --tag "${IMAGE_TAG}" \
    --push \
    --skip-build

# Expected output:
# ✅ Docker push completed
```

### Step 4: Create Runpod Serverless Endpoint

1. **Login to Runpod Console**
   - Go to [Runpod Console](https://www.runpod.io/console)
   - Navigate to "Serverless" section

2. **Create New Endpoint**
   - Click "New Endpoint"
   - Choose "Custom" template

3. **Configure Container**
   ```yaml
   Container Image: your-registry.com/higgs-audio-serverless:v1.0.0
   Container Registry Credentials: [Your registry credentials if private]
   ```

4. **Configure Hardware**
   ```yaml
   GPU Type: A100 (24GB) or H100 (80GB)
   CPU: 8+ cores
   Memory: 32GB+
   Storage: 50GB+
   ```

5. **Configure Scaling**
   ```yaml
   Min Workers: 0
   Max Workers: 5
   Idle Timeout: 30 seconds
   Scale Down Delay: 60 seconds
   ```

6. **Environment Variables**
   ```yaml
   MODEL_NAME_OR_PATH: "sruckh/higgs-audio-v2"
   AUDIO_TOKENIZER_NAME_OR_PATH: "sruckh/higgs-audio-v2"
   DEVICE: "cuda"
   LOG_LEVEL: "INFO"
   MAX_NEW_TOKENS: "1024"
   TEMPERATURE: "0.7"
   VOICE_PROMPTS_DIR: "/app/examples/voice_prompts"
   ```

### Step 5: Test the Deployment

```bash
# Get your endpoint URL from Runpod console
export RUNPOD_ENDPOINT_URL="https://api.runpod.ai/v2/your-endpoint-id/run"
export RUNPOD_API_KEY="your-api-key"

# Test basic TTS
curl -X POST "${RUNPOD_ENDPOINT_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -d '{
    "input": {
      "endpoint_type": "text_to_speech",
      "text": "Hello, this is a test of the Higgs Audio serverless deployment.",
      "voice_id": "en_woman",
      "options": {
        "temperature": 0.7,
        "max_new_tokens": 1024
      }
    }
  }'

# Expected response:
# {
#   "success": true,
#   "timestamp": 1703123456.789,
#   "text": "Generated text...",
#   "audio": {
#     "data": "base64_encoded_wav_data",
#     "sampling_rate": 24000,
#     "format": "wav",
#     "encoding": "base64"
#   },
#   "metadata": {
#     "endpoint_type": "text_to_speech",
#     "processing_time_seconds": 5.23,
#     "memory_info": {...}
#   }
# }
```

## 🔧 Configuration Options

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME_OR_PATH` | `sruckh/higgs-audio-v2` | HuggingFace model path |
| `AUDIO_TOKENIZER_NAME_OR_PATH` | `sruckh/higgs-audio-v2` | Audio tokenizer path |
| `TOKENIZER_NAME_OR_PATH` | `None` | Text tokenizer path (optional) |
| `DEVICE` | `cuda` | Compute device |
| `TORCH_DTYPE` | `auto` | Model dtype |
| `MAX_NEW_TOKENS` | `1024` | Maximum tokens to generate |
| `TEMPERATURE` | `0.7` | Sampling temperature |
| `DO_SAMPLE` | `true` | Enable sampling |
| `SAMPLING_RATE` | `24000` | Audio sampling rate |
| `ENABLE_CUDA_GRAPHS` | `true` | Enable CUDA graphs |
| `BATCH_SIZE` | `1` | Batch size |
| `VOICE_PROMPTS_DIR` | `/app/examples/voice_prompts` | Voice prompts directory |
| `DEFAULT_VOICE` | `en_woman` | Default voice ID |
| `MAX_TEXT_LENGTH` | `10000` | Maximum input text length |
| `MAX_CONCURRENT_REQUESTS` | `5` | Max concurrent requests |
| `REQUEST_TIMEOUT_SECONDS` | `300` | Request timeout |
| `MAX_AUDIO_LENGTH_SECONDS` | `300` | Max audio duration |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALERT_WEBHOOK_URL` | `None` | Webhook for alerts |

### Scaling Configuration

```yaml
# Conservative (cost-focused)
Min Workers: 0
Max Workers: 2
Idle Timeout: 15 seconds
Scale Down Delay: 30 seconds

# Balanced (general use)
Min Workers: 0
Max Workers: 5
Idle Timeout: 30 seconds
Scale Down Delay: 60 seconds

# High Performance (low latency)
Min Workers: 1
Max Workers: 10
Idle Timeout: 60 seconds
Scale Down Delay: 120 seconds
```

## 📊 Monitoring and Observability

### Health Check Endpoint

```bash
# Check service health
curl -X POST "${RUNPOD_ENDPOINT_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -d '{
    "input": {
      "health_check": true
    }
  }'
```

### Performance Monitoring

The deployment includes built-in monitoring:

- **Request Metrics**: Processing time, success rate, throughput
- **Resource Metrics**: GPU memory, CPU usage, system memory
- **Error Tracking**: Error types, frequency, stack traces
- **Performance Alerts**: High error rates, slow responses

### Accessing Logs

```bash
# View logs in Runpod console
# Go to your endpoint → Logs tab
# Filter by time range and log level

# Common log patterns to monitor:
# - "Model pre-loading completed" (startup)
# - "Processing {endpoint_type} request" (requests)
# - "Performance metrics for" (performance)
# - "ERROR" or "CRITICAL" (issues)
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Out of Memory Errors
```
Error: CUDA out of memory
```
**Solutions:**
- Reduce `MAX_NEW_TOKENS` to 512 or lower
- Use GPU with more memory (A100 24GB+)
- Reduce batch size to 1
- Set `ENABLE_CUDA_GRAPHS=false`

#### 2. Slow Cold Starts
```
Cold start taking >60 seconds
```
**Solutions:**
- Increase idle timeout to 60+ seconds
- Set min workers to 1 for critical endpoints
- Use faster storage (NVMe SSD)
- Optimize Docker image size

#### 3. Voice Not Found Errors
```
Voice 'custom_voice' not found
```
**Solutions:**
- Check available voices in response metadata
- Use one of the built-in voices: `en_woman`, `en_man`, `belinda`, etc.
- Upload custom voice prompts to the container

#### 4. Model Loading Failures
```
Failed to load models
```
**Solutions:**
- Check GPU memory availability (need 24GB+)
- Verify internet connectivity for model download
- Check HuggingFace model permissions
- Increase container startup timeout

#### 5. High Error Rates
```
Error rate >10% in monitoring
```
**Solutions:**
- Check GPU memory pressure
- Review error logs for patterns
- Reduce concurrent request limits
- Scale up GPU resources

### Debug Mode

Enable debug mode for detailed logging:

```yaml
Environment Variables:
  LOG_LEVEL: "DEBUG"
  TORCH_DTYPE: "float32"  # For debugging precision issues
```

## 🚨 Production Readiness Checklist

### Before Going Live

- [ ] **Load Testing**: Test with concurrent requests
- [ ] **Error Handling**: Verify all error paths work correctly
- [ ] **Monitoring**: Set up alerts and dashboards
- [ ] **Scaling**: Configure appropriate min/max workers
- [ ] **Security**: Review API access and authentication
- [ ] **Backup**: Document configuration and deployment steps
- [ ] **Cost Management**: Set spending limits and alerts

### Performance Baselines

Target performance metrics:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Cold Start Time | <30s | >60s |
| Warm Request Time | <5s | >15s |
| Error Rate | <1% | >5% |
| GPU Memory Usage | <80% | >90% |
| Throughput | 10+ req/min | <5 req/min |

### Monitoring Setup

1. **Set up alerting webhooks**:
   ```yaml
   Environment Variables:
     ALERT_WEBHOOK_URL: "https://hooks.slack.com/your-webhook"
   ```

2. **Monitor key metrics**:
   - Request volume and success rate
   - Response time percentiles
   - GPU memory and utilization
   - Error types and frequency

3. **Regular health checks**:
   ```bash
   # Automated health check script
   #!/bin/bash
   response=$(curl -s -X POST "${RUNPOD_ENDPOINT_URL}" \
     -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
     -d '{"input":{"health_check":true}}')
   
   if echo "$response" | jq -e '.status == "healthy"' > /dev/null; then
     echo "✅ Service healthy"
   else
     echo "❌ Service unhealthy: $response"
     # Send alert
   fi
   ```

## 💰 Cost Optimization

### Cost-Saving Strategies

1. **Aggressive Scaling Down**:
   ```yaml
   Idle Timeout: 15 seconds
   Scale Down Delay: 30 seconds
   Min Workers: 0
   ```

2. **Use Spot Instances**: If available in your region

3. **Monitor Usage Patterns**:
   - Track peak usage times
   - Adjust scaling based on patterns
   - Use smaller GPUs for low-volume periods

4. **Optimize Model Loading**:
   - Use model quantization if quality allows
   - Cache models in container image
   - Use faster storage for model loading

### Cost Monitoring

```bash
# Get cost estimates from Runpod API
curl -X GET "https://api.runpod.ai/v2/user/billing" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"
```

## 🔗 Next Steps

1. **Custom Voice Training**: Add your own voice samples
2. **API Integration**: Integrate with your applications
3. **Performance Tuning**: Optimize for your specific use cases
4. **Multi-Region Deployment**: Deploy to multiple regions
5. **Advanced Features**: Implement streaming and real-time features

## 📞 Support

- **Runpod Documentation**: [docs.runpod.io](https://docs.runpod.io)
- **Higgs Audio Issues**: Check project GitHub issues
- **Community Support**: Join relevant Discord/Slack channels

---

**Success!** 🎉 Your Higgs Audio V2 serverless deployment should now be running on Runpod with full monitoring, error handling, and production-ready features.