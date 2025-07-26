# Higgs Audio V2 - Multimodal Audio Generation

**Advanced AI-powered audio generation system with zero-shot voice cloning, multi-speaker synthesis, and real-time streaming capabilities.**

🔊 **Official Docker Image**: `gemneye/higgs-audio-v2`  
📚 **Documentation**: [GitHub Repository](https://github.com/sruckh/higgs-audio-v2)  
🚀 **Quick Start**: Ready-to-use containerized deployment with GPU acceleration

## 🌟 Key Features

- **🎭 Zero-Shot Voice Cloning**: Clone any voice with just a few seconds of reference audio
- **🗣️ Multi-Speaker Dialog**: Generate natural conversations between multiple speakers
- **🎵 Creative Audio**: Background music, humming, and environmental sound generation
- **⚡ High-Performance**: Optimized for GPU acceleration with vLLM integration
- **🐳 Production Ready**: Docker container with comprehensive monitoring and scaling
- **🔧 Serverless Support**: Ready for cloud deployment on Runpod, AWS, GCP

## 🚀 Quick Start

### Basic Usage

```bash
# Pull the latest image
docker pull gemneye/higgs-audio-v2:latest

# Run with GPU support
docker run --gpus all -p 8000:8000 \
  -e MODEL_NAME_OR_PATH="sruckh/higgs-audio-v2" \
  gemneye/higgs-audio-v2:latest
```

### Requirements

- **GPU**: 16GB+ VRAM (24GB+ recommended)
- **CUDA**: Compatible GPU with CUDA support
- **Memory**: 32GB+ system RAM
- **Storage**: 20GB+ for models and cache

## 📡 API Endpoints

The container provides 6 primary endpoints for different audio generation tasks:

### 1. Text-to-Speech (TTS)

Convert text to natural-sounding speech.

```python
import requests

response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "text_to_speech",
    "text": "Hello, this is a demonstration of Higgs Audio V2 text-to-speech synthesis.",
    "voice_id": "en_woman",
    "options": {
        "temperature": 0.7,
        "max_new_tokens": 1024,
        "sampling_rate": 24000
    }
})

# Response includes base64-encoded WAV audio
audio_data = response.json()["audio"]["data"]
```

### 2. Zero-Shot Voice Cloning

Clone any voice using a reference audio sample.

```python
response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "voice_cloning", 
    "text": "I'm speaking with a cloned voice that matches the reference audio.",
    "voice_id": "belinda",  # Or upload custom reference
    "options": {
        "temperature": 0.7,
        "max_new_tokens": 1024
    }
})
```

**Available Voice IDs**: `en_woman`, `en_man`, `belinda`, `bigbang_amy`, `bigbang_sheldon`, `chadwick`, `mabel`, `shrek_donkey`, `shrek_fiona`, `vex`, `zh_man_sichuan`

### 3. Multi-Speaker Dialog

Generate natural conversations between multiple speakers.

```python
response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "multi_speaker",
    "text": "[SPEAKER1] Hello there! How are you today? [SPEAKER2] I'm doing great, thanks for asking! [SPEAKER1] Wonderful to hear!",
    "options": {
        "temperature": 0.8,
        "max_new_tokens": 2048
    }
})
```

### 4. High-Throughput vLLM

Optimized for high-throughput inference with streaming support.

```python
response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "vllm",
    "text": "Generate high-quality audio with optimized performance.",
    "options": {
        "temperature": 0.7,
        "max_new_tokens": 1024,
        "stream": True  # Enable streaming for real-time output
    }
})
```

### 5. Scene-Based Generation

Generate audio with environmental context and atmosphere.

```python
response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "scene_based",
    "text": "This conversation is taking place in a quiet indoor setting.",
    "options": {
        "scene_id": "quiet_indoor",  # Options: quiet_indoor, reading_blog
        "temperature": 0.7,
        "max_new_tokens": 1024
    }
})
```

### 6. Experimental Features

Advanced features including background music and sound effects.

```python
response = requests.post("http://localhost:8000/generate", json={
    "endpoint_type": "experimental",
    "text": "Generate creative audio with background music. *soft piano music plays*",
    "options": {
        "experimental_type": "bgm",  # Options: bgm, humming
        "temperature": 0.8,
        "max_new_tokens": 1024
    }
})
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME_OR_PATH` | `sruckh/higgs-audio-v2` | HuggingFace model path |
| `DEVICE` | `cuda` | Compute device (cuda/cpu) |
| `MAX_NEW_TOKENS` | `1024` | Maximum tokens to generate |
| `TEMPERATURE` | `0.7` | Sampling temperature (0.1-2.0) |
| `SAMPLING_RATE` | `24000` | Audio sampling rate |
| `LOG_LEVEL` | `INFO` | Logging level |

### Advanced Configuration

```bash
docker run --gpus all -p 8000:8000 \
  -e MODEL_NAME_OR_PATH="sruckh/higgs-audio-v2" \
  -e DEVICE="cuda" \
  -e MAX_NEW_TOKENS="2048" \
  -e TEMPERATURE="0.8" \
  -e SAMPLING_RATE="24000" \
  -e ENABLE_CUDA_GRAPHS="true" \
  -e LOG_LEVEL="DEBUG" \
  gemneye/higgs-audio-v2:latest
```

## 📊 Response Format

All endpoints return a standardized JSON response:

```json
{
  "success": true,
  "timestamp": 1703123456.789,
  "text": "Generated or input text",
  "audio": {
    "data": "base64_encoded_wav_data",
    "sampling_rate": 24000,
    "format": "wav", 
    "encoding": "base64"
  },
  "metadata": {
    "endpoint_type": "text_to_speech",
    "processing_time_seconds": 3.45,
    "memory_info": {
      "gpu_allocated_gb": 12.5,
      "gpu_cached_gb": 15.2
    },
    "generation_options": {
      "temperature": 0.7,
      "max_new_tokens": 1024
    }
  }
}
```

## 🏥 Health Check

Monitor container health and performance:

```bash
curl -X POST http://localhost:8000/health \
  -H "Content-Type: application/json" \
  -d '{"health_check": true}'
```

Response:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "memory_info": {
    "gpu_allocated_gb": 12.5,
    "gpu_cached_gb": 15.2
  },
  "timestamp": 1703123456.789
}
```

## 🐳 Docker Variants

### Main Image
- **`gemneye/higgs-audio-v2:latest`** - Complete audio generation system
- **`gemneye/higgs-audio-v2:v2.x.x`** - Specific version releases

### vLLM Optimized
- **`gemneye/higgs-audio-v2-vllm:latest`** - High-throughput inference variant
- **`gemneye/higgs-audio-v2-vllm:v2.x.x`** - Specific vLLM version releases

## ☁️ Cloud Deployment

### Runpod Serverless

```bash
# Deploy to Runpod with auto-scaling
curl -X POST "https://api.runpod.ai/v2/endpoints" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "name": "higgs-audio-v2",
    "template": {
      "containerDiskInGb": 50,
      "dockerArgs": "",
      "env": [
        {"key": "MODEL_NAME_OR_PATH", "value": "sruckh/higgs-audio-v2"}
      ],
      "imageName": "gemneye/higgs-audio-v2:latest",
      "ports": "8000/http",
      "volumeInGb": 0
    },
    "workers": {
      "min": 0,
      "max": 5
    }
  }'
