# Examples

This directory contains example scripts demonstrating various features of the Optimizer project.

## Build Dependency Checker

**File:** `check_build_dependencies.py`

Demonstrates how to use the build dependency checker to detect missing system dependencies before installing Python packages.

### Running the Example

```bash
# From the repository root
PYTHONPATH=. python examples/check_build_dependencies.py
```

### What It Shows

1. **Simple Check**: Quick verification that all build tools are installed
2. **Detailed Checking**: Individual tool verification with package manager detection
3. **Error Analysis**: Analyzing build error messages to detect missing dependencies
4. **Complete Verification**: Using the comprehensive verification method

### Expected Output

When all dependencies are installed, you'll see:
- ✓ All build dependencies are installed
- Package manager detection (apt-get, yum, or apk)
- Status of each build tool (gcc, g++, make, python)

### Use Cases

This example is useful for:
- Pre-installation dependency verification
- CI/CD pipeline health checks
- Troubleshooting build failures
- Automated setup scripts
