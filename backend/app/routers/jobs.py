from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job

router = APIRouter()

@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "project_id": job.project_id,
        "type": job.type,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "error_details": job.error_details,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }
