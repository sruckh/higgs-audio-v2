"""
Voice prompt mapping and management for RunPod serverless deployment
"""

import os
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VoicePrompt:
    """Voice prompt configuration"""
    name: str
    description: str
    audio_file: str
    text_file: str
    language: str
    gender: str
    characteristics: List[str]


class VoicePromptManager:
    """
    Manages voice prompts for one-shot voice cloning in the RunPod serverless environment.
    """
    
    def __init__(self, voice_prompts_path: str = "/app/voice_prompts"):
        self.voice_prompts_path = voice_prompts_path
        self.voice_prompts: Dict[str, VoicePrompt] = {}
        self._load_voice_prompts()
    
    def _load_voice_prompts(self):
        """Load all available voice prompts from the voice prompts directory."""
        if not os.path.exists(self.voice_prompts_path):
            logger.warning(f"Voice prompts directory not found: {self.voice_prompts_path}")
            return
        
        # Available voice prompts with their characteristics
        voice_configs = {
            "belinda": VoicePrompt(
                name="belinda",
                description="Female voice with gentle, warm tone",
                audio_file="belinda.wav",
                text_file="belinda.txt", 
                language="en",
                gender="female",
                characteristics=["warm", "gentle", "friendly", "clear"]
            ),
            "en_woman": VoicePrompt(
                name="en_woman",
                description="Standard female English voice",
                audio_file="en_woman.wav",
                text_file="en_woman.txt",
                language="en", 
                gender="female",
                characteristics=["standard", "clear", "neutral"]
            ),
            "en_man": VoicePrompt(
                name="en_man",
                description="Standard male English voice",
                audio_file="en_man.wav", 
                text_file="en_man.txt",
                language="en",
                gender="male",
                characteristics=["standard", "clear", "neutral"]
            ),
            "chadwick": VoicePrompt(
                name="chadwick",
                description="Male voice with British accent",
                audio_file="chadwick.wav",
                text_file="chadwick.txt",
                language="en",
                gender="male",
                characteristics=["british", "articulate", "conversational"]
            ),
            "mabel": VoicePrompt(
                name="mabel", 
                description="Female voice with expressive tone",
                audio_file="mabel.wav",
                text_file="mabel.txt",
                language="en",
                gender="female",
                characteristics=["expressive", "warm", "engaging"]
            ),
            "vex": VoicePrompt(
                name="vex",
                description="Male voice with deep, authoritative tone",
                audio_file="vex.wav",
                text_file="vex.txt",
                language="en",
                gender="male", 
                characteristics=["deep", "authoritative", "clear"]
            ),
            "bigbang_amy": VoicePrompt(
                name="bigbang_amy",
                description="Female voice with nerdy, enthusiastic tone",
                audio_file="bigbang_amy.wav",
                text_file="bigbang_amy.txt",
                language="en",
                gender="female",
                characteristics=["nerdy", "enthusiastic", "energetic"]
            ),
            "bigbang_sheldon": VoicePrompt(
                name="bigbang_sheldon", 
                description="Male voice with intellectual, precise tone",
                audio_file="bigbang_sheldon.wav",
                text_file="bigbang_sheldon.txt",
                language="en",
                gender="male",
                characteristics=["intellectual", "precise", "analytical"]
            ),
            "shrek_shrek": VoicePrompt(
                name="shrek_shrek",
                description="Male voice with Scottish accent, grumpy tone",
                audio_file="shrek_shrek.wav",
                text_file="shrek_shrek.txt",
                language="en",
                gender="male",
                characteristics=["scottish", "grumpy", "humorous"]
            ),
            "shrek_fiona": VoicePrompt(
                name="shrek_fiona",
                description="Female voice with princess-like tone", 
                audio_file="shrek_fiona.wav",
                text_file="shrek_fiona.txt",
                language="en",
                gender="female",
                characteristics=["princess-like", "elegant", "gentle"]
            ),
            "shrek_donkey": VoicePrompt(
                name="shrek_donkey",
                description="Male voice with energetic, excited tone",
                audio_file="shrek_donkey.wav",
                text_file="shrek_donkey.txt", 
                language="en",
                gender="male",
                characteristics=["energetic", "excited", "talkative"]
            ),
            "fiftyshades_anna": VoicePrompt(
                name="fiftyshades_anna",
                description="Female voice with soft, romantic tone",
                audio_file="fiftyshades_anna.wav",
                text_file="fiftyshades_anna.txt",
                language="en",
                gender="female",
                characteristics=["soft", "romantic", "gentle"]
            ),
            "broom_salesman": VoicePrompt(
                name="broom_salesman",
                description="Male voice with salesman-like, persuasive tone",
                audio_file="broom_salesman.wav",
                text_file="broom_salesman.txt",
                language="en",
                gender="male",
                characteristics=["persuasive", "enthusiastic", "salesman-like"]
            ),
            "mabaoguo": VoicePrompt(
                name="mabaoguo",
                description="Male voice with Sichuan Chinese accent",
                audio_file="mabaoguo.wav", 
                text_file="mabaoguo.txt",
                language="zh",
                gender="male",
                characteristics=["sichuan", "energetic", "expressive"]
            ),
            "zh_man_sichuan": VoicePrompt(
                name="zh_man_sichuan",
                description="Male voice with Sichuan Chinese accent",
                audio_file="zh_man_sichuan.wav",
                text_file="zh_man_sichuan.txt",
                language="zh",
                gender="male",
                characteristics=["sichuan", "authentic", "expressive"]
            )
        }
        
        # Load available voice prompts
        for voice_name, config in voice_configs.items():
            audio_path = os.path.join(self.voice_prompts_path, config.audio_file)
            text_path = os.path.join(self.voice_prompts_path, config.text_file)
            
            if os.path.exists(audio_path) and os.path.exists(text_path):
                self.voice_prompts[voice_name] = config
                logger.info(f"Loaded voice prompt: {voice_name}")
            else:
                logger.warning(f"Voice prompt files not found for: {voice_name}")
        
        logger.info(f"Loaded {len(self.voice_prompts)} voice prompts")
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voice names."""
        return list(self.voice_prompts.keys())
    
    def get_voice_prompt(self, voice_name: str) -> Optional[VoicePrompt]:
        """Get voice prompt configuration by name."""
        return self.voice_prompts.get(voice_name)
    
    def get_voice_text(self, voice_name: str) -> Optional[str]:
        """Get reference text for voice cloning."""
        voice_prompt = self.get_voice_prompt(voice_name)
        if not voice_prompt:
            return None
        
        text_path = os.path.join(self.voice_prompts_path, voice_prompt.text_file)
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read voice text for {voice_name}: {e}")
            return None
    
    def get_voice_audio_path(self, voice_name: str) -> Optional[str]:
        """Get audio file path for voice reference."""
        voice_prompt = self.get_voice_prompt(voice_name)
        if not voice_prompt:
            return None
        
        audio_path = os.path.join(self.voice_prompts_path, voice_prompt.audio_file)
        if os.path.exists(audio_path):
            return audio_path
        
        return None
    
    def suggest_voices_for_prompt(self, transcript: str, scene_prompt: str = "") -> List[str]:
        """Suggest suitable voices based on transcript and scene prompt."""
        transcript_lower = transcript.lower()
        scene_prompt_lower = scene_prompt.lower()
        
        suitable_voices = []
        
        # Analyze transcript and scene for voice characteristics
        if any(word in transcript_lower for word in ["excited", "amazing", "wonderful", "fantastic"]):
            suitable_voices.extend(["bigbang_amy", "shrek_donkey"])
        
        if any(word in transcript_lower for word in ["serious", "important", "professional", "business"]):
            suitable_voices.extend(["chadwick", "vex", "en_man"])
        
        if any(word in transcript_lower for word in ["gentle", "soft", "kind", "sweet"]):
            suitable_voices.extend(["belinda", "fiftyshades_anna", "shrek_fiona"])
        
        if any(word in transcript_lower for word in ["intellectual", "smart", "science", "theory"]):
            suitable_voices.extend(["bigbang_sheldon", "chadwick"])
        
        if scene_prompt:
            if any(word in scene_prompt_lower for word in ["warm", "friendly", "casual"]):
                suitable_voices.extend(["belinda", "mabel"])
            
            if any(word in scene_prompt_lower for word in ["professional", "formal", "business"]):
                suitable_voices.extend(["chadwick", "vex"])
            
            if any(word in scene_prompt_lower for word in ["energetic", "excited", "dynamic"]):
                suitable_voices.extend(["bigbang_amy", "shrek_donkey"])
        
        # Remove duplicates and filter to available voices
        suitable_voices = list(dict.fromkeys(suitable_voices))
        suitable_voices = [v for v in suitable_voices if v in self.voice_prompts]
        
        # If no specific suggestions, return default voices
        if not suitable_voices:
            suitable_voices = ["en_woman", "en_man"]
        
        return suitable_voices[:3]  # Return top 3 suggestions


class LLMToneController:
    """
    Controls tone and style using LLM scene prompts.
    """
    
    def __init__(self):
        self.scene_templates = {
            "professional": {
                "system_message": "You are a professional AI assistant designed to convert text into speech with a formal, business-appropriate tone.",
                "scene_prompts": [
                    "professional business setting with formal speaking style",
                    "corporate presentation with clear and articulate pronunciation", 
                    "professional meeting with confident and authoritative tone"
                ]
            },
            "friendly": {
                "system_message": "You are a friendly AI assistant designed to convert text into speech with a warm, approachable tone.",
                "scene_prompts": [
                    "casual conversation with warm and friendly tone",
                    "friendly chat with natural and relaxed speaking style",
                    "informal setting with approachable and pleasant voice"
                ]
            },
            "storytelling": {
                "system_message": "You are an AI assistant designed to convert text into speech with engaging storytelling qualities.",
                "scene_prompts": [
                    "storytelling environment with expressive and dramatic tone",
                    "narrative setting with animated and engaging voice",
                    "bedtime story with gentle and soothing cadence"
                ]
            },
            "educational": {
                "system_message": "You are an AI assistant designed to convert text into speech with clear educational delivery.",
                "scene_prompts": [
                    "educational presentation with clear and articulate speech",
                    "teaching environment with patient and explanatory tone",
                    "academic setting with precise and informative delivery"
                ]
            },
            "energetic": {
                "system_message": "You are an AI assistant designed to convert text into speech with high energy and enthusiasm.",
                "scene_prompts": [
                    "energetic presentation with enthusiastic and excited tone",
                    "motivational speech with dynamic and passionate delivery",
                    "upbeat environment with lively and animated voice"
                ]
            }
        }
    
    def generate_scene_prompt(self, tone: str, custom_description: str = "") -> str:
        """Generate scene prompt for tone control."""
        if tone in self.scene_templates:
            template = self.scene_templates[tone]
            base_prompt = template["scene_prompts"][0]
            
            if custom_description:
                return f"{base_prompt}, {custom_description}"
            return base_prompt
        
        # Default scene prompt for custom tones
        return custom_description if custom_description else "neutral speaking setting with natural voice"
    
    def get_available_tones(self) -> List[str]:
        """Get list of available preset tones."""
        return list(self.scene_templates.keys())
    
    def get_system_message(self, tone: str = "friendly") -> str:
        """Get system message for specific tone."""
        if tone in self.scene_templates:
            return self.scene_templates[tone]["system_message"]
        
        # Default system message
        return "You are an AI assistant designed to convert text into speech."