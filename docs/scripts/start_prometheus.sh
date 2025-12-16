#!/bin/bash
# Start Prometheus with the correct configuration

echo "🚀 Starting Prometheus for Choreo AI Assistant Monitoring"
echo ""

# Set up paths
MONITORING_DIR="/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring"
CONFIG_FILE="$MONITORING_DIR/configs/prometheus.yml"
DATA_DIR="$MONITORING_DIR/prometheus_data"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Prometheus config not found at $CONFIG_FILE"
    exit 1
fi

echo "📁 Configuration: $CONFIG_FILE"
echo "💾 Data directory: $DATA_DIR"
echo "🌐 Web UI: http://localhost:9090"
echo ""
echo "Starting Prometheus..."
echo ""

# Start Prometheus
prometheus \
    --config.file="$CONFIG_FILE" \
    --storage.tsdb.path="$DATA_DIR" \
    --web.console.templates="/usr/share/prometheus/consoles" \
    --web.console.libraries="/usr/share/prometheus/console_libraries" \
    --web.listen-address=":9090" \
    --web.enable-lifecycle

echo ""
echo "To stop Prometheus: Press Ctrl+C or run: pkill prometheus"

