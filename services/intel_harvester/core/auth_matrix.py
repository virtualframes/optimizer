import networkx as nx

from intel_harvester.logging_config import get_logger

logger = get_logger(__name__)

class AuthMatrix:
    """
    Manages node-to-node credential checks using a graph.
    """
    def __init__(self):
        """
        Initializes the authentication matrix.
        """
        self.graph = nx.DiGraph()
        logger.info("Authentication matrix initialized.")

    def add_credential(self, source_node_id: str, target_node_id: str):
        """
        Adds a credential from a source node to a target node.

        Args:
            source_node_id (str): The ID of the source node.
            target_node_id (str): The ID of the target node.
        """
        self.graph.add_edge(source_node_id, target_node_id)
        logger.info(f"Added credential from {source_node_id} to {target_node_id}")

    def has_credential(self, source_node_id: str, target_node_id: str) -> bool:
        """
        Checks if a credential exists from a source node to a target node.

        Args:
            source_node_id (str): The ID of the source node.
            target_node_id (str): The ID of the target node.

        Returns:
            bool: True if a credential exists, False otherwise.
        """
        return self.graph.has_edge(source_node_id, target_node_id)

    def to_dict(self):
        """
        Returns a dictionary representation of the authentication graph.
        """
        # nx.to_dict_of_lists includes nodes that are only targets, with empty lists.
        # The test expects a dictionary of only nodes that are sources.
        adj_dict = {}
        for u, nbrs in self.graph.adjacency():
            if nbrs:
                adj_dict[u] = list(nbrs.keys())
        return adj_dict