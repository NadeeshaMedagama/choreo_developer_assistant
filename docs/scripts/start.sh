#!/bin/bash
# Simple startup script for DevChoreo - works with virtual environments

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

echo "🚀 Starting DevChoreo..."
echo ""

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "✓ Ready to start!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting Backend and Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend
echo "🔧 Starting Backend on port 8000..."
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend
sleep 5

# Start frontend
echo "🎨 Starting Frontend on port 5173..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"

# Wait for frontend
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ DevChoreo is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  Health:    http://localhost:8000/api/health"
echo ""
echo "📝 Next Steps:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Ingest docs with this command in another terminal:"
echo "      curl -X POST 'http://localhost:8000/api/ingest/github?repo_url=https://github.com/NadeeshaMedagama/docs-choreo-dev'"
echo ""
echo "📋 View Logs:"
echo "   tail -f backend.log"
echo "   tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cleanup on exit
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; pkill -f 'uvicorn backend.app:app' 2>/dev/null; pkill -f 'vite' 2>/dev/null; echo 'Stopped'; exit 0" SIGINT SIGTERM

# Keep running
wait

