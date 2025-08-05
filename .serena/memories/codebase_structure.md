# Higgs Audio V2 - Codebase Structure

## Project Directory Structure

```
higgs-audio/
├── boson_multimodal/                    # Main Python package
│   ├── __init__.py                     # Package initialization (empty)
│   ├── constants.py                    # Global constants and tokens
│   ├── data_types.py                   # Data structures for ChatML format
│   ├── data_collator/                  # Training data collation
│   │   ├── __init__.py
│   │   └── higgs_audio_collator.py     # Batch input collation
│   ├── dataset/                         # Dataset loading and processing
│   │   ├── __init__.py
│   │   └── chatml_dataset.py           # ChatML dataset implementation
│   ├── model/                          # Model architecture and implementation
│   │   ├── __init__.py
│   │   └── higgs_audio/
│   │       ├── __init__.py             # Model package initialization
│   │       ├── modeling_higgs_audio.py # Main model class (2,289 lines)
│   │       ├── configuration_higgs_audio.py  # Model configuration classes
│   │       ├── audio_head.py           # Audio decoder projector
│   │       ├── common.py               # Base model class
│   │       ├── cuda_graph_runner.py    # CUDA optimization for performance
│   │       ├── custom_modules.py       # Custom neural network modules
│   │       └── utils.py                # Model utilities and helpers
│   ├── audio_processing/               # Audio tokenization and processing
│   │   ├── __init__.py
│   │   ├── higgs_audio_tokenizer.py    # Audio encoder/decoder
│   │   ├── semantic_module.py          # Semantic audio processing
│   │   ├── quantization/               # Vector quantization for audio
│   │   │   ├── __init__.py
│   │   │   ├── ac.py                   # Arithmetic coding
│   │   │   ├── core_vq.py               # Vector quantization core
│   │   │   ├── core_vq_lsx_version.py  # LSX version of VQ
│   │   │   ├── ddp_utils.py            # Distributed training utilities
│   │   │   ├── distrib.py              # Distributed training helpers
│   │   │   └── vq.py                   # Residual vector quantizer
│   │   └── descriptaudiocodec/         # Third-party Descript Audio Codec
│   │       ├── LICENSE
│   │       └── dac/
│   │           ├── __init__.py
│   │           ├── model/
│   │           │   ├── base.py          # DAC model base
│   │           │   └── dac.py           # DAC implementation
│   │           └── nn/
│   │               ├── layers.py        # Neural network layers
│   │               └── quantize.py      # Quantization layers
│   └── serve/                           # Inference serving engine
│       ├── __init__.py
│       ├── serve_engine.py             # Main serving engine (1,000+ lines)
│       └── utils.py                    # Serving utilities and helpers
├── examples/                            # Usage examples and scripts
│   ├── README.md                        # Examples documentation
│   ├── generation.py                   # Main generation script (600+ lines)
│   ├── scene_prompts/                  # Scene description prompts
│   ├── serve_engine/                    # API server examples
│   │   ├── README.md
│   │   ├── input_samples.py            # Sample input generation
│   │   └── run_hf_example.py           # HuggingFace integration
│   ├── transcript/                     # Multi-speaker dialogue examples
│   │   ├── multi_speaker/
│   │   │   ├── en_argument.txt
│   │   │   └── en_higgs.txt
│   │   └── single_speaker/
│   │       ├── en_basic.txt
│   │       ├── en_dl.txt
│   │       ├── en_higgs_audio_blog.md
│   │       └── experimental/
│   ├── vllm/                           # vLLM integration examples
│   │   ├── README.md
│   │   └── run_chat_completion.py      # OpenAI-compatible API
│   └── voice_prompts/                  # Reference audio for voice cloning
│       ├── belinda.txt belinda.wav
│       ├── bigbang_amy.txt bigbang_amy.wav
│       ├── bigbang_sheldon.txt bigbang_sheldon.wav
│       ├── broom_salesman.txt broom_salesman.wav
│       ├── chadwick.txt chadwick.wav
│       ├── en_man.txt en_man.wav
│       ├── en_woman.txt en_woman.wav
│       ├── fiftyshades_anna.txt fiftyshades_anna.wav
│       ├── mabaoguo.txt mabaoguo.wav
│       ├── mabel.txt mabel.wav
│       ├── profile.yaml                 # Voice profile configuration
│       ├── shrek_donkey.txt shrek_donkey.wav
│       ├── shrek_fiona.txt shrek_fiona.wav
│       ├── shrek_shrek.txt shrek_shrek.wav
│       ├── vex.txt vex.wav
│       ├── zh_man_sichuan.txt zh_man_sichuan.wav
├── figures/                            # Architecture diagrams and metrics
│   ├── dual_ffn_comparison_*          # Performance comparison charts
│   ├── emergent-tts-emotions-win-rate.png
│   ├── higgs_audio_tokenizer_architecture.png
│   ├── higgs_audio_v2_architecture_combined.png
│   └── higgs_audio_v2_open_source_delay_pattern.png
├── tech_blogs/                         # Technical blog posts
│   ├── ARCHITECTURE_BLOG.md            # DualFFN architecture explanation
│   └── TOKENIZER_BLOG.md              # Audio tokenizer technical details
├── .github/workflows/                  # CI/CD pipeline
│   └── test.yml                        # Ruff linting workflow
├── .gitignore                         # Git ignore rules
├── requirements.txt                    # Python dependencies
├── setup.py                           # Package setup script
├── setup.cfg                          # Package setup configuration
├── pyproject.toml                     # Project configuration with ruff settings
├── README.md                          # Main project documentation
└── Documentation files (CLAUDE framework):
    ├── CLAUDE.md                       # AI assistant guidance
    ├── CONDUCTOR.md                    # Project coordination framework
    ├── ARCHITECTURE.md                 # System architecture documentation
    ├── BUILD.md                        # Build and deployment instructions
    ├── CONFIG.md                       # Configuration management
    ├── CONTRIBUTING.md                 # Developer guidelines
    ├── DATA_MODEL.md                   # Data structures and schema
    ├── DESIGN.md                       # Visual design system
    ├── ERRORS.md                       # Error tracking system
    ├── JOURNAL.md                      # Development journal
    ├── PLAYBOOKS/DEPLOY.md             # Deployment procedures
    ├── TASKS.md                        # Active task management
    ├── TEST.md                         # Testing strategy
    ├── UIUX.md                         # User interface guidelines
    └── API.md                          # API documentation
```

