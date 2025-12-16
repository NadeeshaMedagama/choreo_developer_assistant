#!/bin/bash

# Start Ngrok for Backend Service
# Port 8000 (your actual backend port)

echo "🚀 Starting ngrok tunnel for backend on port 8000..."
echo "⏹️  Press Ctrl+C to stop"
echo ""
echo "📡 Once started, you'll get a public URL like:"
echo "   https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""

~/bin/ngrok http 8000

