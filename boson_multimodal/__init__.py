"""Boson Multimodal - Higgs Audio V2 Package"""

__version__ = "0.1.0"
__author__ = "Boson AI"
__email__ = "info@boson.ai"

# Core components
from .data_types import AudioContent, TextContent, Message, ChatMLSample
from .serve.serve_engine import HiggsAudioServeEngine, HiggsAudioResponse
from .model.higgs_audio import HiggsAudioModel, HiggsAudioConfig
from .audio_processing.higgs_audio_tokenizer import HiggsAudioFeatureExtractor, HiggsAudioTokenizer

# RunPod serverless integration
try:
    from .serve.runpod_server import RunPodHiggsAudioServer, handler
    __all__ = [
        'AudioContent', 'TextContent', 'Message', 'ChatMLSample',
        'HiggsAudioServeEngine', 'HiggsAudioResponse', 
        'HiggsAudioModel', 'HiggsAudioConfig',
        'HiggsAudioFeatureExtractor', 'HiggsAudioTokenizer',
        'RunPodHiggsAudioServer', 'handler'
    ]
except ImportError:
    # RunPod not available in this environment
    __all__ = [
        'AudioContent', 'TextContent', 'Message', 'ChatMLSample',
        'HiggsAudioServeEngine', 'HiggsAudioResponse',
        'HiggsAudioModel', 'HiggsAudioConfig', 
        'HiggsAudioFeatureExtractor', 'HiggsAudioTokenizer'
    ]