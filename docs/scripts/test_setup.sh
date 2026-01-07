#!/bin/bash
# Test script to verify local setup
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Choreo AI - Setup Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
ERRORS=0
# Test 1: Port 8000
echo -e "${YELLOW}[1/7]${NC} Checking port 8000..."
if lsof -i:8000 >/dev/null 2>&1; then
    echo -e "      ${RED}✗ Port in use${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "      ${GREEN}✓ Available${NC}"
fi
echo ""
# Test 2: .env file
echo -e "${YELLOW}[2/7]${NC} Checking .env..."
if [ -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "      ${GREEN}✓ Found${NC}"
else
    echo -e "      ${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""
# Test 3: Frontend deps
echo -e "${YELLOW}[3/7]${NC} Checking frontend..."
if [ -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo -e "      ${GREEN}✓ Installed${NC}"
else
    echo -e "      ${YELLOW}⚠ Will install${NC}"
fi
echo ""
# Test 4: Python
echo -e "${YELLOW}[4/7]${NC} Checking Python..."
cd "$SCRIPT_DIR/backend"
if python -c "import fastapi" 2>/dev/null; then
    echo -e "      ${GREEN}✓ FastAPI ready${NC}"
else
    echo -e "      ${RED}✗ FastAPI missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
cd "$SCRIPT_DIR"
echo ""
# Test 5: Config
echo -e "${YELLOW}[5/7]${NC} Checking config..."
if grep -q "isLocalDevelopment" "$SCRIPT_DIR/frontend/public/config.js" 2>/dev/null; then
    echo -e "      ${GREEN}✓ Configured${NC}"
else
    echo -e "      ${RED}✗ Needs update${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""
# Test 6: Scripts
echo -e "${YELLOW}[6/7]${NC} Checking scripts..."
if [ -x "$SCRIPT_DIR/start_local.sh" ] && [ -x "$SCRIPT_DIR/backend/start_local.sh" ]; then
    echo -e "      ${GREEN}✓ Ready${NC}"
else
    echo -e "      ${RED}✗ Missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""
# Test 7: Vite
echo -e "${YELLOW}[7/7]${NC} Checking Vite..."
if grep -q "proxy" "$SCRIPT_DIR/frontend/vite.config.js" 2>/dev/null; then
    echo -e "      ${GREEN}✓ Proxy OK${NC}"
else
    echo -e "      ${RED}✗ No proxy${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""
# Summary
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "Start: ${BLUE}./start_local.sh${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS issues${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    exit 1
fi
