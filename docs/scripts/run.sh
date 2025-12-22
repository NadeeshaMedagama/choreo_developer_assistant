#!/bin/bash

# DevChoreo - Complete Setup and Run Script
# This script checks dependencies, installs if needed, and starts the application

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 DevChoreo - AI Assistant Setup & Runner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get the script directory (project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check .env file
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env not found!${NC}"
    echo "Please create backend/.env with your API keys."
    echo "See backend/.env.example or README.md for details."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found backend/.env"
echo ""

# Check Python
echo -e "${BLUE}Checking Python...${NC}"

# Prefer python over python3 (better for virtual environments)
if command -v python &> /dev/null; then
    PYTHON_CMD=$(command -v python)
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=$(command -v python3)
else
    echo -e "${RED}❌ Python not found! Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check pip (works with virtual environments)
if $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_VERSION=$($PYTHON_CMD -m pip --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} pip $PIP_VERSION found"
else
    echo -e "${RED}❌ pip not found! Run: $PYTHON_CMD -m ensurepip --upgrade${NC}"
    exit 1
fi
echo ""

# Check if backend dependencies are installed
echo -e "${BLUE}Checking Python dependencies...${NC}"
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing Python dependencies (this may take a few minutes)...${NC}"
    $PYTHON_CMD -m pip install -q -r backend/requirements.txt
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${GREEN}✓${NC} Python dependencies already installed"
fi
echo ""

# Check Node.js
echo -e "${BLUE}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found! Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found! Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} npm found"
echo ""

# Check if frontend dependencies are installed
echo -e "${BLUE}Checking frontend dependencies...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing frontend dependencies (this may take a minute)...${NC}"
    cd frontend
    npm install --silent
    cd ..
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${GREEN}✓${NC} Frontend dependencies already installed"
fi
echo ""

# Check if ports are available
echo -e "${BLUE}Checking if ports are available...${NC}"

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
    echo "Would you like to kill the process? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Freed port 8000"
    else
        echo "Please free port 8000 manually and try again"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Port 8000 is available"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 5173 is already in use${NC}"
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Freed port 5173"
else
    echo -e "${GREEN}✓${NC} Port 5173 is available"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✓ All checks passed! Starting services...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
$PYTHON_CMD -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo -n "   Waiting for backend to start"
for i in {1..15}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} Backend started successfully"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check if backend started successfully
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
    tail -n 20 backend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Test Pinecone connection
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Pinecone connected"
else
    echo -e "${YELLOW}⚠️  Pinecone connection issue (app will still work for ingestion)${NC}"
fi
echo ""

# Start frontend
echo -e "${BLUE}🎨 Starting Frontend (React + Vite)...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo -n "   Waiting for frontend to start"
for i in {1..15}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} Frontend started successfully"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check if frontend started successfully
if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend may still be starting. Give it a few more seconds.${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✨ DevChoreo is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${BLUE}Health:${NC}    http://localhost:8000/api/health"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Ingest docs: curl -X POST 'http://localhost:8000/api/ingest/github?repo_url=https://github.com/NadeeshaMedagama/docs-choreo-dev'"
echo "   3. Ask questions in the UI!"
echo ""
echo -e "${YELLOW}📋 Logs:${NC}"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo -e "${RED}Press Ctrl+C to stop all services${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save PIDs to file for cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"

    # Kill backend
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend.pid
        echo -e "${GREEN}✓${NC} Backend stopped"
    fi

    # Kill frontend
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend.pid
        echo -e "${GREEN}✓${NC} Frontend stopped"
    fi

    # Kill any remaining processes
    pkill -f "uvicorn backend.app:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true

    echo -e "${GREEN}✓${NC} All services stopped"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Keep script running and monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend crashed! Check backend.log${NC}"
        tail -n 30 backend.log
        cleanup
    fi

    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend crashed! Check frontend.log${NC}"
        tail -n 30 frontend.log
        cleanup
    fi

    sleep 5
done
