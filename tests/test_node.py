"""Tests for the Node class."""

import pytest
from optimizer.node import Node


def test_node_creation_with_defaults():
    """Test creating a node with default parameters."""
    node = Node()
    
    assert node.node_id is not None
    assert len(node.node_id) > 0
    assert node.position == (0.0, 0.0, 0.0)
    assert node.velocity == (0.0, 0.0, 0.0)
    assert node.mass == 1.0
    assert node.metadata == {}


def test_node_creation_with_custom_values():
    """Test creating a node with custom parameters."""
    node = Node(
        node_id="test-node-1",
        position=(1.0, 2.0, 3.0),
        velocity=(0.5, 0.5, 0.5),
        mass=2.5,
        metadata={"type": "test"}
    )
    
    assert node.node_id == "test-node-1"
    assert node.position == (1.0, 2.0, 3.0)
    assert node.velocity == (0.5, 0.5, 0.5)
    assert node.mass == 2.5
    assert node.metadata == {"type": "test"}


def test_node_update_position():
    """Test updating node position."""
    node = Node()
    new_position = (5.0, 10.0, 15.0)
    
    node.update_position(new_position)
    
    assert node.position == new_position


def test_node_update_velocity():
    """Test updating node velocity."""
    node = Node()
    new_velocity = (1.0, 2.0, 3.0)
    
    node.update_velocity(new_velocity)
    
    assert node.velocity == new_velocity


def test_node_get_state():
    """Test getting node state."""
    node = Node(
        node_id="state-test",
        position=(1.0, 2.0, 3.0),
        velocity=(0.1, 0.2, 0.3),
        mass=1.5,
        metadata={"key": "value"}
    )
    
    state = node.get_state()
    
    assert state["node_id"] == "state-test"
    assert state["position"] == (1.0, 2.0, 3.0)
    assert state["velocity"] == (0.1, 0.2, 0.3)
    assert state["mass"] == 1.5
    assert state["metadata"] == {"key": "value"}


def test_node_repr():
    """Test node string representation."""
    node = Node(node_id="repr-test", position=(1.0, 2.0, 3.0))
    
    repr_str = repr(node)
    
    assert "repr-test" in repr_str
    assert "1.0" in repr_str
    assert "2.0" in repr_str
    assert "3.0" in repr_str


def test_node_unique_ids():
    """Test that nodes get unique IDs when not specified."""
    node1 = Node()
    node2 = Node()
    
    assert node1.node_id != node2.node_id
