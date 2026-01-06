#!/bin/bash
# Test script to verify Choreo configuration implementation

echo "🧪 Testing Choreo Configuration Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check if files exist
echo "📁 Checking required files..."

FILES=(
  "frontend/public/config.js"
  "frontend/src/config.js"
  "frontend/docker-entrypoint.sh"
  "frontend/index.html"
  "frontend/Dockerfile"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file exists"
  else
    echo -e "${RED}✗${NC} $file missing"
    ERRORS=$((ERRORS+1))
  fi
done

echo ""
echo "🔍 Checking file contents..."

# Check index.html contains config.js script
if grep -q '<script src="/config.js"></script>' frontend/index.html; then
  echo -e "${GREEN}✓${NC} index.html loads config.js"
else
  echo -e "${RED}✗${NC} index.html missing config.js script tag"
  ERRORS=$((ERRORS+1))
fi

# Check App.jsx imports getApiUrl
if grep -q "import.*getApiUrl.*from.*config" frontend/src/App.jsx; then
  echo -e "${GREEN}✓${NC} App.jsx imports getApiUrl"
else
  echo -e "${RED}✗${NC} App.jsx missing getApiUrl import"
  ERRORS=$((ERRORS+1))
fi

# Check docker-entrypoint.sh is executable
if [ -x "frontend/docker-entrypoint.sh" ]; then
  echo -e "${GREEN}✓${NC} docker-entrypoint.sh is executable"
else
  echo -e "${YELLOW}⚠${NC} docker-entrypoint.sh may need executable permission"
  echo "  Run: chmod +x frontend/docker-entrypoint.sh"
fi

# Check Dockerfile has entrypoint
if grep -q "ENTRYPOINT.*docker-entrypoint.sh" frontend/Dockerfile; then
  echo -e "${GREEN}✓${NC} Dockerfile has entrypoint configured"
else
  echo -e "${RED}✗${NC} Dockerfile missing entrypoint"
  ERRORS=$((ERRORS+1))
fi

# Count fetch calls with getApiUrl
FETCH_COUNT=$(grep -c "const apiUrl = getApiUrl()" frontend/src/App.jsx 2>/dev/null || echo "0")
if [ "$FETCH_COUNT" -ge 6 ]; then
  echo -e "${GREEN}✓${NC} App.jsx has $FETCH_COUNT fetch calls using dynamic URL"
else
  echo -e "${YELLOW}⚠${NC} App.jsx has only $FETCH_COUNT fetch calls using dynamic URL (expected 7+)"
fi

# Check MonitoringButton
if grep -q "import.*getApiUrl" frontend/src/components/MonitoringButton.jsx; then
  echo -e "${GREEN}✓${NC} MonitoringButton.jsx uses dynamic config"
else
  echo -e "${RED}✗${NC} MonitoringButton.jsx not updated"
  ERRORS=$((ERRORS+1))
fi

echo ""
echo "🔧 Configuration setup summary:"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed!${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Build the frontend: cd frontend && docker build -t choreo-frontend ."
  echo "2. Test locally: docker run -p 8080:80 -e API_URL='http://localhost:8000/' choreo-frontend"
  echo "3. Deploy to Choreo and set API_URL environment variable"
else
  echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
  echo "Please fix the issues above before deploying."
  exit 1
fi

echo ""
echo "📚 Documentation:"
echo "  - Configuration guide: docs/CHOREO_CONFIG_GUIDE.md"
echo "  - Setup instructions: docs/FRONTEND_BACKEND_CONNECTION_SETUP.md"

