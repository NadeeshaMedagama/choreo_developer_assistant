#!/bin/bash
# Installation script for monitoring components
set -e
echo "🔧 Installing Monitoring Components for Choreo AI Assistant"
echo ""
# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# Install Python dependencies
echo -e "${BLUE}📦 Installing Python monitoring dependencies...${NC}"
pip install -r "$SCRIPT_DIR/../configs/requirements.txt"
echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo ""
echo -e "${GREEN}🎉 Monitoring components installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the monitoring system: ./start.sh"
echo "  2. Access Prometheus: http://localhost:9090"
echo "  3. Access Grafana: http://localhost:3000 (admin/admin)"
echo ""
