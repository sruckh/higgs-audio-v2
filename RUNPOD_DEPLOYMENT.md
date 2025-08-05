# RunPod Serverless Deployment Documentation

## Overview

This document provides complete instructions for deploying Higgs Audio V2 as a RunPod serverless endpoint with extreme space optimization, voice cloning, LLM tone control, and S3 integration.

## Quick Start

### Prerequisites

- RunPod account with billing enabled
- Network volume (minimum 50GB) for model storage
- AWS S3 bucket (optional) for audio output storage
- Docker for local testing
- At least 24GB GPU memory recommended

### 1. Setup Network Volume

Run the setup script to download models to your network volume:

```bash
# Network volume must already be created in RunPod console
export NETWORK_VOLUME_ID="your-volume-id"

# Run the setup script
./setup-network-volume.sh
```

The script will download:
- `bosonai/higgs-audio-v2-generation-3B-base` (main model)
- `bosonai/higgs-audio-v2-tokenizer` (audio tokenizer)

### 2. Build Container

```bash
./deploy-runpod.sh
```

This script will:
- Build the optimized Docker container (<5GB)
- Test the container locally
- Create deployment configuration
- Generate test scripts

### 3. Deploy to RunPod

1. Push your container to a registry
2. Use the generated `runpod-config.json` to create your serverless endpoint
3. Configure the endpoint with your AWS credentials (for S3 uploads)

### 4. Test the Deployment

```bash
./test-runpod-api.sh
```

## API Reference

### Request Format

```json
{
  "input": {
    "transcript": "Text to convert to speech",
    "ref_audio": "belinda",  // Voice reference name
    "scene_prompt": "quiet indoor setting with warm, friendly tone",
    
    // Optional parameters
    "temperature": 0.8,
    "top_k": 50,
    "top_p": 0.95,
    "max_new_tokens": 2048,
    "chunk_method": null,  // "speaker", "word", or null
    "chunk_max_word_num": 200,
    "chunk_max_num_turns": 1,
    "ras_win_len": 7,
    "ras_win_max_num_repeat": 2,
    "seed": 123,
    
    // S3 output (optional)
    "s3_bucket": "my-audio-bucket",
    "s3_key": "output/generation_123.wav"
  }
}
```

### Response Format

```json
{
  "output": {
    "success": true,
    "audio_url": "s3://my-audio-bucket/output/generation_123.wav",
    "duration_seconds": 2.5,
    "sample_rate": 24000,
    "text_output": "Text to convert to speech",
    "metadata": {
      "model_used": "bosonai/higgs-audio-v2-generation-3B-base",
      "voice_clone": "belinda",
      "generation_parameters": {
        "temperature": 0.8,
        "top_k": 50,
        "top_p": 0.95,
        "generation_time": 1.2,
        "chunks_processed": 1
      }
    },
    "voice_suggestions": [
      {"name": "belinda", "description": "Female voice with warm tone"},
      {"name": "chadwick", "description": "Male voice with deep tone"},
      ...
    ]
  }
}
```

## Available Voices

The server suggests these built-in voices:

- **belinda**: Female voice with warm tone
- **chadwick**: Male voice with deep tone
- **daffy**: Animated character voice
- **elsa**: Female voice with clear articulation
- **jorts**: Male voice with casual tone

Custom voices can be added to the network volume's `voice_prompts/` directory.

## Environment Variables

### Required

- `MODEL_PATH`: Path to Higgs Audio model on network volume
- `TOKENIZER_PATH`: Path to audio tokenizer on network volume
- `VOICE_PROMPTS_PATH`: Path to voice prompts directory

### Optional (for S3 uploads)

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)

## Configuration Options

### Memory Management

The server includes automatic memory management:

- **Model Caching**: Models kept in memory between requests
- **Memory Cleanup**: Automatic GPU memory cleanup
- **Garbage Collection**: Periodic memory optimization
- **Cleanup Threshold**: 5 minutes of inactivity

