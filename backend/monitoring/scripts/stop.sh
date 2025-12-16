#!/bin/bash
# Stop script for Choreo AI Assistant services

set -e

echo "🛑 Stopping Choreo AI Assistant services..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to kill process on port
kill_port() {
    if lsof -i :$1 >/dev/null 2>&1; then
        echo -e "${YELLOW}Stopping process on port $1${NC}"
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
    fi
}

# Kill processes from PID file
if [ -f "$PROJECT_ROOT/pids.txt" ]; then
    echo "Stopping services from PID file..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Killing process $pid"
            kill -9 $pid 2>/dev/null || true
        fi
    done < "$PROJECT_ROOT/pids.txt"
    rm "$PROJECT_ROOT/pids.txt"
fi

# Also kill by port as backup
kill_port 8000  # FastAPI
kill_port 9090  # Prometheus
kill_port 3000  # Grafana

echo -e "${GREEN}✅ All services stopped${NC}"

