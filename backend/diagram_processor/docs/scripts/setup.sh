#!/bin/bash
# Setup script for Diagram Processor

echo "=========================================="
echo "Diagram Processor Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the diagram_processor directory"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo ""

# Check for Tesseract
echo "Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -1)
    echo "✓ $tesseract_version"
else
    echo "⚠️  Tesseract not found. Install it for OCR support:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   macOS: brew install tesseract"
fi
echo ""

# Check for Graphviz
echo "Checking for Graphviz..."
if command -v dot &> /dev/null; then
    graphviz_version=$(dot -V 2>&1)
    echo "✓ $graphviz_version"
else
    echo "⚠️  Graphviz not found. Install it for graph visualization:"
    echo "   Ubuntu/Debian: sudo apt-get install graphviz"
    echo "   macOS: brew install graphviz"
fi
echo ""

# Create output directories
echo "Creating output directories..."
mkdir -p output/summaries
mkdir -p output/graphs
mkdir -p output/extracted_text
echo "✓ Output directories created"
echo ""

# Make main.py executable
echo "Making main.py executable..."
chmod +x main.py
echo "✓ main.py is now executable"
echo ""

# Check environment variables
echo "Checking environment variables..."
if [ -f "../.env" ]; then
    echo "✓ Found .env file in parent directory"

    # Check for required variables
    source ../.env 2>/dev/null || true

    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  OPENAI_API_KEY not set in .env"
    else
        echo "✓ OPENAI_API_KEY is set"
    fi

    if [ -z "$MILVUS_URI" ]; then
        echo "⚠️  MILVUS_URI not set in .env"
    else
        echo "✓ MILVUS_URI is set"
    fi

    if [ -z "$MILVUS_TOKEN" ]; then
        echo "⚠️  MILVUS_TOKEN not set in .env"
    else
        echo "✓ MILVUS_TOKEN is set"
    fi
else
    echo "⚠️  .env file not found in parent directory"
    echo "   Please ensure your .env file is in the choreo-ai-assistant directory"
fi
echo ""

echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has all required API keys"
echo "2. Run a dry run to test: python3 main.py --dry-run"
echo "3. Process all diagrams: python3 main.py"
echo ""
echo "For help: python3 main.py --help"

