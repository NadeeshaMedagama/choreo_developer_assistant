#!/bin/bash
#
# Docker Build Validation Script
# Tests the fixed Dockerfile to ensure it builds correctly
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================"
echo "🔍 Docker Build Validation"
echo "======================================"
echo ""

cd "$PROJECT_ROOT"

echo "📍 Working directory: $(pwd)"
echo ""

# Check if Dockerfile exists
echo "✅ Checking Dockerfile..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ ERROR: Dockerfile not found!"
    exit 1
fi
echo "   ✓ Dockerfile found"
echo ""

# Check for start.py
echo "✅ Checking start.py..."
if [ ! -f "start.py" ]; then
    echo "❌ ERROR: start.py not found!"
    exit 1
fi
echo "   ✓ start.py found"
echo ""

# Check if start.sh is referenced (should NOT be)
echo "✅ Checking for incorrect start.sh reference..."
if grep -q "start.sh" Dockerfile; then
    echo "❌ ERROR: Dockerfile still references start.sh!"
    echo "   Found in:"
    grep -n "start.sh" Dockerfile
    exit 1
fi
echo "   ✓ No start.sh reference (good!)"
echo ""

# Check chmod command
echo "✅ Checking chmod command..."
if grep -q "chmod.*start.py" Dockerfile; then
    echo "   ✓ chmod +x /app/start.py found"
else
    echo "⚠️  WARNING: No chmod for start.py found"
fi
echo ""

# Display the chmod line
echo "📝 Current chmod command:"
grep -A1 -B1 "chmod" Dockerfile || echo "   No chmod command found"
echo ""

# Try to build (dry run - syntax check)
echo "======================================"
echo "🔨 Attempting Docker Build (Test)"
echo "======================================"
echo ""
echo "This will test the Dockerfile syntax and build process."
echo "Press Ctrl+C within 5 seconds to cancel..."
sleep 5
echo ""

# Build with a test tag
echo "Building Docker image (this may take a few minutes)..."
docker build -t choreo-ai-assistant:test-build -f Dockerfile . || {
    echo ""
    echo "❌ Docker build FAILED!"
    echo ""
    echo "Common issues:"
    echo "  1. Missing files referenced in Dockerfile"
    echo "  2. Syntax errors in Dockerfile"
    echo "  3. Network issues downloading dependencies"
    echo ""
    exit 1
}

echo ""
echo "======================================"
echo "✅ SUCCESS! Docker Build Complete"
echo "======================================"
echo ""
echo "Image created: choreo-ai-assistant:test-build"
echo ""
echo "To run the container:"
echo "  docker run -p 9090:9090 choreo-ai-assistant:test-build"
echo ""
echo "To inspect the image:"
echo "  docker images choreo-ai-assistant:test-build"
echo ""
echo "To remove the test image:"
echo "  docker rmi choreo-ai-assistant:test-build"
echo ""

