#!/bin/bash
# Stop Prometheus + Grafana

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🛑 Stopping Prometheus + Grafana Monitoring Stack         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Stop Prometheus
echo -e "${BLUE}1. Stopping Prometheus...${NC}"
if pgrep -f prometheus > /dev/null; then
    pkill -f prometheus
    sleep 1
    echo -e "${GREEN}   ✅ Prometheus stopped${NC}"
else
    echo "   Prometheus was not running"
fi

# Stop Grafana
echo -e "${BLUE}2. Stopping Grafana...${NC}"
if systemctl is-active --quiet grafana-server 2>/dev/null; then
    sudo systemctl stop grafana-server
    echo -e "${GREEN}   ✅ Grafana stopped${NC}"
else
    echo "   Grafana was not running"
fi

echo ""
echo "✅ Monitoring stack stopped successfully"
echo ""

