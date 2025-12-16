#!/bin/bash

# Script to convert Google Cloud service account JSON to single-line format for Choreo
# Usage: ./prepare_google_creds.sh

set -e

CREDS_FILE="/home/nadeeshame/Downloads/digital-arcade-476402-q1-25afb35862cf.json"
OUTPUT_FILE="/tmp/google-creds-choreo.txt"

echo "======================================================================"
echo "Google Vision Credentials Converter for Choreo"
echo "======================================================================"
echo ""

# Check if file exists
if [ ! -f "$CREDS_FILE" ]; then
    echo "❌ Error: Credentials file not found at: $CREDS_FILE"
    echo ""
    echo "Please update CREDS_FILE variable in this script with the correct path."
    exit 1
fi

echo "📄 Found credentials file: $CREDS_FILE"
echo ""

# Check if jq is installed
if command -v jq &> /dev/null; then
    echo "✓ Using jq for JSON compacting..."
    cat "$CREDS_FILE" | jq -c . > "$OUTPUT_FILE"
else
    echo "⚠️  jq not found, using basic compacting..."
    # Fallback: just remove newlines (less robust but works)
    cat "$CREDS_FILE" | tr -d '\n' > "$OUTPUT_FILE"
fi

echo "✓ Converted to single-line format"
echo ""
echo "======================================================================"
echo "Single-line JSON saved to: $OUTPUT_FILE"
echo "======================================================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Copy the content below (it's also saved in $OUTPUT_FILE):"
echo ""
echo "---BEGIN CREDENTIALS---"
cat "$OUTPUT_FILE"
echo ""
echo "---END CREDENTIALS---"
echo ""
echo "2. Go to Choreo Console → Your Component → DevOps → Configs & Secrets"
echo ""
echo "3. Add new config/secret:"
echo "   Name: GOOGLE_CREDENTIALS_JSON"
echo "   Value: (paste the single-line JSON from above)"
echo ""
echo "4. Save and redeploy your component"
echo ""
echo "✓ Done! Your credentials are ready for Choreo deployment."
echo ""

# Also copy to clipboard if xclip is available
if command -v xclip &> /dev/null; then
    cat "$OUTPUT_FILE" | xclip -selection clipboard
    echo "📎 Credentials also copied to clipboard!"
    echo ""
elif command -v xsel &> /dev/null; then
    cat "$OUTPUT_FILE" | xsel --clipboard
    echo "📎 Credentials also copied to clipboard!"
    echo ""
fi

