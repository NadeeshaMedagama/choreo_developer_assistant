#!/bin/bash

# Choreo AI Assistant - Build Docker Images Script
# This script builds both backend and frontend Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Navigate to project root (3 levels up from scripts directory: scripts -> k8s -> backend -> project root)
cd "$(dirname "$0")/../../.."

PROJECT_ROOT=$(pwd)
print_info "Project root: $PROJECT_ROOT"

# Get image tag from argument or use 'latest'
IMAGE_TAG="${1:-latest}"
print_info "Building images with tag: $IMAGE_TAG"

# Build backend image
print_info "Building backend image..."
docker build -t choreo-ai-backend:$IMAGE_TAG -f Dockerfile .
print_info "✓ Backend image built: choreo-ai-backend:$IMAGE_TAG"

# Build frontend image
print_info "Building frontend image..."
docker build -t choreo-ai-frontend:$IMAGE_TAG -f frontend/Dockerfile ./frontend
print_info "✓ Frontend image built: choreo-ai-frontend:$IMAGE_TAG"

echo ""
print_info "All images built successfully!"
echo ""
print_info "Available images:"
docker images | grep choreo-ai

echo ""
print_info "Next steps:"
echo "  1. If using Minikube, set docker env:"
echo "     eval \$(minikube docker-env)"
echo "     Then run this script again"
echo ""
echo "  2. If using Kind, load images:"
echo "     kind load docker-image choreo-ai-backend:$IMAGE_TAG"
echo "     kind load docker-image choreo-ai-frontend:$IMAGE_TAG"
echo ""
echo "  3. If using cloud registry, tag and push:"
echo "     docker tag choreo-ai-backend:$IMAGE_TAG your-registry/choreo-ai-backend:$IMAGE_TAG"
echo "     docker push your-registry/choreo-ai-backend:$IMAGE_TAG"
echo ""
echo "  4. Deploy to Kubernetes:"
echo "     cd backend/k8s && ./deploy.sh"

