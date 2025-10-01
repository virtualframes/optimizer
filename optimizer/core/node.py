"""Core Node class for simulating VR nodes."""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from uuid import uuid4
import numpy as np


@dataclass
class Node:
    """
    Represents a virtual node in 3D spacetime with physics properties.
    
    Attributes:
        id: Unique identifier for the node
        position: 3D position vector [x, y, z]
        velocity: 3D velocity vector
        mass: Mass of the node
        metadata: Additional metadata for the node
        connections: List of connected node IDs
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    mass: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Ensure position and velocity are numpy arrays."""
        if not isinstance(self.position, np.ndarray):
            self.position = np.array(self.position)
        if not isinstance(self.velocity, np.ndarray):
            self.velocity = np.array(self.velocity)
    
    def connect(self, node_id: str) -> None:
        """Add a connection to another node."""
        if node_id not in self.connections:
            self.connections.append(node_id)
    
    def disconnect(self, node_id: str) -> None:
        """Remove a connection to another node."""
        if node_id in self.connections:
            self.connections.remove(node_id)
    
    def update_position(self, new_position: np.ndarray) -> None:
        """Update the node's position."""
        self.position = np.array(new_position)
    
    def update_velocity(self, new_velocity: np.ndarray) -> None:
        """Update the node's velocity."""
        self.velocity = np.array(new_velocity)
    
    def distance_to(self, other: "Node") -> float:
        """Calculate Euclidean distance to another node."""
        return float(np.linalg.norm(self.position - other.position))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist(),
            "mass": self.mass,
            "metadata": self.metadata,
            "connections": self.connections,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Create a Node from dictionary representation."""
        return cls(
            id=data.get("id", str(uuid4())),
            position=np.array(data.get("position", [0, 0, 0])),
            velocity=np.array(data.get("velocity", [0, 0, 0])),
            mass=data.get("mass", 1.0),
            metadata=data.get("metadata", {}),
            connections=data.get("connections", []),
        )
