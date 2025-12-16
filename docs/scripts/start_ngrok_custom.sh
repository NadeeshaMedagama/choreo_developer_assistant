#!/bin/bash

# Start Ngrok with custom port
# Usage: ./start_ngrok_custom.sh <port>

if [ -z "$1" ]; then
    echo "Usage: $0 <port>"
    echo "Example: $0 8080"
    exit 1
fi

PORT=$1

echo "Starting ngrok tunnel on port $PORT..."
echo "Press Ctrl+C to stop"
echo ""
echo "Once started, you'll get a public URL like: https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""

ngrok http $PORT

