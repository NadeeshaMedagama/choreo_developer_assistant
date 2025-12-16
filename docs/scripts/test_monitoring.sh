#!/bin/bash
# Test script to verify monitoring system is working

echo "🧪 Testing Choreo AI Assistant Monitoring System"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Test 1: Check if monitoring module can be imported
echo -n "Test 1: Importing monitoring module... "
if python3 -c "from backend.monitoring import metrics_middleware" 2>/dev/null; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 2: Check if all scripts exist
echo -n "Test 2: Checking script files... "
if [[ -f "backend/monitoring/start.sh" ]] && \
   [[ -f "backend/monitoring/stop.sh" ]] && \
   [[ -f "backend/monitoring/install.sh" ]] && \
   [[ -f "backend/monitoring/load_test.sh" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 3: Check if scripts are executable
echo -n "Test 3: Checking script permissions... "
if [[ -x "backend/monitoring/start.sh" ]] && \
   [[ -x "backend/monitoring/stop.sh" ]] && \
   [[ -x "backend/monitoring/install.sh" ]] && \
   [[ -x "backend/monitoring/load_test.sh" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 4: Check if configuration files exist
echo -n "Test 4: Checking configuration files... "
if [[ -f "backend/monitoring/prometheus.yml" ]] && \
   [[ -f "backend/monitoring/alert_rules.yml" ]] && \
   [[ -f "backend/monitoring/grafana_dashboard.json" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 5: Check if frontend component exists
echo -n "Test 5: Checking frontend monitoring button... "
if [[ -f "frontend/src/components/MonitoringButton.jsx" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 6: Check if Python dependencies are installed
echo -n "Test 6: Checking Python dependencies... "
if python3 -c "import prometheus_client, psutil" 2>/dev/null; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    echo -e "${YELLOW}   Run: pip install prometheus-client psutil${NC}"
    ((FAILED++))
fi

# Test 7: Check if documentation exists
echo -n "Test 7: Checking documentation... "
if [[ -f "backend/monitoring/README.md" ]] && \
   [[ -f "backend/monitoring/SETUP_GUIDE.md" ]] && \
   [[ -f "backend/monitoring/QUICK_REFERENCE.md" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo "================================================"
echo "Test Results: $PASSED passed, $FAILED failed"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed! Monitoring system is ready.${NC}"
    echo ""
    echo "Quick start:"
    echo "  cd backend/monitoring"
    echo "  ./start.sh"
    echo ""
    echo "Then open: http://localhost:8000/metrics"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the errors above.${NC}"
    exit 1
fi

