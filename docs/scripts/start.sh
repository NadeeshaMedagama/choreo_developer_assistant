#!/bin/bash
# Startup script for Choreo deployment
# Uses PORT environment variable provided by Choreo

# Default to 9090 if PORT is not set (for local development)
PORT=${PORT:-9090}

echo "Starting Choreo AI Assistant on port $PORT..."
echo "Binding to 0.0.0.0:$PORT"

# Start uvicorn with the PORT environment variable
exec uvicorn backend.app:app --host 0.0.0.0 --port "$PORT"

