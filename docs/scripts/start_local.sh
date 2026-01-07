#!/bin/bash
# Startup script for running both backend and frontend locally
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Choreo AI Assistant - Local Setup${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    wait
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM
# Check directories
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found${NC}"
    exit 1
fi
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found${NC}"
    exit 1
fi
# Check .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: backend/.env not found${NC}"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
# Create logs directories
mkdir -p "$BACKEND_DIR/logs"
mkdir -p "$FRONTEND_DIR/logs"
# Start backend
echo -e "${BLUE}[1/3]${NC} Starting Backend on ${GREEN}http://localhost:8000${NC}"
cd "$BACKEND_DIR"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload > logs/local_backend.log 2>&1 &
BACKEND_PID=$!
echo -e "      PID: $BACKEND_PID"
# Wait for backend
echo -e "${YELLOW}      Waiting for backend...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}      ✓ Backend running${NC}"
        break
    fi
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}      ✗ Backend failed${NC}"
        exit 1
    fi
    sleep 1
done
echo ""
# Check frontend dependencies
echo -e "${BLUE}[2/3]${NC} Checking Frontend dependencies"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}      Installing...${NC}"
    npm install
fi
echo -e "${GREEN}      ✓ Ready${NC}"
echo ""
# Start frontend
echo -e "${BLUE}[3/3]${NC} Starting Frontend on ${GREEN}http://localhost:5173${NC}"
npm run dev > logs/local_frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "      PID: $FRONTEND_PID"
sleep 2
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ Application is running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Frontend:  ${GREEN}http://localhost:5173${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""
# Wait for processes
wait
