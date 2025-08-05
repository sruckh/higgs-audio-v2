# Higgs Audio V2 - RunPod Serverless System Architecture

## System Overview

The Higgs Audio V2 RunPod Serverless system is designed as a high-performance, space-optimized audio generation endpoint that leverages one-shot voice cloning and LLM-controlled tone modulation. The architecture follows a microservices pattern optimized for serverless deployment with extreme space constraints (5GB container limit).

### Core Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    RunPod Serverless Platform                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   HTTP Handler  │  │ Model Manager   │  │ S3 Uploader     │  │
│  │    (FastAPI)    │  │   (Singleton)   │  │   (boto3)       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Request       │  │   Audio         │  │   File          │  │
│  │   Validator      │  │   Generator     │  │   Manager       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Input         │  │   Higgs Audio   │  │   Temporary     │  │
│  │   Processor      │  │   Model Client  │  │   Storage       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     Network Volume                          │ │
│  │  /runpod-volume/higgs_audio/                              │ │
│  │  ├─ bosonai/higgs-audio-v2-generation-3B-base           │ │
│  │  ├─ bosonai/higgs-audio-v2-tokenizer                     │ │
│  │  └─ voice_prompts/                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Environment Variables                     │ │
│  │  ├─ AWS_ACCESS_KEY_ID                                     │ │
│  │  ├─ AWS_SECRET_ACCESS_KEY                                 │ │
│  │  ├─ AWS_DEFAULT_REGION                                  │ │
│  │  └─ MODEL_PATH=/runpod-volume/higgs_audio                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Design Specifications

### 1. HTTP Handler Component (`api_handler.py`)

**Responsibilities:**
- HTTP request/response handling
- RunPod serverless protocol compliance
- Request validation and parsing
- Error handling and response formatting

**Interface:**
```python
class RunPodAPIHandler:
    def __init__(self, model_manager: ModelManager, s3_uploader: S3Uploader):
        self.model_manager = model_manager
        self.s3_uploader = s3_uploader
    
    async def handle_request(self, request: dict) -> dict:
        """Handle incoming RunPod serverless request"""
        pass
    
    def validate_request(self, request_data: dict) -> ValidationResult:
        """Validate input request format and parameters"""
        pass
    
    def format_response(self, success: bool, data: dict, error: str = None) -> dict:
        """Format response according to RunPod specification"""
        pass
```

**API Endpoints:**
```
POST /runsync    # Synchronous audio generation
GET  /health     # Health check endpoint
GET  /ready      # Readiness check
GET  /metrics    # Performance metrics
```

### 2. Model Manager Component (`model_manager.py`)

**Responsibilities:**
- Model lifecycle management (loading, unloading, caching)
- Memory optimization and garbage collection
- Model inference orchestration
- KV cache management

**Interface:**
```python
class ModelManager:
    def __init__(self, model_path: str, tokenizer_path: str, device: str = "cuda:0"):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.device = device
        self._model = None
        self._tokenizer = None
        self._collator = None
        self._kv_caches = None
        self._last_access = None
    
    async def load_models(self) -> None:
        """Load models with memory optimization"""
        pass
    
    async def generate_audio(self, request: GenerationRequest) -> GenerationResult:
        """Generate audio with optimal memory usage"""
        pass
    
    def cleanup_memory(self) -> None:
        """Clean up GPU memory and unused resources"""
        pass
    
    def get_model_info(self) -> ModelInfo:
        """Get current model status and information"""
        pass
```

**Memory Management Strategy:**
- **Lazy Loading**: Load models only when first request arrives
- **LRU Caching**: Keep models in memory with access-based prioritization
- **Static KV Cache**: Pre-compile KV caches for different lengths
- **Garbage Collection**: Periodic cleanup of unused resources

### 3. Audio Generator Component (`audio_generator.py`)

**Responsibilities:**
- Audio generation pipeline orchestration
- Voice cloning parameter processing
- LLM tone control implementation
- Chunking strategy management

**Interface:**
```python
class AudioGenerator:
    def __init__(self, model_client: HiggsAudioModelClient, audio_tokenizer):
        self.model_client = model_client
        self.audio_tokenizer = audio_tokenizer
    
    async def generate(
        self,
        transcript: str,
        ref_audio: Optional[str] = None,
        scene_prompt: Optional[str] = None,
        generation_params: GenerationParameters = None,
    ) -> AudioGenerationResult:
        """Generate audio with voice cloning and tone control"""
        pass
    
    def prepare_generation_context(
        self,
        transcript: str,
        ref_audio: Optional[str],
        scene_prompt: Optional[str],
    ) -> Tuple[List[Message], List[torch.Tensor]]:
        """Prepare generation context with voice and tone parameters"""
        pass
    
    def chunk_text(self, text: str, chunk_method: str = None) -> List[str]:
        """Apply text chunking strategy for long transcripts"""
        pass
    
    def apply_tone_control(
        self,
        messages: List[Message],
        scene_prompt: Optional[str],
    ) -> List[Message]:
        """Apply LLM-based tone control through scene prompting"""
        pass
```