### Performance Optimization

- **Static KV Cache**: Pre-compiled KV caches for faster inference
- **CUDA Graphs**: Optimized GPU execution paths
- **Bfloat16 Precision**: Efficient GPU memory usage
- **Lazy Loading**: Models loaded only when needed

### Security Features

- **Input Validation**: Comprehensive parameter validation
- **Path Protection**: Prevention of path traversal attacks
- **S3 Security**: Secure credential handling
- **Error Handling**: Graceful error responses

## Use Cases

### 1. Basic Text-to-Speech

```bash
curl -X POST "https://your-endpoint.runpod.run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "Hello, world!",
      "ref_audio": "belinda"
    }
  }'
```

### 2. Voice Cloning with Scene Prompt

```bash
curl -X POST "https://your-endpoint.runpod.run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "Welcome to our presentation.",
      "ref_audio": "chadwick",
      "scene_prompt": "professional conference setting with clear, authoritative tone"
    }
  }'
```

### 3. S3 Upload Integration

```bash
curl -X POST "https://your-endpoint.runpod.run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "This audio will be uploaded to S3.",
      "ref_audio": "elsa",
      "s3_bucket": "my-audio-bucket",
      "s3_key": "presentations/welcome_$(date +%s).wav"
    }
  }'
```

### 4. Long Text Generation

```bash
curl -X POST "https://your-endpoint.runpod.run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "transcript": "This is a very long text that will be automatically chunked for optimal processing...",
      "ref_audio": "belinda",
      "chunk_method": "word",
      "chunk_max_word_num": 100
    }
  }'
```

## Monitoring and Observability

### Health Check

```bash
curl -X GET "https://your-endpoint.runpod.run/health"
```

Response:
```json
{
  "status": "healthy",
  "timestamp": 1634567890,
  "model_info": {
    "model_path": "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-generation-3B-base",
    "device": "cuda:0",
    "models_loaded": true,
    "voice_prompts_available": 5
  },
  "voice_suggestions": [
    {"name": "belinda", "description": "Female voice with warm tone"},
    ...
  ]
}
```

### Performance Metrics

Monitor these key metrics:

- **Request Duration**: Total time per request
- **Generation Time**: Audio generation latency
- **Memory Usage**: GPU and system memory consumption
- **Success Rate**: Request success/failure ratio
- **Container Size**: Ensure <5GB limit compliance

## Troubleshooting

### Common Issues

**1. Container Size Exceeds 5GB**
- Check `docker images` for image size
- Remove unnecessary dependencies from `requirements.runpod`
- Use multi-stage builds if needed

**2. Model Loading Errors**
- Verify network volume is mounted correctly
- Check model paths in environment variables
- Ensure sufficient disk space on network volume

**3. Out of Memory Errors**
- Reduce `max_new_tokens` parameter
- Use smaller batch sizes
- Enable memory cleanup more frequently

**4. S3 Upload Failures**
- Verify AWS credentials are correct
- Check S3 bucket permissions
- Ensure valid S3 key format

**5. Slow Performance**
- Ensure CUDA graphs are enabled
- Use static KV cache when possible
- Optimize chunking parameters

### Debug Commands

```bash
# Check container logs
docker logs <container-id>

# Test container locally
docker run -p 8080:8080 -v /path/to/network/volume:/runpod-volume/higgs-audio higgs-audio-runpod:latest

# Monitor GPU usage
nvidia-smi

# Check memory usage
terraform show

# Test API endpoint
curl -f "https://your-endpoint.runpod.run/health"
```

## Cost Optimization

### Container Optimization

- **Minimal Dependencies**: Only essential packages included
- **Model Separate**: Models stored on network volume, not in container
- **Efficient Builds**: Multi-stage builds with cleanup
- **Caching**: Build cache optimization

### Runtime Optimization

- **Memory Management**: Automatic cleanup and caching
- **GPU Efficiency**: bfloat16 precision and CUDA graphs
- **Request Optimization**: Efficient parameter validation
- **Network Optimization**: Connection pooling and compression

