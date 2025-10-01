"""Tests for FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from optimizer.api.app import create_app
from optimizer.api.routes.ingest import nodes_storage


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear nodes storage before each test."""
    nodes_storage.clear()
    yield
    nodes_storage.clear()


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_node(client):
    """Test creating a node."""
    node_data = {
        "position": [1.0, 2.0, 3.0],
        "velocity": [0.1, 0.2, 0.3],
        "mass": 2.5,
        "metadata": {"key": "value"}
    }
    
    response = client.post("/api/v1/ingest/nodes", json=node_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["position"] == [1.0, 2.0, 3.0]
    assert data["velocity"] == [0.1, 0.2, 0.3]
    assert data["mass"] == 2.5


def test_create_nodes_batch(client):
    """Test creating multiple nodes."""
    nodes_data = [
        {"position": [1.0, 2.0, 3.0], "mass": 1.0},
        {"position": [4.0, 5.0, 6.0], "mass": 2.0},
    ]
    
    response = client.post("/api/v1/ingest/nodes/batch", json=nodes_data)
    assert response.status_code == 201
    
    data = response.json()
    assert len(data) == 2


def test_get_node(client):
    """Test retrieving a node."""
    # Create a node first
    node_data = {"position": [1.0, 2.0, 3.0]}
    create_response = client.post("/api/v1/ingest/nodes", json=node_data)
    node_id = create_response.json()["id"]
    
    # Get the node
    response = client.get(f"/api/v1/query/nodes/{node_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == node_id


def test_get_node_not_found(client):
    """Test getting non-existent node."""
    response = client.get("/api/v1/query/nodes/nonexistent")
    assert response.status_code == 404


def test_update_node(client):
    """Test updating a node."""
    # Create a node first
    node_data = {"position": [1.0, 2.0, 3.0]}
    create_response = client.post("/api/v1/ingest/nodes", json=node_data)
    node_id = create_response.json()["id"]
    
    # Update the node
    update_data = {"position": [4.0, 5.0, 6.0], "mass": 3.0}
    response = client.put(f"/api/v1/ingest/nodes/{node_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["position"] == [4.0, 5.0, 6.0]
    assert data["mass"] == 3.0


def test_delete_node(client):
    """Test deleting a node."""
    # Create a node first
    node_data = {"position": [1.0, 2.0, 3.0]}
    create_response = client.post("/api/v1/ingest/nodes", json=node_data)
    node_id = create_response.json()["id"]
    
    # Delete the node
    response = client.delete(f"/api/v1/ingest/nodes/{node_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/v1/query/nodes/{node_id}")
    assert response.status_code == 404


def test_list_nodes(client):
    """Test listing nodes."""
    # Create some nodes
    for i in range(5):
        node_data = {"position": [float(i), 0.0, 0.0]}
        client.post("/api/v1/ingest/nodes", json=node_data)
    
    # List nodes
    response = client.get("/api/v1/query/nodes")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 5


def test_connect_nodes(client):
    """Test connecting two nodes."""
    # Create two nodes
    node1_data = {"position": [1.0, 2.0, 3.0]}
    node2_data = {"position": [4.0, 5.0, 6.0]}
    
    node1_id = client.post("/api/v1/ingest/nodes", json=node1_data).json()["id"]
    node2_id = client.post("/api/v1/ingest/nodes", json=node2_data).json()["id"]
    
    # Connect them
    response = client.post(f"/api/v1/ingest/nodes/{node1_id}/connect/{node2_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert node2_id in data["connections"]


def test_get_system_stats(client):
    """Test getting system statistics."""
    # Create some nodes
    for i in range(3):
        node_data = {"position": [float(i), 0.0, 0.0], "mass": float(i + 1)}
        client.post("/api/v1/ingest/nodes", json=node_data)
    
    # Get stats
    response = client.get("/api/v1/query/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_nodes"] == 3
    assert "average_mass" in data
