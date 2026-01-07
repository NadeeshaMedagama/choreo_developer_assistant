#!/bin/bash
# Local development startup script for frontend
cd "$(dirname "$0")"
echo "============================================"
echo "  Choreo AI Assistant - Frontend"
echo "============================================"
echo ""
echo "Starting on: http://localhost:5173"
echo ""
echo "Make sure backend is running on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi
# Start Vite dev server
npm run dev