### Storage Optimization

- **Network Volume**: Efficient model storage
- **S3 Integration**: Scalable output storage
- **Temporary Files**: Efficient temp file handling
- **Cache Management**: Smart cache eviction

## Security Considerations

### Input Security

- **Parameter Validation**: All inputs validated
- **Path Security**: Path traversal protection
- **Size Limits**: Maximum input size enforcement
- **Content Filtering**: Malicious content detection

### Credential Security

- **Environment Variables**: Secure credential injection
- **No Hardcoded**: No credentials in container
- **AWS IAM**: Support for IAM roles
- **Temporary Credentials**: Short-lived credential support

### Output Security

- **S3 Security**: Secure upload permissions
- **URL Security**: Secure URL generation
- **Content Validation**: Output content verification
- **Audit Logging**: Complete request logging

## Performance Benchmarks

### Expected Performance

- **Container Size**: ~4.5GB
- **Startup Time**: ~30-60 seconds (model loading)
- **Memory Usage**: ~8-12GB (with models loaded)
- **GPU Memory**: ~6-8GB for inference
- **Generation Speed**: ~2-5 seconds per minute of audio
- **Concurrent Requests**: 1-2 requests (GPU-dependent)

### Example Response Times

```json
{
  "generation_metrics": {
    "total_request_time": 8.2,
    "model_loading_time": 0.0,  // Cached
    "generation_time": 4.5,
    "s3_upload_time": 1.2,
    "audio_duration": 15.3,
    "chunks_processed": 2
  }
}
```

## Integration Examples

### Python Client

```python
import requests
import json

def generate_audio(text, voice="belinda", scene_prompt=None, s3_bucket=None):
    url = "https://your-endpoint.runpod.run"
    
    payload = {
        "input": {
            "transcript": text,
            "ref_audio": voice,
            "scene_prompt": scene_prompt
        }
    }
    
    if s3_bucket:
        payload["input"]["s3_bucket"] = s3_bucket
        payload["input"]["s3_key"] = f"generated_{int(time.time())}.wav"
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["output"]["success"]:
        return result["output"]["audio_url"], result["output"]["duration_seconds"]
    else:
        raise Exception(result["output"]["error"])

# Example usage
audio_url, duration = generate_audio(
    text="Hello from Python client!",
    voice="belinda",
    scene_prompt="friendly conversational tone"
)
```

### JavaScript Client

```javascript
async function generateAudio(text, voice = 'belinda', options = {}) {
    const response = await fetch('https://your-endpoint.runpod.run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            input: {
                transcript: text,
                ref_audio: voice,
                ...options
            }
        })
    });
    
    const result = await response.json();
    return result.output;
}

// Example usage
const audio = await generateAudio('Hello from JavaScript!', 'belinda', {
    scene_prompt: 'enthusiastic and engaging tone',
    temperature: 0.7
});
```

## Deployment Checklist

- [ ] Create RunPod network volume (minimum 50GB)
- [ ] Download models to network volume
- [ ] Build and test container locally
- [ ] Push container to registry
- [ ] Configure AWS credentials (for S3)
- [ ] Deploy serverless endpoint
- [ ] Test health check endpoint
- [ ] Validate audio generation
- [ ] Test S3 upload integration
- [ ] Monitor performance metrics
- [ ] Set up logging and monitoring

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review container logs
3. Validate model paths and permissions
4. Test with simple examples first
5. RunPod documentation: https://docs.runpod.io
6. Higgs Audio documentation: See project README

## Version History

- **v1.0.0**: Initial serverless deployment
- **v1.1.0**: Added voice suggestions and improved memory management
- **v1.2.0**: Enhanced S3 integration and error handling
- **v1.3.0**: Performance optimizations and monitoring improvements

---

*This deployment leverages extreme space optimization techniques to fit within RunPod's 5GB container limit while maintaining full functionality of the Higgs Audio V2 model.*