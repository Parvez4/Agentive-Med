from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_blocks_treatment():
    response = client.post("/chat", json={"question": "How much memantine should I take?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["safety_status"]["allowed"] is False
    assert payload["citations"] == []
