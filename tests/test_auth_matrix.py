"""Tests for AuthMatrix class."""

import pytest
from optimizer.auth import AuthMatrix


def test_auth_matrix_creation():
    """Test basic auth matrix creation."""
    auth_matrix = AuthMatrix()
    assert auth_matrix.get_node_count() == 0
    assert auth_matrix.get_credential_count() == 0


def test_add_remove_node():
    """Test adding and removing nodes."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_node("node1")
    assert auth_matrix.get_node_count() == 1
    
    auth_matrix.add_node("node2")
    assert auth_matrix.get_node_count() == 2
    
    auth_matrix.remove_node("node1")
    assert auth_matrix.get_node_count() == 1


def test_add_credential():
    """Test adding credentials between nodes."""
    auth_matrix = AuthMatrix()
    
    credential = auth_matrix.add_credential(
        "node1",
        "node2",
        "trust",
        trust_level=0.8
    )
    
    assert credential.source_node == "node1"
    assert credential.target_node == "node2"
    assert credential.credential_type == "trust"
    assert credential.trust_level == 0.8
    assert auth_matrix.get_credential_count() == 1


def test_remove_credential():
    """Test removing credentials."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust")
    assert auth_matrix.get_credential_count() == 1
    
    auth_matrix.remove_credential("node1", "node2")
    assert auth_matrix.get_credential_count() == 0


def test_has_credential():
    """Test checking if credential exists."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust")
    
    assert auth_matrix.has_credential("node1", "node2") is True
    assert auth_matrix.has_credential("node2", "node1") is False


def test_get_trusted_nodes():
    """Test getting nodes that are trusted."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust", trust_level=0.8)
    auth_matrix.add_credential("node1", "node3", "trust", trust_level=0.6)
    auth_matrix.add_credential("node1", "node4", "trust", trust_level=0.3)
    
    trusted = auth_matrix.get_trusted_nodes("node1", min_trust=0.5)
    assert len(trusted) == 2
    assert "node2" in trusted
    assert "node3" in trusted
    assert "node4" not in trusted


def test_get_trusting_nodes():
    """Test getting nodes that trust a given node."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node2", "node1", "trust", trust_level=0.8)
    auth_matrix.add_credential("node3", "node1", "trust", trust_level=0.6)
    
    trusting = auth_matrix.get_trusting_nodes("node1", min_trust=0.5)
    assert len(trusting) == 2
    assert "node2" in trusting
    assert "node3" in trusting


def test_verify_trust_path():
    """Test finding trust paths between nodes."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust")
    auth_matrix.add_credential("node2", "node3", "trust")
    
    path = auth_matrix.verify_trust_path("node1", "node3")
    assert path == ["node1", "node2", "node3"]
    
    path = auth_matrix.verify_trust_path("node3", "node1")
    assert path is None


def test_get_trust_score():
    """Test calculating trust score along a path."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust", trust_level=0.8)
    auth_matrix.add_credential("node2", "node3", "trust", trust_level=0.9)
    
    score = auth_matrix.get_trust_score("node1", "node3")
    assert score == pytest.approx(0.72)  # 0.8 * 0.9
    
    # No path
    score = auth_matrix.get_trust_score("node3", "node1")
    assert score == 0.0


def test_to_dict():
    """Test exporting auth matrix to dictionary."""
    auth_matrix = AuthMatrix()
    
    auth_matrix.add_credential("node1", "node2", "trust", trust_level=0.8)
    
    data = auth_matrix.to_dict()
    
    assert "nodes" in data
    assert "credentials" in data
    assert len(data["credentials"]) == 1
    assert data["credentials"][0]["source"] == "node1"
    assert data["credentials"][0]["target"] == "node2"
