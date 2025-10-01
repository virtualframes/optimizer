"""Query endpoints for retrieving node and system data."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from optimizer.api.routes.ingest import nodes_storage, NodeResponse
from optimizer.config.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter()


class SystemStats(BaseModel):
    """System statistics model."""
    total_nodes: int
    total_connections: int
    average_mass: float
    average_velocity_magnitude: float


@router.get("/nodes", response_model=List[NodeResponse])
async def list_nodes(
    skip: int = Query(0, ge=0, description="Number of nodes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes to return"),
):
    """
    List all nodes with pagination.
    
    Args:
        skip: Number of nodes to skip
        limit: Maximum number of nodes to return
        
    Returns:
        List of node data
    """
    nodes = list(nodes_storage.values())[skip:skip + limit]
    logger.info("Listed nodes", count=len(nodes), skip=skip, limit=limit)
    
    return [NodeResponse(**node.to_dict()) for node in nodes]


@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    """
    Get a specific node by ID.
    
    Args:
        node_id: Node ID to retrieve
        
    Returns:
        Node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = nodes_storage[node_id]
    logger.info("Retrieved node", node_id=node_id)
    
    return NodeResponse(**node.to_dict())


@router.get("/nodes/{node_id}/connections", response_model=List[NodeResponse])
async def get_node_connections(node_id: str):
    """
    Get all nodes connected to a specific node.
    
    Args:
        node_id: Node ID to get connections for
        
    Returns:
        List of connected node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = nodes_storage[node_id]
    connected_nodes = []
    
    for conn_id in node.connections:
        if conn_id in nodes_storage:
            connected_nodes.append(NodeResponse(**nodes_storage[conn_id].to_dict()))
    
    logger.info("Retrieved node connections", node_id=node_id, count=len(connected_nodes))
    
    return connected_nodes


@router.get("/nodes/{node_id}/nearby", response_model=List[NodeResponse])
async def get_nearby_nodes(
    node_id: str,
    radius: float = Query(..., gt=0, description="Search radius"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of nearby nodes"),
):
    """
    Get nodes within a certain distance of the specified node.
    
    Args:
        node_id: Reference node ID
        radius: Search radius
        limit: Maximum number of nodes to return
        
    Returns:
        List of nearby node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    reference_node = nodes_storage[node_id]
    nearby_nodes = []
    
    for nid, node in nodes_storage.items():
        if nid != node_id:
            distance = reference_node.distance_to(node)
            if distance <= radius:
                nearby_nodes.append((distance, node))
    
    # Sort by distance and limit results
    nearby_nodes.sort(key=lambda x: x[0])
    nearby_nodes = nearby_nodes[:limit]
    
    logger.info(
        "Retrieved nearby nodes",
        node_id=node_id,
        radius=radius,
        count=len(nearby_nodes)
    )
    
    return [NodeResponse(**node.to_dict()) for _, node in nearby_nodes]


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get system-wide statistics.
    
    Returns:
        System statistics
    """
    import numpy as np
    
    if not nodes_storage:
        return SystemStats(
            total_nodes=0,
            total_connections=0,
            average_mass=0.0,
            average_velocity_magnitude=0.0,
        )
    
    total_nodes = len(nodes_storage)
    total_connections = sum(len(node.connections) for node in nodes_storage.values())
    average_mass = np.mean([node.mass for node in nodes_storage.values()])
    
    velocities = [node.velocity for node in nodes_storage.values()]
    velocity_magnitudes = [np.linalg.norm(v) for v in velocities]
    average_velocity_magnitude = np.mean(velocity_magnitudes) if velocity_magnitudes else 0.0
    
    logger.info("Retrieved system stats", total_nodes=total_nodes)
    
    return SystemStats(
        total_nodes=total_nodes,
        total_connections=total_connections,
        average_mass=float(average_mass),
        average_velocity_magnitude=float(average_velocity_magnitude),
    )


@router.get("/search", response_model=List[NodeResponse])
async def search_nodes(
    min_mass: Optional[float] = Query(None, description="Minimum mass filter"),
    max_mass: Optional[float] = Query(None, description="Maximum mass filter"),
    metadata_key: Optional[str] = Query(None, description="Metadata key to filter by"),
    metadata_value: Optional[str] = Query(None, description="Metadata value to filter by"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes to return"),
):
    """
    Search for nodes based on various criteria.
    
    Args:
        min_mass: Minimum mass filter
        max_mass: Maximum mass filter
        metadata_key: Metadata key to filter by
        metadata_value: Metadata value to filter by
        limit: Maximum number of nodes to return
        
    Returns:
        List of matching node data
    """
    filtered_nodes = []
    
    for node in nodes_storage.values():
        # Mass filters
        if min_mass is not None and node.mass < min_mass:
            continue
        if max_mass is not None and node.mass > max_mass:
            continue
        
        # Metadata filters
        if metadata_key is not None and metadata_value is not None:
            if node.metadata.get(metadata_key) != metadata_value:
                continue
        
        filtered_nodes.append(node)
        
        if len(filtered_nodes) >= limit:
            break
    
    logger.info("Searched nodes", count=len(filtered_nodes))
    
    return [NodeResponse(**node.to_dict()) for node in filtered_nodes]
