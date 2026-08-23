from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SystemSetting
from app.schemas import SettingsSchema, SettingsResponse

router = APIRouter()

KEYS = [
    "anthropic_api_key",
    "openai_api_key",
    "transcription_engine",
    "whisper_model_size",
    "default_aspect_ratio",
    "default_caption_style",
    "default_watermark_text"
]

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings_dict = {}
    db_settings = db.query(SystemSetting).all()
    for setting in db_settings:
        settings_dict[setting.key] = setting.value

    anthropic_key = settings_dict.get("anthropic_api_key", "")
    openai_key = settings_dict.get("openai_api_key", "")

    return SettingsResponse(
        anthropic_api_key=f"***{anthropic_key[-4:]}" if len(anthropic_key) > 4 else ("***" if anthropic_key else ""),
        openai_api_key=f"***{openai_key[-4:]}" if len(openai_key) > 4 else ("***" if openai_key else ""),
        has_anthropic_key=bool(anthropic_key),
        has_openai_key=bool(openai_key),
        transcription_engine=settings_dict.get("transcription_engine", "faster-whisper"),
        whisper_model_size=settings_dict.get("whisper_model_size", "base"),
        default_aspect_ratio=settings_dict.get("default_aspect_ratio", "9:16"),
        default_caption_style=settings_dict.get("default_caption_style", "yellow_highlight"),
        default_watermark_text=settings_dict.get("default_watermark_text", "")
    )

@router.post("", response_model=SettingsResponse)
def update_settings(payload: SettingsSchema, db: Session = Depends(get_db)):
    updates = payload.model_dump(exclude_unset=True)
    for key, val in updates.items():
        if val is None:
            continue
        # Masked values starting with *** mean do not update secret key
        if key in ["anthropic_api_key", "openai_api_key"] and str(val).startswith("***"):
            continue
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not setting:
            setting = SystemSetting(key=key, value=str(val))
            db.add(setting)
        else:
            setting.value = str(val)
    db.commit()
    return get_settings(db)
