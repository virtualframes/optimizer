from fastapi.testclient import TestClient
from optimizer.api.main import app

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "ts": response.json()["ts"]}