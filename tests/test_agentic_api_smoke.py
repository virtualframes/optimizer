from optimizer.agentic_api.router import app
from fastapi.testclient import TestClient

def test_quorum_and_fp():
    c = TestClient(app)
    r = c.post("/fingerprint", json={"data":{"x":1}})
    assert r.status_code == 200 and "fingerprint" in r.json()
    r = c.post("/quorum/validate", json={"outputs":["ok:a","nope"], "threshold":1})
    assert r.json()["pass"] is True