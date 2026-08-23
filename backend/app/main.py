import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import projects, settings, jobs

app = FastAPI(
    title="AI Video Clipper API",
    description="Local self-hosted backend API for AI Video Clipper",
    version="1.0.0"
)

# CORS configuration for local Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
init_db()

# Mount Static File Server for uploaded video files and exported clips
DEFAULT_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage"))
STORAGE_DIR = os.getenv("STORAGE_PATH", DEFAULT_STORAGE)
os.makedirs(STORAGE_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# Include Routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Video Clipper Backend is running"}
