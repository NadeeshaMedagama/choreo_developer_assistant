#!/bin/bash

# Choreo AI Assistant - Status Check Script
# This script displays the current status of all K8s resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Check if namespace exists
if ! kubectl get namespace choreo-ai-assistant &> /dev/null; then
    echo -e "${RED}Namespace 'choreo-ai-assistant' does not exist.${NC}"
    echo "Run './deploy.sh' to deploy the application."
    exit 1
fi

print_header "Choreo AI Assistant - Status"

# Namespace info
print_info "Namespace:"
kubectl get namespace choreo-ai-assistant

# Pods
print_header "Pods"
kubectl get pods -n choreo-ai-assistant -o wide

# Deployments
print_header "Deployments"
kubectl get deployments -n choreo-ai-assistant

# Services
print_header "Services"
kubectl get services -n choreo-ai-assistant

# Ingress
print_header "Ingress"
kubectl get ingress -n choreo-ai-assistant

# HPA
print_header "Horizontal Pod Autoscalers"
kubectl get hpa -n choreo-ai-assistant

# PVC
print_header "Persistent Volume Claims"
kubectl get pvc -n choreo-ai-assistant

# ConfigMap
print_header "ConfigMaps"
kubectl get configmap -n choreo-ai-assistant

# Secrets
print_header "Secrets"
kubectl get secret -n choreo-ai-assistant

# Events
print_header "Recent Events"
kubectl get events -n choreo-ai-assistant --sort-by='.lastTimestamp' | tail -20

# Resource usage (if metrics-server is installed)
print_header "Resource Usage"
if kubectl top nodes &> /dev/null; then
    echo "Node metrics:"
    kubectl top nodes
    echo ""
    echo "Pod metrics:"
    kubectl top pods -n choreo-ai-assistant
else
    echo -e "${YELLOW}Metrics server not installed. Cannot show resource usage.${NC}"
fi

# Quick health check
print_header "Health Check"
BACKEND_POD=$(kubectl get pods -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$BACKEND_POD" ]; then
    echo "Testing backend health endpoint..."
    if kubectl exec -n choreo-ai-assistant "$BACKEND_POD" -- curl -s http://localhost:9090/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${RED}✗ Backend health check failed${NC}"
    fi
else
    echo -e "${YELLOW}No backend pods found${NC}"
fi

echo ""
print_info "For detailed pod logs, run:"
echo "  kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f"
echo "  kubectl logs -n choreo-ai-assistant -l app=choreo-ai-frontend -f"
echo ""
print_info "To access the application:"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090"

