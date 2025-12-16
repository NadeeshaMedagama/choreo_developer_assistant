#!/bin/bash

# Quick Start Script for Backend + Ngrok
# This script helps you run both backend and ngrok

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Choreo AI Assistant - Backend + Ngrok Starter        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend is running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is already running on port 8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend is NOT running on port 8000${NC}"
    echo ""
    echo "To start the backend, open a NEW terminal and run:"
    echo -e "${BLUE}cd '/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant'${NC}"
    echo -e "${BLUE}python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload${NC}"
    echo ""
    read -p "Press Enter when backend is running, or Ctrl+C to cancel..."
fi

echo ""
echo -e "${GREEN}Starting ngrok tunnel on port 8000...${NC}"
echo ""

# Start ngrok
~/bin/ngrok http 8000

