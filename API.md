# Higgs Audio V2 Serverless API

## Overview
Higgs Audio V2 Serverless API provides six powerful endpoints for advanced audio generation, including text-to-speech, zero-shot voice cloning, multi-speaker dialog, high-throughput inference, scene-based generation, and experimental features like background music and humming.

## Base URL (Runpod Deployment)
```
https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run
```

## Authentication
Runpod endpoints require authentication via API key:
```http
Authorization: Bearer {YOUR_RUNPOD_API_KEY}
```

## Request Format
All requests use POST method with JSON body:
```http
POST https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run
Content-Type: application/json
Authorization: Bearer {YOUR_RUNPOD_API_KEY}
```

## Response Format
All responses follow this structure:
```json
{
  "id": "sync-request-id",
  "status": "COMPLETED" | "FAILED",
  "output": {
    "success": true,
    "audio_base64": "base64-encoded-wav-file",
    "text": "generated-text-content",
    "sampling_rate": 24000,
    "metadata": {
      "audio_shape": [audio_length],
      "generation_options": {...}
    }
  }
}
```

## Endpoints

### 1. Text-to-Speech (Smart Voice)
Generate speech with automatically selected voice based on content.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "text_to_speech",
    "text": "The sun rises in the east and sets in the west. This simple fact has been observed by humans for thousands of years.",
    "options": {
      "temperature": 0.3,
      "max_new_tokens": 1024,
      "do_sample": true
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "text_to_speech" |
| text | string | Yes | Text to convert to speech (max 10,000 chars) |
| options.temperature | float | No | Sampling temperature (0.1-1.0, default: 0.7) |
| options.max_new_tokens | int | No | Max tokens to generate (default: 1024) |
| options.do_sample | bool | No | Enable sampling (default: true) |

**Example cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "text_to_speech",
      "text": "Hello, this is a test of the Higgs Audio V2 system.",
      "options": {"temperature": 0.3}
    }
  }'
```

---

### 2. Zero-Shot Voice Cloning
Generate speech that mimics a specific voice from available voice prompts.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "voice_cloning",
    "text": "The sun rises in the east and sets in the west. This simple fact has been observed by humans for thousands of years.",
    "voice_id": "belinda",
    "options": {
      "temperature": 0.3,
      "max_new_tokens": 1024
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "voice_cloning" |
| text | string | Yes | Text to convert to speech |
| voice_id | string | Yes | Voice identifier from available voices |
| options | object | No | Generation options (same as text_to_speech) |

**Available Voices**
- `en_woman` - English female voice
- `en_man` - English male voice  
- `belinda` - Female character voice
- `bigbang_amy` - Amy Farrah Fowler character
- `bigbang_sheldon` - Sheldon Cooper character
- `broom_salesman` - Salesman character
- `chadwick` - Male character voice
- `fiftyshades_anna` - Anna character
- `mabaoguo` - Chinese character
- `mabel` - Female character
- `shrek_donkey` - Donkey character
- `shrek_fiona` - Fiona character
- `shrek_shrek` - Shrek character
- `vex` - Character voice
- `zh_man_sichuan` - Chinese male (Sichuan dialect)

**Example cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "voice_cloning",
      "text": "Hello, this is a voice cloning demonstration.",
      "voice_id": "belinda",
      "options": {"temperature": 0.3}
    }
  }'
```

---

### 3. Multi-Speaker Dialog
Generate dialog with multiple speakers using speaker tags.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "multi_speaker",
    "text": "[SPEAKER1] Hey there! How are you doing today? [SPEAKER2] I'm doing great, thanks for asking! How about you? [SPEAKER1] Pretty good! Just working on some exciting new projects.",
    "options": {
      "temperature": 0.7,
      "max_new_tokens": 2048
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "multi_speaker" |
| text | string | Yes | Text with [SPEAKER1], [SPEAKER2] etc. tags |
| options | object | No | Generation options |

**Speaker Tag Format**
- Use `[SPEAKER1]`, `[SPEAKER2]`, etc. to designate different speakers
- The model will automatically assign distinct voices to each speaker
- No limit on number of speakers, but 2-4 speakers work best

**Example cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "multi_speaker",
      "text": "[SPEAKER1] Good morning! [SPEAKER2] Good morning! How can I help you today?",
      "options": {"temperature": 0.7}
    }
  }'
