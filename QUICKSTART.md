# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## CLI Commands

### Display System Info
```bash
optimizer info
```

### Run Physics Simulation
```bash
# Basic simulation with 10 nodes
optimizer simulate --nodes 10 --steps 100

# With GUI
optimizer simulate --nodes 5 --steps 50 --gui
```

### Test Authentication Matrix
```bash
optimizer auth --nodes 5 --credentials 10
```

### Use Custom Config
```bash
# Copy example config
cp config.example.yml config.yml

# Edit config.yml as needed, then:
optimizer --config config.yml info
```

## API Usage

### Start the API Server
```bash
uvicorn optimizer.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker-compose up
```

### API Endpoints

Access interactive docs at: http://localhost:8000/docs

#### Create a Node
```bash
curl -X POST http://localhost:8000/api/v1/ingest/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "position": [1.0, 2.0, 3.0],
    "velocity": [0.1, 0.2, 0.3],
    "mass": 2.5,
    "metadata": {"type": "sensor"}
  }'
```

#### List Nodes
```bash
curl http://localhost:8000/api/v1/query/nodes
```

#### Get System Stats
```bash
curl http://localhost:8000/api/v1/query/stats
```

## Python Usage

```python
from optimizer.core import Node
from optimizer.engine import PyBulletEngine
from optimizer.auth import AuthMatrix
import numpy as np

# Create and simulate nodes
node1 = Node(position=[0, 0, 1], velocity=[1, 0, 0])
node2 = Node(position=[5, 0, 1], velocity=[-1, 0, 0])

with PyBulletEngine(gui=False) as engine:
    engine.add_node(node1)
    engine.add_node(node2)
    
    for _ in range(100):
        engine.step_simulation()
    
    engine.update_node_from_simulation(node1)
    print(f"Final position: {node1.position}")

# Use authentication matrix
auth_matrix = AuthMatrix()
auth_matrix.add_credential("node1", "node2", "trust", trust_level=0.9)
trust_score = auth_matrix.get_trust_score("node1", "node2")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=optimizer

# Lint code
flake8 optimizer --max-line-length=127
```

## Docker

```bash
# Build image
docker build -t optimizer .

# Run container
docker run -p 8000:8000 optimizer

# Use docker-compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Configuration

Create a `config.yml` file:

```yaml
app_name: optimizer
debug: false

simulation:
  time_step: 0.004166666666666667
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
  format: json
  output_file: null
```

## Environment Variables

Configuration can also be set via environment variables:

```bash
export DEBUG=true
export LOGGING__LEVEL=DEBUG
export LOGGING__FORMAT=console
export API__PORT=8080
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [API documentation](http://localhost:8000/docs) when the server is running
- Review test files in `tests/` for usage examples
- Explore the codebase starting with `optimizer/core/node.py`
