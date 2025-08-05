"""Basic data types for multimodal ChatML format."""

from dataclasses import dataclass
from typing import Union


@dataclass
class AudioContent:
    audio_url: str
    # Base64 encoded audio bytes
    raw_audio: str | None = None
    offset: float | None = None
    duration: float | None = None
    row_id: int | None = None
    type: str = "audio"


@dataclass
class TextContent:
    text: str
    type: str = "text"


@dataclass
class Message:
    role: str
    content: Union[str, AudioContent, TextContent, list[Union[str, AudioContent, TextContent]]]
    recipient: str | None = None


@dataclass
class ChatMLSample:
    """Dataclass to hold multimodal ChatML data."""

    messages: list[Message]
    start_index: int | None = None  # We will mask the messages[:start_index] when finetuning the LLM.
    misc: dict | None = None
    speaker: str | None = None
