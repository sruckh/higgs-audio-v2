# Suggested Commands

## Essential Development Commands

### Environment Setup
```bash
# Using NVIDIA Docker (recommended)
docker run --gpus all --ipc=host --net=host --ulimit memlock=-1 --ulimit stack=67108864 -it --rm nvcr.io/nvidia/pytorch:25.02-py3 bash

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Code Quality
```bash
# Format code (auto-fix)
ruff format .

# Check formatting (CI)
ruff format --check .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

### Testing and Generation
```bash
# Basic audio generation test
python examples/generation.py --transcript "Hello world" --temperature 0.3 --out_path test.wav

# Zero-shot voice cloning
python examples/generation.py --transcript "Text here" --ref_audio belinda --temperature 0.3 --out_path generation.wav

# Multi-speaker dialog
python examples/generation.py --transcript examples/transcript/multi_speaker/en_argument.txt --seed 12345 --out_path generation.wav

# Test specific GPU device
python examples/generation.py --transcript "Text" --device_id 0 --out_path test.wav
```

### vLLM High-Performance Serving
```bash
# Start vLLM server
docker run --gpus all --ipc=host --shm-size=20gb --network=host \
bosonai/higgs-audio-vllm:latest \
--served-model-name "higgs-audio-v2-generation-3B-base" \
--model "bosonai/higgs-audio-v2-generation-3B-base" \
--audio-tokenizer-type "bosonai/higgs-audio-v2-tokenizer" \
--limit-mm-per-prompt audio=50 \
--max-model-len 8192 \
--port 8000 \
--gpu-memory-utilization 0.8

# Test vLLM API
python examples/vllm/run_chat_completion.py --api-base http://localhost:8000/v1 --task voice_clone
```

### Git and Version Control
```bash
# Standard Git workflow
git checkout -b feature/feature-name
git add .
git commit -m "feat: description of changes"
git push origin feature/feature-name

# Keep fork updated
git fetch upstream
git checkout main
git merge upstream/main
```

### Project Structure Exploration
```bash
# List voice samples
ls examples/voice_prompts/

# Check model configuration
ls boson_multimodal/model/higgs_audio/

# View transcripts for testing
ls examples/transcript/
```

### CI/CD
```bash
# Run the same checks as CI
ruff format --check .
```

## Essential Python Usage
```python
# Basic programmatic usage
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
from boson_multimodal.data_types import ChatMLSample, Message

engine = HiggsAudioServeEngine(
    "bosonai/higgs-audio-v2-generation-3B-base",
    "bosonai/higgs-audio-v2-tokenizer"
)
```