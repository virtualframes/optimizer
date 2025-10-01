"""Tests for the Engine class."""

import pytest
from optimizer.node import Node
from optimizer.engine import Engine


def test_engine_creation():
    """Test creating an engine instance."""
    engine = Engine(gui=False)
    
    assert engine.gui is False
    assert engine.gravity == (0.0, 0.0, -9.81)
    assert engine.time_step == 1.0/240.0
    assert engine.is_running is False


def test_engine_start_stop():
    """Test starting and stopping the engine."""
    engine = Engine(gui=False)
    
    assert engine.is_running is False
    
    engine.start()
    assert engine.is_running is True
    assert engine.physics_client is not None
    
    engine.stop()
    assert engine.is_running is False
    assert engine.physics_client is None


def test_engine_context_manager():
    """Test using engine as a context manager."""
    with Engine(gui=False) as engine:
        assert engine.is_running is True
    
    # After context exit, engine should be stopped
    assert engine.is_running is False


def test_engine_add_node():
    """Test adding a node to the engine."""
    node = Node(node_id="test-node", position=(0.0, 0.0, 5.0))
    
    with Engine(gui=False) as engine:
        engine.add_node(node)
        
        assert node.node_id in engine.node_bodies
        assert isinstance(engine.node_bodies[node.node_id], int)


def test_engine_add_node_not_started():
    """Test that adding a node fails if engine not started."""
    engine = Engine(gui=False)
    node = Node()
    
    with pytest.raises(RuntimeError, match="Engine not started"):
        engine.add_node(node)


def test_engine_step():
    """Test stepping the simulation."""
    with Engine(gui=False) as engine:
        node = Node(position=(0.0, 0.0, 5.0))
        engine.add_node(node)
        
        # Should not raise an error
        engine.step()


def test_engine_step_not_started():
    """Test that stepping fails if engine not started."""
    engine = Engine(gui=False)
    
    with pytest.raises(RuntimeError, match="Engine not started"):
        engine.step()


def test_engine_sync_node():
    """Test synchronizing node state from physics engine."""
    node = Node(position=(0.0, 0.0, 5.0), velocity=(1.0, 0.0, 0.0))
    
    with Engine(gui=False) as engine:
        engine.add_node(node)
        
        # Step the simulation a few times
        for _ in range(10):
            engine.step()
        
        # Sync the node
        engine.sync_node(node)
        
        # Position should have changed due to gravity/velocity
        # (just check that sync doesn't crash)
        assert node.position is not None
        assert node.velocity is not None


def test_engine_get_node_state():
    """Test getting node state from engine."""
    node = Node(node_id="state-test", position=(0.0, 0.0, 5.0))
    
    with Engine(gui=False) as engine:
        engine.add_node(node)
        
        state = engine.get_node_state(node.node_id)
        
        assert state is not None
        assert "position" in state
        assert "orientation" in state
        assert "linear_velocity" in state
        assert "angular_velocity" in state


def test_engine_get_node_state_not_found():
    """Test getting state for non-existent node."""
    with Engine(gui=False) as engine:
        state = engine.get_node_state("non-existent-node")
        assert state is None


def test_engine_custom_gravity():
    """Test creating engine with custom gravity."""
    engine = Engine(gui=False, gravity=(0.0, -10.0, 0.0))
    
    assert engine.gravity == (0.0, -10.0, 0.0)