```

### AWS/GCP Deployment

Compatible with:
- **AWS SageMaker**: Real-time and batch inference
- **Google Cloud Run**: Serverless container deployment  
- **Azure Container Instances**: Scalable container hosting
- **Kubernetes**: Production orchestration with GPU node pools

## 🔍 Monitoring & Observability

Built-in monitoring capabilities:

- **Performance Metrics**: Response times, throughput, GPU utilization
- **Error Tracking**: Comprehensive error logging and alerting
- **Resource Monitoring**: Memory usage, GPU health, system metrics
- **Request Analytics**: Endpoint usage patterns and optimization insights

## 🛠️ Development

### Local Development

```bash
# Clone repository
git clone https://github.com/sruckh/higgs-audio-v2
cd higgs-audio-v2

# Build development image
docker build -t higgs-audio-v2-dev .

# Run with development mount
docker run --gpus all -p 8000:8000 \
  -v $(pwd):/app \
  higgs-audio-v2-dev
```

### Custom Voice Training

```bash
# Add custom voice samples
mkdir -p custom_voices
echo "This is my voice sample text" > custom_voices/my_voice.txt
# Add my_voice.wav file

# Mount custom voices
docker run --gpus all -p 8000:8000 \
  -v $(pwd)/custom_voices:/app/examples/voice_prompts \
  gemneye/higgs-audio-v2:latest
```

## 📈 Performance Benchmarks

| Metric | Value | Hardware |
|--------|-------|----------|
| Cold Start | <30s | A100 24GB |
| Warm Inference | <5s | A100 24GB |
| Throughput | 10+ req/min | A100 24GB |
| Max Concurrent | 5 requests | A100 24GB |
| Memory Usage | 12-20GB VRAM | Model dependent |

## 🔗 Links & Resources

- **🏠 Homepage**: [GitHub Repository](https://github.com/sruckh/higgs-audio-v2)
- **📚 Documentation**: [Full API Documentation](https://github.com/sruckh/higgs-audio-v2/blob/main/README.md)
- **🐛 Issues**: [Report Issues](https://github.com/sruckh/higgs-audio-v2/issues)
- **💬 Discussions**: [Community Discussions](https://github.com/sruckh/higgs-audio-v2/discussions)
- **📦 Model Hub**: [HuggingFace Model](https://huggingface.co/sruckh/higgs-audio-v2)

## 📄 License

This project is open source and available under the [MIT License](https://github.com/sruckh/higgs-audio-v2/blob/main/LICENSE).

---

**🚀 Ready to generate amazing audio? Pull the image and start creating!**

```bash
docker pull gemneye/higgs-audio-v2:latest && docker run --gpus all -p 8000:8000 gemneye/higgs-audio-v2:latest
```