### 4. S3 Uploader Component (`s3_uploader.py`)

**Responsibilities:**
- S3 client management and credential handling
- Audio file upload and metadata storage
- Upload progress tracking and error handling
- URL generation andsigned URL support

**Interface:**
```python
class S3Uploader:
    def __init__(
        self,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = "us-east-1",
    ):
        self.aws_credentials = {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'region_name': region_name,
        }
        self._s3_client = None
    
    async def upload_audio(
        self,
        audio_data: torch.Tensor,
        sample_rate: int,
        bucket: str,
        key: str,
        metadata: dict = None,
    ) -> S3UploadResult:
        """Upload audio data to S3 bucket"""
        pass
    
    def generate_s3_url(self, bucket: str, key: str) -> str:
        """Generate S3 URL for uploaded file"""
        pass
    
    def validate_bucket_access(self, bucket: str) -> bool:
        """Validate S3 bucket permissions and accessibility"""
        pass
```

### 5. Request Validator Component (`request_validator.py`)

**Responsibilities:**
- Input parameter validation
- Security constraint checking
- Business logic validation
- Error message generation

**Interface:**
```python
class RequestValidator:
    def __init__(self, max_transcript_length: int = 10000):
        self.max_transcript_length = max_transcript_length
    
    def validate_generation_request(self, request_data: dict) -> ValidationResult:
        """Validate audio generation request parameters"""
        pass
    
    def validate_s3_parameters(self, bucket: str, key: str) -> ValidationResult:
        """Validate S3 bucket and key parameters"""
        pass
    
    def validate_voice_reference(self, ref_audio: str) -> ValidationResult:
        """Validate voice reference audio availability"""
        pass

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None, data: dict = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.data = data or {}
```

## Data Structures and Interfaces

### 1. Request/Response Data Models

**Generation Request:**
```python
@dataclass
class GenerationRequest:
    transcript: str                    # Text to convert to speech
    ref_audio: Optional[str] = None     # Voice reference name
    scene_prompt: Optional[str] = None # Scene description for tone control
    temperature: float = 1.0           # Generation temperature
    top_k: int = 50                    # Top-k filtering
    top_p: float = 0.95               # Top-p filtering
    max_new_tokens: int = 2048         # Maximum audio tokens
    chunk_method: Optional[str] = None # Text chunking strategy
    chunk_max_word_num: int = 200      # Word chunking limit
    chunk_max_num_turns: int = 1       # Turn chunking limit
    ras_win_len: int = 7               # RAS window length
    ras_win_max_num_repeat: int = 2    # RAS max repeat
    seed: Optional[int] = None         # Random seed
    s3_bucket: Optional[str] = None     # S3 bucket for output
    s3_key: Optional[str] = None        # S3 key for output
```

**Generation Response:**
```python
@dataclass
class GenerationResponse:
    success: bool                      # Operation success status
    audio_url: Optional[str] = None     # S3 URL to generated audio
    duration_seconds: Optional[float] = None  # Audio duration
    sample_rate: int = 24000           # Audio sample rate
    text_output: Optional[str] = None   # Generated text transcript
    metadata: dict = None              # Generation metadata
    error: Optional[str] = None         # Error message if failed
```

**Generation Parameters:**
```python
@dataclass
class GenerationParameters:
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.95
    max_new_tokens: int = 2048
    chunk_method: Optional[str] = None
    chunk_max_word_num: int = 200
    chunk_max_num_turns: int = 1
    ras_win_len: int = 7
    ras_win_max_num_repeat: int = 2
    seed: Optional[int] = None
```

### 2. Internal Data Models

**Model Configuration:**
```python
@dataclass
class ModelConfig:
    model_path: str
    tokenizer_path: str
    device: str
    dtype: torch.dtype = torch.bfloat16
    kv_cache_sizes: List[int] = None
    use_static_kv_cache: bool = True
    max_new_tokens: int = 2048
```

**Audio Generation Result:**
```python
@dataclass
class AudioGenerationResult:
    audio_data: torch.Tensor           # Generated audio waveform
    sample_rate: int                   # Audio sample rate
    text_output: str                   # Output text transcript
    generation_time: float             # Generation time in seconds
    chunks_processed: int             # Number of chunks processed
    model_info: dict                   # Model information
```

**S3 Upload Result:**
```python
@dataclass
class S3UploadResult:
    success: bool
    url: str
    upload_time: float
    file_size: int
    etag: Optional[str] = None
    error: Optional[str] = None
```

## Container Architecture Design

