# RunPod Serverless Deployment Plan for Higgs Audio V2

## Overview
Deploy Higgs Audio model as RunPod serverless endpoint with extreme space optimization (5GB limit), one-shot voice cloning, LLM tone control, and S3 output storage.

## Selected Workflow: serverless-ml-deployment

### Core Requirements
- **Platform**: RunPod serverless with GPU acceleration
- **Container Size**: Must stay under 5GB limit
- **Model Storage**: AI models on Network Volume `/runpod-volume/higgs_audio`
- **Output Storage**: S3 via environment variable credentials
- **Primary Features**: One-shot voice cloning + TTS with LLM tone control

## Essential API Parameters (from generation.py)

### Core Generation Parameters
```python
# Required Parameters:
- transcript: str                    # Text to convert to speech
- ref_audio: str                     # Voice reference (e.g., "belinda", "chadwick")
- scene_prompt: str                  # Scene description for tone/context (LLM control)

# Optional Parameters:
- temperature: float = 1.0          # Controls randomness
- top_k: int = 50                   # Top-k filtering
- top_p: float = 0.95               # Top-p filtering
- max_new_tokens: int = 2048        # Maximum audio tokens
- chunk_method: str = None          # "speaker", "word", or None
- chunk_max_word_num: int = 200     # Word chunking limit
- chunk_max_num_turns: int = 1      # Turn chunking limit
- ras_win_len: int = 7              # RAS sampling window
- ras_win_max_num_repeat: int = 2   # RAS max repeat
- seed: int = None                  # Random seed
- s3_bucket: str                    # S3 bucket for output
- s3_key: str                       # S3 key for output
```

### Model Loading Requirements
- **Model Path**: `/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-generation-3B-base`
- **Audio Tokenizer**: `/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-tokenizer`
- **Device**: CUDA with static KV cache optimization
- **Device Options**: auto, cuda, mps, none

## Container Architecture Strategy

### 1. Ultra-Thin Base Container
```dockerfile
FROM python:3.10-slim
# Skip CUDA installation - provided by RunPod serverless
RUN pip install --no-cache-dir runpod==0.8.4 torch==2.0.1 transformers

# Minimal dependencies for Higgs Audio
RUN pip install --no-cache-dir soundfile loguru click langid jieba tqdm pyyaml boto3

# Install package without models
COPY setup.py setup.cfg pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Only copy essential source files (exclude models)
COPY boson_multimodal/ /app/boson_multimodal/
WORKDIR /app
```

### 2. Network Volume Integration
```python
MODEL_PATH = "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-generation-3B-base"
TOKENIZER_PATH = "/runpod-volume/higgs_audio/bosonai/higgs-audio-v2-tokenizer"

def load_models():
    model = HiggsAudioModel.from_pretrained(
        MODEL_PATH,
        device_map="cuda:0",
        torch_dtype=torch.bfloat16,
    )
    tokenizer = load_higgs_audio_tokenizer(TOKENIZER_PATH, device="cuda:0")
    return model, tokenizer
```

### 3. S3 Output Integration
```python
import boto3
import os

def upload_to_s3(audio_data, sample_rate, bucket, key):
    """Upload audio data to S3 bucket"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    # Convert audio to bytes
    audio_bytes = BytesIO()
    sf.write(audio_bytes, audio_data, sample_rate)
    audio_bytes.seek(0)
    
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=audio_bytes.getvalue(),
        ContentType='audio/wav'
    )
    
    return f"s3://{bucket}/{key}"
```

## API Interface Design

### Input Format (RunPod Compatible)
```json
{
  "input": {
    "transcript": "Hello world, this is a test.",
    "ref_audio": "belinda",
    "scene_prompt": "quiet indoor setting with warm, friendly tone",
    "temperature": 0.8,
    "top_p": 0.9,
    "s3_bucket": "my-audio-bucket",
    "s3_key": "output/generation_123.wav"
  }
}
```

