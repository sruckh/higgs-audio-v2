# Code Style and Conventions

## Code Formatting
- **Tool**: Ruff (version 0.12.2) for formatting and linting
- **Line Length**: 119 characters (configured in pyproject.toml)
- **Indentation**: 4 spaces (space-based, not tabs)
- **Quote Style**: Double quotes for strings
- **Target Python**: 3.10+

## Naming Conventions
- **Classes**: PascalCase (e.g., `HiggsAudioServeEngine`, `HiggsAudioModel`)
- **Functions/Methods**: snake_case (e.g., `prepare_inputs`, `load_higgs_audio_tokenizer`)
- **Variables**: snake_case (e.g., `audio_tokenizer`, `model_name_or_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `AUDIO_PLACEHOLDER_TOKEN`, `CURR_DIR`)
- **Private Methods**: Leading underscore (e.g., `_prepare_inputs`, `_prepare_kv_caches`)

## Type Hints
- **Required**: All function parameters and return types should have type hints
- **Imports**: Use `from typing import Optional, Union, List, Dict` etc.
- **Example**: `def __init__(self, model_name_or_path: str, device: str = "cuda") -> None:`

## Documentation
- **Docstrings**: Use triple quotes with detailed parameter descriptions
- **Format**: Google-style docstrings with Args, Returns sections
- **Example**:
```python
"""
Initialize the HiggsAudioServeEngine.

Args:
    model_name_or_path (str): The name or path of the model to load.
    device (str): The device to use for the model.
    
Returns:
    None
"""
```

## Import Organization
- **Standard library**: First
- **Third-party**: Second, with 2 lines after imports
- **Local imports**: Last
- **Ruff handles**: Import sorting automatically

## File Organization
- **Main package**: `boson_multimodal/`
- **Models**: `boson_multimodal/model/higgs_audio/`
- **Audio processing**: `boson_multimodal/audio_processing/`
- **Serving**: `boson_multimodal/serve/`
- **Examples**: `examples/` (separate from main package)

## Error Handling
- Use proper exception handling with specific exception types
- Log errors using `loguru` logger
- Provide meaningful error messages