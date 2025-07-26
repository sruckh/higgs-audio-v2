"""
Main serverless handler for Runpod deployment.
Handles routing between different endpoints and model inference.
"""

import os
import json
import time
import base64
import traceback
import tempfile
import soundfile as sf
import numpy as np
from typing import Dict, Any, Optional, List
from loguru import logger

from .model_loader import get_serve_engine, is_ready, get_memory_info, initialize_models
from .config import get_config
from .endpoints import (
    handle_text_to_speech,
    handle_voice_cloning,
    handle_multi_speaker,
    handle_vllm,
    handle_scene_based,
    handle_experimental
)
from .monitoring import monitor_request, monitor_error, get_monitoring_dashboard
from .performance import performance_monitor, gpu_memory_manager


def validate_input(job_input: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate the input format for the serverless function.
    
    Args:
        job_input: The input dictionary from Runpod
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(job_input, dict):
        return False, "Input must be a dictionary"
    
    if "endpoint_type" not in job_input:
        return False, "Missing required field: endpoint_type"
    
    endpoint_type = job_input["endpoint_type"]
    valid_endpoints = [
        "text_to_speech", 
        "voice_cloning", 
        "multi_speaker", 
        "vllm", 
        "scene_based", 
        "experimental"
    ]
    
    if endpoint_type not in valid_endpoints:
        return False, f"Invalid endpoint_type. Must be one of: {valid_endpoints}"
    
    if "text" not in job_input:
        return False, "Missing required field: text"
    
    return True, ""


def encode_audio_to_base64(audio: np.ndarray, sampling_rate: int) -> str:
    """
    Encode audio array to base64 string.
    
    Args:
        audio: Audio array
        sampling_rate: Audio sampling rate
        
    Returns:
        Base64 encoded audio string
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio, sampling_rate)
            
            with open(tmp_file.name, "rb") as f:
                audio_bytes = f.read()
            
            os.unlink(tmp_file.name)
            return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encode audio to base64: {e}")
        raise


def create_response(audio: Optional[np.ndarray] = None, 
                   text: Optional[str] = None,
                   sampling_rate: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   error: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized response format.
    
    Args:
        audio: Generated audio array
        text: Generated text
        sampling_rate: Audio sampling rate
        metadata: Additional metadata
        error: Error message if any
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": error is None,
        "timestamp": time.time(),
    }
    
    if error:
        response["error"] = error
        return response
    
    if text:
        response["text"] = text
    
    if audio is not None and sampling_rate:
        response["audio"] = {
            "data": encode_audio_to_base64(audio, sampling_rate),
            "sampling_rate": sampling_rate,
            "format": "wav",
            "encoding": "base64"
        }
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main serverless handler function for Runpod.
    
    Args:
        job: Job input from Runpod containing the request data
        
    Returns:
        Response dictionary with generated content or error
    """
    start_time = time.time()
    
    try:
        # Extract input from job
        job_input = job.get("input", {})
        logger.info(f"Processing job with input keys: {list(job_input.keys())}")
        
        # Validate input
        is_valid, error_msg = validate_input(job_input)
        if not is_valid:
            logger.error(f"Input validation failed: {error_msg}")
            return create_response(error=f"Input validation failed: {error_msg}")
        
        # Check if models are ready
        if not is_ready():
            logger.error("Models not loaded")
            return create_response(error="Models not loaded. Please wait for initialization.")
        
        # Handle special endpoints first
        if job_input.get("health_check"):
            return health_check()
        
        if job_input.get("monitoring_dashboard"):
            return get_monitoring_dashboard()
        
        # Extract parameters
        endpoint_type = job_input["endpoint_type"]
        text = job_input["text"]
        voice_id = job_input.get("voice_id")
        options = job_input.get("options", {})
        
        logger.info(f"Processing {endpoint_type} request with text length: {len(text)}")
        
        # Use performance monitoring context
        with performance_monitor.measure_performance(f"{endpoint_type}_request"):
            # Route to appropriate endpoint handler
            try:
                if endpoint_type == "text_to_speech":
                    result = handle_text_to_speech(text, voice_id, options)
                elif endpoint_type == "voice_cloning":
                    result = handle_voice_cloning(text, voice_id, options)
                elif endpoint_type == "multi_speaker":
                    result = handle_multi_speaker(text, options)
                elif endpoint_type == "vllm":
                    result = handle_vllm(text, options)
                elif endpoint_type == "scene_based":
                    result = handle_scene_based(text, options)
                elif endpoint_type == "experimental":
                    result = handle_experimental(text, options)
                else:
                    return create_response(error=f"Unsupported endpoint: {endpoint_type}")
            
            # Add timing and memory info to metadata
            processing_time = time.time() - start_time
            memory_info = get_memory_info()
            
            # Log successful request
            monitor_request(
                endpoint_type=endpoint_type,
                processing_time=processing_time,
                success=True,
                input_length=len(text),
                audio_length_seconds=result.get("audio_length_seconds"),
                memory_usage_gb=memory_info.get("gpu_allocated_gb", 0)
            )
            
            metadata = {
                "endpoint_type": endpoint_type,
                "processing_time_seconds": processing_time,
                "memory_info": memory_info,
                **result.get("metadata", {})
            }
            
            logger.info(f"Successfully processed {endpoint_type} in {processing_time:.2f}s")
            
            return create_response(
                audio=result.get("audio"),
                text=result.get("text"),
                sampling_rate=result.get("sampling_rate"),
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = f"Endpoint processing failed: {str(e)}"
            
            # Log failed request
            monitor_request(
                endpoint_type=endpoint_type,
                processing_time=time.time() - start_time,
                success=False,
                input_length=len(text) if 'text' in locals() else 0
            )
            
            # Log error for monitoring
            monitor_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint_type=endpoint_type,
                stack_trace=traceback.format_exc(),
                user_input_length=len(text) if 'text' in locals() else 0
            )
            
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return create_response(error=error_msg)
        
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return create_response(error=error_msg)


# Initialize models on container startup
def serverless_start():
    """
    Initialization function called when the serverless container starts.
    This pre-loads models to minimize cold start times.
    """
    try:
        logger.info("Starting serverless container initialization...")
        
        # Get configuration
        config = get_config()
        model_config = config.get("model", {})
        
        # Initialize models
        initialize_models(model_config)
        
        logger.info("Serverless container initialization completed successfully!")
        
        # Log memory usage
        memory_info = get_memory_info()
        if memory_info:
            logger.info(f"Memory usage after initialization: {memory_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize serverless container: {e}")
        logger.error(traceback.format_exc())
        return False


# Health check endpoint
def health_check() -> Dict[str, Any]:
    """
    Health check function to verify the service is running properly.
    
    Returns:
        Health status dictionary
    """
    try:
        return {
            "status": "healthy" if is_ready() else "initializing",
            "models_loaded": is_ready(),
            "memory_info": get_memory_info(),
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


# Export main functions
__all__ = ["handler", "serverless_start", "health_check"]