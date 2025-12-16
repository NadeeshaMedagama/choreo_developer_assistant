#!/bin/bash

# DevChoreo - Start Development Environment
# This script starts both backend and frontend servers

set -e

echo "🚀 Starting DevChoreo Development Environment..."
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found!"
    echo "Please create backend/.env with your API keys. See README.md for details."
    echo ""
fi

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start backend
echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo -e "${GREEN}✓ Backend running on http://localhost:8000${NC}"
echo ""

# Start frontend
echo -e "${BLUE}🎨 Starting Frontend (React + Vite)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend running on http://localhost:5173${NC}"
echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✓ DevChoreo is ready!${NC}"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Health:   http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "═══════════════════════════════════════════════════════"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    # Kill any remaining processes
    pkill -f "uvicorn app:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo "✓ Stopped"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID

