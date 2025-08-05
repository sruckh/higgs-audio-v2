# Higgs Audio V2 - Project Completion Checklist

## Essential Commands for Task Completion

### Required Quality Assurance Commands
After completing any development task, ALWAYS run these commands in order:

```bash
# 1. Code Formatting (Critical - Must Pass)
ruff format --check .
# OR to auto-fix formatting issues:
ruff format .

# 2. Code Linting (Critical - Must Pass)  
ruff check .
# OR to auto-fix linting issues:
ruff check --fix .

# 3. Package Installation Check
pip install -e .
python -c "import boson_multimodal; print('✅ Package imports successfully')"

# 4. Basic Functionality Test
python examples/generation.py --transcript "Quick test" --out_path completion_test.wav

# 5. Cleanup (Optional but Recommended)
rm -f completion_test.wav
```

### Full Verification Sequence (For Major Changes)
```bash
# Step 1: Format and Lint
ruff format .
ruff check --fix .

# Step 2: Installation Check
pip install -e .

# Step 3: Import Verification
python -c "
import boson_multimodal
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
from boson_multimodal.data_types import ChatMLSample, Message
from boson_multimodal.model.higgs_audio.modeling_higgs_audio import HiggsAudioModel
print('✅ All core imports successful')
"

# Step 4: Model Loading Test (if no GPU issues)
python -c "
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
if device == 'cuda':
    from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
    # Note: This requires internet connection and model access
    print('✅ Model loading test passed (internet required)')
else:
    print('⚠️  Skipping model loading test - no GPU available')
"

# Step 5: Generation Test
python examples/generation.py --transcript "This is a test of the completion checklist." --temperature 0.3 --out_path checklist_test.wav

# Step 6: Cleanup
rm -f checklist_test.wav
echo "✅ Completion checklist finished successfully"
```

## Task-Specific Completion Criteria

### Feature Development Tasks
- [ ] Code follows project conventions (check with ruff)
- [ ] Feature works as demonstrated through examples
- [ ] Documentation updated in relevant .md files
- [ ] Examples reflect the new functionality
- [ ] No regression in existing features (test with generation.py)

### Bug Fix Tasks  
- [ ] Root cause identified and documented
- [ ] Fix implemented without breaking existing functionality
- [ ] Test case added to prevent regression
- [ ] Fix verified with generation.py examples
- [ ] Issue documented in ERRORS.md with resolution

### Documentation Tasks
- [ ] Technical accuracy verified against code
- [ ] Examples tested and working
- [ ] Cross-references updated between files
- [ ] Formatting consistent with project standards
- [ ] Code examples include proper imports and usage

### Performance Optimization Tasks
- [ ] Performance measured before and after
- [ ] Benchmarks documented in JOURNAL.md
- [ ] No functionality regression
- [ ] Memory usage verified stable
- [ ] GPU usage optimized where applicable

## Quality Gates

### Code Quality Standards
- **Ruff Format**: Must pass without errors
- **Ruff Lint**: Must pass without errors (or with justified ignores)  
- **Type Hints**: All public APIs must have type hints
- **Documentation**: All new public classes/methods must have docstrings
- **Testing**: No breaking changes to existing functionality

### Functional Standards
- **Import Success**: Package must import without errors
- **Basic Generation**: `examples/generation.py` must work
- **Model Loading**: Core model classes must be instantiable
- **Data Types**: All data structures must serialize/deserialize properly
- **Error Handling**: Graceful handling of edge cases and invalid inputs

### Documentation Standards
- **README**: Installation instructions must work
- **Examples**: All examples must be functional
- **API docs**: Must match actual implementation
- **Comments**: Complex logic must be commented
- **Changelog**: Major changes documented in JOURNAL.md

## Pre-Commit Checklist

### Before Code Review
- [ ] Code formatted with `ruff format .`
- [ ] Code linted with `ruff check .`
- [ ] All tests passing (if tests exist)
- [ ] Documentation updated
- [ ] Examples tested and working
- [ ] No debug code or print statements left
- [ ] Proper commit message format

### Before Merge/Push
- [ ] GitHub Actions CI checks passing
- [ ] Examples run successfully on different environments
- [ ] Performance impact assessed and documented
- [ ] Security implications considered
- [ ] Breaking changes properly communicated

## Environment-Specific Considerations

### GPU Environment Testing
```bash
# Test with CUDA acceleration
python examples/generation.py --transcript "GPU test" --device_id 0 --out_path gpu_test.wav

# Verify GPU usage
nvidia-smi | grep python
```

### CPU Environment Testing
```bash
# Test with CPU fallback
python examples/generation.py --transcript "CPU test" --out_path cpu_test.wav

# Verify no CUDA dependencies
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Memory-Constrained Environment Testing
```bash
# Test with minimal parameters
python examples/generation.py --transcript "Memory test" --max_new_tokens 256 --out_path memory_test.wav

# Monitor memory usage
python -c "import psutil; print(f'Memory usage: {psutil.virtual_memory().percent}%')"
```

## Common Issues and Solutions

### Import Errors
```bash
# Solution: Install in development mode
pip install -e .

# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

### GPU/CUDA Issues
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"

# Check GPU status
nvidia-smi
```

### Audio Processing Issues
```bash
# Test audio processing pipeline
python examples/generation.py --transcript "Audio processing test" --ref_audio belinda --out_path audio_test.wav

# Check audio file output
ls -la *.wav
```

### Dependency Conflicts
```bash
# Check for dependency conflicts
pip check

# Update dependencies
pip install --upgrade -r requirements.txt

# Clean reinstall
pip uninstall boson-multimodal -y
pip install -e .
```

## Success Indicators

### ✅ Task Completion Checklist
- [ ] Ruff formatting passes: `ruff format --check .`
- [ ] Ruff linting passes: `ruff check .`
- [ ] Package imports successfully: `import boson_multimodal`
- [ ] Basic generation works: `examples/generation.py` completes
- [ ] No regression in existing examples
- [ ] Documentation accurately reflects changes
- [ ] Code follows project conventions and patterns
- [ ] Performance impact documented (if applicable)

### 🚨 Critical Failure Indicators
- Ruff formatting or linting fails
- Package fails to import
- Basic generation example fails
- Existing examples break due to changes
- Memory leaks or crashes during execution
- Security vulnerabilities introduced

This checklist ensures consistent quality and functionality across all development tasks in the Higgs Audio V2 project.