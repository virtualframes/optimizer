# optimizer

Augmented optimizer for virtual node and game-engine authentication matrix simulation of all nodes and data points. AI architecture verifies across and graphs in a 3D spacetime-inspired physics engine environment.

## Overview

The `optimizer` package provides a comprehensive framework for simulating virtual nodes in a 3D physics environment with authentication and authorization capabilities. It combines:

- **Virtual Node Simulation**: Core `Node` class for representing simulation entities
- **Physics Engine Integration**: Interface to PyBullet for realistic 3D physics
- **Authentication Matrix**: Node-to-node credential verification system
- **CLI Interface**: Command-line tool for launching and configuring simulations

## Installation

### From Source

```bash
git clone https://github.com/virtualframes/optimizer.git
cd optimizer
pip install -e .
```

### For Development

```bash
pip install -e .[dev]
```

## Quick Start

### Using the CLI

Run a basic simulation with 5 nodes:

```bash
optimizer run --nodes 5 --duration 10.0
```

Run with GUI enabled:

```bash
optimizer run --nodes 10 --gui
```

Run with authentication enabled:

```bash
optimizer run --nodes 5 --auth
```

### Using the Python API

```python
from optimizer import Node, Engine, AuthMatrix, PermissionLevel

# Create nodes
node1 = Node(position=(0.0, 0.0, 5.0))
node2 = Node(position=(2.0, 0.0, 5.0))

# Set up authentication
auth = AuthMatrix()
token1 = auth.register_node(node1.node_id)
token2 = auth.register_node(node2.node_id)

# Verify nodes
auth.verify_node(node1.node_id, token1)
auth.verify_node(node2.node_id, token2)

# Grant permissions
auth.grant_permission(node1.node_id, node2.node_id, PermissionLevel.READ)

# Run physics simulation
with Engine(gui=False) as engine:
    engine.add_node(node1)
    engine.add_node(node2)
    
    for _ in range(100):
        engine.step()
    
    engine.sync_node(node1)
    engine.sync_node(node2)
    
    print(f"Node 1: {node1}")
    print(f"Node 2: {node2}")
```

## Architecture

### Core Components

1. **Node** (`optimizer.node.Node`)
   - Represents virtual entities in the simulation
   - Maintains position, velocity, mass, and metadata
   - Unique identifier for tracking and authentication

2. **Engine** (`optimizer.engine.Engine`)
   - Interface to PyBullet physics engine
   - Manages simulation state and time stepping
   - Synchronizes node states with physics calculations

3. **AuthMatrix** (`optimizer.auth_matrix.AuthMatrix`)
   - Token-based node authentication
   - Permission matrix for node-to-node access control
   - Support for multiple permission levels (NONE, READ, WRITE, ADMIN)

4. **CLI** (`optimizer.cli`)
   - Command-line interface for running simulations
   - Configurable parameters for nodes, duration, and features
   - Built-in help and version information

## Development

### Running Tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=optimizer --cov-report=term-missing
```

### Code Quality

The project uses:
- **pytest** for testing
- **black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Run all checks:

```bash
black optimizer/ tests/
isort optimizer/ tests/
flake8 optimizer/ tests/
```

## CI/CD

The project includes GitHub Actions workflows for:
- Running tests on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Testing on multiple platforms (Ubuntu, Windows)
- Code quality checks (formatting, linting)
- Coverage reporting

## Requirements

- Python >= 3.8
- PyBullet >= 3.2.0
- NumPy >= 1.21.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
