#!/bin/bash
# test-requirements.sh
# Test if requirements can be installed without conflicts
# This does a dry-run to check for dependency issues

set -e

echo "🔍 Testing requirements for dependency conflicts..."
echo ""

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Created temp directory: $TEMP_DIR"

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv "$TEMP_DIR/venv"

# Activate it
source "$TEMP_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Try to install requirements (dry-run first)
echo ""
echo "Testing backend/requirements.txt..."
pip install --dry-run -r backend/requirements.txt

echo ""
echo "Testing backend/choreo-ai-assistant/requirements.txt..."
pip install --dry-run -r backend/choreo-ai-assistant/requirements.txt

echo ""
echo "Testing backend/diagram_processor/requirements.txt..."
pip install --dry-run -r backend/diagram_processor/requirements.txt

echo ""
echo "✅ All requirements files are compatible!"
echo ""
echo "To actually install (for testing):"
echo "  pip install -r requirements-consolidated.txt"

# Cleanup
deactivate
rm -rf "$TEMP_DIR"

echo ""
echo "Test completed successfully! 🎉"

