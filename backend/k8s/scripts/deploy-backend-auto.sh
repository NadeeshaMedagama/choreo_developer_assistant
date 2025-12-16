#!/bin/bash

# Choreo AI Assistant - Automated Backend Deployment Script
# This script automatically diagnoses issues and deploys the backend to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="choreo-ai-assistant"
BACKEND_IMAGE="choreo-ai-backend:latest"
DEPLOYMENT_NAME="choreo-ai-backend"
SERVICE_NAME="choreo-ai-backend-service"

# Navigate to k8s directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Choreo AI Assistant - Backend Auto Deployment           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored messages
print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[→]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================
print_header "Step 1: Checking Prerequisites"

# Check kubectl
print_step "Checking kubectl..."
if command_exists kubectl; then
    print_info "kubectl is installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client 2>&1 | head -1)"
else
    print_error "kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check Docker
print_step "Checking Docker..."
if command_exists docker; then
    if docker ps >/dev/null 2>&1; then
        print_info "Docker is running"
    else
        print_error "Docker is installed but not running"
        echo "Please start Docker and try again"
        exit 1
    fi
else
    print_error "Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Kubernetes cluster
print_step "Checking Kubernetes cluster..."
if kubectl cluster-info >/dev/null 2>&1; then
    CLUSTER_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
    print_info "Connected to cluster: $CLUSTER_CONTEXT"
else
    print_error "Cannot connect to Kubernetes cluster"
    echo ""
    echo "Please start a Kubernetes cluster. Options:"
    echo "  - Minikube: minikube start --cpus=4 --memory=8192"
    echo "  - Kind: kind create cluster --name choreo-cluster"
    echo "  - Docker Desktop: Enable Kubernetes in settings"
    exit 1
fi

# Detect cluster type
CLUSTER_TYPE="unknown"
if kubectl config current-context 2>/dev/null | grep -q "minikube"; then
    CLUSTER_TYPE="minikube"
    print_info "Detected cluster type: Minikube"
elif kubectl config current-context 2>/dev/null | grep -q "kind"; then
    CLUSTER_TYPE="kind"
    print_info "Detected cluster type: Kind"
elif kubectl config current-context 2>/dev/null | grep -q "docker-desktop"; then
    CLUSTER_TYPE="docker-desktop"
    print_info "Detected cluster type: Docker Desktop"
else
    print_warning "Unknown cluster type, proceeding anyway..."
fi

# ============================================================================
# STEP 2: Build or Check Backend Image
# ============================================================================
print_header "Step 2: Backend Docker Image"

print_step "Checking if backend image exists..."
if docker images | grep -q "choreo-ai-backend"; then
    print_info "Backend image found"
    docker images | grep "choreo-ai-backend"
else
    print_warning "Backend image not found"
    read -p "Build backend image now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Building backend image..."
        cd ../../..
        docker build -t choreo-ai-backend:latest -f docker/Dockerfile .
        cd backend/k8s
        print_info "Backend image built successfully"
    else
        print_error "Cannot deploy without backend image"
        exit 1
    fi
fi

# Load image into cluster if needed
if [[ "$CLUSTER_TYPE" == "minikube" ]]; then
    print_step "Checking if image is available in Minikube..."
    if minikube ssh "docker images | grep choreo-ai-backend" >/dev/null 2>&1; then
        print_info "Image already available in Minikube"
    else
        print_step "Loading image into Minikube..."
        minikube image load choreo-ai-backend:latest
        print_info "Image loaded into Minikube"
    fi
elif [[ "$CLUSTER_TYPE" == "kind" ]]; then
    print_step "Loading image into Kind cluster..."
    CLUSTER_NAME=$(kubectl config current-context | sed 's/kind-//')
    kind load docker-image choreo-ai-backend:latest --name "$CLUSTER_NAME"
    print_info "Image loaded into Kind cluster"
fi

# ============================================================================
# STEP 3: Check and Create Namespace
# ============================================================================
print_header "Step 3: Namespace Setup"

print_step "Checking namespace..."
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    print_info "Namespace '$NAMESPACE' already exists"
else
    print_step "Creating namespace..."
    kubectl create namespace "$NAMESPACE"
    print_info "Namespace '$NAMESPACE' created"
fi

# ============================================================================
# STEP 4: Check Secrets
# ============================================================================
print_header "Step 4: Secrets Configuration"

print_step "Checking secrets..."
if kubectl get secret choreo-ai-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
    print_info "Secret 'choreo-ai-secrets' exists"

    # Check if secrets have placeholder values
    MILVUS_URI=$(kubectl get secret choreo-ai-secrets -n "$NAMESPACE" -o jsonpath='{.data.MILVUS_URI}' | base64 -d 2>/dev/null || echo "")
    if [[ "$MILVUS_URI" == *"your_"* ]] || [[ -z "$MILVUS_URI" ]]; then
        print_warning "Secrets contain placeholder values"
        echo ""
        echo "Please update your secrets before deploying:"
        echo "  1. Edit: base/config/secret.yaml"
        echo "  2. Or create from environment:"
        echo "     kubectl create secret generic choreo-ai-secrets \\"
        echo "       --from-literal=MILVUS_URI=\$MILVUS_URI \\"
        echo "       --from-literal=MILVUS_TOKEN=\$MILVUS_TOKEN \\"
        echo "       --from-literal=GITHUB_TOKEN=\$GITHUB_TOKEN \\"
        echo "       -n $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Deployment cancelled"
            exit 1
        fi
    fi
