#!/bin/bash
# Startup script for Choreo AI Assistant with monitoring
# This script starts FastAPI, Prometheus, and Grafana

set -e

echo "🚀 Starting Choreo AI Assistant with Monitoring..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/monitoring/prometheus_data"
mkdir -p "$PROJECT_ROOT/monitoring/grafana_data"

# Check if running in Choreo or locally
if [ -n "$CHOREO_ENVIRONMENT" ]; then
    echo -e "${GREEN}Running in Choreo environment${NC}"
    MODE="choreo"
else
    echo -e "${GREEN}Running in local environment${NC}"
    MODE="local"
fi

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        echo -e "${YELLOW}Killing process on port $1${NC}"
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 8000  # FastAPI
kill_port 9090  # Prometheus
kill_port 3000  # Grafana

# Start FastAPI
echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
cd "$PROJECT_ROOT"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!
echo "FastAPI started with PID: $FASTAPI_PID"

# Wait for FastAPI to be ready
echo "Waiting for FastAPI to be ready..."
sleep 3
if ! port_in_use 8000; then
    echo -e "${YELLOW}Warning: FastAPI may not have started correctly${NC}"
fi

if [ "$MODE" == "local" ]; then
    # Start Prometheus (only in local mode)
    echo -e "${GREEN}Starting Prometheus on port 9090...${NC}"

    # Check if prometheus is installed
    if command -v prometheus &> /dev/null; then
        cd "$SCRIPT_DIR/.."
        prometheus --config.file=configs/prometheus.yml \
                   --storage.tsdb.path=prometheus_data \
                   --web.listen-address=:9090 &
        PROMETHEUS_PID=$!
        echo "Prometheus started with PID: $PROMETHEUS_PID"
    else
        echo -e "${YELLOW}Prometheus not found. Please install Prometheus:${NC}"
        echo "  wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz"
        echo "  tar xvfz prometheus-2.47.0.linux-amd64.tar.gz"
        echo "  cd prometheus-2.47.0.linux-amd64"
        echo "  sudo cp prometheus /usr/local/bin/"
        echo "  sudo cp promtool /usr/local/bin/"
    fi

    # Start Grafana (only in local mode)
    echo -e "${GREEN}Starting Grafana on port 3000...${NC}"

    # Check if grafana-server is installed
    if command -v grafana-server &> /dev/null; then
        grafana-server --homepath=/usr/share/grafana \
                      --config=/etc/grafana/grafana.ini \
                      web &
        GRAFANA_PID=$!
        echo "Grafana started with PID: $GRAFANA_PID"
    else
        echo -e "${YELLOW}Grafana not found. Please install Grafana:${NC}"
        echo "  sudo apt-get install -y adduser libfontconfig1"
        echo "  wget https://dl.grafana.com/oss/release/grafana_10.2.0_amd64.deb"
        echo "  sudo dpkg -i grafana_10.2.0_amd64.deb"
        echo "  sudo systemctl enable grafana-server"
    fi
fi

# Save PIDs to file for cleanup
echo "$FASTAPI_PID" > "$PROJECT_ROOT/pids.txt"
if [ -n "$PROMETHEUS_PID" ]; then
    echo "$PROMETHEUS_PID" >> "$PROJECT_ROOT/pids.txt"
fi
if [ -n "$GRAFANA_PID" ]; then
    echo "$GRAFANA_PID" >> "$PROJECT_ROOT/pids.txt"
fi

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📊 Service URLs:"
echo "  FastAPI:     http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Metrics:     http://localhost:8000/metrics"

if [ "$MODE" == "local" ]; then
    echo "  Prometheus:  http://localhost:9090"
    echo "  Grafana:     http://localhost:3000 (admin/admin)"
fi

echo ""
echo "📝 Logs location: $PROJECT_ROOT/logs/"
echo ""
echo "To stop all services, run: ./monitoring/stop.sh"
echo ""

# Wait for all background processes
wait

