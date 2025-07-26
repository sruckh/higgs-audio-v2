# Runpod Serverless Deployment for Higgs Audio V2

This directory contains the serverless deployment implementation for Higgs Audio V2 on Runpod platform, enabling scalable cloud-based audio generation with automatic scaling and cost efficiency.

## 🚀 Quick Start

### 1. Build Docker Image

```bash
cd /path/to/higgs-audio
docker build -f runpod_serverless/Dockerfile -t higgs-audio-serverless .
```

### 2. Test Locally

```bash
# Set environment variables
export MODEL_NAME_OR_PATH="sruckh/higgs-audio-v2"
export AUDIO_TOKENIZER_NAME_OR_PATH="sruckh/higgs-audio-v2"
export DEVICE="cuda"

# Run container
docker run --gpus all -p 8000:8000 higgs-audio-serverless
```

### 3. Deploy to Runpod

1. Push Docker image to a registry (Docker Hub, etc.)
2. Create a new Runpod serverless endpoint
3. Configure with your Docker image
4. Set GPU requirements (24GB+ recommended)

## 📡 API Endpoints

The serverless function provides 6 primary endpoints for different audio generation tasks:

### 1. Text-to-Speech
Basic text-to-speech generation.

```json
{
  "input": {
    "endpoint_type": "text_to_speech",
    "text": "Hello, this is a test message.",
    "voice_id": "en_woman",
    "options": {
      "temperature": 0.7,
      "max_new_tokens": 1024
    }
  }
}
```

### 2. Voice Cloning
Zero-shot voice cloning using reference audio.

```json
{
  "input": {
    "endpoint_type": "voice_cloning",
    "text": "Clone this voice speaking new text.",
    "voice_id": "belinda",
    "options": {
      "temperature": 0.7,
      "max_new_tokens": 1024
    }
  }
}
```

### 3. Multi-Speaker Dialog
Generate conversations with multiple speakers.

```json
{
  "input": {
    "endpoint_type": "multi_speaker",
    "text": "[SPEAKER1] Hello there! [SPEAKER2] Hi, how are you?",
    "options": {
      "temperature": 0.7,
      "max_new_tokens": 2048
    }
  }
}
```

### 4. vLLM High-Throughput
High-throughput generation using vLLM optimization.

```json
{
  "input": {
    "endpoint_type": "vllm",
    "text": "Generate high-quality audio efficiently.",
    "options": {
      "temperature": 0.7,
      "max_new_tokens": 1024
    }
  }
}
```

### 5. Scene-Based Generation
Generate audio with environmental context.

```json
{
  "input": {
    "endpoint_type": "scene_based",
    "text": "This is a quiet indoor conversation.",
    "options": {
      "scene_id": "quiet_indoor",
      "temperature": 0.7,
      "max_new_tokens": 1024
    }
  }
}
```

### 6. Experimental Features
Advanced features like background music and humming.

```json
{
  "input": {
    "endpoint_type": "experimental",
    "text": "Generate creative audio with music.",
    "options": {
      "experimental_type": "bgm",
      "temperature": 0.8,
      "max_new_tokens": 1024
    }
  }
}
```

## 📊 Response Format

All endpoints return a standardized response format:

