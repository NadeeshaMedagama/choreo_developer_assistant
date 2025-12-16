#!/bin/bash

# Ngrok Setup Script for Choreo AI Assistant
# This script sets up ngrok with the authtoken and creates tunnel configurations

set -e

echo "========================================="
echo "Ngrok Setup for Choreo AI Assistant"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Your ngrok authtoken
NGROK_AUTHTOKEN="34j8bmSyKrTNHW3t2X4FNORQPBa_7sqpGbMobVAnTBoaQvGZj"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}Ngrok not found. Installing ngrok...${NC}"

    # Create local bin directory if it doesn't exist
    mkdir -p ~/bin
    cd ~/bin

    # Download ngrok
    echo "Downloading ngrok..."
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

    # Extract
    echo "Extracting ngrok..."
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    chmod +x ngrok

    # Clean up
    rm ngrok-v3-stable-linux-amd64.tgz

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/bin:$PATH"
    fi

    echo -e "${GREEN}Ngrok installed successfully at ~/bin/ngrok${NC}"
else
    echo -e "${GREEN}Ngrok is already installed at: $(which ngrok)${NC}"
fi

# Configure authtoken
echo ""
echo "Configuring ngrok authtoken..."
ngrok config add-authtoken "$NGROK_AUTHTOKEN"
echo -e "${GREEN}Authtoken configured successfully!${NC}"

# Display ngrok version
echo ""
echo "Ngrok version:"
ngrok version

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Ngrok setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Available ports in your application:"
echo "  - Backend (Dockerfile): 9090"
echo "  - Backend (docker-compose): 8000"
echo "  - Frontend (dev): 5173"
echo ""
echo "To start ngrok tunnels, use one of these commands:"
echo ""
echo "  ${YELLOW}Backend (port 9090):${NC}"
echo "    ngrok http 9090"
echo ""
echo "  ${YELLOW}Backend (docker-compose port 8000):${NC}"
echo "    ngrok http 8000"
echo ""
echo "  ${YELLOW}Frontend (port 5173):${NC}"
echo "    ngrok http 5173"
echo ""
echo "  ${YELLOW}Custom port (e.g., 8080):${NC}"
echo "    ngrok http 8080"
echo ""
echo "Or use the provided helper scripts:"
echo "  ./start_ngrok_backend.sh  - Start ngrok for backend (port 9090)"
echo "  ./start_ngrok_frontend.sh - Start ngrok for frontend (port 5173)"
echo ""

