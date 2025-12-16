#!/bin/bash

# Start Ngrok for Frontend Service
# Port 5173 (Vite dev server default)

echo "Starting ngrok tunnel for frontend on port 5173..."
echo "Press Ctrl+C to stop"
echo ""
echo "Once started, you'll get a public URL like: https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""

ngrok http 5173

