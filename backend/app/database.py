import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

STORAGE_DIR = os.getenv("STORAGE_PATH", os.path.expanduser("~/ai-video-clipper/storage"))
os.makedirs(STORAGE_DIR, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(STORAGE_DIR, 'app.db')}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
