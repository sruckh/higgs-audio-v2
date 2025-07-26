# Codebase Structure

## Main Package Structure
```
boson_multimodal/
├── __init__.py
├── constants.py              # Project-wide constants
├── data_types.py            # Core data structures (ChatMLSample, Message, AudioContent)
├── audio_processing/        # Audio tokenization and codec
│   ├── higgs_audio_tokenizer.py    # Main audio tokenizer (HiggsAudioTokenizer)
│   ├── semantic_module.py          # Semantic audio processing
│   ├── descriptaudiocodec/         # Audio codec implementation
│   └── quantization/               # Vector quantization modules
├── model/higgs_audio/       # Core model implementation
│   ├── modeling_higgs_audio.py     # Main model (HiggsAudioModel) - 2289 lines
│   ├── configuration_higgs_audio.py # Model configuration
│   ├── audio_head.py               # Audio decoder projector
│   ├── common.py                   # Base model classes
│   ├── custom_modules.py           # Specialized model components
│   ├── cuda_graph_runner.py       # CUDA optimization
│   └── utils.py                    # Model utilities and helper functions
├── serve/                   # Inference and serving
│   ├── serve_engine.py             # Main serving engine (HiggsAudioServeEngine)
│   └── utils.py                    # Serving utilities
├── data_collator/          # Data processing for training/inference
│   └── higgs_audio_collator.py     # Data batching and collation
└── dataset/                # Dataset handling
    └── chatml_dataset.py           # ChatML format dataset processing
```

## Examples and Scripts
```
examples/
├── generation.py           # Main CLI generation script
├── serve_engine/          # Serving examples
│   └── run_hf_example.py  # HuggingFace integration example
├── vllm/                  # High-throughput inference
│   ├── run_chat_completion.py  # vLLM client example
│   └── README.md          # vLLM setup instructions
├── voice_prompts/         # Reference audio files and configurations
│   ├── *.wav             # Audio samples for voice cloning
│   ├── *.txt             # Corresponding transcripts
│   └── profile.yaml      # Voice configuration
├── transcript/           # Text samples for generation
│   ├── single_speaker/   # Single speaker examples
│   └── multi_speaker/    # Multi-speaker dialog examples
└── scene_prompts/        # Scene description templates
```

## Key Files and Their Purposes

### Core Model Files
- **`modeling_higgs_audio.py`**: Main model implementation (HiggsAudioModel class, 2289 lines)
- **`serve_engine.py`**: Primary inference interface (HiggsAudioServeEngine)
- **`higgs_audio_tokenizer.py`**: Audio encoding/decoding (critical for audio processing)

### Configuration and Setup
- **`pyproject.toml`**: Ruff configuration, Python packaging
- **`requirements.txt`**: Dependencies list
- **`setup.cfg`**: Package metadata

### Documentation and Examples
- **`README.md`**: Main project documentation
- **`CLAUDE.md`**: AI assistant guidance
- **`examples/generation.py`**: Main user interface for generation

## Import Patterns
- Models: `from boson_multimodal.model.higgs_audio import HiggsAudioModel`
- Serving: `from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine`
- Data types: `from boson_multimodal.data_types import ChatMLSample, Message`
- Audio processing: `from boson_multimodal.audio_processing import load_higgs_audio_tokenizer`

## Critical Dependencies Between Components
- **Serve Engine** depends on **Model** + **Audio Tokenizer** + **Data Collator**
- **Model** depends on **Configuration** + **Audio Head** + **Custom Modules**
- **Examples** depend on **Serve Engine** + **Data Types**
- **vLLM integration** requires specific model format and tokenizer compatibility