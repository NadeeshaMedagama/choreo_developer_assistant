#!/bin/bash
# Complete system startup script

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   🚀 Starting Choreo AI Assistant (Full Stack + Monitoring)  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python; then
    echo -e "${YELLOW}⚠️  Python not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check Node
if ! command_exists node; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo -e "${BLUE}1/4 Checking dependencies...${NC}"
cd "$PROJECT_ROOT"

# Activate virtual environment if exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

echo -e "${BLUE}2/4 Starting Backend (FastAPI)...${NC}"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  URL: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Metrics: http://localhost:8000/metrics"
echo ""

# Wait for backend to be ready
sleep 3

echo -e "${BLUE}3/4 Starting Frontend (Vite)...${NC}"
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  URL: http://localhost:5173"
echo ""

# Wait for frontend to be ready
sleep 2

echo -e "${BLUE}4/4 Starting Monitoring (Optional)...${NC}"
cd "$PROJECT_ROOT/backend/monitoring"

# Start Prometheus if available
if command_exists prometheus; then
    prometheus --config.file=prometheus.yml --storage.tsdb.path=prometheus_data &
    PROMETHEUS_PID=$!
    echo -e "${GREEN}✓ Prometheus started (PID: $PROMETHEUS_PID)${NC}"
    echo "  URL: http://localhost:9090"
else
    echo -e "${YELLOW}⚠️  Prometheus not installed (optional)${NC}"
fi

# Start Grafana if available
if command_exists grafana-server; then
    grafana-server --homepath=/usr/share/grafana &
    GRAFANA_PID=$!
    echo -e "${GREEN}✓ Grafana started (PID: $GRAFANA_PID)${NC}"
    echo "  URL: http://localhost:3000 (admin/admin)"
else
    echo -e "${YELLOW}⚠️  Grafana not installed (optional)${NC}"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ All Services Running!                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Access Points:"
echo "  • DevChoreo UI:  http://localhost:5173"
echo "  • Backend API:   http://localhost:8000"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • Metrics:       http://localhost:8000/metrics"
echo "  • Health Check:  http://localhost:8000/api/health"
if [ -n "$PROMETHEUS_PID" ]; then
echo "  • Prometheus:    http://localhost:9090"
fi
if [ -n "$GRAFANA_PID" ]; then
echo "  • Grafana:       http://localhost:3000"
fi
echo ""
echo "📝 Tips:"
echo "  • Click the blue monitoring icon in DevChoreo UI"
echo "  • Check logs in: $PROJECT_ROOT/logs/"
echo "  • Stop all: Press Ctrl+C or run ./stop_all.sh"
echo ""
echo "🎉 Happy Coding!"
echo ""

# Save PIDs for cleanup
echo "$BACKEND_PID" > "$PROJECT_ROOT/pids.txt"
echo "$FRONTEND_PID" >> "$PROJECT_ROOT/pids.txt"
[ -n "$PROMETHEUS_PID" ] && echo "$PROMETHEUS_PID" >> "$PROJECT_ROOT/pids.txt"
[ -n "$GRAFANA_PID" ] && echo "$GRAFANA_PID" >> "$PROJECT_ROOT/pids.txt"

# Wait for user to stop
wait

