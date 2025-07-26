# Technology Stack

## Core Technologies
- **Python 3.10+**: Primary programming language
- **PyTorch**: Deep learning framework for model implementation
- **Transformers**: HuggingFace library for model architecture
- **CUDA**: GPU acceleration (24GB+ GPU memory recommended)

## Audio Processing
- **librosa**: Audio processing and feature extraction
- **torchaudio**: PyTorch audio processing
- **descript-audio-codec**: Audio codec implementation

## Key Dependencies
- **transformers**: >=4.45.1,<4.47.0 (specific version range required)
- **accelerate**: >=0.26.0 for distributed training
- **vector_quantize_pytorch**: Vector quantization for audio tokens
- **boto3**: AWS S3 integration for model storage
- **pydantic**: Data validation and type hints

## Infrastructure
- **Docker**: NVIDIA Deep Learning Containers (nvcr.io/nvidia/pytorch:25.02-py3)
- **vLLM**: High-throughput inference engine
- **HuggingFace Hub**: Model hosting and distribution
- **AWS S3**: Storage backend

## Development Tools
- **ruff**: Code formatting and linting (version 0.12.2)
- **click**: CLI interface development
- **loguru**: Advanced logging
- **pydub**: Audio manipulation

## Hardware Requirements
- **GPU**: NVIDIA GPU with 24GB+ VRAM recommended
- **Memory**: Sufficient system RAM for large models
- **Storage**: Space for model weights (3.6B LLM + 2.2B audio adapter)