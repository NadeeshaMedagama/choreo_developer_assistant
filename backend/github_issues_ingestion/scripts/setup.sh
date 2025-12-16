#!/bin/bash
# Installation and Setup Script for GitHub Issues Ingestion System

set -e

echo "========================================================================"
echo "GitHub Issues Ingestion System - Setup"
echo "========================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo -e "${RED}✗ Error: .env file not found in backend directory${NC}"
    echo "Please create a .env file with required configuration."
    echo "See README.md for required environment variables."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found .env file"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"
echo ""

# Check if required packages are installed
echo "Checking required packages..."

check_package() {
    package=$1
    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package is installed"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $package is not installed"
        return 1
    fi
}

missing_packages=()

if ! check_package "requests"; then
    missing_packages+=("requests")
fi

if ! check_package "openai"; then
    missing_packages+=("openai")
fi

if ! check_package "pinecone"; then
    missing_packages+=("pinecone-client")
fi

if ! check_package "dotenv"; then
    missing_packages+=("python-dotenv")
fi

echo ""

# Install missing packages if any
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing packages...${NC}"
    pip install "${missing_packages[@]}"
    echo ""
fi

# Verify installation
echo "========================================================================"
echo "Verifying Installation"
echo "========================================================================"
echo ""

echo "Running configuration test..."
if python -c "import sys; sys.path.insert(0, '..'); from github_issues_ingestion.config import Settings; s = Settings.from_env(); print('✓ Configuration loaded successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Configuration is valid"
else
    echo -e "${RED}✗${NC} Configuration test failed"
    echo "Please check your .env file has all required variables."
    exit 1
fi

echo ""
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Run tests:"
echo "   python test_system.py"
echo ""
echo "2. Try examples:"
echo "   python examples.py"
echo ""
echo "3. Ingest your first repository:"
echo "   python main.py wso2/choreo --max-issues 5"
echo ""
echo "4. Query the vector database:"
echo "   python main.py wso2/choreo --query 'your query here'"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md: Complete documentation"
echo "  - QUICKSTART.md: Quick start guide"
echo "  - PROJECT_SUMMARY.md: Project overview"
echo ""
echo -e "${GREEN}Ready to use!${NC} 🚀"
echo ""

