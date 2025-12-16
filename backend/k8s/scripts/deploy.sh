#!/bin/bash
# Choreo AI Assistant - Kubernetes Deployment Script
# This script helps deploy the Choreo AI Assistant to Kubernetes
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
# Check if secrets need to be updated
print_warning "Before deploying, make sure you have updated the secrets in base/config/secret.yaml"
read -p "Have you updated the secrets? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please update base/config/secret.yaml with your actual API keys before deploying."
    exit 1
fi
# Deploy using kustomize
print_info "Deploying Choreo AI Assistant using kustomize..."
cd "$(dirname "$0")/.."
# Apply all resources
kubectl apply -k .
print_info "Waiting for namespace to be ready..."
kubectl wait --for=jsonpath='{.status.phase}'=Active namespace/choreo-ai-assistant --timeout=60s
print_info "Waiting for deployments to be ready..."
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant --timeout=300s
kubectl rollout status deployment/choreo-ai-frontend -n choreo-ai-assistant --timeout=300s
echo ""
print_info "Deployment completed successfully!"
echo ""
# Display pod status
print_info "Pod Status:"
kubectl get pods -n choreo-ai-assistant
echo ""
print_info "Service Status:"
kubectl get svc -n choreo-ai-assistant
echo ""
print_info "Ingress Status:"
kubectl get ingress -n choreo-ai-assistant
echo ""
print_info "HPA Status:"
kubectl get hpa -n choreo-ai-assistant
echo ""
print_info "To access the application:"
echo "  1. Using port-forward:"
echo "     kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80"
echo "     kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090"
echo ""
echo "  2. Using ingress (add to /etc/hosts):"
echo "     echo \"\$(kubectl get ingress -n choreo-ai-assistant -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}') choreo-ai.local\" | sudo tee -a /etc/hosts"
echo ""
echo "  3. Check logs:"
echo "     kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f"
echo ""
print_info "Health check:"
echo "     kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090"
echo "     curl http://localhost:9090/health"
