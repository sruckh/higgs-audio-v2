# Docker CI/CD Infrastructure

## Overview
Complete Docker CI/CD pipeline implementation for Higgs Audio v2 project targeting gemneye/ DockerHub namespace.

## GitHub Actions Workflow
**File**: `.github/workflows/docker-build-push.yml`

### Trigger Conditions
- **Push**: main, develop branches
- **Tags**: v* (version tags like v1.0.0)
- **Pull Requests**: main branch (build only, no push)

### Build Features
- **Multi-platform**: linux/amd64, linux/arm64
- **Caching**: GitHub Actions cache for faster builds
- **Authentication**: DockerHub login using repository secrets
- **Metadata**: Automatic tag generation based on branch/tag names

### Docker Images Built
1. **Main Application**: `gemneye/higgs-audio-v2`
2. **vLLM Variant**: `gemneye/higgs-audio-v2-vllm`

## Docker Configuration

### Main Dockerfile
**Base**: `nvcr.io/nvidia/pytorch:25.02-py3`
**Features**:
- CUDA support and GPU detection
- Complete Python environment setup
- Audio processing dependencies (ffmpeg, librosa, torchaudio)
- Flexible entrypoint for multiple use cases

### vLLM Dockerfile  
**Location**: `examples/vllm/Dockerfile`
**Purpose**: High-throughput inference with vLLM engine
**Features**:
- vLLM integration for OpenAI-compatible API
- Voice presets management
- Optimized for production serving

### Supporting Files
- **docker-entrypoint.sh**: Main application entrypoint with CUDA detection
- **examples/vllm/vllm-entrypoint.sh**: vLLM server entrypoint
- **.dockerignore**: Optimized build context (excludes docs, cache, models)

## Docker Hub Integration
- **Namespace**: gemneye/
- **Authentication**: DOCKER_USERNAME and DOCKER_PASSWORD secrets
- **Auto-tagging**: Branch names, version tags, latest tag for main branch
- **Registry**: docker.io (Docker Hub)

## Build Optimization
- **Layer Caching**: GitHub Actions cache for Docker layers
- **Multi-stage**: Separate requirements installation for better caching
- **Context Optimization**: .dockerignore excludes unnecessary files
- **Parallel Builds**: Both main and vLLM images build simultaneously