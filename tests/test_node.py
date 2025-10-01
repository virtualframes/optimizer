"""Tests for Node class."""

import numpy as np
import pytest
from optimizer.core import Node


def test_node_creation():
    """Test basic node creation."""
    node = Node()
    assert node.id is not None
    assert isinstance(node.position, np.ndarray)
    assert isinstance(node.velocity, np.ndarray)
    assert node.mass == 1.0


def test_node_with_parameters():
    """Test node creation with parameters."""
    position = [1.0, 2.0, 3.0]
    velocity = [0.1, 0.2, 0.3]
    mass = 2.5
    
    node = Node(position=position, velocity=velocity, mass=mass)
    
    np.testing.assert_array_equal(node.position, position)
    np.testing.assert_array_equal(node.velocity, velocity)
    assert node.mass == mass


def test_node_connections():
    """Test node connection management."""
    node1 = Node()
    node2 = Node()
    
    node1.connect(node2.id)
    assert node2.id in node1.connections
    
    node1.disconnect(node2.id)
    assert node2.id not in node1.connections


def test_node_distance():
    """Test distance calculation between nodes."""
    node1 = Node(position=[0, 0, 0])
    node2 = Node(position=[3, 4, 0])
    
    distance = node1.distance_to(node2)
    assert distance == 5.0


def test_node_update_position():
    """Test position update."""
    node = Node()
    new_position = [5.0, 6.0, 7.0]
    
    node.update_position(new_position)
    np.testing.assert_array_equal(node.position, new_position)


def test_node_update_velocity():
    """Test velocity update."""
    node = Node()
    new_velocity = [1.0, 2.0, 3.0]
    
    node.update_velocity(new_velocity)
    np.testing.assert_array_equal(node.velocity, new_velocity)


def test_node_to_dict():
    """Test node serialization to dict."""
    node = Node(
        position=[1, 2, 3],
        velocity=[0.1, 0.2, 0.3],
        mass=2.0,
        metadata={"key": "value"}
    )
    
    data = node.to_dict()
    
    assert data["id"] == node.id
    assert data["position"] == [1, 2, 3]
    assert data["velocity"] == [0.1, 0.2, 0.3]
    assert data["mass"] == 2.0
    assert data["metadata"] == {"key": "value"}


def test_node_from_dict():
    """Test node deserialization from dict."""
    data = {
        "id": "test-id",
        "position": [1, 2, 3],
        "velocity": [0.1, 0.2, 0.3],
        "mass": 2.0,
        "metadata": {"key": "value"},
        "connections": ["node1", "node2"]
    }
    
    node = Node.from_dict(data)
    
    assert node.id == "test-id"
    np.testing.assert_array_equal(node.position, [1, 2, 3])
    np.testing.assert_array_equal(node.velocity, [0.1, 0.2, 0.3])
    assert node.mass == 2.0
    assert node.metadata == {"key": "value"}
    assert node.connections == ["node1", "node2"]
