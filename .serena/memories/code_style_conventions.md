# Higgs Audio V2 - Code Style and Conventions

## Python Code Style

### Formatting Rules (Ruff Configuration)
- **Line Length**: 119 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Quote Style**: Double quotes for strings
- **Target Python Version**: Python 3.10+
- **Trailing Commas**: Enabled in data structures

### Naming Conventions
- **Classes**: PascalCase (e.g., `HiggsAudioModel`, `AudioContent`)
- **Methods and Functions**: snake_case (e.g., `_prepare_kv_cache`, `generate_audio`)
- **Variables**: snake_case (e.g., `audio_tokens`, `model_weights`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `AUDIO_IN_TOKEN`, `EOS_TOKEN`)
- **Private Members**: Leading underscore (e.g., `_forward_core`, `_update_causal_mask`)

### Type Hints
- **Usage**: Comprehensive type hints throughout the codebase
- **Imports**: `from typing import Optional, Tuple, Union, List, Dict, Any`
- **Style**: Use Union types sparingly, prefer specific types
- **Optional**: Extensive use of `Optional` for nullable fields

### Docstrings
- **Format**: Triple quotes for module, class, and method documentation
- **Style**: Clear, concise descriptions explaining purpose and usage
- **Examples**: Main classes and methods include usage examples

### Import Organization
- **Standard Libraries**: First (e.g., `import os`, `import math`)
- **Third-Party**: Second (e.g., `import torch`, `from dataclasses import dataclass`)
- **Local Imports**: Third with relative imports (e.g., `from .common import HiggsAudioPreTrainedModel`)
- **Sorting**: Alphabetical within groups
- **Blank Lines**: 2 blank lines between import groups

## Code Structure Patterns

### Class Design
- **Inheritance**: Based on HuggingFace patterns (PreTrainedModel)
- **Composition**: Preferred over deep inheritance
- **Data Classes**: Used for simple data structures (AudioContent, TextContent)
- **Enums**: Used for finite state sets (GenerationMode)

### Method Organization
- **Public Methods**: Main functionality with comprehensive docstrings
- **Private Methods**: Internal implementation with leading underscore
- **Special Methods**: `__init__`, `__call__`, etc. as needed
- **Properties**: Used for attribute access when needed

### Error Handling
- **Logging**: Uses `transformers.utils.logging` for consistent logging
- **Validation**: Input validation in public methods
- **Type Safety**: Runtime type checks where necessary

### Configuration Management
- **Configuration Classes**: Separate classes for model configuration
- **DataClasses**: Used for structured configuration
- **Environment Variables**: Used for deployment-specific settings

## AI/ML Specific Conventions

### Model Architecture
- **Transformer-Based**: Follows HuggingFace transformer patterns
- **Modular Design**: Clear separation of encoder, decoder, and attention components
- **Caching**: KV caching implemented for generation efficiency

### Torch/PyTorch Patterns
- **Device Management**: Explicit device handling (`cuda`, `cpu`)
- **Tensor Operations**: Proper tensor shapes and dimensions
- **Training/Inference**: Separate paths for training vs inference optimizations

### Audio Processing
- **Sampling Rates**: Explicit handling of audio sampling rates
- **Tokenization**: Separate tokenizer classes for audio encoding/decoding
- **Multi-modal**: Unified handling of text and audio data

## Testing and Quality

### Testing Framework
- **Unit Testing**: Uses pytest-style patterns (pytest directory not visible but likely used)
- **Integration Testing**: Model loading and basic functionality
- **Example Scripts**: Comprehensive examples in `examples/` directory

### Code Quality Tools
- **Linter**: Ruff v0.12.2 with specific configuration
- **Formatter**: Ruff format for consistent code style
- **Pre-commit**: GitHub Actions workflow for linting on push/PR

### Performance Considerations
- **CUDA Optimization**: CUDA graph runner for performance
- **Memory Management**: Careful tensor memory handling
- **Batch Processing**: Support for batched inference

## Documentation Standards

### Code Documentation
- **Module Headers**: Comprehensive module descriptions
- **Class Docs**: Clear purpose and usage instructions
- **Method Docs**: Parameter descriptions and return value explanations
- **Inline Comments**: Strategic comments for complex logic

### External Documentation
- **README**: Comprehensive installation and usage instructions
- **Examples**: Working example scripts for all major features
- **Technical Blogs**: Architecture and tokenizer explanations in `tech_blogs/`

## Git and Version Control

### Commit Style
- **Conventional Commits**: Following standard commit message format
- **Branch Naming**: Feature branches for development
- **PR Process**: Code review through pull requests

### Repository Organization
- **Clear Structure**: Well-organized directory hierarchy
- **Modular Code**: Logical grouping of related functionality
- **Examples Included**: Comprehensive usage examples

This codebase follows modern Python best practices with strong typing, comprehensive documentation, and maintains consistency with HuggingFace transformer patterns for AI/ML development.