## Core Component Breakdown

### 1. Main Package (`boson_multimodal/`)
**Purpose**: Contains all the core functionality for audio generation

#### `constants.py`
- **Purpose**: Global constants and token definitions
- **Key Elements**: `AUDIO_IN_TOKEN`, `AUDIO_OUT_TOKEN`, `EOS_TOKEN`
- **Line Count**: ~50 lines

#### `data_types.py`
- **Purpose**: Data structures for multimodal conversations
- **Key Classes**: `AudioContent`, `TextContent`, `Message`, `ChatMLSample`
- **Usage**: Defines the ChatML format for text/audio conversations
- **Line Count**: ~80 lines

### 2. Model Subsystem (`boson_multimodal/model/higgs_audio/`)
**Purpose**: Core model architecture and neural network components

#### `modeling_higgs_audio.py` (2,289 lines)
- **Purpose**: Main model class and generation logic
- **Key Class**: `HiggsAudioModel` (lines 793-2288)
- **Key Methods**:
  - `forward()` - Main forward pass
  - `generate()` - Audio generation logic
  - `_sample_audio_tokens()` - Audio token sampling
  - `_prepare_kv_cache()` - KV cache management
- **Dependencies**: Based on HuggingFace transformer patterns

#### `configuration_higgs_audio.py`
- **Purpose**: Model configuration classes
- **Key Classes**: `HiggsAudioConfig`, `HiggsAudioEncoderConfig`
- **Usage**: Defines model architecture parameters

#### `audio_head.py`
- **Purpose**: Audio decoder and projection components
- **Key Classes**: `HiggsAudioDecoderProjector`

#### `custom_modules.py`
- **Purpose**: Custom neural network modules
- **Key Classes**: `PartiallyFrozenLinear`, `PartiallyFrozenEmbedding`

### 3. Audio Processing (`boson_multimodal/audio_processing/`)
**Purpose**: Audio encoding/decoding and tokenization

#### `higgs_audio_tokenizer.py`
- **Purpose**: Audio feature extraction and tokenization
- **Key Classes**: `HiggsAudioFeatureExtractor`, `HiggsAudioTokenizer`
- **Function**: Converts audio to/from token representations

