import hashlib
import json
from typing import Dict, Any, Tuple


class Node:
    """
    Represents a virtual simulation node with physical properties and a unique fingerprint.
    """

    def __init__(
        self,
        node_id: str,
        position: Tuple[float, float, float],
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        metadata: Dict[str, Any] = None,
    ):
        """
        Initializes a Node.

        Args:
            node_id (str): The unique identifier for the node.
            position (tuple): The (x, y, z) coordinates of the node.
            velocity (tuple): The (vx, vy, vz) velocity of the node.
            metadata (Dict[str, Any], optional): Additional data associated with the node.
        """
        self.node_id = node_id
        self.position = position
        self.velocity = velocity
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Node(node_id='{self.node_id}', position={self.position}, velocity={self.velocity})"

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the node.
        """
        return {
            "node_id": self.node_id,
            "position": self.position,
            "velocity": self.velocity,
            "metadata": self.metadata,
        }

    def get_fingerprint(self) -> str:
        """
        Computes a SHA-256 fingerprint of the node's state for auditing and lineage tracking.
        """
        # Sort keys to ensure consistent hash results
        node_json = json.dumps(self.to_dict(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(node_json).hexdigest()
