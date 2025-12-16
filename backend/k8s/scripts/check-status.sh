#!/bin/bash

# Quick status checker for the rebuild process

echo "🔍 Checking Rebuild Status..."
echo "================================"
echo ""

# Check if images exist in Minikube
echo "Images in Minikube Docker:"
eval $(minikube docker-env)
docker images | grep choreo-ai | head -5
echo ""

# Check pod status
echo "Pod Status:"
kubectl get pods -n choreo-ai-assistant
echo ""

# Check latest backend pod logs
echo "Latest Backend Pod Log (last 10 lines):"
BACKEND_POD=$(kubectl get pod -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    kubectl logs -n choreo-ai-assistant $BACKEND_POD --tail=10 2>&1 | tail -5 || echo "Pod not ready yet"
else
    echo "No backend pods found yet"
fi
echo ""

echo "================================"
echo ""
echo "To check build progress, run:"
echo "  tail -20 /tmp/backend-build.log"
echo ""
echo "To watch pods:"
echo "  kubectl get pods -n choreo-ai-assistant -w"

