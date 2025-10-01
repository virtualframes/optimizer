"""
Optimizer - Augmented optimizer for virtual node and game-engine authentication matrix simulation.

This package provides a 3D spacetime physics environment for simulating virtual nodes,
authentication matrices, and data point verification across a graph architecture.
"""

__version__ = "0.1.0"

from .node import Node
from .engine import Engine
from .auth_matrix import AuthMatrix

__all__ = ["Node", "Engine", "AuthMatrix"]