```

---

### 4. vLLM High-Throughput
High-performance inference optimized for batch processing and concurrent requests.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "vllm",
    "text": "Generate high-quality speech with optimized throughput.",
    "options": {
      "temperature": 0.5,
      "max_new_tokens": 1024,
      "do_sample": true
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "vllm" |
| text | string | Yes | Text to convert to speech |
| options | object | No | Generation options optimized for throughput |

**Performance Features**
- Optimized for concurrent requests
- Better GPU memory utilization
- Faster inference for batch processing
- OpenAI-compatible API integration ready

**Example cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "vllm",
      "text": "This is optimized for high-throughput processing.",
      "options": {"temperature": 0.5}
    }
  }'
```

---

### 5. Scene-Based Generation
Generate speech with environmental context and acoustic adaptation.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "scene_based",
    "text": "Welcome to our quiet reading room. Please keep your voices down while you browse our collection.",
    "options": {
      "scene_id": "quiet_indoor",
      "temperature": 0.6,
      "max_new_tokens": 1024
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "scene_based" |
| text | string | Yes | Text to convert to speech |
| options.scene_id | string | No | Scene context identifier |
| options | object | No | Other generation options |

**Available Scenes**
- `quiet_indoor` - Indoor quiet environment (default)
- `reading_blog` - Reading/narration context

**Scene Effects**
- Adjusts speaking style for environment
- Modifies acoustic properties
- Adapts prosody and pacing
- Contextual voice selection

**Example cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "scene_based",
      "text": "The library is a place of quiet contemplation and learning.",
      "options": {"scene_id": "quiet_indoor", "temperature": 0.6}
    }
  }'
```

---

### 6. Experimental Features
Advanced capabilities including background music and humming generation.

**Request Body**
```json
{
  "input": {
    "endpoint_type": "experimental",
    "text": "Once upon a time, in a land far away... [hum a gentle melody] ...there lived a princess who loved to sing.",
    "options": {
      "experimental_type": "humming",
      "temperature": 0.8,
      "max_new_tokens": 2048
    }
  }
}
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| endpoint_type | string | Yes | Must be "experimental" |
| text | string | Yes | Text with experimental content markers |
| options.experimental_type | string | No | Type of experimental feature |
| options | object | No | Generation options |

**Experimental Types**
- `bgm` - Background music generation (default)
- `humming` - Humming and melodic content
- `general` - General experimental features

**Experimental Capabilities**
- **Background Music**: Generate speech with instrumental background
- **Humming**: Melodic humming with voice cloning
- **Sound Effects**: Environmental audio elements
- **Musical Speech**: Speech with musical prosody

**Example cURL (Background Music)**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "experimental",
      "text": "Welcome to our relaxing meditation session. [soft ambient music]",
      "options": {"experimental_type": "bgm", "temperature": 0.8}
    }
  }'
```

**Example cURL (Humming)**
```bash
curl -X POST "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run" \
  -H "Authorization: Bearer {YOUR_RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "endpoint_type": "experimental", 
      "text": "Let me sing you a lullaby... [hum a gentle melody]",
      "options": {"experimental_type": "humming", "temperature": 0.8}
    }
  }'
