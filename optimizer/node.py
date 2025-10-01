"""
Core Node class representing virtual simulation nodes.

Nodes are the fundamental units in the optimizer simulation, representing virtual
entities that can be positioned in 3D space and interact with the physics engine.
"""

from typing import Dict, Any, Optional, Tuple
import uuid


class Node:
    """
    Represents a virtual simulation node in the 3D physics environment.
    
    Attributes:
        node_id: Unique identifier for the node
        position: 3D coordinates (x, y, z) in the simulation space
        velocity: 3D velocity vector (vx, vy, vz)
        mass: Mass of the node for physics calculations
        metadata: Additional node-specific data
    """
    
    def __init__(
        self,
        node_id: Optional[str] = None,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        mass: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new Node.
        
        Args:
            node_id: Unique identifier (generated if not provided)
            position: Initial position in 3D space
            velocity: Initial velocity vector
            mass: Node mass for physics simulation
            metadata: Optional additional data
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.metadata = metadata or {}
        
    def update_position(self, new_position: Tuple[float, float, float]) -> None:
        """
        Update the node's position.
        
        Args:
            new_position: New 3D coordinates (x, y, z)
        """
        self.position = new_position
        
    def update_velocity(self, new_velocity: Tuple[float, float, float]) -> None:
        """
        Update the node's velocity.
        
        Args:
            new_velocity: New velocity vector (vx, vy, vz)
        """
        self.velocity = new_velocity
        
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the node.
        
        Returns:
            Dictionary containing node state information
        """
        return {
            "node_id": self.node_id,
            "position": self.position,
            "velocity": self.velocity,
            "mass": self.mass,
            "metadata": self.metadata
        }
        
    def __repr__(self) -> str:
        """String representation of the node."""
        return f"Node(id={self.node_id}, pos={self.position}, vel={self.velocity})"
