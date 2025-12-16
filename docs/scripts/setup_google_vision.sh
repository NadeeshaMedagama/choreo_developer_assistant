#!/bin/bash
# Script to securely copy Google Vision API credentials

CREDENTIALS_DIR="/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/credentials"
SOURCE_FILE="$1"

if [ -z "$SOURCE_FILE" ]; then
    echo "Usage: ./setup_google_vision.sh <path-to-credentials.json>"
    echo ""
    echo "Example:"
    echo "  ./setup_google_vision.sh ~/Downloads/digital-arcade-476402-q1-25afb35862cf.json"
    exit 1
fi

if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: File not found: $SOURCE_FILE"
    exit 1
fi

# Copy the file
echo "📋 Copying credentials to: $CREDENTIALS_DIR"
cp "$SOURCE_FILE" "$CREDENTIALS_DIR/"

# Get the filename
FILENAME=$(basename "$SOURCE_FILE")

# Set secure permissions
chmod 600 "$CREDENTIALS_DIR/$FILENAME"

echo "✅ Credentials installed successfully!"
echo ""
echo "📁 Location: $CREDENTIALS_DIR/$FILENAME"
echo "🔒 Permissions: 600 (read-write for owner only)"
echo ""
echo "Testing configuration..."
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python3 -c "from diagram_processor.utils import Config; Config.validate(); print('✓ Google Vision credentials loaded successfully!' if Config.GOOGLE_APPLICATION_CREDENTIALS else '❌ Credentials not detected')"

