"""Ingest endpoints for creating and updating nodes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from optimizer.core import Node
from optimizer.config.logging_config import get_logger
import numpy as np


logger = get_logger(__name__)
router = APIRouter()

# In-memory storage (would be replaced with database in production)
nodes_storage: Dict[str, Node] = {}


class NodeCreate(BaseModel):
    """Request model for creating a node."""
    position: List[float] = Field(..., min_length=3, max_length=3, description="3D position [x, y, z]")
    velocity: Optional[List[float]] = Field(default=[0, 0, 0], min_length=3, max_length=3, description="3D velocity")
    mass: float = Field(default=1.0, gt=0, description="Node mass")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    connections: List[str] = Field(default_factory=list, description="Connected node IDs")


class NodeUpdate(BaseModel):
    """Request model for updating a node."""
    position: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    velocity: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    mass: Optional[float] = Field(None, gt=0)
    metadata: Optional[Dict[str, Any]] = None
    connections: Optional[List[str]] = None


class NodeResponse(BaseModel):
    """Response model for node data."""
    id: str
    position: List[float]
    velocity: List[float]
    mass: float
    metadata: Dict[str, Any]
    connections: List[str]


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(node_data: NodeCreate):
    """
    Create a new node in the system.
    
    Args:
        node_data: Node creation data
        
    Returns:
        Created node data
    """
    node = Node(
        position=np.array(node_data.position),
        velocity=np.array(node_data.velocity),
        mass=node_data.mass,
        metadata=node_data.metadata,
        connections=node_data.connections,
    )
    
    nodes_storage[node.id] = node
    logger.info("Created node", node_id=node.id)
    
    return NodeResponse(**node.to_dict())


@router.post("/nodes/batch", response_model=List[NodeResponse], status_code=status.HTTP_201_CREATED)
async def create_nodes_batch(nodes_data: List[NodeCreate]):
    """
    Create multiple nodes in a batch.
    
    Args:
        nodes_data: List of node creation data
        
    Returns:
        List of created node data
    """
    created_nodes = []
    
    for node_data in nodes_data:
        node = Node(
            position=np.array(node_data.position),
            velocity=np.array(node_data.velocity),
            mass=node_data.mass,
            metadata=node_data.metadata,
            connections=node_data.connections,
        )
        nodes_storage[node.id] = node
        created_nodes.append(NodeResponse(**node.to_dict()))
    
    logger.info("Created nodes batch", count=len(created_nodes))
    
    return created_nodes


@router.put("/nodes/{node_id}", response_model=NodeResponse)
async def update_node(node_id: str, node_update: NodeUpdate):
    """
    Update an existing node.
    
    Args:
        node_id: Node ID to update
        node_update: Node update data
        
    Returns:
        Updated node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = nodes_storage[node_id]
    
    if node_update.position is not None:
        node.update_position(np.array(node_update.position))
    if node_update.velocity is not None:
        node.update_velocity(np.array(node_update.velocity))
    if node_update.mass is not None:
        node.mass = node_update.mass
    if node_update.metadata is not None:
        node.metadata.update(node_update.metadata)
    if node_update.connections is not None:
        node.connections = node_update.connections
    
    logger.info("Updated node", node_id=node_id)
    
    return NodeResponse(**node.to_dict())


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(node_id: str):
    """
    Delete a node.
    
    Args:
        node_id: Node ID to delete
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    del nodes_storage[node_id]
    logger.info("Deleted node", node_id=node_id)
    
    return None


@router.post("/nodes/{node_id}/connect/{target_id}", response_model=NodeResponse)
async def connect_nodes(node_id: str, target_id: str):
    """
    Create a connection between two nodes.
    
    Args:
        node_id: Source node ID
        target_id: Target node ID
        
    Returns:
        Updated source node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    if target_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {target_id} not found")
    
    node = nodes_storage[node_id]
    node.connect(target_id)
    
    logger.info("Connected nodes", source=node_id, target=target_id)
    
    return NodeResponse(**node.to_dict())


@router.delete("/nodes/{node_id}/disconnect/{target_id}", response_model=NodeResponse)
async def disconnect_nodes(node_id: str, target_id: str):
    """
    Remove a connection between two nodes.
    
    Args:
        node_id: Source node ID
        target_id: Target node ID
        
    Returns:
        Updated source node data
    """
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = nodes_storage[node_id]
    node.disconnect(target_id)
    
    logger.info("Disconnected nodes", source=node_id, target=target_id)
    
    return NodeResponse(**node.to_dict())
