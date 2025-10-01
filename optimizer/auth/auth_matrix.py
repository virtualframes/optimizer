"""Authentication matrix for managing node credential graphs."""

from typing import Dict, List, Set, Optional, Tuple
import networkx as nx
from dataclasses import dataclass, field
from optimizer.config.logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class Credential:
    """Represents a credential between nodes."""
    source_node: str
    target_node: str
    credential_type: str
    trust_level: float = 1.0
    metadata: Dict = field(default_factory=dict)


class AuthMatrix:
    """
    Authentication matrix for managing node credential relationships.
    
    Uses a directed graph to represent trust and authentication relationships
    between nodes in the virtual environment.
    """
    
    def __init__(self):
        """Initialize the authentication matrix."""
        self.graph = nx.DiGraph()
        self.credentials: Dict[Tuple[str, str], Credential] = {}
        
    def add_node(self, node_id: str, **attributes) -> None:
        """
        Add a node to the authentication matrix.
        
        Args:
            node_id: Unique identifier for the node
            **attributes: Additional node attributes
        """
        self.graph.add_node(node_id, **attributes)
        logger.info("Added node to auth matrix", node_id=node_id)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the authentication matrix."""
        if node_id in self.graph:
            # Remove all credentials involving this node
            edges_to_remove = [
                (s, t) for s, t in self.credentials.keys()
                if s == node_id or t == node_id
            ]
            for edge in edges_to_remove:
                del self.credentials[edge]
            
            self.graph.remove_node(node_id)
            logger.info("Removed node from auth matrix", node_id=node_id)
    
    def add_credential(
        self,
        source_node: str,
        target_node: str,
        credential_type: str,
        trust_level: float = 1.0,
        **metadata
    ) -> Credential:
        """
        Add a credential relationship between two nodes.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            credential_type: Type of credential (e.g., "auth", "trust", "verify")
            trust_level: Trust level (0.0 to 1.0)
            **metadata: Additional credential metadata
            
        Returns:
            Created Credential object
        """
        # Ensure nodes exist
        if source_node not in self.graph:
            self.add_node(source_node)
        if target_node not in self.graph:
            self.add_node(target_node)
        
        # Create credential
        credential = Credential(
            source_node=source_node,
            target_node=target_node,
            credential_type=credential_type,
            trust_level=trust_level,
            metadata=metadata
        )
        
        # Add edge to graph
        self.graph.add_edge(
            source_node,
            target_node,
            credential_type=credential_type,
            trust_level=trust_level
        )
        
        self.credentials[(source_node, target_node)] = credential
        logger.info(
            "Added credential",
            source=source_node,
            target=target_node,
            type=credential_type,
            trust=trust_level
        )
        
        return credential
    
    def remove_credential(self, source_node: str, target_node: str) -> None:
        """Remove a credential relationship."""
        if (source_node, target_node) in self.credentials:
            del self.credentials[(source_node, target_node)]
            if self.graph.has_edge(source_node, target_node):
                self.graph.remove_edge(source_node, target_node)
            logger.info("Removed credential", source=source_node, target=target_node)
    
    def get_credential(self, source_node: str, target_node: str) -> Optional[Credential]:
        """Get credential between two nodes."""
        return self.credentials.get((source_node, target_node))
    
    def has_credential(self, source_node: str, target_node: str) -> bool:
        """Check if a credential exists between two nodes."""
        return (source_node, target_node) in self.credentials
    
    def get_trusted_nodes(self, node_id: str, min_trust: float = 0.5) -> List[str]:
        """
        Get all nodes that the given node trusts above a threshold.
        
        Args:
            node_id: Node ID to check
            min_trust: Minimum trust level threshold
            
        Returns:
            List of trusted node IDs
        """
        trusted = []
        if node_id not in self.graph:
            return trusted
        
        for target in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, target)
            if edge_data and edge_data.get("trust_level", 0) >= min_trust:
                trusted.append(target)
        
        return trusted
    
    def get_trusting_nodes(self, node_id: str, min_trust: float = 0.5) -> List[str]:
        """
        Get all nodes that trust the given node above a threshold.
        
        Args:
            node_id: Node ID to check
            min_trust: Minimum trust level threshold
            
        Returns:
            List of trusting node IDs
        """
        trusting = []
        if node_id not in self.graph:
            return trusting
        
        for source in self.graph.predecessors(node_id):
            edge_data = self.graph.get_edge_data(source, node_id)
            if edge_data and edge_data.get("trust_level", 0) >= min_trust:
                trusting.append(source)
        
        return trusting
    
    def verify_trust_path(self, source_node: str, target_node: str) -> Optional[List[str]]:
        """
        Find a trust path between two nodes.
        
        Args:
            source_node: Starting node
            target_node: Ending node
            
        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        try:
            path = nx.shortest_path(self.graph, source_node, target_node)
            logger.info("Found trust path", source=source_node, target=target_node, path=path)
            return path
        except nx.NetworkXNoPath:
            logger.info("No trust path found", source=source_node, target=target_node)
            return None
    
    def get_trust_score(self, source_node: str, target_node: str) -> float:
        """
        Calculate cumulative trust score along the shortest path.
        
        Args:
            source_node: Starting node
            target_node: Ending node
            
        Returns:
            Trust score (0.0 to 1.0), 0.0 if no path exists
        """
        path = self.verify_trust_path(source_node, target_node)
        if not path or len(path) < 2:
            return 0.0
        
        # Calculate product of trust levels along path
        trust_score = 1.0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data:
                trust_score *= edge_data.get("trust_level", 0.0)
        
        return trust_score
    
    def get_node_count(self) -> int:
        """Get total number of nodes in the matrix."""
        return self.graph.number_of_nodes()
    
    def get_credential_count(self) -> int:
        """Get total number of credentials."""
        return len(self.credentials)
    
    def to_dict(self) -> Dict:
        """Export the authentication matrix to a dictionary."""
        return {
            "nodes": list(self.graph.nodes(data=True)),
            "credentials": [
                {
                    "source": cred.source_node,
                    "target": cred.target_node,
                    "type": cred.credential_type,
                    "trust_level": cred.trust_level,
                    "metadata": cred.metadata,
                }
                for cred in self.credentials.values()
            ],
        }
