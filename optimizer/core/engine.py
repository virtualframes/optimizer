import pybullet as p
import time

from optimizer.config.settings import settings
from optimizer.logging_config import get_logger

logger = get_logger(__name__)


class Engine:
    """
    An adapter for the PyBullet physics engine.
    """

    def __init__(self):
        """
        Initializes the physics engine.
        """
        self.physics_client = p.connect(p.DIRECT)
        p.setGravity(0, 0, settings.simulation.gravity)
        p.setTimeStep(settings.simulation.time_step)
        logger.info("PyBullet engine initialized.")

    def step_simulation(self):
        """
        Advances the simulation by one time step.
        """
        p.stepSimulation()

    def disconnect(self):
        """
        Disconnects from the physics engine.
        """
        p.disconnect()
        logger.info("PyBullet engine disconnected.")

    def add_node_to_simulation(self, node):
        """
        Adds a node to the simulation.
        For now, this is a placeholder. In a real scenario, this would create
        a physics body for the node.
        """
        logger.info(f"Adding node {node.node_id} to simulation at {node.position}")
        # Example of creating a simple sphere.
        # In a real application, you would store the body ID and associate it with the node.
        p.createCollisionShape(p.GEOM_SPHERE, radius=0.1)
        p.createMultiBody(
            baseMass=1,
            baseCollisionShapeIndex=-1,
            baseVisualShapeIndex=-1,
            basePosition=node.position,
        )
