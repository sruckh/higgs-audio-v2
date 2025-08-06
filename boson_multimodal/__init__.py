"""Boson Multimodal - Higgs Audio V2 Package"""

__version__ = "0.1.0"
__author__ = "Boson AI"
__email__ = "info@boson.ai"

# Protect against imports during package installation only
import os
import sys

def _is_installing():
    """Check if we're in the middle of package installation"""
    # Check if we're being imported by pip install
    for frame in sys._current_frames().values():
        try:
            filename = frame.f_code.co_filename
            if 'pip' in filename or 'setuptools' in filename:
                return True
        except:
            continue
    return False

# Only import if we're not in package installation mode
# This ensures models are loaded at startup for warm inference, not lazy loaded
if not _is_installing():
    from .audio_processing.higgs_audio_tokenizer import HiggsAudioFeatureExtractor, HiggsAudioTokenizer
    from .data_types import AudioContent, ChatMLSample, Message, TextContent
    from .model.higgs_audio import HiggsAudioConfig, HiggsAudioModel
    from .serve.serve_engine import HiggsAudioResponse, HiggsAudioServeEngine
else:
    # During installation, create placeholders that will be replaced later
    HiggsAudioFeatureExtractor = None
    HiggsAudioTokenizer = None
    AudioContent = None
    ChatMLSample = None
    Message = None
    TextContent = None
    HiggsAudioConfig = None
    HiggsAudioModel = None
    HiggsAudioResponse = None
    HiggsAudioServeEngine = None

# RunPod serverless integration
try:
    if not _is_installing():
        from .serve.runpod_server import RunPodHiggsAudioServer, handler
        __all__ = [
            "AudioContent",
            "TextContent",
            "Message",
            "ChatMLSample",
            "HiggsAudioServeEngine",
            "HiggsAudioResponse",
            "HiggsAudioModel",
            "HiggsAudioConfig",
            "HiggsAudioFeatureExtractor",
            "HiggsAudioTokenizer",
            "RunPodHiggsAudioServer",
            "handler",
        ]
    else:
        RunPodHiggsAudioServer = None
        handler = None
        __all__ = [
            "AudioContent",
            "TextContent",
            "Message",
            "ChatMLSample",
            "HiggsAudioServeEngine",
            "HiggsAudioResponse",
            "HiggsAudioModel",
            "HiggsAudioConfig",
            "HiggsAudioFeatureExtractor",
            "HiggsAudioTokenizer",
            "RunPodHiggsAudioServer",
            "handler",
        ]
except ImportError:
    # RunPod not available in this environment
    __all__ = [
        "AudioContent",
        "TextContent",
        "Message",
        "ChatMLSample",
        "HiggsAudioServeEngine",
        "HiggsAudioResponse",
        "HiggsAudioModel",
        "HiggsAudioConfig",
        "HiggsAudioFeatureExtractor",
        "HiggsAudioTokenizer",
    ]
