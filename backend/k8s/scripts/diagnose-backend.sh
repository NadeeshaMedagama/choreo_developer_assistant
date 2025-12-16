#!/bin/bash

# Choreo AI Assistant - Backend Diagnostic Script
# This script diagnoses issues with the backend Kubernetes deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

NAMESPACE="choreo-ai-assistant"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Choreo AI Assistant - Backend Diagnostics               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_info() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_step() { echo -e "${BLUE}[→]${NC} $1"; }

# ============================================================================
# Check Cluster Connection
# ============================================================================
print_header "Cluster Connection"

if kubectl cluster-info >/dev/null 2>&1; then
    CLUSTER=$(kubectl config current-context 2>/dev/null || echo "unknown")
    print_info "Connected to cluster: $CLUSTER"
else
    print_error "Cannot connect to Kubernetes cluster"
    echo "Please start your cluster first:"
    echo "  - Minikube: minikube start"
    echo "  - Kind: kind create cluster"
    echo "  - Docker Desktop: Enable Kubernetes in settings"
    exit 1
fi

# ============================================================================
# Check Namespace
# ============================================================================
print_header "Namespace Check"

if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    print_info "Namespace '$NAMESPACE' exists"
else
    print_error "Namespace '$NAMESPACE' does not exist"
    echo "The namespace needs to be created. Run the deployment script:"
    echo "  ./scripts/deploy-backend-auto.sh"
    exit 1
fi

# ============================================================================
# Check Backend Pods
# ============================================================================
print_header "Backend Pods Status"

if kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend >/dev/null 2>&1; then
    echo "Current pod status:"
    kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o wide
    echo ""

    # Check for pod issues
    PENDING_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.phase=="Pending")].metadata.name}')
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.phase=="Failed")].metadata.name}')
    CRASHLOOP_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.containerStatuses[0].state.waiting.reason=="CrashLoopBackOff")].metadata.name}')
    IMAGEPULL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.containerStatuses[0].state.waiting.reason=="ImagePullBackOff")].metadata.name}' 2>/dev/null || echo "")
    ERRIMAGEPULL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.containerStatuses[0].state.waiting.reason=="ErrImagePull")].metadata.name}' 2>/dev/null || echo "")

    if [[ -n "$PENDING_PODS" ]]; then
        print_warning "Pending pods detected: $PENDING_PODS"
        for pod in $PENDING_PODS; do
            echo ""
            echo "Diagnosing $pod:"
            kubectl describe pod "$pod" -n "$NAMESPACE" | grep -A 10 "Events:"
        done
    fi

    if [[ -n "$FAILED_PODS" ]]; then
        print_error "Failed pods detected: $FAILED_PODS"
        for pod in $FAILED_PODS; do
            echo ""
            echo "Logs for $pod:"
            kubectl logs "$pod" -n "$NAMESPACE" --tail=30 2>/dev/null || echo "No logs available"
        done
    fi

    if [[ -n "$CRASHLOOP_PODS" ]]; then
        print_error "CrashLoopBackOff pods detected: $CRASHLOOP_PODS"
        echo ""
        echo "Common causes:"
        echo "  1. Application startup errors"
        echo "  2. Missing or incorrect environment variables/secrets"
        echo "  3. Port conflicts"
        echo "  4. Insufficient resources"
        echo ""
        for pod in $CRASHLOOP_PODS; do
            echo "Logs for $pod:"
            kubectl logs "$pod" -n "$NAMESPACE" --tail=50 2>/dev/null || echo "No logs available"
            echo ""
            echo "Previous container logs:"
            kubectl logs "$pod" -n "$NAMESPACE" --previous --tail=50 2>/dev/null || echo "No previous logs"
            echo ""
        done
    fi

    if [[ -n "$IMAGEPULL_PODS" ]] || [[ -n "$ERRIMAGEPULL_PODS" ]]; then
        print_error "Image pull error detected"
        echo ""
        echo "Possible solutions:"
        echo "  1. For local images, ensure imagePullPolicy is set to 'Never'"
        echo "  2. For Minikube: Load image with 'minikube image load choreo-ai-backend:latest'"
        echo "  3. For Kind: Load image with 'kind load docker-image choreo-ai-backend:latest'"
        echo "  4. Verify image exists: docker images | grep choreo-ai-backend"
        echo ""

        for pod in $IMAGEPULL_PODS $ERRIMAGEPULL_PODS; do
            [[ -z "$pod" ]] && continue
            echo "Details for $pod:"
            kubectl describe pod "$pod" -n "$NAMESPACE" | grep -A 5 "Events:"
            echo ""
        done
    fi

    # Check running pods
    RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}')
    if [[ -n "$RUNNING_PODS" ]]; then
        print_info "Running pods: $RUNNING_PODS"
    fi

else
    print_error "No backend pods found"
    echo "Backend deployment may not exist. Check deployment:"
    kubectl get deployment -n "$NAMESPACE" 2>/dev/null || echo "No deployments found"
fi

# ============================================================================
# Check Deployment
# ============================================================================
print_header "Deployment Status"

