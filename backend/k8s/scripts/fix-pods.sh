#!/bin/bash

# Script to rebuild images and restart pods in Minikube

set -e

echo "🔧 Fixing Backend Pods - Complete Script"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Setting Minikube Docker Environment${NC}"
eval $(minikube docker-env)
echo "✓ Using Minikube's Docker"
echo ""

echo -e "${YELLOW}Step 2: Building Backend Image${NC}"
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
docker build -t choreo-ai-backend:latest -f Dockerfile .
echo "✓ Backend image built"
echo ""

echo -e "${YELLOW}Step 3: Building Frontend Image${NC}"
cd frontend
docker build -t choreo-ai-frontend:latest .
cd ..
echo "✓ Frontend image built"
echo ""

echo -e "${YELLOW}Step 4: Verifying Images${NC}"
docker images | grep choreo-ai
echo ""

echo -e "${YELLOW}Step 5: Deleting Old Backend Pods${NC}"
kubectl delete pods -n choreo-ai-assistant -l app=choreo-ai-backend
echo "✓ Old backend pods deleted"
echo ""

echo -e "${YELLOW}Step 6: Waiting for New Pods to Start${NC}"
sleep 5
kubectl get pods -n choreo-ai-assistant
echo ""

echo -e "${YELLOW}Step 7: Waiting for Pods to be Ready (30s)${NC}"
sleep 30
kubectl get pods -n choreo-ai-assistant
echo ""

echo -e "${GREEN}Step 8: Checking Pod Status${NC}"
kubectl get pods -n choreo-ai-assistant -o wide
echo ""

echo -e "${GREEN}Step 9: Checking Backend Logs${NC}"
BACKEND_POD=$(kubectl get pod -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}')
echo "Backend pod: $BACKEND_POD"
kubectl logs -n choreo-ai-assistant $BACKEND_POD --tail=20 || echo "Pod not ready yet"
echo ""

echo "========================================"
echo -e "${GREEN}✓ Script Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Check if pods are Running: kubectl get pods -n choreo-ai-assistant"
echo "2. If still crashing, check logs: kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend --tail=50"
echo "3. Port-forward: kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090"

