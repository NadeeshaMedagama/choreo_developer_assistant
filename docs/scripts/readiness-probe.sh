#!/bin/bash
# Readiness probe script for Choreo deployment
# This script checks if the service is ready to accept traffic

set -e

# Configuration
HOST="${HOST:-localhost}"
PORT="${PORT:-9090}"
TIMEOUT="${TIMEOUT:-5}"
MAX_RETRIES="${MAX_RETRIES:-3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check health
check_health() {
    local retry=0

    echo "Checking service health at http://${HOST}:${PORT}/health..."

    while [ $retry -lt $MAX_RETRIES ]; do
        if curl -f -s --max-time $TIMEOUT "http://${HOST}:${PORT}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service is healthy${NC}"
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}⚠ Health check failed (attempt ${retry}/${MAX_RETRIES}), retrying...${NC}"
            sleep 2
        fi
    done

    echo -e "${RED}✗ Service is not healthy after ${MAX_RETRIES} attempts${NC}"
    return 1
}

# Function to check detailed health
check_detailed_health() {
    echo "Checking detailed service health..."

    local response=$(curl -s --max-time 10 "http://${HOST}:${PORT}/api/health" || echo "")

    if [ -n "$response" ]; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 0
    else
        echo -e "${RED}✗ Failed to get detailed health status${NC}"
        return 1
    fi
}

# Main execution
echo "=========================================="
echo "Choreo AI Assistant - Readiness Check"
echo "=========================================="
echo "Host: ${HOST}"
echo "Port: ${PORT}"
echo "Timeout: ${TIMEOUT}s"
echo "Max Retries: ${MAX_RETRIES}"
echo "=========================================="
echo ""

# Basic health check
if check_health; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Service is ready to accept traffic${NC}"
    echo "=========================================="
    exit 0
else
    echo ""
    echo "=========================================="
    echo -e "${RED}Service is NOT ready${NC}"
    echo "=========================================="
    exit 1
fi

