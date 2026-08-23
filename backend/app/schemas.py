from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SettingsSchema(BaseModel):
    anthropic_api_key: Optional[str] = ""
    openai_api_key: Optional[str] = ""
    transcription_engine: str = "faster-whisper" # "faster-whisper" or "openai-whisper"
    whisper_model_size: str = "base" # "tiny", "base", "small", "medium"
    default_aspect_ratio: str = "9:16"
    default_caption_style: str = "yellow_highlight"
    default_watermark_text: Optional[str] = ""

class SettingsResponse(SettingsSchema):
    has_anthropic_key: bool
    has_openai_key: bool

class ProjectCreate(BaseModel):
    title: str

class YouTubeImportRequest(BaseModel):
    url: str

class ClipUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    aspect_ratio: Optional[str] = None
    caption_style: Optional[str] = None
    word_level_highlight: Optional[bool] = None
    watermark_text: Optional[str] = None

class RenderClipRequest(BaseModel):
    clip_id: str
    aspect_ratio: str = "9:16"
    caption_style: str = "yellow_highlight"
    word_level_highlight: bool = True
    watermark_text: Optional[str] = None
