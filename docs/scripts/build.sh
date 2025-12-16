#!/bin/bash
# Quick build and run script

set -e  # Exit on error

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "🐳 Building Choreo Ingestion Docker Image..."
cd "$SCRIPT_DIR"
docker-compose -f docker-compose.yml build

echo ""
echo "✅ Build complete!"
echo ""
echo "Available commands:"
echo "  cd docker && docker-compose up              # Run ingestion"
echo "  cd docker && docker-compose up -d           # Run in background"
echo "  cd docker && docker-compose logs -f         # View logs"
echo "  cd docker && docker-compose down            # Stop service"
echo ""
echo "Run ingestion now? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "🚀 Starting ingestion..."
    docker-compose -f docker-compose.yml up
fi