if kubectl get deployment choreo-ai-backend -n "$NAMESPACE" >/dev/null 2>&1; then
    kubectl get deployment choreo-ai-backend -n "$NAMESPACE"
    echo ""
    kubectl describe deployment choreo-ai-backend -n "$NAMESPACE" | grep -A 10 "Replicas:"
else
    print_error "Backend deployment not found"
    echo "Create deployment with: kubectl apply -f base/deployments/backend-deployment.yaml"
fi

# ============================================================================
# Check Service
# ============================================================================
print_header "Service Status"

if kubectl get svc choreo-ai-backend-service -n "$NAMESPACE" >/dev/null 2>&1; then
    kubectl get svc choreo-ai-backend-service -n "$NAMESPACE"
    echo ""
    print_info "Service exists"

    # Check endpoints
    ENDPOINTS=$(kubectl get endpoints choreo-ai-backend-service -n "$NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)
    if [[ -n "$ENDPOINTS" ]]; then
        print_info "Service has endpoints: $ENDPOINTS"
    else
        print_warning "Service has no endpoints (no ready pods)"
    fi
else
    print_error "Backend service not found"
    echo "Create service with: kubectl apply -f base/services/backend-service.yaml"
fi

# ============================================================================
# Check Secrets
# ============================================================================
print_header "Secrets Check"

if kubectl get secret choreo-ai-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
    print_info "Secret 'choreo-ai-secrets' exists"

    # Check if secrets have placeholder values
    MILVUS_URI=$(kubectl get secret choreo-ai-secrets -n "$NAMESPACE" -o jsonpath='{.data.MILVUS_URI}' | base64 -d 2>/dev/null || echo "")
    if [[ "$MILVUS_URI" == *"your_"* ]] || [[ -z "$MILVUS_URI" ]]; then
        print_warning "Secrets may contain placeholder values"
        echo "Update secrets in: base/config/secret.yaml"
    fi

    # List secret keys
    echo "Secret keys:"
    kubectl get secret choreo-ai-secrets -n "$NAMESPACE" -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || \
    kubectl get secret choreo-ai-secrets -n "$NAMESPACE" -o yaml | grep -A 20 "^data:" | grep "  " | cut -d: -f1
else
    print_error "Secret 'choreo-ai-secrets' not found"
    echo "Create secret with: kubectl apply -f base/config/secret.yaml"
fi

# ============================================================================
# Check ConfigMap
# ============================================================================
print_header "ConfigMap Check"

if kubectl get configmap choreo-ai-config -n "$NAMESPACE" >/dev/null 2>&1; then
    print_info "ConfigMap 'choreo-ai-config' exists"
else
    print_error "ConfigMap 'choreo-ai-config' not found"
    echo "Create configmap with: kubectl apply -f base/config/configmap.yaml"
fi

# ============================================================================
# Check Recent Events
# ============================================================================
print_header "Recent Events"

kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -20

# ============================================================================
# Check Docker Image
# ============================================================================
print_header "Docker Image Check"

if docker images | grep -q "choreo-ai-backend"; then
    print_info "Backend image exists locally"
    docker images | grep "choreo-ai-backend"
else
    print_error "Backend image not found locally"
    echo "Build image with: docker build -t choreo-ai-backend:latest -f docker/Dockerfile ."
fi

# ============================================================================
# Resource Usage (if metrics-server available)
# ============================================================================
print_header "Resource Usage"

if kubectl top nodes >/dev/null 2>&1; then
    echo "Node metrics:"
    kubectl top nodes
    echo ""
    echo "Pod metrics:"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "No pod metrics available"
else
    print_warning "Metrics server not available"
fi

# ============================================================================
# Recommendations
# ============================================================================
print_header "Recommendations"

echo "Based on the diagnostics above, try these solutions:"
echo ""
echo "1. If pods are in CrashLoopBackOff:"
echo "   - Check logs: kubectl logs -n $NAMESPACE <pod-name>"
echo "   - Check secrets: kubectl get secret choreo-ai-secrets -n $NAMESPACE -o yaml"
echo "   - Verify environment variables in deployment"
echo ""
echo "2. If pods are in ImagePullBackOff:"
echo "   - Build image: docker build -t choreo-ai-backend:latest -f docker/Dockerfile ."
echo "   - For Minikube: minikube image load choreo-ai-backend:latest"
echo "   - For Kind: kind load docker-image choreo-ai-backend:latest"
echo "   - Set imagePullPolicy to 'Never' in deployment"
echo ""
echo "3. If no pods are created:"
echo "   - Check deployment: kubectl get deployment -n $NAMESPACE"
echo "   - Apply deployment: kubectl apply -f base/deployments/backend-deployment.yaml"
echo ""
echo "4. To redeploy backend:"
echo "   - Run: ./scripts/deploy-backend-auto.sh"
echo ""
echo "5. To delete and start fresh:"
echo "   - kubectl delete namespace $NAMESPACE"
echo "   - Then run: ./scripts/deploy-backend-auto.sh"
echo ""

print_info "Diagnostics complete!"
echo ""
echo "For automated deployment, run:"
echo "  ./scripts/deploy-backend-auto.sh"

