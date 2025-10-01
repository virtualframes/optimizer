from fastapi.testclient import TestClient
from optimizer.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_node():
    response = client.post(
        "/ingest/node",
        json={
            "node_id": "test_node",
            "position": [1, 2, 3],
            "metadata": {"key": "value"},
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "Node ingested successfully",
        "node_id": "test_node",
    }


def test_query_node():
    # First, ingest a node to query
    client.post(
        "/ingest/node",
        json={"node_id": "query_node", "position": [4, 5, 6]},
    )

    response = client.get("/query/node/query_node")
    assert response.status_code == 200
    assert response.json() == {
        "node_id": "query_node",
        "position": [4, 5, 6],
        "metadata": {},
    }


def test_query_nonexistent_node():
    response = client.get("/query/node/nonexistent_node")
    assert response.status_code == 404


def test_ingest_credential():
    response = client.post(
        "/ingest/credential",
        json={"source_node_id": "node_a", "target_node_id": "node_b"},
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Credential ingested successfully"}


def test_query_auth_matrix():
    # Ingest a credential first
    client.post(
        "/ingest/credential",
        json={"source_node_id": "node_c", "target_node_id": "node_d"},
    )

    response = client.get("/query/auth_matrix")
    assert response.status_code == 200
    # The exact content will depend on what other tests ran, so we just check for the new credential
    assert "node_c" in response.json()
    assert "node_d" in response.json()["node_c"]
