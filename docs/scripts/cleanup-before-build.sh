#!/bin/bash
# cleanup-before-build.sh
# Run this script to clean up unnecessary files before building for Choreo

set -e

echo "🧹 Cleaning up unnecessary files to reduce build size..."

# Remove development and test files
echo "Removing test files..."
find . -type f -name "*_test.py" -delete
find . -type f -name "test_*.py" -delete
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true

# Remove Python cache
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove logs
echo "Removing logs..."
find . -type f -name "*.log" -delete
rm -rf logs/ 2>/dev/null || true

# Remove data and output directories
echo "Removing data and output directories..."
rm -rf data/diagrams/ 2>/dev/null || true
rm -rf backend/diagram_processor/output/ 2>/dev/null || true
rm -rf backend/diagram_processor/repositories/ 2>/dev/null || true

# Remove notebooks
echo "Removing notebooks..."
rm -rf notebooks/ 2>/dev/null || true
find . -type f -name "*.ipynb" -delete

# Remove large model files
echo "Removing large model files..."
find . -type f -name "*.bin" -delete
find . -type f -name "*.pt" -delete
find . -type f -name "*.pth" -delete
find . -type f -name "*.onnx" -delete
find . -type f -name "*.h5" -delete

# Remove backup files
echo "Removing backup files..."
find . -type f -name "*.backup" -delete
find . -type f -name "*.bak" -delete
find . -type f -name "*~" -delete

# Remove IDE files
echo "Removing IDE files..."
rm -rf .vscode/ .idea/ 2>/dev/null || true

# Remove documentation TXT files (keep requirements.txt)
echo "Removing unnecessary documentation files..."
find . -type f -name "*.txt" ! -name "requirements.txt" -delete

# Remove frontend build artifacts
echo "Removing frontend build artifacts..."
rm -rf frontend/node_modules/ 2>/dev/null || true
rm -rf frontend/.vite/ 2>/dev/null || true

# Remove monitoring directory
echo "Removing monitoring directory..."
rm -rf backend/monitoring/ 2>/dev/null || true

# Show disk usage
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Current directory size:"
du -sh .
echo ""
echo "Top 10 largest directories:"
du -sh */ 2>/dev/null | sort -rh | head -10

