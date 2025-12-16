#!/bin/bash
# Choreo AI Assistant - Automatic Kubernetes Deployment Script (No prompts)
# This script deploys without asking for confirmation
set -e
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Choreo AI Assistant - K8s Deployment        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}
print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}
# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi
# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubectl configuration."
    exit 1
fi
print_info "Connected to Kubernetes cluster: $(kubectl config current-context)"
# Deploy using kustomize
print_info "Deploying Choreo AI Assistant using kustomize..."
cd "$(dirname "$0")/.."
# Apply all resources
print_info "Applying Kubernetes manifests..."
kubectl apply -k .
print_info "Waiting for namespace to be ready..."
kubectl wait --for=jsonpath='{.status.phase}'=Active namespace/choreo-ai-assistant --timeout=60s 2>/dev/null || true
print_info "Waiting for deployments to be ready..."
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant --timeout=300s 2>/dev/null || print_warning "Backend deployment not ready yet"
kubectl rollout status deployment/choreo-ai-frontend -n choreo-ai-assistant --timeout=300s 2>/dev/null || print_warning "Frontend deployment not ready yet"
echo ""
print_info "Deployment completed!"
echo ""
# Display pod status
print_info "Pod Status:"
kubectl get pods -n choreo-ai-assistant
echo ""
print_info "Service Status:"
kubectl get svc -n choreo-ai-assistant
echo ""
print_info "To access the application:"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80 &"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &"
echo ""
echo "Then visit:"
echo "  Frontend: http://localhost:8080"
echo "  Backend:  http://localhost:9090"
