#!/bin/bash
# Test GitHub Repository Access

echo "🔍 Testing GitHub Repository Access"
echo "Repository: NadeeshaMedagama/docs-choreo-dev"
echo ""

# Test 1: Check if repo exists
echo "1️⃣  Testing if repository exists..."
RESULT=$(curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/NadeeshaMedagama/docs-choreo-dev")

if [ "$RESULT" = "200" ]; then
    echo "✓ Repository exists and is accessible"
elif [ "$RESULT" = "404" ]; then
    echo "✗ Repository not found (404)"
    echo "  Please check:"
    echo "  - Repository name spelling"
    echo "  - Repository is public or you have access"
    exit 1
elif [ "$RESULT" = "403" ]; then
    echo "⚠️  API rate limit exceeded (403)"
    echo "  Try with authentication token"
    exit 1
else
    echo "✗ Unexpected response: $RESULT"
    exit 1
fi

echo ""
echo "2️⃣  Checking repository contents..."
curl -s "https://api.github.com/repos/NadeeshaMedagama/docs-choreo-dev/contents" | head -20

echo ""
echo "3️⃣  Searching for .md files..."
curl -s "https://api.github.com/search/code?q=extension:md+repo:NadeeshaMedagama/docs-choreo-dev" | grep -o '"total_count":[0-9]*'

echo ""
echo "✅ Test complete"

