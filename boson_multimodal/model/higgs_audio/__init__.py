import os

# Only register models when not in offline mode (prevents downloads during Docker build)
if not os.environ.get("HF_HUB_OFFLINE"):
    from transformers import AutoConfig, AutoModel

    from .configuration_higgs_audio import HiggsAudioConfig, HiggsAudioEncoderConfig
    from .modeling_higgs_audio import HiggsAudioModel

    AutoConfig.register("higgs_audio_encoder", HiggsAudioEncoderConfig)
    AutoConfig.register("higgs_audio", HiggsAudioConfig)
    AutoModel.register(HiggsAudioConfig, HiggsAudioModel)
else:
    # Define dummy imports for offline mode
    HiggsAudioConfig = None
    HiggsAudioEncoderConfig = None
    HiggsAudioModel = None
