import pytest
from intel_harvester.core.node import Node
from intel_harvester.core.auth_matrix import AuthMatrix
from intel_harvester.core.engine import Engine

def test_node_creation():
    node = Node(node_id="test_node", position=(1, 2, 3), metadata={"info": "test"})
    assert node.node_id == "test_node"
    assert node.position == (1, 2, 3)
    assert node.metadata == {"info": "test"}

def test_node_to_dict():
    node = Node(node_id="test_node", position=(1, 2, 3))
    assert node.to_dict() == {
        "node_id": "test_node",
        "position": (1, 2, 3),
        "metadata": {},
    }

def test_auth_matrix():
    auth = AuthMatrix()
    auth.add_credential("node1", "node2")
    assert auth.has_credential("node1", "node2")
    assert not auth.has_credential("node2", "node1")

def test_auth_matrix_to_dict():
    auth = AuthMatrix()
    auth.add_credential("node1", "node2")
    auth.add_credential("node1", "node3")
    assert auth.to_dict() == {"node1": ["node2", "node3"]}

def test_engine_initialization():
    engine = Engine()
    assert engine.physics_client is not None
    engine.disconnect()

def test_engine_simulation_step():
    engine = Engine()
    # Not much to assert here without visible objects, but we can ensure it runs without error
    try:
        engine.step_simulation()
    except Exception as e:
        pytest.fail(f"Engine simulation step failed: {e}")
    finally:
        engine.disconnect()