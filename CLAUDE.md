# CLAUDE.md
<!-- Generated by Claude Conductor v1.1.2 -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Context (Read First)
- **Tech Stack**: Python, PyTorch, Transformers, Audio Processing (librosa, torchaudio)
- **Main File**: boson_multimodal/serve/serve_engine.py (HiggsAudioServeEngine)
- **Core Mechanic**: 9627 lines of Python code across multimodal audio generation architecture
- **Key Integration**: HuggingFace Transformers, vLLM, CUDA optimization, AWS S3
- **Platform Support**: CUDA GPU (24GB+ recommended), Docker, Linux
- **DO NOT**: Modify audio tokenizer without understanding codec architecture, skip CUDA optimizations

## Session Startup Checklist
**IMPORTANT**: At the start of each session, check these items:
1. **Check TASKS.md** - Look for any IN_PROGRESS or BLOCKED tasks from previous sessions
2. **Review recent JOURNAL.md entries** - Scan last 2-3 entries for context
3. **If resuming work**: Load the current task context from TASKS.md before proceeding

## Table of Contents
1. [Architecture](ARCHITECTURE.md) - Tech stack, folder structure, infrastructure
2. [Design Tokens](DESIGN.md) - Colors, typography, visual system
3. [UI/UX Patterns](UIUX.md) - Components, interactions, accessibility
4. [Runtime Config](CONFIG.md) - Environment variables, feature flags
5. [Data Model](DATA_MODEL.md) - Database schema, entities, relationships
6. [API Contracts](API.md) - Endpoints, request/response formats, auth
7. [Build & Release](BUILD.md) - Build process, deployment, CI/CD
8. [Testing Guide](TEST.md) - Test strategies, E2E scenarios, coverage
9. [Operational Playbooks](PLAYBOOKS/DEPLOY.md) - Deployment, rollback, monitoring
10. [Contributing](CONTRIBUTING.md) - Code style, PR process, conventions
11. [Error Ledger](ERRORS.md) - Critical P0/P1 error tracking
12. [Task Management](TASKS.md) - Active tasks, phase tracking, context preservation

## Quick Reference
**Main Model**: `boson_multimodal/model/higgs_audio/modeling_higgs_audio.py:1-2289` - Core HiggsAudio model architecture  
**Serve Engine**: `boson_multimodal/serve/serve_engine.py:1-50+` - Main inference engine and API  
**Audio Tokenizer**: `boson_multimodal/audio_processing/higgs_audio_tokenizer.py:43-50+` - Audio encoding/decoding  
**Generation Script**: `examples/generation.py:1-50+` - CLI generation interface  
**Data Types**: `boson_multimodal/data_types.py` - ChatML and audio content structures  
**Config**: `boson_multimodal/model/higgs_audio/configuration_higgs_audio.py` - Model configuration  
**Audio Head**: `boson_multimodal/model/higgs_audio/audio_head.py` - Audio decoder projector  
**Collator**: `boson_multimodal/data_collator/higgs_audio_collator.py` - Data batching for training  
**Dataset**: `boson_multimodal/dataset/chatml_dataset.py` - ChatML dataset processing  
**vLLM Integration**: `examples/vllm/run_chat_completion.py` - High-throughput inference

## Current State
- [x] Core audio generation model (v2) - Complete
- [x] Zero-shot voice cloning - Complete  
- [x] Multi-speaker dialog generation - Complete
- [x] vLLM integration for high throughput - Complete
- [x] HuggingFace integration - Complete
- [x] Docker deployment - Complete
- [ ] Performance optimizations - Ongoing
- [ ] Additional language support - Planned

## Development Workflow
1. **Environment Setup**: Use NVIDIA Docker container (nvcr.io/nvidia/pytorch:25.02-py3)
2. **Install Dependencies**: `pip install -r requirements.txt && pip install -e .`
3. **Test Generation**: Run `python examples/generation.py` with sample audio
4. **Model Development**: Modify core model in `boson_multimodal/model/higgs_audio/`
5. **Audio Processing**: Update tokenizer in `boson_multimodal/audio_processing/`
6. **Serve Integration**: Test changes through `HiggsAudioServeEngine`

## Task Templates
### 1. Add New Voice Sample
1. Place audio file in `examples/voice_prompts/[name].wav`
2. Create corresponding text file `examples/voice_prompts/[name].txt`
3. Test with `python examples/generation.py --ref_audio [name]`
4. Update voice_prompts/profile.yaml if needed

### 2. Model Architecture Changes
1. Modify core model in `boson_multimodal/model/higgs_audio/modeling_higgs_audio.py:1-2289`
2. Update configuration in `configuration_higgs_audio.py`
3. Test with basic generation script
4. Run performance benchmarks
5. Update documentation in tech_blogs/

### 3. Audio Processing Updates
1. Modify tokenizer in `boson_multimodal/audio_processing/higgs_audio_tokenizer.py:43+`
2. Update quantization modules if needed
3. Test encoding/decoding with sample audio
4. Verify compatibility with existing models
5. Update tokenizer documentation

### 4. vLLM Integration Testing
1. Start vLLM server with `examples/vllm/run_chat_completion.py`
2. Test OpenAI-compatible API endpoints
3. Verify performance benchmarks
4. Update vLLM README with changes

## Anti-Patterns (Avoid These)
❌ **Don't modify audio tokenizer without codec understanding** - Changes affect model compatibility  
❌ **Don't skip CUDA memory optimization** - Model requires 24GB+ GPU memory  
❌ **Don't ignore delay pattern in audio generation** - Critical for multi-speaker timing  
❌ **Don't modify quantization without testing** - Breaks audio quality severely  
❌ **Don't hardcode sampling rates** - Different models use 16kHz vs 24kHz  
❌ **Don't bypass HiggsAudioServeEngine** - Skip important preprocessing steps

## Journal Update Requirements
**IMPORTANT**: Update JOURNAL.md regularly throughout our work sessions:
- After completing any significant feature or fix
- When encountering and resolving errors
- At the end of each work session
- When making architectural decisions
- Format: What/Why/How/Issues/Result structure

## Task Management Integration
**How TASKS.md and JOURNAL.md work together**:
1. **Active Work**: TASKS.md tracks current/incomplete tasks with full context
2. **Completed Work**: When tasks complete, they generate JOURNAL.md entries with `|TASK:ID|` tags
3. **History**: JOURNAL.md preserves complete task history even if Claude Code is reinstalled
4. **Context Recovery**: Search JOURNAL.md for `|TASK:` to see all completed tasks over time
5. **Clean Handoffs**: TASKS.md always shows what needs to be resumed or completed

## Version History
- **v1.0.0** - Initial release
- **v1.1.0** - Feature added (see JOURNAL.md YYYY-MM-DD)  
[Link major versions to journal entries]