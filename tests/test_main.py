from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "api_version": "1.0.0"}


def test_play_video_invalid_path():
    response = client.post(
        "/player/play",
        json={"video_path": "/invalid/path.mp4", "loop": True, "fullscreen": True},
    )
    assert response.status_code == 422
    assert "Video file does not exist" in response.json()["detail"]
