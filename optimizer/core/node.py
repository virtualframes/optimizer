from typing import Dict, Any


class Node:
    """
    Represents a virtual simulation node.
    """

    def __init__(self, node_id: str, position: tuple, metadata: Dict[str, Any] = None):
        """
        Initializes a Node.

        Args:
            node_id (str): The unique identifier for the node.
            position (tuple): The (x, y, z) coordinates of the node.
            metadata (Dict[str, Any], optional): Additional data associated with the node. Defaults to None.
        """
        self.node_id = node_id
        self.position = position
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Node(node_id='{self.node_id}', position={self.position})"

    def to_dict(self):
        """
        Returns a dictionary representation of the node.
        """
        return {
            "node_id": self.node_id,
            "position": self.position,
            "metadata": self.metadata,
        }
