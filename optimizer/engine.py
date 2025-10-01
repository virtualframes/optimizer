"""
Engine interface to PyBullet for 3D physics simulation.

Provides an interface layer between the optimizer's virtual nodes and the
PyBullet physics engine for realistic 3D spacetime physics simulation.
"""

from typing import Dict, List, Optional, Tuple, Any
import pybullet as p
import pybullet_data

from .node import Node


class Engine:
    """
    Interface to PyBullet physics engine for node simulation.
    
    Manages the physics simulation environment, including gravity, time stepping,
    and collision detection for virtual nodes.
    """
    
    def __init__(
        self,
        gui: bool = False,
        gravity: Tuple[float, float, float] = (0.0, 0.0, -9.81),
        time_step: float = 1.0/240.0
    ):
        """
        Initialize the physics engine.
        
        Args:
            gui: Whether to show the PyBullet GUI (default: False for headless)
            gravity: Gravity vector (x, y, z) in m/s^2
            time_step: Physics simulation time step in seconds
        """
        self.gui = gui
        self.gravity = gravity
        self.time_step = time_step
        self.physics_client = None
        self.node_bodies: Dict[str, int] = {}  # Maps node_id to PyBullet body ID
        self.is_running = False
        
    def start(self) -> None:
        """Start the physics engine."""
        if self.is_running:
            return
            
        if self.gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)
            
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(*self.gravity)
        p.setTimeStep(self.time_step)
        self.is_running = True
        
    def stop(self) -> None:
        """Stop the physics engine and disconnect."""
        if self.is_running:
            p.disconnect()
            self.physics_client = None
            self.node_bodies.clear()
            self.is_running = False
            
    def add_node(self, node: Node, shape: str = "sphere", radius: float = 0.5) -> None:
        """
        Add a node to the physics simulation.
        
        Args:
            node: The Node object to add
            shape: Collision shape type (default: "sphere")
            radius: Size of the collision shape
        """
        if not self.is_running:
            raise RuntimeError("Engine not started. Call start() first.")
            
        # Create collision shape
        if shape == "sphere":
            collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
        else:
            raise ValueError(f"Unsupported shape: {shape}")
            
        # Create multi-body
        body_id = p.createMultiBody(
            baseMass=node.mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=node.position,
            baseOrientation=[0, 0, 0, 1]
        )
        
        # Set initial velocity
        p.resetBaseVelocity(body_id, linearVelocity=node.velocity)
        
        # Store mapping
        self.node_bodies[node.node_id] = body_id
        
    def step(self) -> None:
        """Advance the simulation by one time step."""
        if not self.is_running:
            raise RuntimeError("Engine not started. Call start() first.")
        p.stepSimulation()
        
    def sync_node(self, node: Node) -> None:
        """
        Synchronize node state from the physics engine.
        
        Updates the node's position and velocity from the physics simulation.
        
        Args:
            node: The Node object to synchronize
        """
        if not self.is_running:
            raise RuntimeError("Engine not started. Call start() first.")
            
        body_id = self.node_bodies.get(node.node_id)
        if body_id is None:
            raise ValueError(f"Node {node.node_id} not found in simulation")
            
        # Get position and orientation
        position, _ = p.getBasePositionAndOrientation(body_id)
        node.update_position(position)
        
        # Get velocity
        linear_vel, _ = p.getBaseVelocity(body_id)
        node.update_velocity(linear_vel)
        
    def get_node_state(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current physics state of a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Dictionary with position and velocity, or None if not found
        """
        if not self.is_running:
            return None
            
        body_id = self.node_bodies.get(node_id)
        if body_id is None:
            return None
            
        position, orientation = p.getBasePositionAndOrientation(body_id)
        linear_vel, angular_vel = p.getBaseVelocity(body_id)
        
        return {
            "position": position,
            "orientation": orientation,
            "linear_velocity": linear_vel,
            "angular_velocity": angular_vel
        }
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
