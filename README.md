# Optimizer

Augmented optimizer for virtual node and game-engine authentication matrix simulation in a 3D spacetime physics environment.

This project provides a framework for simulating complex systems with a focus on:
- **Virtual Node Simulation**: Core `Node` class for representing virtual simulation nodes.
- **Physics Engine Integration**: An `Engine` adapter for PyBullet for 3D physics.
- **Authentication Matrix**: An `AuthMatrix` module for node-to-node credential checks.
- **REST API**: A FastAPI backend with `ingest` and `query` endpoints.
- **CLI**: A command-line interface for launching and configuring simulations.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/optimizer.git
   cd optimizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
- **Via CLI**:
  ```bash
  optimizer --config-path config.yml
  ```
- **Via Docker**:
  ```bash
  docker-compose up --build
  ```

## Testing
To run the test suite:
```bash
pytest
```

## CI/CD
This project uses GitHub Actions for continuous integration. The workflow runs `pytest` and `flake8` on every push and pull request.