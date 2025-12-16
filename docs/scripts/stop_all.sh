#!/bin/bash
# Stop all services

echo "🛑 Stopping all services..."

PROJECT_ROOT="/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Kill processes from PID file
if [ -f "$PROJECT_ROOT/pids.txt" ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Stopping process $pid"
            kill -9 $pid 2>/dev/null || true
        fi
    done < "$PROJECT_ROOT/pids.txt"
    rm "$PROJECT_ROOT/pids.txt"
fi

# Also kill by port as backup
for port in 8000 5173 9090 3000; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "  Stopping process on port $port"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
    fi
done

echo "✅ All services stopped"

