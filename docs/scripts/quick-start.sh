#!/bin/bash
# Quick Start - DevChoreo Project
# Run this script to start everything with one command

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

echo "🚀 Starting DevChoreo..."
echo ""

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Run the comprehensive script
./run.sh

