"""Tests for the AuthMatrix class."""

import pytest
from optimizer.auth_matrix import AuthMatrix, PermissionLevel


def test_auth_matrix_creation():
    """Test creating an authentication matrix."""
    auth = AuthMatrix()
    
    assert len(auth.permissions) == 0
    assert len(auth.node_tokens) == 0
    assert len(auth.verified_nodes) == 0


def test_register_node():
    """Test registering a node."""
    auth = AuthMatrix()
    token = auth.register_node("node1")
    
    assert token is not None
    assert len(token) > 0
    assert "node1" in auth.permissions
    assert "node1" in auth.node_tokens


def test_register_node_without_token():
    """Test registering a node without generating a token."""
    auth = AuthMatrix()
    token = auth.register_node("node1", generate_token=False)
    
    assert token is None
    assert "node1" in auth.permissions
    assert "node1" not in auth.node_tokens


def test_verify_node_valid_token():
    """Test verifying a node with a valid token."""
    auth = AuthMatrix()
    token = auth.register_node("node1")
    
    is_valid = auth.verify_node("node1", token)
    
    assert is_valid is True
    assert "node1" in auth.verified_nodes


def test_verify_node_invalid_token():
    """Test verifying a node with an invalid token."""
    auth = AuthMatrix()
    auth.register_node("node1")
    
    is_valid = auth.verify_node("node1", "wrong-token")
    
    assert is_valid is False
    assert "node1" not in auth.verified_nodes


def test_verify_node_unregistered():
    """Test verifying an unregistered node."""
    auth = AuthMatrix()
    
    is_valid = auth.verify_node("node1", "any-token")
    
    assert is_valid is False


def test_grant_permission():
    """Test granting permission between nodes."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    
    success = auth.grant_permission("node1", "node2", PermissionLevel.READ)
    
    assert success is True
    assert "node2" in auth.permissions["node1"]
    assert auth.permissions["node1"]["node2"] == PermissionLevel.READ


def test_grant_permission_unregistered_node():
    """Test granting permission with unregistered node."""
    auth = AuthMatrix()
    auth.register_node("node1")
    
    success = auth.grant_permission("node1", "node2", PermissionLevel.READ)
    
    assert success is False


def test_revoke_permission():
    """Test revoking permission between nodes."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    auth.grant_permission("node1", "node2", PermissionLevel.READ)
    
    success = auth.revoke_permission("node1", "node2")
    
    assert success is True
    assert "node2" not in auth.permissions["node1"]


def test_revoke_permission_not_granted():
    """Test revoking a permission that was not granted."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    
    success = auth.revoke_permission("node1", "node2")
    
    assert success is False


def test_check_permission_sufficient():
    """Test checking permission when it is sufficient."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    auth.grant_permission("node1", "node2", PermissionLevel.WRITE)
    
    has_permission = auth.check_permission("node1", "node2", PermissionLevel.READ)
    
    assert has_permission is True


def test_check_permission_insufficient():
    """Test checking permission when it is insufficient."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    auth.grant_permission("node1", "node2", PermissionLevel.READ)
    
    has_permission = auth.check_permission("node1", "node2", PermissionLevel.WRITE)
    
    assert has_permission is False


def test_check_permission_none():
    """Test checking permission when none is granted."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    
    has_permission = auth.check_permission("node1", "node2", PermissionLevel.READ)
    
    assert has_permission is False


def test_get_node_permissions():
    """Test getting all permissions for a node."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    auth.register_node("node3")
    auth.grant_permission("node1", "node2", PermissionLevel.READ)
    auth.grant_permission("node1", "node3", PermissionLevel.WRITE)
    
    permissions = auth.get_node_permissions("node1")
    
    assert len(permissions) == 2
    assert permissions["node2"] == PermissionLevel.READ
    assert permissions["node3"] == PermissionLevel.WRITE


def test_get_authorized_nodes():
    """Test getting list of authorized nodes."""
    auth = AuthMatrix()
    auth.register_node("node1")
    auth.register_node("node2")
    auth.register_node("node3")
    auth.register_node("node4")
    auth.grant_permission("node1", "node2", PermissionLevel.READ)
    auth.grant_permission("node1", "node3", PermissionLevel.WRITE)
    auth.grant_permission("node1", "node4", PermissionLevel.ADMIN)
    
    # Get nodes with at least READ permission
    authorized = auth.get_authorized_nodes("node1", PermissionLevel.READ)
    assert len(authorized) == 3
    assert "node2" in authorized
    assert "node3" in authorized
    assert "node4" in authorized
    
    # Get nodes with at least WRITE permission
    authorized_write = auth.get_authorized_nodes("node1", PermissionLevel.WRITE)
    assert len(authorized_write) == 2
    assert "node3" in authorized_write
    assert "node4" in authorized_write


def test_is_verified():
    """Test checking if a node is verified."""
    auth = AuthMatrix()
    token = auth.register_node("node1")
    
    assert auth.is_verified("node1") is False
    
    auth.verify_node("node1", token)
    
    assert auth.is_verified("node1") is True


def test_permission_level_enum():
    """Test permission level enum values."""
    assert PermissionLevel.NONE.value == 0
    assert PermissionLevel.READ.value == 1
    assert PermissionLevel.WRITE.value == 2
    assert PermissionLevel.ADMIN.value == 3
