#!/bin/bash

# CRITICAL FIX: Build Images in Minikube's Docker
# The issue: You built images in HOST Docker, not Minikube's Docker!

set -e

echo "=========================================="
echo "🚨 CRITICAL: Building in MINIKUBE Docker"
echo "=========================================="
echo ""

# STEP 1: Set Minikube Docker environment
echo "Step 1: Setting Minikube Docker environment..."
eval $(minikube docker-env)
echo "✓ Now using Minikube's Docker daemon"
echo ""

# Verify we're using Minikube
echo "Verifying Docker context:"
docker context ls | grep -E "NAME|minikube" || docker info | grep -i "name"
echo ""

# STEP 2: Build Backend (this will take 10-15 minutes!)
echo "Step 2: Building BACKEND image in Minikube..."
echo "⏱️  This will take 10-15 minutes - BE PATIENT!"
echo "Using --no-cache to ensure fresh dependencies are installed"
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

docker build --no-cache -t choreo-ai-backend:latest -f Dockerfile .

echo "✓ Backend image built in Minikube's Docker"
echo ""

# STEP 3: Build Frontend (fast)
echo "Step 3: Building FRONTEND image in Minikube..."
cd frontend
docker build --no-cache -t choreo-ai-frontend:latest .
cd ..

echo "✓ Frontend image built in Minikube's Docker"
echo ""

# STEP 4: Verify images exist in Minikube
echo "Step 4: Verifying images in Minikube's Docker..."
docker images | grep choreo-ai
echo ""

# STEP 5: Delete old pods
echo "Step 5: Deleting old backend pods..."
kubectl delete pods -n choreo-ai-assistant -l app=choreo-ai-backend || true
echo "✓ Old pods deleted"
echo ""

# STEP 6: Wait for new pods
echo "Step 6: Waiting for new pods to start (60 seconds)..."
sleep 60
echo ""

# STEP 7: Check status
echo "Step 7: Checking pod status..."
kubectl get pods -n choreo-ai-assistant
echo ""

echo "=========================================="
echo "✅ BUILD COMPLETE IN MINIKUBE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Wait 1-2 minutes for pods to fully start"
echo "2. Check: kubectl get pods -n choreo-ai-assistant"
echo "3. Check logs if still crashing: kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend --tail=50"
echo ""

