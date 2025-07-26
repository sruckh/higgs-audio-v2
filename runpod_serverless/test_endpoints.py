"""
Test scripts for Runpod serverless endpoints.
Tests all 6 endpoint types to verify functionality.
"""

import json
import time
import base64
import tempfile
import soundfile as sf
from typing import Dict, Any
from loguru import logger

from .handler import handler, health_check
from .model_loader import initialize_models, is_ready


def save_audio_from_response(response: Dict[str, Any], filename: str) -> bool:
    """
    Save audio from response to file for verification.
    
    Args:
        response: Handler response containing audio data
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not response.get("success"):
            logger.error(f"Response not successful: {response.get('error')}")
            return False
        
        audio_data = response.get("audio", {}).get("data")
        sampling_rate = response.get("audio", {}).get("sampling_rate", 24000)
        
        if not audio_data:
            logger.error("No audio data in response")
            return False
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        
        # Save to temporary file first, then read and save as requested format
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # Read audio and save to final location
            audio, sr = sf.read(tmp_file.name)
            sf.write(filename, audio, sr)
        
        logger.info(f"Saved audio to {filename} (shape: {audio.shape}, sr: {sr})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        return False


def test_text_to_speech():
    """Test basic text-to-speech endpoint."""
    logger.info("Testing text-to-speech endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "text_to_speech",
            "text": "Hello, this is a test of the text-to-speech system. How does it sound?",
            "voice_id": "en_woman",
            "options": {
                "temperature": 0.7,
                "max_new_tokens": 1024
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"TTS processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_tts.wav")
        logger.info("✅ Text-to-speech test passed")
        return True
    else:
        logger.error(f"❌ Text-to-speech test failed: {response.get('error')}")
        return False


def test_voice_cloning():
    """Test voice cloning endpoint."""
    logger.info("Testing voice cloning endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "voice_cloning",
            "text": "I am speaking with a cloned voice. This demonstrates zero-shot voice cloning capabilities.",
            "voice_id": "belinda",
            "options": {
                "temperature": 0.7,
                "max_new_tokens": 1024
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"Voice cloning processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_voice_cloning.wav")
        logger.info("✅ Voice cloning test passed")
        return True
    else:
        logger.error(f"❌ Voice cloning test failed: {response.get('error')}")
        return False


def test_multi_speaker():
    """Test multi-speaker dialog endpoint."""
    logger.info("Testing multi-speaker dialog endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "multi_speaker",
            "text": "[SPEAKER1] Hello there! How are you doing today? [SPEAKER2] I'm doing great, thanks for asking! How about you? [SPEAKER1] Excellent! I love testing multi-speaker conversations.",
            "options": {
                "temperature": 0.8,
                "max_new_tokens": 2048
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"Multi-speaker processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_multi_speaker.wav")
        logger.info("✅ Multi-speaker test passed")
        return True
    else:
        logger.error(f"❌ Multi-speaker test failed: {response.get('error')}")
        return False


def test_vllm():
    """Test vLLM high-throughput endpoint."""
    logger.info("Testing vLLM high-throughput endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "vllm",
            "text": "This is a test of the high-throughput vLLM generation system. It should be optimized for speed and efficiency.",
            "options": {
                "temperature": 0.7,
                "max_new_tokens": 1024
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"vLLM processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_vllm.wav")
        logger.info("✅ vLLM test passed")
        return True
    else:
        logger.error(f"❌ vLLM test failed: {response.get('error')}")
        return False


def test_scene_based():
    """Test scene-based generation endpoint."""
    logger.info("Testing scene-based generation endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "scene_based",
            "text": "This is a quiet conversation taking place in an indoor setting. The atmosphere is calm and peaceful.",
            "options": {
                "scene_id": "quiet_indoor",
                "temperature": 0.7,
                "max_new_tokens": 1024
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"Scene-based processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_scene_based.wav")
        logger.info("✅ Scene-based test passed")
        return True
    else:
        logger.error(f"❌ Scene-based test failed: {response.get('error')}")
        return False


def test_experimental():
    """Test experimental features endpoint."""
    logger.info("Testing experimental features endpoint...")
    
    job = {
        "input": {
            "endpoint_type": "experimental",
            "text": "This is an experimental audio generation with background music elements. *music plays softly*",
            "options": {
                "experimental_type": "bgm",
                "temperature": 0.8,
                "max_new_tokens": 1024
            }
        }
    }
    
    start_time = time.time()
    response = handler(job)
    processing_time = time.time() - start_time
    
    logger.info(f"Experimental processing time: {processing_time:.2f}s")
    
    if response.get("success"):
        save_audio_from_response(response, "/tmp/test_experimental.wav")
        logger.info("✅ Experimental test passed")
        return True
    else:
        logger.error(f"❌ Experimental test failed: {response.get('error')}")
        return False


def test_health_check():
    """Test health check functionality."""
    logger.info("Testing health check...")
    
    health = health_check()
    
    if health.get("status") == "healthy":
        logger.info("✅ Health check passed")
        logger.info(f"Memory info: {health.get('memory_info', {})}")
        return True
    else:
        logger.error(f"❌ Health check failed: {health}")
        return False


def test_invalid_input():
    """Test error handling with invalid input."""
    logger.info("Testing invalid input handling...")
    
    # Test missing endpoint_type
    job = {
        "input": {
            "text": "This should fail"
        }
    }
    
    response = handler(job)
    
    if not response.get("success") and "endpoint_type" in response.get("error", ""):
        logger.info("✅ Invalid input test passed")
        return True
    else:
        logger.error(f"❌ Invalid input test failed: {response}")
        return False


def run_all_tests():
    """
    Run all endpoint tests.
    
    Returns:
        Dictionary with test results
    """
    logger.info("🚀 Starting comprehensive endpoint testing...")
    
    # Check if models are loaded
    if not is_ready():
        logger.error("Models not loaded. Please initialize models first.")
        return {"success": False, "error": "Models not loaded"}
    
    tests = [
        ("Health Check", test_health_check),
        ("Invalid Input", test_invalid_input),
        ("Text-to-Speech", test_text_to_speech),
        ("Voice Cloning", test_voice_cloning),
        ("Multi-Speaker", test_multi_speaker),
        ("vLLM", test_vllm),
        ("Scene-Based", test_scene_based),
        ("Experimental", test_experimental),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    start_time = time.time()
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    total_time = time.time() - start_time
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Total time: {total_time:.2f}s")
    logger.info(f"Success rate: {passed/total*100:.1f}%")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    return {
        "success": passed == total,
        "passed": passed,
        "total": total,
        "success_rate": passed/total,
        "total_time": total_time,
        "results": results
    }


if __name__ == "__main__":
    # Initialize models if not already loaded
    if not is_ready():
        logger.info("Initializing models for testing...")
        initialize_models()
    
    # Run all tests
    results = run_all_tests()
    
    if results["success"]:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.error(f"\n💥 {results['total'] - results['passed']} tests failed!")
        exit(1)