### 1. Container Structure
```
/app/
├── serverless_handler.py          # Main entry point
├── components/
│   ├── api_handler.py            # HTTP request handling
│   ├── model_manager.py          # Model lifecycle management
│   ├── audio_generator.py        # Audio generation pipeline
│   ├── s3_uploader.py           # S3 upload functionality
│   ├── request_validator.py     # Input validation
│   └── file_manager.py          # File/temporary storage
├── utils/
│   ├── memory_utils.py          # Memory optimization utilities
│   ├── audio_utils.py           # Audio processing utilities
│   ├── logging_utils.py         # Logging configuration
│   └── metrics_utils.py        # Performance metrics
├── boson_multimodal/            # Higgs Audio source code (minimal)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container build file
└── config.yaml                  # Configuration settings
```

### 2. Minimal Dependencies Strategy
```txt
# Core dependencies only
torch==2.0.1
transformers>=4.24.0
runpod==0.8.4
soundfile>=0.12.0
loguru>=0.7.0
boto3>=1.26.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.20.0

# Only essential audio packages
jieba>=0.42.1
langid>=1.1.6
tqdm>=4.64.0
pyyaml>=6.0
numpy>=1.22.0

# Development (excluded from production)
-r requirements-dev.txt
```

### 3. Dockerfile Design
```dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODEL_PATH=/runpod-volume/higgs_audio

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code (minimal)
COPY serverless_handler.py /app/
COPY components/ /app/components/
COPY utils/ /app/utils/
COPY boson_multimodal/ /app/boson_multimodal/

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "serverless_handler.py"]
```

## Data Flow and Integration Patterns

### 1. Request Processing Flow
```
1. HTTP Request → RunPod Serverless
   ↓
2. HTTP Handler → Request Validation
   ↓
3. Request Validator → Component Orchestration
   ↓
4. Model Manager → Audio Generation
   ↓
5. Audio Generator → S3 Upload
   ↓
6. S3 Uploader → Response Formatting
   ↓
7. HTTP Response → Client
```

### 2. Model Loading Flow
```
1. First Request → Model Manager
   ↓
2. Check Network Volume → Load Models
   ↓
3. Initialize KV Caches → Capture CUDA Graphs
   ↓
4. Cache Models → Return Ready Status
   ↓
5. Subsequent Requests → Use Cached Models
```

### 3. Audio Generation Flow
```
1. Generation Request → Audio Generator
   ↓
2. Prepare Context → Process Voice Reference
   ↓
3. Apply Tone Control → Chunk Text (if needed)
   ↓
4. Model Inference → Generate Audio Tokens
   ↓
5. Decode Audio → Return Waveform
```

### 4. S3 Integration Flow
```
1. Audio Result → S3 Uploader
   ↓
2. Convert to Bytes → Prepare Upload
   ↓
3. S3 Client Upload → Track Progress
   ↓
4. Generate URL → Return Result
```

## Error Handling and Resilience

### 1. Error Classification
```python
class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    MODEL_ERROR = "model_error"
    INFERENCE_ERROR = "inference_error"
    S3_UPLOAD_ERROR = "s3_upload_error"
    SYSTEM_ERROR = "system_error"
    TIMEOUT_ERROR = "timeout_error"
```

### 2. Error Response Format
```json
{
  "output": {
    "success": false,
    "error": {
      "type": "validation_error",
      "message": "Invalid transcript format",
      "code": "INVALID_TRANSCRIPT",
      "details": {
        "field": "transcript",
        "constraint": "max_length=10000",
        "actual_length": 15000
      }
    }
  }
}
```

### 3. Resilience Patterns
- **Circuit Breaker**: For model loading failures
- **Retry Logic**: For S3 upload failures
- **Graceful Degradation**: For partial generation failures
- **Health Checks**: Continuous model health monitoring

## Security Considerations

### 1. Input Security
- Maximum transcript length limits
- Voice reference whitelist validation
- Path traversal protection for file paths
- SQL injection prevention for S3 keys

### 2. Credential Security
- Environment variable injection for AWS credentials
- No hardcoded credentials in container
- Temporary credential rotation support
- IAM role assumption capability

### 3. Output Security
- S3 bucket permission validation
- Signed URL expiration control
- Content-type validation for uploads
- Audit logging for all operations

## Performance Optimization Patterns

### 1. Memory Optimization
- **Model Caching**: LRU-based model instance caching
- **KV Cache Pre-allocation**: Static KV cache for common lengths
- **Garbage Collection**: Periodic memory cleanup
- **Tensor Management**: Efficient tensor allocation and cleanup

### 2. Inference Optimization
- **CUDA Graphs**: Pre-compiled CUDA graphs for static KV caches
- **Batch Processing**: Support for multiple requests batching
- **Prefetching**: Model warmup for first requests
- **Quantization**: bfloat16 precision for efficiency

### 3. I/O Optimization
- **Streaming Upload**: S3 multipart upload for large files
- **Buffer Management**: Efficient audio buffer handling
- **Network Optimization**: Connection pooling for S3
- **Caching**: Audio chunk caching for repeated requests

This architecture provides a comprehensive foundation for deploying Higgs Audio V2 as a RunPod serverless endpoint while meeting all specified constraints and requirements.