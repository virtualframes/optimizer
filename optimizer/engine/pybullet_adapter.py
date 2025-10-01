"""PyBullet adapter for 3D physics simulation."""

from typing import Dict, Optional, Tuple
import pybullet as p
import pybullet_data
import numpy as np
from optimizer.core.node import Node
from optimizer.config.logging_config import get_logger


logger = get_logger(__name__)


class PyBulletEngine:
    """
    Adapter class for PyBullet physics engine.
    
    Manages 3D physics simulation for virtual nodes in a spacetime environment.
    """
    
    def __init__(self, gui: bool = False, gravity: Tuple[float, float, float] = (0, 0, -9.81)):
        """
        Initialize PyBullet physics engine.
        
        Args:
            gui: Whether to use GUI mode (True) or headless (False)
            gravity: Gravity vector (x, y, z)
        """
        self.gui = gui
        self.gravity = gravity
        self.client_id: Optional[int] = None
        self.node_bodies: Dict[str, int] = {}  # Map node IDs to PyBullet body IDs
        self.is_connected = False
        
    def connect(self) -> None:
        """Connect to PyBullet physics server."""
        if self.is_connected:
            logger.warning("Already connected to PyBullet")
            return
            
        if self.gui:
            self.client_id = p.connect(p.GUI)
        else:
            self.client_id = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(*self.gravity)
        self.is_connected = True
        logger.info("Connected to PyBullet", gui=self.gui, gravity=self.gravity)
    
    def disconnect(self) -> None:
        """Disconnect from PyBullet physics server."""
        if self.is_connected:
            p.disconnect()
            self.is_connected = False
            self.node_bodies.clear()
            logger.info("Disconnected from PyBullet")
    
    def add_node(self, node: Node, shape: str = "sphere", radius: float = 0.5) -> int:
        """
        Add a node to the physics simulation.
        
        Args:
            node: Node to add
            shape: Shape type ("sphere", "box", "cylinder")
            radius: Size parameter for the shape
            
        Returns:
            PyBullet body ID
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to PyBullet. Call connect() first.")
        
        # Create collision shape
        if shape == "sphere":
            collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
        elif shape == "box":
            collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[radius] * 3)
        elif shape == "cylinder":
            collision_shape = p.createCollisionShape(p.GEOM_CYLINDER, radius=radius, height=radius * 2)
        else:
            raise ValueError(f"Unknown shape: {shape}")
        
        # Create visual shape with random color
        visual_shape = p.createVisualShape(
            p.GEOM_SPHERE if shape == "sphere" else p.GEOM_BOX,
            radius=radius if shape == "sphere" else None,
            halfExtents=[radius] * 3 if shape == "box" else None,
            rgbaColor=np.random.rand(4).tolist()
        )
        
        # Create multi-body
        body_id = p.createMultiBody(
            baseMass=node.mass,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=node.position.tolist(),
            baseOrientation=[0, 0, 0, 1]
        )
        
        # Set initial velocity
        p.resetBaseVelocity(body_id, linearVelocity=node.velocity.tolist())
        
        self.node_bodies[node.id] = body_id
        logger.info("Added node to simulation", node_id=node.id, body_id=body_id)
        
        return body_id
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the simulation."""
        if node_id in self.node_bodies:
            body_id = self.node_bodies[node_id]
            p.removeBody(body_id)
            del self.node_bodies[node_id]
            logger.info("Removed node from simulation", node_id=node_id)
    
    def step_simulation(self, time_step: float = 1.0 / 240.0) -> None:
        """Advance the simulation by one time step."""
        if not self.is_connected:
            raise RuntimeError("Not connected to PyBullet. Call connect() first.")
        p.stepSimulation()
    
    def update_node_from_simulation(self, node: Node) -> None:
        """Update a node's state from the physics simulation."""
        if node.id not in self.node_bodies:
            logger.warning("Node not in simulation", node_id=node.id)
            return
        
        body_id = self.node_bodies[node.id]
        position, orientation = p.getBasePositionAndOrientation(body_id)
        velocity, angular_velocity = p.getBaseVelocity(body_id)
        
        node.update_position(np.array(position))
        node.update_velocity(np.array(velocity))
    
    def get_all_positions(self) -> Dict[str, np.ndarray]:
        """Get positions of all nodes in simulation."""
        positions = {}
        for node_id, body_id in self.node_bodies.items():
            position, _ = p.getBasePositionAndOrientation(body_id)
            positions[node_id] = np.array(position)
        return positions
    
    def reset_simulation(self) -> None:
        """Reset the simulation state."""
        if self.is_connected:
            p.resetSimulation()
            p.setGravity(*self.gravity)
            self.node_bodies.clear()
            logger.info("Reset simulation")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
