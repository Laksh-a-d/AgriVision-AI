import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """
    Test the /api/health endpoint returns expected status, application name and version.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application"] == "AgriPulse"
    assert data["version"] == "0.1.0"


def test_root():
    """
    Test the root / endpoint returns welcome payload.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "AgriPulse"
    assert data["health_check"] == "/api/health"
