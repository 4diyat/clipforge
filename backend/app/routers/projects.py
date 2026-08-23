import os
import uuid
import subprocess
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Project, Clip, Job
from app.schemas import ClipUpdate

router = APIRouter()

STORAGE_DIR = os.getenv("STORAGE_PATH", os.path.expanduser("~/ai-video-clipper/storage"))

def get_video_duration(file_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", file_path
        ]
        output = subprocess.check_output(cmd).decode().strip()
        return float(output)
    except Exception:
        return 0.0

@router.get("")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects

@router.post("/{project_id}/analyze")
def trigger_ai_analysis(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        project_id=project_id,
        type="analyze",
        status="pending",
        progress=0,
        message="Queued for AI highlight detection"
    )
    db.add(job)
    db.commit()

    from app.services.ai import analyze_transcript
    background_tasks.add_task(analyze_transcript, project_id, job_id, SessionLocal)

    return {"job_id": job_id, "message": "AI Analysis started"}

@router.post("/{project_id}/render")
def trigger_render(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        project_id=project_id,
        type="render_clip",
        status="pending",
        progress=0,
        message="Queued for video rendering & export"
    )
    db.add(job)
    db.commit()

    from app.services.export import render_project_clips
    background_tasks.add_task(render_project_clips, project_id, job_id, SessionLocal)

    return {"job_id": job_id, "message": "Video export rendering started"}

@router.patch("/clips/{clip_id}")
def update_clip(
    clip_id: str,
    payload: ClipUpdate,
    db: Session = Depends(get_db)
):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        if v is not None:
            setattr(clip, k, v)
    db.commit()
    db.refresh(clip)
    return clip

@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    clips = db.query(Clip).filter(Clip.project_id == project_id).order_by(Clip.start_time.asc()).all()
    return {
        "project": project,
        "clips": clips
    }

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    db: Session = Depends(get_db)
):
    project_id = str(uuid.uuid4())
    project_dir = os.path.join(STORAGE_DIR, "projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1] or ".mp4"
    file_path = os.path.join(project_dir, f"source{file_ext}")

    # Save uploaded file in chunks
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024 * 5): # 5MB chunk
            buffer.write(chunk)

    duration = get_video_duration(file_path)
    proj_title = title or file.filename

    project = Project(
        id=project_id,
        title=proj_title,
        source_type="upload",
        file_path=file_path,
        duration_seconds=duration,
        status="uploaded"
    )
    db.add(project)

    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        project_id=project_id,
        type="transcribe",
        status="pending",
        progress=0,
        message="Upload received, queued for transcription"
    )
    db.add(job)
    db.commit()

    from app.services.transcribe import run_transcription
    background_tasks.add_task(run_transcription, project_id, job_id, SessionLocal)

    return {
        "project_id": project_id,
        "job_id": job_id,
        "message": "Video uploaded successfully"
    }

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Clean up files
    project_dir = os.path.dirname(project.file_path)
    if os.path.exists(project_dir):
        import shutil
        shutil.rmtree(project_dir, ignore_errors=True)

    db.delete(project)
    db.commit()
    return {"status": "deleted", "project_id": project_id}
