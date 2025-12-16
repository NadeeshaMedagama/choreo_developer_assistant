#!/bin/bash
# Start Prometheus + Grafana Together

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONITORING_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🚀 Starting Prometheus + Grafana Monitoring Stack         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$MONITORING_DIR/logs"

# Check and start Grafana
echo -e "${BLUE}1. Checking Grafana...${NC}"
if systemctl is-active --quiet grafana-server 2>/dev/null; then
    echo -e "${GREEN}   ✅ Grafana is already running${NC}"
else
    echo "   Starting Grafana..."
    sudo systemctl start grafana-server 2>/dev/null || {
        echo -e "${YELLOW}   ⚠️  Grafana service not found (may not be installed)${NC}"
    }
    sleep 2
    if systemctl is-active --quiet grafana-server 2>/dev/null; then
        echo -e "${GREEN}   ✅ Grafana started${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Grafana not running (optional)${NC}"
    fi
fi

# Start Prometheus
echo -e "${BLUE}2. Starting Prometheus...${NC}"
cd "$MONITORING_DIR"

# Kill any existing Prometheus processes
if pgrep -f prometheus > /dev/null; then
    echo "   Stopping existing Prometheus instance..."
    pkill -f prometheus
    sleep 2
fi

# Start Prometheus in background
nohup prometheus \
    --config.file=configs/prometheus.yml \
    --storage.tsdb.path=prometheus_data \
    --web.listen-address=":9090" \
    > logs/prometheus.log 2>&1 &

PROM_PID=$!
echo $PROM_PID > prometheus_data/prometheus.pid

sleep 3

# Verify Prometheus started
if pgrep -f prometheus > /dev/null; then
    echo -e "${GREEN}   ✅ Prometheus started (PID: $PROM_PID)${NC}"
else
    echo -e "   ❌ Prometheus failed to start. Check logs/prometheus.log"
    exit 1
fi

# Verify services are responding
echo ""
echo -e "${BLUE}3. Verifying services...${NC}"

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Prometheus is healthy (http://localhost:9090)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Prometheus not responding yet (starting up...)${NC}"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Grafana is healthy (http://localhost:3000)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Grafana not responding (may not be installed)${NC}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            ✅ Monitoring Stack Started!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Access Points:"
echo "   • Prometheus:  http://localhost:9090"
echo "   • Grafana:     http://localhost:3000 (admin/admin)"
echo ""
echo "📝 Next Steps:"
echo "   1. Start backend:  python -m uvicorn backend.app:app --reload"
echo "   2. Start frontend: cd frontend && npm run dev"
echo "   3. Open DevChoreo and click the monitoring icon"
echo ""
echo "📋 View Logs:"
echo "   • Prometheus: tail -f $MONITORING_DIR/logs/prometheus.log"
echo "   • Grafana:    sudo journalctl -u grafana-server -f"
echo ""
echo "🛑 To stop monitoring:"
echo "   • Run: $SCRIPT_DIR/stop_monitoring.sh"
echo ""