```json
{
  "success": true,
  "timestamp": 1703123456.789,
  "text": "Generated text output",
  "audio": {
    "data": "base64_encoded_wav_data",
    "sampling_rate": 24000,
    "format": "wav",
    "encoding": "base64"
  },
  "metadata": {
    "endpoint_type": "text_to_speech",
    "processing_time_seconds": 5.23,
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

## 🔧 Configuration

Configure the serverless function using environment variables:

### Model Configuration
- `MODEL_NAME_OR_PATH`: Model path/name (default: "sruckh/higgs-audio-v2")
- `AUDIO_TOKENIZER_NAME_OR_PATH`: Audio tokenizer path (default: "sruckh/higgs-audio-v2")
- `TOKENIZER_NAME_OR_PATH`: Text tokenizer path (optional)
- `DEVICE`: Compute device (default: "cuda")
- `TORCH_DTYPE`: Model dtype (default: "auto")

### Generation Defaults
- `MAX_NEW_TOKENS`: Maximum tokens to generate (default: 1024)
- `TEMPERATURE`: Sampling temperature (default: 0.7)
- `DO_SAMPLE`: Enable sampling (default: true)
- `SAMPLING_RATE`: Audio sampling rate (default: 24000)

### Performance Settings
- `ENABLE_CUDA_GRAPHS`: Enable CUDA graphs (default: true)
- `BATCH_SIZE`: Batch size for generation (default: 1)

### Voice Configuration
- `VOICE_PROMPTS_DIR`: Voice prompts directory (default: "/app/examples/voice_prompts")
- `DEFAULT_VOICE`: Default voice ID (default: "en_woman")

### Limits and Security
- `MAX_TEXT_LENGTH`: Maximum input text length (default: 10000)
- `MAX_CONCURRENT_REQUESTS`: Max concurrent requests (default: 5)
- `REQUEST_TIMEOUT_SECONDS`: Request timeout (default: 300)
- `MAX_AUDIO_LENGTH_SECONDS`: Max audio duration (default: 300)

## 🏗️ Architecture

The serverless deployment consists of several key components:

### Core Components
- **`handler.py`**: Main serverless handler with request routing
- **`model_loader.py`**: Singleton model loader with pre-initialization
- **`endpoints.py`**: Individual endpoint handlers for each use case
- **`config.py`**: Configuration management and environment variables

### Model Pre-loading
The system uses a singleton pattern to pre-load models during container startup, minimizing cold start times:

1. **Container Startup**: Models are loaded into GPU memory
2. **Request Handling**: Pre-loaded models serve requests instantly
3. **Memory Management**: Efficient GPU memory usage and monitoring

### Request Flow
1. **Input Validation**: Validate request format and parameters
2. **Endpoint Routing**: Route to appropriate handler based on endpoint_type
3. **Model Inference**: Generate audio using pre-loaded models
4. **Response Formatting**: Return standardized response with audio data

## 📈 Performance

### Performance Targets
- **Cold Start**: <30 seconds (model loading)
- **Warm Request**: <5 seconds for short audio
- **Throughput**: 10+ concurrent requests per worker
- **Availability**: 99.9% uptime
- **Error Rate**: <1% for valid inputs

### GPU Requirements
- **Minimum**: 16GB GPU memory
- **Recommended**: 24GB+ GPU memory (A100, H100)
- **CPU**: 8+ cores recommended
- **RAM**: 32GB+ system memory

### Optimization Features
- **Model Pre-loading**: Eliminates model loading time per request
- **CUDA Graphs**: Optimized GPU kernel execution
- **KV Cache**: Multiple cache sizes for different sequence lengths
- **Memory Management**: Efficient GPU memory usage and cleanup

## 🛠️ Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r runpod_serverless/requirements.txt

# Set environment variables
export MODEL_NAME_OR_PATH="sruckh/higgs-audio-v2"
export DEVICE="cuda"

# Test model loading
python -c "from runpod_serverless.model_loader import initialize_models; initialize_models()"

# Test specific endpoint
python -c "
from runpod_serverless.endpoints import handle_text_to_speech
result = handle_text_to_speech('Hello world', None, {})
print(f'Generated audio shape: {result[\"audio\"].shape}')
"
```

### Testing
```bash
# Test the handler locally
python -c "
from runpod_serverless.handler import handler
job = {
    'input': {
        'endpoint_type': 'text_to_speech',
        'text': 'Hello, this is a test.',
        'options': {'temperature': 0.7}
    }
}
result = handler(job)
print(f'Success: {result[\"success\"]}')
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce batch size or use smaller model
2. **Slow Cold Start**: Ensure GPU is available and models can pre-load
3. **Voice Not Found**: Check voice_id against available voices list
4. **Invalid Input**: Validate request format matches API specification

### Monitoring
The service provides health check and memory monitoring:

```python
from runpod_serverless.handler import health_check, get_memory_info

# Check service health
status = health_check()
print(f"Service status: {status['status']}")

# Monitor memory usage
memory = get_memory_info()
print(f"GPU memory: {memory.get('gpu_allocated_gb', 0):.2f} GB")
```

## 📋 Available Voices

The following voice IDs are available for voice cloning:

- `en_woman` - English female voice
- `en_man` - English male voice  
- `belinda` - Character voice
- `bigbang_amy` - TV character voice
- `bigbang_sheldon` - TV character voice
- `broom_salesman` - Character voice
- `chadwick` - Character voice
- `fiftyshades_anna` - Character voice
- `mabaoguo` - Chinese male voice
- `mabel` - Character voice
- `shrek_donkey` - Animated character voice
- `shrek_fiona` - Animated character voice
- `shrek_shrek` - Animated character voice
- `vex` - Character voice
- `zh_man_sichuan` - Chinese Sichuan dialect

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview and setup
- [Examples](../examples/README.md) - Usage examples and scripts
- [vLLM Integration](../examples/vllm/README.md) - High-throughput inference setup
- [Architecture](../ARCHITECTURE.md) - Technical architecture details