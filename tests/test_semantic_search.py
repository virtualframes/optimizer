from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# We need to set the environment variables before importing the app
import os

os.environ["MILVUS_HOST"] = "mock-milvus"
os.environ["OPENAI_API_KEY"] = "mock-key"

from services.semantic_search_api.main import app

client = TestClient(app)


@pytest.fixture
def mock_openai():
    """Fixture to mock the OpenAI async client."""
    with patch(
        "services.semantic_search_api.main.client", new_callable=AsyncMock
    ) as mock_client:
        # Mock the embedding creation
        mock_embedding = MagicMock()
        mock_embedding.embedding = [0.1] * 1536  # Dummy vector
        mock_response = MagicMock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_milvus():
    """Fixture to mock the Milvus Collection."""
    with patch("services.semantic_search_api.main.Collection") as mock_collection_class:
        # Mock the class methods
        mock_collection_class.exists.return_value = True

        # Mock the instance methods
        mock_collection_instance = MagicMock()
        mock_hit = MagicMock()
        mock_hit.id = "note:123"
        mock_hit.score = 0.95
        mock_hit.entity.get.side_effect = lambda key: {
            "text": "This is a test note.",
            "timestamp": "2023-01-01T00:00:00Z",
        }.get(key)
        mock_collection_instance.search.return_value = [[mock_hit]]

        mock_collection_class.return_value = mock_collection_instance
        yield mock_collection_class


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_semantic_search_success(mock_openai, mock_milvus):
    """Test a successful semantic search request."""
    response = client.post(
        "/search",
        json={"query": "test query", "sources": ["notes"], "limit": 1},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "note:123"
    assert results[0]["text"] == "This is a test note."
    assert results[0]["score"] > 0.9

    # Verify mocks were called
    mock_openai.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small", input="test query", dimensions=1536
    )
    mock_milvus.assert_called_with("synapse_notes")
    mock_milvus.return_value.load.assert_called_once()
    mock_milvus.return_value.search.assert_called_once()


def test_semantic_search_collection_not_found(mock_openai, mock_milvus):
    """Test searching when a collection does not exist."""
    # Configure the mock to simulate the collection not existing
    mock_milvus.exists.return_value = False

    response = client.post(
        "/search",
        json={"query": "test query", "sources": ["nonexistent"], "limit": 1},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0

    # Verify Milvus search was NOT called
    mock_milvus.return_value.search.assert_not_called()


def test_semantic_search_multiple_sources(mock_openai, mock_milvus):
    """Test searching across multiple sources, one of which does not exist."""
    # Use side_effect to have different return values for different calls
    mock_milvus.exists.side_effect = lambda name: name == "synapse_notes"

    response = client.post(
        "/search",
        json={"query": "test query", "sources": ["notes", "nonexistent"], "limit": 5},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "note:123"

    # Verify exists was called for both
    assert mock_milvus.exists.call_count == 2
    # Verify search was only called once
    mock_milvus.return_value.search.assert_called_once()