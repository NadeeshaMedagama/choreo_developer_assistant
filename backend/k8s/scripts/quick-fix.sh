#!/bin/bash

# Quick Fix Script - Rebuild and Redeploy Backend
# This script fixes the langchain dependency issue and redeploys

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Quick Fix: Rebuild & Redeploy Backend                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_step() {
    echo -e "${BLUE}[→]${NC} $1"
}

print_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Navigate to project root
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Step 1: Build new image
print_step "Building new Docker image with fixed dependencies..."
echo "This may take several minutes..."
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile . > /tmp/docker-build.log 2>&1 &
BUILD_PID=$!

# Show progress
while kill -0 $BUILD_PID 2>/dev/null; do
    echo -n "."
    sleep 2
done
wait $BUILD_PID
BUILD_STATUS=$?

if [ $BUILD_STATUS -eq 0 ]; then
    print_info "Docker image built successfully"
else
    echo -e "${RED}[✗]${NC} Docker build failed. Check /tmp/docker-build.log"
    tail -50 /tmp/docker-build.log
    exit 1
fi

# Step 2: Load image into Minikube
print_step "Loading image into Minikube..."
minikube image load choreo-ai-backend:v2-fixed

print_info "Image loaded into Minikube"

# Step 3: Restart deployment
print_step "Restarting backend deployment..."
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

print_step "Waiting for new pods to start..."
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant --timeout=5m

# Step 4: Check status
print_step "Checking pod status..."
kubectl get pods -n choreo-ai-assistant -l app=choreo-ai-backend

echo ""
print_info "Backend redeployment complete!"
echo ""
echo "To check logs:"
echo "  kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f"
echo ""
echo "To test health:"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090"
echo "  curl http://localhost:9090/health"

