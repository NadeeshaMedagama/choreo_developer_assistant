#!/bin/bash
# Validate Choreo frontend component configuration

echo "🔍 Validating Choreo Frontend Component Configuration..."
echo ""

ERRORS=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if component.yaml exists
if [ ! -f ".choreo/component.yaml" ]; then
    echo -e "${RED}✗${NC} .choreo/component.yaml not found"
    exit 1
fi

echo -e "${BLUE}📋 Checking component.yaml structure...${NC}"

# Check required fields
if grep -q "schemaVersion: 1.2" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Schema version: 1.2"
else
    echo -e "${RED}✗${NC} Missing or incorrect schemaVersion"
    ERRORS=$((ERRORS+1))
fi

if grep -q "implementation: WebApplication" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Implementation type: WebApplication"
else
    echo -e "${RED}✗${NC} Implementation type should be WebApplication"
    ERRORS=$((ERRORS+1))
fi

# Check build configuration
if grep -q "buildType: dockerfile" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Build type: dockerfile"
else
    echo -e "${RED}✗${NC} Build type not set to dockerfile"
    ERRORS=$((ERRORS+1))
fi

if grep -q "dockerfilePath: Dockerfile" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Dockerfile path configured"
else
    echo -e "${RED}✗${NC} Dockerfile path not configured"
    ERRORS=$((ERRORS+1))
fi

# Check endpoints
if grep -q "port: 80" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Endpoint port: 80"
else
    echo -e "${YELLOW}⚠${NC} Port may not be set to 80 (nginx default)"
    WARNINGS=$((WARNINGS+1))
fi

if grep -q "type: WebApplication" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Endpoint type: WebApplication"
else
    echo -e "${RED}✗${NC} Endpoint type not WebApplication"
    ERRORS=$((ERRORS+1))
fi

if grep -q "networkVisibilities:" .choreo/component.yaml && grep -q "- Public" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Network visibility: Public"
else
    echo -e "${YELLOW}⚠${NC} Network visibility may not be Public"
    WARNINGS=$((WARNINGS+1))
fi

# Check dependencies
if grep -q "dependsOn:" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Backend dependency declared"
else
    echo -e "${YELLOW}⚠${NC} No backend dependency declared"
    WARNINGS=$((WARNINGS+1))
fi

if grep -q "name: choreo-ai-backend" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Backend component name: choreo-ai-backend"
else
    echo -e "${YELLOW}⚠${NC} Backend component name may need adjustment"
    WARNINGS=$((WARNINGS+1))
fi

# Check environment variables
if grep -q "API_URL" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} API_URL environment variable configured"
else
    echo -e "${RED}✗${NC} API_URL not configured"
    ERRORS=$((ERRORS+1))
fi

if grep -q "connectionRef:" .choreo/component.yaml; then
    echo -e "${GREEN}✓${NC} Connection reference configured"
else
    echo -e "${RED}✗${NC} Connection reference missing"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo -e "${BLUE}📦 Checking required files...${NC}"

# Check Dockerfile
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✓${NC} Dockerfile exists"

    # Check Dockerfile contents
    if grep -q "FROM node:.*alpine.*AS build" Dockerfile; then
        echo -e "${GREEN}✓${NC} Dockerfile has multi-stage build"
    else
        echo -e "${YELLOW}⚠${NC} Dockerfile may not have multi-stage build"
        WARNINGS=$((WARNINGS+1))
    fi

    if grep -q "FROM nginx:.*alpine" Dockerfile; then
        echo -e "${GREEN}✓${NC} Dockerfile uses nginx for serving"
    else
        echo -e "${RED}✗${NC} Dockerfile doesn't use nginx"
        ERRORS=$((ERRORS+1))
    fi

    if grep -q "ENTRYPOINT.*docker-entrypoint.sh" Dockerfile; then
        echo -e "${GREEN}✓${NC} Dockerfile has entrypoint configured"
    else
        echo -e "${RED}✗${NC} Dockerfile missing entrypoint"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} Dockerfile not found"
    ERRORS=$((ERRORS+1))
fi

# Check docker-entrypoint.sh
if [ -f "docker-entrypoint.sh" ]; then
    echo -e "${GREEN}✓${NC} docker-entrypoint.sh exists"

    if [ -x "docker-entrypoint.sh" ]; then
        echo -e "${GREEN}✓${NC} docker-entrypoint.sh is executable"
    else
        echo -e "${YELLOW}⚠${NC} docker-entrypoint.sh may need executable permission"
        echo "  Run: chmod +x docker-entrypoint.sh"
        WARNINGS=$((WARNINGS+1))
    fi

    if grep -q "window.configs" docker-entrypoint.sh; then
        echo -e "${GREEN}✓${NC} docker-entrypoint.sh generates config.js"
    else
        echo -e "${RED}✗${NC} docker-entrypoint.sh doesn't generate config"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} docker-entrypoint.sh not found"
    ERRORS=$((ERRORS+1))
fi

# Check other required files
if [ -f "public/config.js" ]; then
    echo -e "${GREEN}✓${NC} public/config.js template exists"
else
    echo -e "${RED}✗${NC} public/config.js not found"
    ERRORS=$((ERRORS+1))
fi

if [ -f "src/config.js" ]; then
    echo -e "${GREEN}✓${NC} src/config.js utility exists"
else
    echo -e "${RED}✗${NC} src/config.js not found"
    ERRORS=$((ERRORS+1))
fi

if [ -f "index.html" ]; then
    echo -e "${GREEN}✓${NC} index.html exists"

    if grep -q '<script src="/config.js"></script>' index.html; then
        echo -e "${GREEN}✓${NC} index.html loads config.js"
    else
        echo -e "${RED}✗${NC} index.html doesn't load config.js"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} index.html not found"
    ERRORS=$((ERRORS+1))
fi

if [ -f "nginx.conf" ]; then
    echo -e "${GREEN}✓${NC} nginx.conf exists"
else
    echo -e "${YELLOW}⚠${NC} nginx.conf not found"
    WARNINGS=$((WARNINGS+1))
fi

# Check YAML syntax (basic check)
echo ""
echo -e "${BLUE}🔧 Checking YAML syntax...${NC}"

if python3 -c "import yaml; yaml.safe_load(open('.choreo/component.yaml'))" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} component.yaml is valid YAML"
else
    echo -e "${RED}✗${NC} component.yaml has YAML syntax errors"
    ERRORS=$((ERRORS+1))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 Validation Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Perfect! All checks passed!${NC}"
    echo ""
    echo "Your frontend component is ready for Choreo deployment."
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend component first"
    echo "2. Create connection from frontend to backend"
    echo "3. Deploy frontend component"
    echo ""
    echo "📚 Documentation:"
    echo "  - .choreo/README.md"
    echo "  - .choreo/DEPLOYMENT_GUIDE.md"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s) found${NC}"
    echo ""
    echo "Configuration is valid but has some warnings."
    echo "Review warnings above and fix if needed."
    echo ""
    echo "You can proceed with deployment if warnings are acceptable."
else
    echo -e "${RED}❌ ${ERRORS} error(s) and ${WARNINGS} warning(s) found${NC}"
    echo ""
    echo "Please fix the errors above before deploying to Choreo."
    exit 1
fi

echo ""