### Output Format
```json
{
  "output": {
    "success": true,
    "audio_url": "s3://my-audio-bucket/output/generation_123.wav",
    "duration_seconds": 2.5,
    "sample_rate": 24000,
    "text_output": "Hello world, this is a test.",
    "metadata": {
      "model_used": "bosonai/higgs-audio-v2-generation-3B-base",
      "voice_clone": "belinda",
      "generation_parameters": {
        "temperature": 0.8,
        "top_p": 0.9
      }
    }
  },
  "error": null
}
```

## Optimization Strategies

### 1. Memory Management
- **On-demand Loading**: Load models only when request received
- **Model Caching**: Keep models in memory between requests
- **Static KV Cache**: Use static KV cache for faster inference
- **CUDA Memory Cleanup**: Proper cleanup after each request
- **Garbage Collection**: Regular memory cleanup

### 2. Space Optimization
- **Minimal Dependencies**: Only essential packages
- **System Libraries**: Use system Python where possible
- **Exclude Model Weights**: Models stored on network volume
- **Lean Source**: Only copy necessary source files
- **No Build Tools**: Exclude build tools and documentation

### 3. Performance Optimization
- **CUDA Graphs**: Capture CUDA graphs for static KV cache lengths
- **Pre-warming**: Pre-warm model inference paths
- **Request Batching**: Support for batch processing if needed
- **GPU Optimization**: Use bfloat16 for efficiency
- **Caching**: Cache audio tokenizer and collator objects

## Critical Success Factors

### 1. Model Sharing Strategy
- Models loaded from network volume, not container
- Proper permissions on network volume
- Efficient model loading with memory mapping

### 2. Credentials Security
- S3 credentials via environment variables only
- No hardcoded credentials in container
- Secure credential injection by RunPod

### 3. LLM Tone Control
- Leverage scene_prompt parameter for tone modulation
- Support for detailed scene descriptions
- Flexible tone and style control

### 4. Voice Cloning Capability
- One-shot voice cloning via ref_audio parameter
- Support for multi-speaker scenarios
- Reference audio from predefined voice prompts

### 5. Container Size Management
- Continuous monitoring of container size
- Optimization of dependencies and files
- Removal of unnecessary components

## Implementation Phases

### Phase 1: Container Setup
1. Create ultra-thin Dockerfile
2. Set up network volume mounting
3. Configure environment variables
4. Test container size compliance

### Phase 2: Core API Handler
1. Implement RunPod HTTP handler
2. Create model loading utilities
3. Add input validation and parsing
4. Implement basic generation flow

### Phase 3: S3 Integration
1. Add S3 upload functionality
2. Implement error handling for S3 operations
3. Add progress tracking for uploads
4. Test S3 integration with credentials

### Phase 4: Optimization
1. Implement model caching
2. Add memory management
3. Optimize inference performance
4. Add monitoring and logging

### Phase 5: Production Ready
1. Add comprehensive error handling
2. Implement health checks
3. Add metrics and monitoring
4. Create deployment scripts

## Expected Performance Characteristics

### Memory Usage
- **Container Size**: < 5GB
- **Runtime Memory**: ~8-12GB (with models loaded)
- **GPU Memory**: ~6-8GB for model inference
- **Startup Time**: ~30-60 seconds (model loading)

### Inference Performance
- **Audio Generation**: ~2-5 seconds per minute of audio
- **S3 Upload**: ~1-3 seconds depending on file size
- **Total Request Time**: ~5-15 seconds
- **Concurrent Requests**: Limited by GPU memory (1-2 requests)

### Cost Optimization
- **Pay-per-use**: Only pay for actual GPU time
- **Memory Efficiency**: Minimal container overhead
- **Network Volume**: Efficient model storage
- **S3 Storage**: Scalable output storage

## Monitoring and Observability

### Key Metrics
- Request success rate
- Audio generation latency
- S3 upload success rate
- Memory and GPU usage
- Container size compliance

### Error Tracking
- Model loading failures
- S3 upload errors
- Invalid input parameters
- GPU memory errors
- Network volume access issues

This plan provides a comprehensive approach to deploying Higgs Audio V2 as a RunPod serverless endpoint while meeting all specified constraints and requirements.