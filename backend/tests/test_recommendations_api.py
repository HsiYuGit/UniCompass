from fastapi.testclient import TestClient

from src.api.recommendations import app


def test_health_endpoint_is_available():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommendations_fail_closed_without_backend_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = TestClient(app).post(
        "/v1/recommendations",
        json={"transcript": {}, "programmes": [{"school": "A", "program": "B"}]},
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
