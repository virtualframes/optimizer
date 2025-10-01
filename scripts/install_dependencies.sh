#!/bin/bash
# Script to detect missing system dependencies and suggest installation commands
# This script focuses on build dependencies required for Python packages like pybullet

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flag to track if any dependencies are missing
MISSING_DEPS=0

# Detect package manager
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt-get"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v apk &> /dev/null; then
        echo "apk"
    else
        echo "unknown"
    fi
}

# Check if a command exists
check_command() {
    local cmd=$1
    local package=$2
    local pkg_manager=$3
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $cmd is NOT installed"
        MISSING_DEPS=1
        
        # Suggest installation command based on package manager
        case "$pkg_manager" in
            apt-get)
                echo -e "${YELLOW}  → Install with: sudo apt-get update && sudo apt-get install -y $package${NC}"
                ;;
            yum)
                echo -e "${YELLOW}  → Install with: sudo yum install -y $package${NC}"
                ;;
            apk)
                echo -e "${YELLOW}  → Install with: apk add --no-cache $package${NC}"
                ;;
            *)
                echo -e "${YELLOW}  → Please install $package using your system's package manager${NC}"
                ;;
        esac
        return 1
    fi
}

# Main function
main() {
    echo "======================================================"
    echo "   Build Dependency Checker for Optimizer"
    echo "======================================================"
    echo ""
    
    # Detect package manager
    PKG_MANAGER=$(detect_package_manager)
    echo "Detected package manager: $PKG_MANAGER"
    echo ""
    
    echo "Checking for required build dependencies..."
    echo ""
    
    # Check for essential build tools
    check_command "gcc" "gcc" "$PKG_MANAGER"
    check_command "g++" "g++" "$PKG_MANAGER"
    check_command "make" "make" "$PKG_MANAGER"
    
    echo ""
    
    # Check for commonly needed build dependencies
    echo "Checking for additional build dependencies..."
    echo ""
    
    # For Debian/Ubuntu systems, suggest build-essential
    if [ "$PKG_MANAGER" = "apt-get" ]; then
        # Check if build-essential is installed
        if ! dpkg -l build-essential &> /dev/null; then
            echo -e "${YELLOW}ℹ${NC} build-essential package not found"
            echo -e "${YELLOW}  → Install all build tools with: sudo apt-get update && sudo apt-get install -y build-essential${NC}"
            MISSING_DEPS=1
        else
            echo -e "${GREEN}✓${NC} build-essential is installed"
        fi
    fi
    
    echo ""
    echo "======================================================"
    
    if [ $MISSING_DEPS -eq 1 ]; then
        echo -e "${RED}Some dependencies are missing!${NC}"
        echo ""
        echo "To install all dependencies at once:"
        
        case "$PKG_MANAGER" in
            apt-get)
                echo -e "${YELLOW}  sudo apt-get update && sudo apt-get install -y build-essential${NC}"
                ;;
            yum)
                echo -e "${YELLOW}  sudo yum groupinstall -y 'Development Tools'${NC}"
                ;;
            apk)
                echo -e "${YELLOW}  apk add --no-cache build-base${NC}"
                ;;
            *)
                echo -e "${YELLOW}  Please install build tools using your system's package manager${NC}"
                ;;
        esac
        
        echo ""
        echo "After installing dependencies, run:"
        echo "  pip install -r requirements.txt"
        echo "======================================================"
        exit 1
    else
        echo -e "${GREEN}All required dependencies are installed!${NC}"
        echo "======================================================"
        exit 0
    fi
}

# Run main function
main
