#!/bin/bash

# Choreo AI Assistant - Cleanup Script
# This script removes all Kubernetes resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${RED}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  Choreo AI Assistant - K8s Cleanup           ║${NC}"
echo -e "${RED}╚═══════════════════════════════════════════════╝${NC}"
echo ""

print_warning "This will delete all Choreo AI Assistant resources from Kubernetes!"
print_warning "This includes:"
echo "  - All deployments and pods"
echo "  - All services"
echo "  - All persistent volume claims (DATA WILL BE LOST)"
echo "  - The entire choreo-ai-assistant namespace"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Cleanup cancelled."
    exit 0
fi

cd "$(dirname "$0")"

print_info "Deleting all resources..."

# Try to delete using kustomize first
if kubectl delete -k . 2>/dev/null; then
    print_info "Resources deleted using kustomize"
else
    print_warning "Kustomize delete failed, deleting namespace instead..."
    kubectl delete namespace choreo-ai-assistant 2>/dev/null || true
fi

print_info "Waiting for namespace to be fully deleted..."
kubectl wait --for=delete namespace/choreo-ai-assistant --timeout=120s 2>/dev/null || true

echo ""
print_info "Cleanup completed!"
print_info "All Choreo AI Assistant resources have been removed from the cluster."

