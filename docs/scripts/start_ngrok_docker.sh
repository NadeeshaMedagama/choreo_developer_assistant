#!/bin/bash

# Start Ngrok for Docker Compose Backend
# Port 8000 (as configured in docker-compose.yml)

echo "Starting ngrok tunnel for backend (docker-compose) on port 8000..."
echo "Press Ctrl+C to stop"
echo ""
echo "Once started, you'll get a public URL like: https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""

ngrok http 8000