else
    print_warning "Secret 'choreo-ai-secrets' not found"

    # Check if .env file exists
    if [[ -f "../../.env" ]]; then
        print_step "Found .env file, creating secrets from it..."

        # Source .env file
        set -a
        source ../../.env
        set +a

        # Create secret
        kubectl create secret generic choreo-ai-secrets \
            --from-literal=MILVUS_URI="${MILVUS_URI:-https://your-milvus-instance.serverless.aws-eu-central-1.cloud.zilliz.com}" \
            --from-literal=MILVUS_TOKEN="${MILVUS_TOKEN:-your_milvus_token}" \
            --from-literal=MILVUS_COLLECTION_NAME="${MILVUS_COLLECTION_NAME:-readme_embeddings}" \
            --from-literal=GITHUB_TOKEN="${GITHUB_TOKEN:-your_github_token}" \
            --from-literal=AZURE_OPENAI_KEY="${AZURE_OPENAI_KEY:-your_azure_openai_key}" \
            --from-literal=AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT:-https://your-resource.openai.azure.com/}" \
            --from-literal=AZURE_OPENAI_DEPLOYMENT="${AZURE_OPENAI_DEPLOYMENT:-your-deployment}" \
            --from-literal=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="${AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT:-your-embeddings-deployment}" \
            --from-literal=GOOGLE_VISION_API_KEY="${GOOGLE_VISION_API_KEY:-}" \
            --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
            -n "$NAMESPACE"

        print_info "Secrets created from .env file"
    else
        print_step "Applying default secrets from secret.yaml..."
        kubectl apply -f base/config/secret.yaml
        print_warning "Using placeholder secrets - update them for production!"
    fi
fi

# ============================================================================
# STEP 5: Deploy Backend
# ============================================================================
print_header "Step 5: Deploying Backend"

print_step "Applying ConfigMap..."
kubectl apply -f base/config/configmap.yaml

print_step "Applying RBAC..."
kubectl apply -f base/security/rbac.yaml

print_step "Applying Backend Deployment..."
kubectl apply -f base/deployments/backend-deployment.yaml

print_step "Applying Backend Service..."
kubectl apply -f base/services/backend-service.yaml

print_info "Backend resources applied"

# ============================================================================
# STEP 6: Wait for Deployment
# ============================================================================
print_header "Step 6: Waiting for Deployment"

print_step "Waiting for pods to be ready..."
echo ""
kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=300s

# ============================================================================
# STEP 7: Check Deployment Status
# ============================================================================
print_header "Step 7: Deployment Status"

# Get pod status
print_step "Pod Status:"
kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o wide

# Check for issues
FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}')
if [[ -n "$FAILED_PODS" ]]; then
    print_warning "Some pods are not running:"
    for pod in $FAILED_PODS; do
        echo ""
        echo "Pod: $pod"
        kubectl describe pod "$pod" -n "$NAMESPACE" | tail -20
        echo ""
        echo "Recent logs:"
        kubectl logs "$pod" -n "$NAMESPACE" --tail=20 2>/dev/null || echo "No logs available"
    done
fi

# Get service status
echo ""
print_step "Service Status:"
kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE"

# ============================================================================
# STEP 8: Health Check
# ============================================================================
print_header "Step 8: Health Check"

BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [[ -n "$BACKEND_POD" ]]; then
    print_step "Testing backend health endpoint..."

    # Wait a bit for the app to fully start
    sleep 5

    if kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- curl -sf http://localhost:9090/health >/dev/null 2>&1; then
        print_info "Backend health check PASSED ✓"

        # Show health response
        echo ""
        echo "Health endpoint response:"
        kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- curl -s http://localhost:9090/health | jq . 2>/dev/null || \
        kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- curl -s http://localhost:9090/health
    else
        print_warning "Backend health check FAILED"
        echo ""
        echo "Checking pod logs for errors:"
        kubectl logs "$BACKEND_POD" -n "$NAMESPACE" --tail=30
    fi
else
    print_error "No backend pods found"
fi

# ============================================================================
# STEP 9: Access Instructions
# ============================================================================
print_header "Step 9: Access Instructions"

echo -e "${GREEN}Deployment completed!${NC}"
echo ""
echo "To access the backend:"
echo ""
echo "  1. Port Forward (recommended for testing):"
echo -e "     ${CYAN}kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 9090:9090${NC}"
echo "     Then open: http://localhost:9090/docs"
echo ""
echo "  2. View Logs:"
echo -e "     ${CYAN}kubectl logs -n $NAMESPACE -l app=choreo-ai-backend -f${NC}"
echo ""
echo "  3. Get Pod Status:"
echo -e "     ${CYAN}kubectl get pods -n $NAMESPACE${NC}"
echo ""
echo "  4. Execute Shell in Pod:"
echo -e "     ${CYAN}kubectl exec -it -n $NAMESPACE $BACKEND_POD -- bash${NC}"
echo ""

if [[ "$CLUSTER_TYPE" == "minikube" ]]; then
    echo "  5. Minikube Service URL:"
    echo -e "     ${CYAN}minikube service $SERVICE_NAME -n $NAMESPACE --url${NC}"
    echo ""
fi

echo "To check deployment status anytime:"
echo -e "  ${CYAN}./scripts/status.sh${NC}"
echo ""
echo "To view in Makefile:"
echo -e "  ${CYAN}make status${NC}"
echo -e "  ${CYAN}make logs-backend${NC}"
echo ""

print_info "Backend deployment complete! 🚀"