```

## Error Handling

### Error Response Format
```json
{
  "id": "sync-request-id",
  "status": "FAILED",
  "error": "Error description"
}
```

### Common Error Scenarios
- **Invalid endpoint_type**: Use one of the six valid endpoint types
- **Missing text field**: Text is required for all endpoints
- **Voice not found**: Check available voices list for voice_cloning
- **Text too long**: Maximum 10,000 characters
- **Invalid temperature**: Must be between 0.1 and 1.0
- **GPU memory**: Insufficient GPU memory for large requests

### Status Codes
- `COMPLETED` - Request processed successfully
- `FAILED` - Request failed with error message
- `IN_PROGRESS` - Request is being processed (for async requests)

## Rate Limiting
- Maximum 5 concurrent requests per endpoint
- Request timeout: 300 seconds (5 minutes)
- Maximum audio length: 300 seconds (5 minutes)

## Performance Guidelines

### Optimal Settings by Use Case
1. **Quality**: temperature=0.3, max_new_tokens=1024
2. **Speed**: temperature=0.7, max_new_tokens=512, use vllm endpoint
3. **Creative**: temperature=0.8, max_new_tokens=2048, experimental endpoint
4. **Voice Cloning**: temperature=0.3, voice_cloning endpoint
5. **Dialog**: temperature=0.7, multi_speaker endpoint
6. **Narration**: temperature=0.6, scene_based endpoint

### Hardware Requirements
- **GPU**: 24GB+ VRAM recommended (A100/H100)
- **Memory**: 32GB+ system RAM
- **Storage**: 50GB+ for model weights and cache

## SDK Examples

### Python SDK Example
```python
import requests
import base64
import io
from pydub import AudioSegment

def generate_audio(text, endpoint_type="text_to_speech", **options):
    url = "https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run"
    headers = {
        "Authorization": "Bearer {YOUR_RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "endpoint_type": endpoint_type,
            "text": text,
            "options": options
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    if result["status"] == "COMPLETED":
        # Decode base64 audio
        audio_data = base64.b64decode(result["output"]["audio_base64"])
        audio = AudioSegment.from_wav(io.BytesIO(audio_data))
        return audio, result["output"]
    else:
        raise Exception(f"Generation failed: {result.get('error')}")

# Examples
audio, metadata = generate_audio("Hello world!", temperature=0.3)
audio, metadata = generate_audio("Hello!", "voice_cloning", voice_id="belinda")
audio, metadata = generate_audio("[SPEAKER1] Hi! [SPEAKER2] Hello!", "multi_speaker")
```

### JavaScript SDK Example
```javascript
async function generateAudio(text, endpointType = "text_to_speech", options = {}) {
    const response = await fetch("https://api.runpod.ai/v2/{YOUR_ENDPOINT_ID}/run", {
        method: "POST",
        headers: {
            "Authorization": "Bearer {YOUR_RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            input: {
                endpoint_type: endpointType,
                text: text,
                options: options
            }
        })
    });
    
    const result = await response.json();
    
    if (result.status === "COMPLETED") {
        // Convert base64 to audio blob
        const audioBytes = atob(result.output.audio_base64);
        const audioArray = new Uint8Array(audioBytes.length);
        for (let i = 0; i < audioBytes.length; i++) {
            audioArray[i] = audioBytes.charCodeAt(i);
        }
        const audioBlob = new Blob([audioArray], { type: "audio/wav" });
        return { audio: audioBlob, metadata: result.output };
    } else {
        throw new Error(`Generation failed: ${result.error}`);
    }
}

// Usage examples
const result1 = await generateAudio("Hello world!", "text_to_speech", {temperature: 0.3});
const result2 = await generateAudio("Hello!", "voice_cloning", {voice_id: "belinda"});
```

## Changelog
- **v2.1.0** - Added experimental BGM and humming features
- **v2.0.0** - Complete serverless API with six endpoints
- **v1.0.0** - Initial Higgs Audio V2 release

## Keywords <!-- #keywords -->
- higgs-audio
- text-to-speech
- voice-cloning
- multi-speaker
- serverless
- runpod
- audio-generation
- experimental-audio