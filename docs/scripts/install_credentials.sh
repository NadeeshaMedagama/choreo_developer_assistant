#!/bin/bash
# Quick setup command - just paste the file path when you have it

echo "=========================================="
echo "Google Vision API Credentials Setup"
echo "=========================================="
echo ""
echo "Looking for credentials file..."

# Check common locations
LOCATIONS=(
    "/home/nadeeshame/Downloads/digital-arcade-476402-q1-25afb35862cf.json"
    "/home/nadeeshame/Downloads/*.json"
    "~/Downloads/digital-arcade-476402-q1-25afb35862cf.json"
)

FOUND_FILE=""
for loc in "${LOCATIONS[@]}"; do
    if ls $loc 2>/dev/null; then
        FOUND_FILE=$(ls $loc 2>/dev/null | head -1)
        break
    fi
done

if [ -n "$FOUND_FILE" ]; then
    echo "✓ Found credentials: $FOUND_FILE"
    echo ""
    echo "Installing..."
    bash /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant/setup_google_vision.sh "$FOUND_FILE"
else
    echo "❌ Credentials file not found in Downloads"
    echo ""
    echo "Please download the file from Google Cloud Console, then run:"
    echo ""
    echo "  bash setup_google_vision.sh ~/Downloads/digital-arcade-476402-q1-25afb35862cf.json"
    echo ""
    echo "Or drag and drop the file into the terminal after typing:"
    echo "  bash setup_google_vision.sh "
fi

