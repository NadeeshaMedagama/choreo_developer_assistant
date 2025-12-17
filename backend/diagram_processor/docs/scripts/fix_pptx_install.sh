#!/bin/bash
# Install python-pptx in the correct Python environment

echo "================================================================================"
echo "Installing python-pptx for PPTX file support"
echo "================================================================================"
echo ""

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"

# Get the Python executable that main.py uses
PYTHON_EXE=$(head -1 main.py | sed 's/#!//;s/env //')

if [ -z "$PYTHON_EXE" ]; then
    PYTHON_EXE="python3"
fi

echo "Using Python: $PYTHON_EXE"
$PYTHON_EXE --version
echo ""

# Install python-pptx
echo "Installing python-pptx..."
$PYTHON_EXE -m pip install python-pptx

echo ""
echo "Verifying installation..."
if $PYTHON_EXE -c "import pptx; print('✓ python-pptx version:', pptx.__version__)" 2>/dev/null; then
    echo ""
    echo "================================================================================"
    echo "✅ SUCCESS! python-pptx is now installed"
    echo "================================================================================"
    echo ""
    echo "You can now run: python main.py --incremental"
else
    echo ""
    echo "================================================================================"
    echo "❌ FAILED - python-pptx is not installed correctly"
    echo "================================================================================"
    echo ""
    echo "Please try manually:"
    echo "  cd /home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
    echo "  source .venv/bin/activate"
    echo "  pip install python-pptx"
fi

