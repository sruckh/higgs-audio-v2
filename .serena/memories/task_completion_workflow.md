# Task Completion Workflow

## Pre-Implementation Checklist
- [ ] Understand the existing codebase patterns in the relevant area
- [ ] Check for existing similar implementations
- [ ] Verify compatibility with current model architecture
- [ ] Ensure CUDA memory requirements are considered

## Development Workflow
1. **Make Changes**: Implement features following existing patterns
2. **Test Locally**: Run basic generation to ensure no regressions
3. **Format Code**: Run `ruff format .` to auto-format
4. **Check Code Quality**: Run `ruff format --check .` and `ruff check .`
5. **Test Generation**: Run example generation scripts to verify functionality
6. **Test Edge Cases**: Verify with different audio inputs and parameters

## Required Commands After Changes

### Code Quality (Always Required)
```bash
# Format check (this is what CI runs)
ruff format --check .

# If formatting fails, auto-fix with:
ruff format .
```

### Functional Testing
```bash
# Basic functionality test
python examples/generation.py --transcript "The sun rises in the east." --temperature 0.3 --out_path test.wav

# Voice cloning test (if audio processing changed)
python examples/generation.py --transcript "Test message" --ref_audio belinda --out_path test_clone.wav

# Multi-speaker test (if dialog features changed)
python examples/generation.py --transcript examples/transcript/multi_speaker/en_argument.txt --out_path test_multi.wav
```

### Performance Testing (If Core Changes)
```bash
# vLLM integration test
python examples/vllm/run_chat_completion.py --api-base http://localhost:8000/v1 --task voice_clone
```

## Critical Areas Requiring Extra Testing
- **Audio Tokenizer Changes**: Test encoding/decoding with sample audio files
- **Model Architecture**: Verify compatibility with existing checkpoints  
- **Serve Engine**: Test both direct usage and vLLM integration
- **CUDA Optimizations**: Verify memory usage and performance benchmarks

## Git Workflow
```bash
# Before committing
ruff format --check .  # Must pass
python examples/generation.py --transcript "Test" --out_path verify.wav  # Must work

# Commit with proper message format
git commit -m "feat(component): description of what was added/changed"
git commit -m "fix(component): description of what was fixed"
git commit -m "refactor(component): description of refactoring"
```

## Documentation Updates Required
- Update relevant README sections if user-facing changes
- Update examples if new features are added
- Update voice_prompts/profile.yaml if new voices are added
- Update tech_blogs/ if architectural changes are made

## Performance Considerations
- Always test with 24GB+ GPU memory requirements
- Verify CUDA graph capture still works after model changes
- Test both single and multi-speaker generation
- Verify audio quality hasn't degraded