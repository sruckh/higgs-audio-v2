# Import models only when not in offline mode
import os
if not os.environ.get("HF_HUB_OFFLINE"):
    from .model.higgs_audio import HiggsAudioConfig, HiggsAudioModel
