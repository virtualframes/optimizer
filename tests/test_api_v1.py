from fastapi.testclient import TestClient
from optimizer.api.main import app

client = TestClient(app)


def test_get_health_v1():
    """
    Tests the GET /api/v1/health endpoint.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_status_v1():
    """
    Tests the GET /api/v1/status endpoint.
    """
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    expected_response = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-10-01T09:37:38Z",
        "services": {
            "neo4j": "connected",
            "redis": "connected",
            "vector_db": "connected",
            "mcp_servers": 3,
        },
        "system": {
            "cpu_usage": 15.2,
            "memory_usage": 45.8,
            "disk_usage": 23.1,
        },
    }
    assert response.json() == expected_response