from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "bedtime-story-generator"
    assert "model" in data

if __name__ == "__main__":
    test_health()
    print("Smoke test passed: /health returned 200 OK")
