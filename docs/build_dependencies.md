# Build Dependency Detection

## Overview

This feature automatically detects when a build fails due to missing system dependencies and suggests installation commands for the required packages. It focuses on common missing packages like `g++`, `gcc`, and `make` that are required for compiling Python packages like pybullet.

## Components

### 1. Shell Script (`scripts/install_dependencies.sh`)

A standalone bash script that:
- Detects the system's package manager (apt-get, yum, or apk)
- Checks for required build tools (gcc, g++, make)
- Provides colored, user-friendly output
- Suggests appropriate installation commands for the detected package manager
- Returns exit code 0 if all dependencies are present, 1 otherwise

**Usage:**
```bash
./scripts/install_dependencies.sh
```

**Output Example:**
```
======================================================
   Build Dependency Checker for Optimizer
======================================================

Detected package manager: apt-get

Checking for required build dependencies...

✓ gcc is installed
✓ g++ is installed
✓ make is installed

Checking for additional build dependencies...

✓ build-essential is installed

======================================================
All required dependencies are installed!
======================================================
```

### 2. Python Module (`optimizer/utils/build_helper.py`)

A comprehensive Python module that provides:

#### Classes

**`DependencyChecker`**
- Main class for dependency checking
- Methods:
  - `check_command(command)` - Check if a specific command exists
  - `check_all_build_tools()` - Check all essential build tools
  - `get_installation_command()` - Get the appropriate installation command
  - `get_detailed_suggestions()` - Get detailed per-dependency suggestions
  - `verify_and_suggest(raise_error)` - Complete verification with error handling
  - `print_status()` - Print human-readable status

**`BuildDependencyError`**
- Custom exception for missing dependencies

#### Functions

**`check_build_dependencies(raise_error=False)`**
- Convenience function for quick checks
- Returns boolean indicating if all dependencies are present

**`analyze_build_error(error_output)`**
- Analyzes error output from failed builds
- Detects common patterns indicating missing dependencies
- Returns helpful suggestions if missing dependencies are detected

### 3. Docker Integration

Both Dockerfiles have been updated to:
- Copy the dependency checking script
- Explicitly install build-essential (or equivalent)
- Include comments explaining why these tools are needed

**Dockerfile:**
```dockerfile
# Copy dependency checker script
COPY scripts/install_dependencies.sh /tmp/install_dependencies.sh
RUN chmod +x /tmp/install_dependencies.sh

# Install build dependencies required for pybullet and other packages
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
```

### 4. CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) now includes:
- A dependency check step that runs before installation
- Verifies all required tools are present in the CI environment

```yaml
- name: Check system dependencies
  run: |
    chmod +x scripts/install_dependencies.sh
    ./scripts/install_dependencies.sh
```

## Usage Examples

### Command Line

**Check dependencies with shell script:**
```bash
./scripts/install_dependencies.sh
```

**Check dependencies with Python:**
```bash
python -m optimizer.utils.build_helper
```

### Programmatic Usage

**Simple check:**
```python
from optimizer.utils.build_helper import check_build_dependencies

if not check_build_dependencies():
    print("Missing dependencies detected!")
```

**Detailed checking:**
```python
from optimizer.utils.build_helper import DependencyChecker

checker = DependencyChecker()
all_present, message = checker.verify_and_suggest()

if not all_present:
    print(message)
```

**Analyze build errors:**
```python
from optimizer.utils.build_helper import analyze_build_error

error_output = "error: command 'gcc' failed with exit status 1"
suggestion = analyze_build_error(error_output)

if suggestion:
    print(suggestion)
```

### In Build Scripts

**Pre-installation check:**
```python
from optimizer.utils.build_helper import check_build_dependencies

# Check before attempting pip install
if not check_build_dependencies():
    raise RuntimeError("Required build dependencies are missing")

# Proceed with installation
import subprocess
subprocess.run(["pip", "install", "-r", "requirements.txt"])
```

**Error handling:**
```python
from optimizer.utils.build_helper import BuildDependencyError, DependencyChecker

try:
    checker = DependencyChecker()
    checker.verify_and_suggest(raise_error=True)
except BuildDependencyError as e:
    print(f"Build dependency error: {e}")
    sys.exit(1)
```

## Supported Platforms

The feature supports multiple package managers:

| Platform | Package Manager | Installation Command |
|----------|----------------|---------------------|
| Ubuntu/Debian | apt-get | `sudo apt-get install -y build-essential` |
| Red Hat/CentOS | yum | `sudo yum groupinstall -y 'Development Tools'` |
| Alpine | apk | `apk add --no-cache build-base` |

## Testing

The feature includes comprehensive tests (`tests/test_build_helper.py`) covering:
- Dependency checker initialization
- Command existence detection
- Individual and all-tools checking
- Installation command generation
- Error message formatting
- Build error analysis
- Multiple package managers

**Run tests:**
```bash
pytest tests/test_build_helper.py -v
```

## Error Messages

When dependencies are missing, the user receives clear, actionable error messages:

```
============================================================
ERROR: Missing required build dependencies!
============================================================

The following build tools are required but not found:
  ✗ gcc
  ✗ g++

These tools are needed to compile Python packages like pybullet.

To install all required dependencies, run:
  sudo apt-get update && sudo apt-get install -y build-essential

After installing dependencies, try again with:
  pip install -r requirements.txt

============================================================
```

## Integration Points

1. **Pre-build checks** - Run before attempting to install Python packages
2. **CI/CD pipelines** - Verify environment has required tools
3. **Docker builds** - Explicit installation with clear documentation
4. **Error analysis** - Post-mortem analysis of failed builds
5. **Setup scripts** - Automated environment verification

## Benefits

1. **Faster debugging** - Immediately identifies missing dependencies
2. **Clear instructions** - Provides exact commands to fix issues
3. **Multi-platform** - Works across different Linux distributions
4. **Developer-friendly** - Both CLI and programmatic interfaces
5. **CI/CD ready** - Integrates seamlessly with automation pipelines
6. **Well-tested** - Comprehensive test coverage ensures reliability

## Future Enhancements

Potential improvements for future versions:
- Support for additional package managers (brew, pacman, etc.)
- Detection of specific library dependencies (OpenGL, X11, etc.)
- Integration with setuptools for automatic pre-install checks
- Cache results to avoid repeated checks
- Network-based dependency information updates
