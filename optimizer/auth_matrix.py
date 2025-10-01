"""
AuthMatrix module for node-to-node credential checks.

Provides authentication and authorization mechanisms for virtual nodes
to verify and validate connections in the simulation network.
"""

from typing import Dict, Set, Optional, List
from enum import Enum
import hashlib
import secrets


class PermissionLevel(Enum):
    """Permission levels for node interactions."""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3


class AuthMatrix:
    """
    Authentication matrix for managing node-to-node access control.
    
    Maintains a matrix of permissions between nodes, allowing verification
    of whether one node has permission to interact with another.
    """
    
    def __init__(self):
        """Initialize an empty authentication matrix."""
        self.permissions: Dict[str, Dict[str, PermissionLevel]] = {}
        self.node_tokens: Dict[str, str] = {}
        self.verified_nodes: Set[str] = set()
        
    def register_node(self, node_id: str, generate_token: bool = True) -> Optional[str]:
        """
        Register a node in the authentication matrix.
        
        Args:
            node_id: Unique identifier for the node
            generate_token: Whether to generate an authentication token
            
        Returns:
            Authentication token if generated, None otherwise
        """
        if node_id not in self.permissions:
            self.permissions[node_id] = {}
            
        token = None
        if generate_token:
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.node_tokens[node_id] = token_hash
            
        return token
        
    def verify_node(self, node_id: str, token: str) -> bool:
        """
        Verify a node's authentication token.
        
        Args:
            node_id: Node identifier
            token: Authentication token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        if node_id not in self.node_tokens:
            return False
            
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        is_valid = self.node_tokens[node_id] == token_hash
        
        if is_valid:
            self.verified_nodes.add(node_id)
            
        return is_valid
        
    def grant_permission(
        self,
        from_node: str,
        to_node: str,
        level: PermissionLevel
    ) -> bool:
        """
        Grant permission for one node to access another.
        
        Args:
            from_node: Node requesting access
            to_node: Target node
            level: Permission level to grant
            
        Returns:
            True if permission was granted, False if nodes not registered
        """
        if from_node not in self.permissions or to_node not in self.permissions:
            return False
            
        self.permissions[from_node][to_node] = level
        return True
        
    def revoke_permission(self, from_node: str, to_node: str) -> bool:
        """
        Revoke permission for one node to access another.
        
        Args:
            from_node: Node with access
            to_node: Target node
            
        Returns:
            True if permission was revoked, False if not found
        """
        if from_node in self.permissions and to_node in self.permissions[from_node]:
            del self.permissions[from_node][to_node]
            return True
        return False
        
    def check_permission(
        self,
        from_node: str,
        to_node: str,
        required_level: PermissionLevel = PermissionLevel.READ
    ) -> bool:
        """
        Check if a node has sufficient permission to access another.
        
        Args:
            from_node: Node requesting access
            to_node: Target node
            required_level: Minimum permission level required
            
        Returns:
            True if permission is sufficient, False otherwise
        """
        if from_node not in self.permissions:
            return False
            
        granted_level = self.permissions[from_node].get(to_node, PermissionLevel.NONE)
        return granted_level.value >= required_level.value
        
    def get_node_permissions(self, node_id: str) -> Dict[str, PermissionLevel]:
        """
        Get all permissions for a specific node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Dictionary mapping target node IDs to permission levels
        """
        return self.permissions.get(node_id, {}).copy()
        
    def get_authorized_nodes(
        self,
        node_id: str,
        min_level: PermissionLevel = PermissionLevel.READ
    ) -> List[str]:
        """
        Get list of nodes that a given node can access.
        
        Args:
            node_id: Node identifier
            min_level: Minimum permission level required
            
        Returns:
            List of node IDs that can be accessed
        """
        if node_id not in self.permissions:
            return []
            
        return [
            target for target, level in self.permissions[node_id].items()
            if level.value >= min_level.value
        ]
        
    def is_verified(self, node_id: str) -> bool:
        """
        Check if a node has been verified.
        
        Args:
            node_id: Node identifier
            
        Returns:
            True if node is verified, False otherwise
        """
        return node_id in self.verified_nodes
