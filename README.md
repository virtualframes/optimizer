# Optimizer

Augmented optimizer for virtual node and game engine authentication matrix simulation of all nodes and data points. AI architecture verifies across and graphs nodes in a 3D spacetime-inspired physics engine environment.

## Features

- **Core Node System**: Virtual node representation with 3D position, velocity, and metadata
- **Physics Engine**: PyBullet adapter for realistic 3D physics simulation
- **Authentication Matrix**: Graph-based credential and trust management between nodes
- **REST API**: FastAPI-based API with ingest and query endpoints
- **CLI Tool**: Command-line interface for running simulations and managing nodes
- **Configuration**: YAML-based configuration with Pydantic models
- **Semantic Logging**: Structured logging with JSON output support
- **Docker Support**: Containerized deployment with Docker and docker-compose
- **CI/CD**: GitHub Actions workflow with pytest and flake8

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/virtualframes/optimizer.git
cd optimizer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build manually
docker build -t optimizer .
docker run -p 8000:8000 optimizer
```

## Quick Start

### CLI Usage

```bash
# Display system information
optimizer info

# Run a physics simulation with 10 nodes
optimizer simulate --nodes 10 --steps 100

# Run simulation with GUI
optimizer simulate --nodes 5 --steps 50 --gui

# Demonstrate authentication matrix
optimizer auth --nodes 5 --credentials 10

# Use custom config file
optimizer --config config.yml info
```

### API Usage

Start the API server:

```bash
# Using uvicorn directly
uvicorn optimizer.api.app:create_app --factory --host 0.0.0.0 --port 8000

# Or with docker-compose
docker-compose up
```

Access the API documentation at `http://localhost:8000/docs`

#### Example API Requests

```python
import requests

# Create a node
response = requests.post(
    "http://localhost:8000/api/v1/ingest/nodes",
    json={
        "position": [1.0, 2.0, 3.0],
        "velocity": [0.1, 0.2, 0.3],
        "mass": 2.5,
        "metadata": {"type": "sensor"}
    }
)
node = response.json()

# Get node details
response = requests.get(f"http://localhost:8000/api/v1/query/nodes/{node['id']}")

# List all nodes
response = requests.get("http://localhost:8000/api/v1/query/nodes")

# Get system statistics
response = requests.get("http://localhost:8000/api/v1/query/stats")
```

### Python Usage

```python
from optimizer.core import Node
from optimizer.engine import PyBulletEngine
from optimizer.auth import AuthMatrix
import numpy as np

# Create nodes
node1 = Node(position=[0, 0, 1], velocity=[1, 0, 0], mass=1.5)
node2 = Node(position=[5, 0, 1], velocity=[-1, 0, 0], mass=2.0)

# Run physics simulation
with PyBulletEngine(gui=False) as engine:
    engine.add_node(node1)
    engine.add_node(node2)
    
    for _ in range(100):
        engine.step_simulation()
    
    engine.update_node_from_simulation(node1)
    print(f"Node1 final position: {node1.position}")

# Use authentication matrix
auth_matrix = AuthMatrix()
auth_matrix.add_credential("node1", "node2", "trust", trust_level=0.9)
auth_matrix.add_credential("node2", "node3", "trust", trust_level=0.8)

trust_score = auth_matrix.get_trust_score("node1", "node3")
print(f"Trust score from node1 to node3: {trust_score}")
```

## Configuration

Create a `config.yml` file:

```yaml
app_name: optimizer
debug: false

simulation:
  time_step: 0.004166666666666667  # 1/240
  max_steps: 1000
  gravity: [0, 0, -9.81]
  use_gui: false

api:
  host: "0.0.0.0"
  port: 8000
  reload: false
  log_level: info

logging:
  level: INFO
  format: json  # json or console
  output_file: null  # or path to log file
```

Load configuration in your code:

```python
from optimizer.config import load_settings_from_yaml
from pathlib import Path

settings = load_settings_from_yaml(Path("config.yml"))
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov flake8

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=optimizer --cov-report=term

# Run linter
flake8 optimizer --max-line-length=127
```

### Project Structure

```
optimizer/
├── optimizer/              # Main package
│   ├── core/              # Core node implementation
│   ├── engine/            # Physics engine adapter
│   ├── auth/              # Authentication matrix
│   ├── api/               # FastAPI application
│   │   └── routes/        # API endpoints
│   ├── config/            # Configuration and logging
│   └── cli.py             # CLI entrypoint
├── tests/                 # Test suite
├── .github/
│   └── workflows/         # GitHub Actions CI
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
├── config.example.yml    # Example configuration
└── README.md             # This file
```

## API Endpoints

### Ingest Endpoints (`/api/v1/ingest`)

- `POST /nodes` - Create a new node
- `POST /nodes/batch` - Create multiple nodes
- `PUT /nodes/{node_id}` - Update a node
- `DELETE /nodes/{node_id}` - Delete a node
- `POST /nodes/{node_id}/connect/{target_id}` - Connect two nodes
- `DELETE /nodes/{node_id}/disconnect/{target_id}` - Disconnect two nodes

### Query Endpoints (`/api/v1/query`)

- `GET /nodes` - List all nodes (with pagination)
- `GET /nodes/{node_id}` - Get specific node
- `GET /nodes/{node_id}/connections` - Get node connections
- `GET /nodes/{node_id}/nearby?radius={radius}` - Get nearby nodes
- `GET /stats` - Get system statistics
- `GET /search` - Search nodes by criteria

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
