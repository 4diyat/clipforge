import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "transcription_engine" in data
    assert "default_aspect_ratio" in data

def test_projects_list():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
