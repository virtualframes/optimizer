# Optimizer

Augmented optimizer for virtual node and game-engine authentication matrix simulation in a 3D spacetime physics environment.

This project provides a framework for simulating complex systems with a focus on:
- **Virtual Node Simulation**: Core `Node` class for representing virtual simulation nodes.
- **Physics Engine Integration**: An `Engine` adapter for PyBullet for 3D physics.
- **Authentication Matrix**: An `AuthMatrix` module for node-to-node credential checks.
- **REST API**: A FastAPI backend with `ingest` and `query` endpoints.
- **VM/Container Management**: API routes for deploying and managing containerized agents.
- **CLI**: A command-line interface for launching and configuring simulations.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)
- Build tools (gcc, g++, make) - required for compiling Python packages like pybullet

### Checking System Dependencies
Before installing, you can check if all required build dependencies are available:
```bash
# Using the shell script
./scripts/install_dependencies.sh

# Or using Python
python -m optimizer.utils.build_helper
```

If any dependencies are missing, the script will provide installation commands for your system.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/optimizer.git
   cd optimizer
   ```
2. Check and install system dependencies (if needed):
   ```bash
   # Check what's missing
   ./scripts/install_dependencies.sh

   # Install on Ubuntu/Debian
   sudo apt-get update && sudo apt-get install -y build-essential

   # Or on Red Hat/CentOS
   sudo yum groupinstall -y 'Development Tools'
   ```
3. Install Python dependencies:
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

## API Documentation

The Optimizer API provides several endpoint categories:

### Core Endpoints
- **Node Management**: `/ingest/node`, `/query/node/{node_id}`
- **Authentication Matrix**: `/ingest/credential`, `/query/auth_matrix`
- **Health Check**: `/`

### VM/Container Management (Jules Mission Ω)
New VM routes for managing containerized agents:
- **Deploy Agent**: `POST /api/v1/vm/deploy` - Clone repo, build image, run container
- **List Deployments**: `GET /api/v1/vm/list` - List active containers
- **Stop Deployment**: `POST /api/v1/vm/stop` - Stop/remove container
- **Health Check**: `GET /api/v1/vm/health/{container_name}` - Check container health

See [docs/api/vm-routes.md](docs/api/vm-routes.md) for detailed API documentation.

**Interactive API Documentation:**
When the API server is running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Build Dependencies

This project includes utilities to automatically detect missing build dependencies and suggest installation commands.

### Automated Dependency Checking
The build process automatically checks for required system dependencies (gcc, g++, make) and provides helpful error messages with installation instructions if any are missing.

### Using the Dependency Checker

**Shell Script:**
```bash
./scripts/install_dependencies.sh
```

**Python Module:**
```python
from optimizer.utils.build_helper import check_build_dependencies, DependencyChecker

# Simple check
if not check_build_dependencies():
    print("Some dependencies are missing")

# Detailed checking
checker = DependencyChecker()
all_present, message = checker.verify_and_suggest()
if not all_present:
    print(message)
```

### Analyzing Build Errors
The build helper can also analyze error output to detect missing dependencies:
```python
from optimizer.utils.build_helper import analyze_build_error

error_output = "error: command 'gcc' failed with exit status 1"
suggestion = analyze_build_error(error_output)
if suggestion:
    print(suggestion)
```

## CI/CD
This project uses GitHub Actions for continuous integration. The workflow runs `pytest` and `flake8` on every push and pull request.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Code of Conduct
- Development workflow (GitHub Flow)
- Commit message conventions (Conventional Commits)
- Code style (Black + Ruff)
- Testing requirements
- Pull request process

Quick start:
```bash
# Fork and clone the repo
git checkout -b feat/my-feature

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Make changes, test, and commit
black .
ruff check .
pytest
git commit -m "feat: my new feature"
```

## License

MIT License - see LICENSE file for details.