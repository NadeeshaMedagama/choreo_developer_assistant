#!/bin/bash
# Local development startup script for backend
cd "$(dirname "$0")"
echo "============================================"
echo "  Choreo AI Assistant - Backend Server"
echo "============================================"
echo ""
echo "Starting on: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Health:      http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""
# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Copy .env.example to .env and configure it"
    echo ""
fi
# Start uvicorn with hot reload
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
