"""Tests for PyBullet engine adapter."""

import pytest
import numpy as np
from optimizer.core import Node
from optimizer.engine import PyBulletEngine


def test_engine_creation():
    """Test basic engine creation."""
    engine = PyBulletEngine(gui=False)
    assert engine.gui is False
    assert engine.is_connected is False


def test_engine_connect_disconnect():
    """Test connecting and disconnecting from PyBullet."""
    engine = PyBulletEngine(gui=False)
    
    engine.connect()
    assert engine.is_connected is True
    assert engine.client_id is not None
    
    engine.disconnect()
    assert engine.is_connected is False


def test_engine_context_manager():
    """Test using engine as context manager."""
    with PyBulletEngine(gui=False) as engine:
        assert engine.is_connected is True
    
    assert engine.is_connected is False


def test_add_node_to_simulation():
    """Test adding a node to the simulation."""
    node = Node(position=[0, 0, 1])
    
    with PyBulletEngine(gui=False) as engine:
        body_id = engine.add_node(node)
        
        assert body_id is not None
        assert node.id in engine.node_bodies


def test_remove_node_from_simulation():
    """Test removing a node from the simulation."""
    node = Node(position=[0, 0, 1])
    
    with PyBulletEngine(gui=False) as engine:
        engine.add_node(node)
        assert node.id in engine.node_bodies
        
        engine.remove_node(node.id)
        assert node.id not in engine.node_bodies


def test_step_simulation():
    """Test stepping the simulation."""
    node = Node(position=[0, 0, 1])
    
    with PyBulletEngine(gui=False) as engine:
        engine.add_node(node)
        
        # Should not raise an error
        engine.step_simulation()


def test_update_node_from_simulation():
    """Test updating node state from simulation."""
    node = Node(position=[0, 0, 1])
    
    with PyBulletEngine(gui=False) as engine:
        engine.add_node(node)
        
        # Step simulation a few times
        for _ in range(10):
            engine.step_simulation()
        
        # Update node from simulation
        engine.update_node_from_simulation(node)
        
        # Position should have changed due to gravity
        assert not np.array_equal(node.position, [0, 0, 1])


def test_get_all_positions():
    """Test getting all node positions."""
    nodes = [Node(position=[i, 0, 1]) for i in range(3)]
    
    with PyBulletEngine(gui=False) as engine:
        for node in nodes:
            engine.add_node(node)
        
        positions = engine.get_all_positions()
        
        assert len(positions) == 3
        for node in nodes:
            assert node.id in positions


def test_reset_simulation():
    """Test resetting the simulation."""
    node = Node(position=[0, 0, 1])
    
    with PyBulletEngine(gui=False) as engine:
        engine.add_node(node)
        assert len(engine.node_bodies) == 1
        
        engine.reset_simulation()
        assert len(engine.node_bodies) == 0
