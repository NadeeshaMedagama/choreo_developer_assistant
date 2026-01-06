#!/bin/bash
# Development server startup script
# Run this from the project root directory

cd "$(dirname "$0")/backend"
echo "Starting Choreo AI Assistant Backend (Development Mode)"
echo "Working directory: $(pwd)"
echo ""
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