#### `semantic_module.py`
- **Purpose**: Semantic audio processing components
- **Architecture**: Encoder-decoder structure for audio understanding

#### `quantization/`
- **Purpose**: Vector quantization for efficient audio representation
- **Key Components**: Vector quantization, arithmetic coding
- **Files**: `core_vq.py`, `vq.py`, `ac.py`, `distrib.py`

#### `descriptaudiocodec/`
- **Purpose**: Third-party Descript Audio Codec integration
- **Origin**: Derived from xcodec repository
- **License**: Separate LICENSE file attribution

### 4. Dataset and Training (`boson_multimodal/dataset/`, `boson_multimodal/data_collator/`)
**Purpose**: Data loading and training preparation

#### `chatml_dataset.py`
- **Purpose**: CharterML format dataset handling
- **Key Classes**: `ChatMLDatasetSample`, `DatasetInterface`
- **Function**: Loads and processes conversation datasets

#### `higgs_audio_collator.py`
- **Purpose**: Batch creation for training
- **Key Classes**: `HiggsAudioBatchInput`, `HiggsAudioSampleCollator`
- **Function**: Prepares batches for efficient training

### 5. Serving Engine (`boson_multimodal/serve/`)
**Purpose**: Inference serving and API functionality

#### `serve_engine.py`
- **Purpose**: Main serving engine for audio generation
- **Key Classes**: `HiggsAudioServeEngine`, `HiggsAudioResponse`
- **Key Features**: Async generation, streaming support, batch processing
- **Line Count**: ~1,000+ lines

#### `utils.py`
- **Purpose**: Serving utilities and helpers
- **Functions**: Text processing, audio format conversion, base64 encoding

### 6. Examples (`examples/`)
**Purpose**: Comprehensive usage examples and integration scripts

#### `generation.py`
- **Purpose**: Main generation script for all features
- **Key Features**: 
  - Zero-shot voice cloning
  - Multi-speaker dialogue
  - Smart voice assignment
  - Reference audio processing
- **Line Count**: ~600+ lines

#### `vllm/run_chat_completion.py`
- **Purpose**: OpenAI-compatible API server using vLLM
- **Features**: High-throughput inference, chat completion format

#### `serve_engine/run_hf_example.py`
- **Purpose**: HuggingFace integration example
- **Usage**: Shows how to use the model with HuggingFace ecosystem

### 7. Documentation and Resources
**Purpose**: Comprehensive documentation and technical details

#### `README.md`
- **Purpose**: Main project documentation
- **Content**: Installation, usage, benchmark results, examples

#### `tech_blogs/`
- **ARCHITECTURE_BLOG.md**: DualFFN architecture technical details
- **TOKENIZER_BLOG.md`: Audio tokenizer design and implementation

#### `figures/`
- **Purpose**: Visual aids and performance metrics
- **Content**: Architecture diagrams, comparison charts, win-rate graphs

## Key Design Patterns

### 1. HuggingFace Integration
- **Pattern**: Extends HuggingFace transformer patterns
- **Base Classes**: Uses `PreTrainedModel` as foundation
- **Configuration**: Follows HuggingFace configuration patterns
- **Compatibility**: Designed to work with HuggingFace ecosystem

### 2. Modular Architecture
- **Pattern**: Clear separation of concerns
- **Advantage**: Easy to swap components (tokenizers, models, etc.)
- **Implementation**: Separate modules for audio, model, serving

### 3. Data Flow
1. **Input**: ChatML format with text/audio mixing
2. **Tokenization**: Audio tokenized via `higgs_audio_tokenizer.py`
3. **Model**: `HiggsAudioModel` processes tokens
4. **Generation**: `generate()` method produces audio tokens
5. **Output**: `serve_engine.py` converts tokens to audio files

### 4. Performance Optimization
- **CUDA Graphs**: `cuda_graph_runner.py` for GPU optimization
- **Caching**: KV caching in `modeling_higgs_audio.py`
- **Batching**: Support for batch processing throughout
- **Memory**: Careful memory management in audio processing

This well-organized codebase follows modern AI/ML development practices with clear separation of concerns, comprehensive documentation, and production-ready deployment capabilities.