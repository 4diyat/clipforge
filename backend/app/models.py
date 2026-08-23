import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source_type = Column(String, default="upload") # "upload" or "youtube"
    source_url = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String, default="uploaded") # "uploaded", "transcribing", "transcribed", "analyzing", "ready", "error"
    raw_transcript = Column(JSON, nullable=True) # Full transcript with timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clips = relationship("Clip", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")

class Clip(Base):
    __tablename__ = "clips"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    hook = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    virality_score = Column(Integer, default=80)

    # Auto SEO Metadata
    suggested_titles = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)

    # Export Options
    aspect_ratio = Column(String, default="9:16") # "9:16", "1:1", "16:9"
    caption_style = Column(String, default="bold_center") # "bold_center", "yellow_highlight", "minimal_bottom"
    word_level_highlight = Column(Integer, default=1) # 1 for True, 0 for False
    watermark_text = Column(String, nullable=True)

    # Processed Output Files
    export_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    status = Column(String, default="pending") # "pending", "rendering", "rendered", "error"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="clips")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    type = Column(String, nullable=False) # "transcribe", "analyze", "render_clip"
    status = Column(String, default="pending") # "pending", "processing", "completed", "failed"
    progress = Column(Integer, default=0)
    message = Column(String, nullable=True)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="jobs")

class SystemSetting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=True)
