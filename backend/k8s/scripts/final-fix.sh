#!/bin/bash

# FINAL FIX SCRIPT - This will get your pods running!

set -e

echo "🚀 FINAL FIX - Complete Rebuild and Redeploy"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "Step 1: Setting Minikube Docker environment..."
eval $(minikube docker-env)
echo "✓ Using Minikube's Docker daemon"
echo ""

print_info "Step 2: Checking current images..."
docker images | grep choreo-ai-backend | head -3
echo ""

print_info "Step 3: Deleting old deployment..."
kubectl delete deployment choreo-ai-backend -n choreo-ai-assistant || true
sleep 5
echo "✓ Old deployment deleted"
echo ""

print_info "Step 4: Applying updated deployment (with imagePullPolicy: Never)..."
kubectl apply -f /home/nadeeshame/CHOREO\ AI\ Assistant/choreo-ai-assistant/backend/k8s/base/deployments/backend-deployment.yaml
echo "✓ Deployment applied"
echo ""

print_info "Step 5: Waiting for pods to start (30 seconds)..."
sleep 30
echo ""

print_info "Step 6: Checking pod status..."
kubectl get pods -n choreo-ai-assistant
echo ""

print_info "Step 7: Checking backend pod logs..."
BACKEND_POD=$(kubectl get pod -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    echo "Backend pod: $BACKEND_POD"
    kubectl logs -n choreo-ai-assistant $BACKEND_POD --tail=30 || true
else
    print_warn "No backend pods found yet, waiting longer..."
    sleep 30
    kubectl get pods -n choreo-ai-assistant
fi
echo ""

print_info "==========================================="
print_info "If pods are STILL crashing with RemoveMessage error:"
echo "  1. The image might not have been built correctly in Minikube"
echo "  2. Run: eval \$(minikube docker-env) && docker images | grep choreo-ai"
echo "  3. Rebuild with: cd /path/to/project && docker build --no-cache -t choreo-ai-backend:latest -f Dockerfile ."
echo ""
print_info "If pods are Running:"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80 &"
echo "  curl http://localhost:9090/health"

