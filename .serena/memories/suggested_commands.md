# Higgs Audio V2 - Development Commands and Procedures

## Code Quality and Completion Commands

### When Tasks Are Completed (Required Commands)
After making any code changes, run these commands in order:

```bash
# 1. Code Formatting Check (required)
ruff format --check .

# 2. Code Linting (required)  
ruff check .

# 3. Type Checking (if mypy is available)
mypy boson_multimodal/ --ignore-missing-imports

# 4. Run Tests (if tests exist)
pytest tests/ -v

# 5. Build Verification
pip install -e .
python -c "import boson_multimodal; print('Import successful')"
```

### Full Development Cycle Commands
For complete development workflow:

```bash
# Step 1: Install dependencies
pip install -r requirements.txt
pip install -e .

# Step 2: Code formatting (before commits)
ruff format .

# Step 3: Run linting
ruff check --fix .

# Step 4: Type checking (optional but recommended)
mypy boson_multimodal/ --ignore-missing-imports

# Step 5: Run tests
pytest tests/ -v --cov=boson_multimodal

# Step 6: Build verification
python examples/generation.py --help
```

## Entry Points and Examples

### Main Entry Points
```bash
# Core generation example
python examples/generation.py --transcript "Hello world" --out_path output.wav

# Voice cloning with reference audio
python examples/generation.py --transcript "Hello world" --ref_audio belinda --out_path output.wav

# Multi-speaker dialogue generation
python examples/generation.py --transcript examples/transcript/multi_speaker/en_argument.txt --out_path output.wav

# Serve engine API server
python -m boson_multimodal.serve.serve_engine

# vLLM integration (high-throughput)
python examples/vllm/run_chat_completion.py
```

### Model Testing Commands
```bash
# Test model loading
python -c "
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
engine = HiggsAudioServeEngine('bosonai/higgs-audio-v2-generation-3B-base', 'bosonai/higgs-audio-v2-tokenizer')
print('Model loaded successfully')
"

# Test basic generation
python examples/generation.py --transcript "The sun rises in the east." --temperature 0.3 --out_path test.wav

# Test voice cloning
python examples/generation.py --transcript "Testing voice cloning" --ref_audio belinda --out_path clone_test.wav
```

## System Commands (Linux Environment)

### Essential Development Commands
```bash
# File operations and navigation
ls -la                    # List files with details
find . -name "*.py"       # Find all Python files
wc -l boson_multimodal/model/higgs_audio/modeling_higgs_audio.py  # Count lines

# Git operations
git status               # Check repository status
git diff                 # Show changes
git add .               # Stage all changes
git commit -m "feat: add new functionality"  # Commit changes
git pull origin main    # Update from remote
git push origin main    # Push changes to remote

# Python environment management
python --version        # Check Python version
pip list               # List installed packages
pip install -r requirements.txt  # Install dependencies
pip install -e .       # Install package in development mode

# System monitoring
nvidia-smi             # Check GPU status (if available)
htop                   # System resource monitor
df -h                  # Disk space usage
free -h                # Memory usage
```

### Advanced File Operations
```bash
# Search and grep operations
grep -r "class HiggsAudio" boson_multimodal/     # Find class definitions
grep -r "def generate" boson_multimodal/         # Find function definitions
find . -name "*.py" -exec wc -l {} + | sort -n   # Count lines in all Python files

# Directory operations
mkdir -p temp_test                      # Create directory with parents
rm -rf temp_test                        # Remove directory recursively
cp -r examples examples_backup          # Copy directory
mv old_name new_name                    # Rename file/directory

# Archive operations
tar -czf backup.tar.gz boson_multimodal/  # Create compressed archive
tar -xzf backup.tar.gz                    # Extract archive

# Process management
ps aux | grep python                       # Find running Python processes
kill -9 <pid>                             # Kill process by ID
nohup python script.py > output.log 2>&1 &  # Run script in background
```

## Testing and Validation Commands

### Unit Testing (if pytest is available)
```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=boson_multimodal --cov-report=html

# Run specific test file
pytest tests/test_model.py -v

# Run tests matching pattern
pytest tests/ -k "test_generation" -v

# Run tests in parallel
pytest tests/ -n auto
```

### Integration Testing
```bash
# Test model loading and basic functionality
python -c "
import torch
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
device = 'cuda' if torch.cuda.is_available() else 'cpu'
engine = HiggsAudioServeEngine('bosonai/higgs-audio-v2-generation-3B-base', 'bosonai/higgs-audio-v2-tokenizer', device=device)
print('Integration test passed')
"

# Test audio processing pipeline
python examples/generation.py --transcript "Quick integration test" --out_path integration_test.wav
```

### Performance Testing
```bash
# Measure generation time
time python examples/generation.py --transcript "Performance test" --out_path perf_test.wav

# Test with different batch sizes
python examples/generation.py --transcript "Batch test 1; Batch test 2" --chunk_method speaker --out_path batch_test.wav
```

## Build and Deployment Commands

### Build Commands
```bash
# Build package
python setup.py build

# Build distribution
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/boson_multimodal-0.1.0-py3-none-any.whl
```

### Docker Commands (if available)
```bash
# Build Docker image
docker build -t higgs-audio .

# Run Docker container
docker run --gpus all --ipc=host --net=host -it higgs-audio

# Run with volume mount
docker run --gpus all -v $(pwd):/workspace -it higgs-audio
```

### Environment Setup Commands
```bash
# Using conda (recommended)
conda create -y --prefix ./conda_env --override-channels --strict-channel-priority --channel "conda-forge" "python==3.10.*"
conda activate ./conda_env
pip install -r requirements.txt
pip install -e .

# Using venv
python3 -m venv higgs_audio_env
source higgs_audio_env/bin/activate
pip install -r requirements.txt
pip install -e .

# Using uv (modern alternative)
uv venv --python 3.10
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -e .
```

## Continuous Integration/Continuous Deployment (CI/CD)

### GitHub Actions Commands
```bash
# Trigger CI workflow manually (if configured)
# This is typically done through the GitHub web interface

# Run CI locally
act -j lint  # Run lint job locally (using act)

# Check workflow syntax
# GitHub Actions workflows are in .github/workflows/
```

### Pre-commit Hooks (if configured)
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-format
```

## Troubleshooting Commands

### Common Issues
```bash
# Check Python path and imports
python -c "import sys; print(sys.path)"
python -c "import boson_multimodal; print('Package found')"

# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
nvidia-smi

# Check disk space and permissions
df -h .
ls -la boson_multimodal/

# Check for dependency conflicts
pip check

# Debug imports with verbose output
python -v -c "import boson_multimodal"
```

### Performance Debugging
```bash
# Monitor GPU usage during generation
nvidia-smi -l 1 &

# Check memory usage
python -c "
import torch
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
engine = HiggsAudioServeEngine('bosonai/higgs-audio-v2-generation-3B-base', 'bosonai/higgs-audio-v2-tokenizer')
print(f'Model loaded on: {next(engine.model.parameters()).device}')
"

# Profile generation time
python -m cProfile -o profile.prof examples/generation.py --transcript "Profile test"
```

This comprehensive command reference covers all essential development operations for the Higgs Audio V2 project.