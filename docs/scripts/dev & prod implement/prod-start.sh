#!/bin/bash
# Production-like server startup script
# Run this from the project root directory

cd "$(dirname "$0")/backend"
echo "Starting Choreo AI Assistant Backend (Production Mode)"
echo "Working directory: $(pwd)"
echo ""
python -m uvicorn app:app --host 0.0.0.0 --port 9090

