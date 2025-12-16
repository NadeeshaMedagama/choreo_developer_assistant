#!/bin/bash

# Choreo AI Assistant - Update Secrets Script
# This script helps create/update Kubernetes secrets from environment variables

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

echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Choreo AI Assistant - Secret Manager        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed."
    exit 1
fi

# Load .env file if it exists
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    print_info "Loading secrets from $ENV_FILE"
    source "$ENV_FILE"
else
    print_warning "$ENV_FILE not found. You'll need to enter values manually."
fi

# Function to get secret value
get_secret() {
    local var_name=$1
    local default_value=$2
    local current_value=${!var_name}

    if [ -z "$current_value" ]; then
        current_value=$default_value
    fi

    echo "$current_value"
}

# Collect all secret values
PINECONE_API_KEY=$(get_secret "PINECONE_API_KEY" "your_pinecone_api_key_here")
GITHUB_TOKEN=$(get_secret "GITHUB_TOKEN" "your_github_token_here")
AZURE_OPENAI_KEY=$(get_secret "AZURE_OPENAI_KEY" "your_azure_openai_key_here")
AZURE_OPENAI_ENDPOINT=$(get_secret "AZURE_OPENAI_ENDPOINT" "https://your-resource.openai.azure.com/")
AZURE_OPENAI_DEPLOYMENT=$(get_secret "AZURE_OPENAI_DEPLOYMENT" "your-deployment-name")
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=$(get_secret "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT" "your-embeddings-deployment")
GOOGLE_VISION_API_KEY=$(get_secret "GOOGLE_VISION_API_KEY" "your_google_vision_api_key_here")
OPENAI_API_KEY=$(get_secret "OPENAI_API_KEY" "your_openai_api_key_here")

# Check if namespace exists
if ! kubectl get namespace choreo-ai-assistant &> /dev/null; then
    print_info "Creating namespace choreo-ai-assistant..."
    kubectl create namespace choreo-ai-assistant
fi

# Check if secret already exists
if kubectl get secret choreo-ai-secrets -n choreo-ai-assistant &> /dev/null; then
    print_warning "Secret 'choreo-ai-secrets' already exists."
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret choreo-ai-secrets -n choreo-ai-assistant
        print_info "Existing secret deleted."
    else
        print_info "Keeping existing secret. Exiting."
        exit 0
    fi
fi

# Create the secret
print_info "Creating Kubernetes secret..."
kubectl create secret generic choreo-ai-secrets \
  --from-literal=MILVUS_URI="$MILVUS_URI" \
  --from-literal=MILVUS_TOKEN="$MILVUS_TOKEN" \
  --from-literal=MILVUS_COLLECTION_NAME="$MILVUS_COLLECTION_NAME" \
  --from-literal=GITHUB_TOKEN="$GITHUB_TOKEN" \
  --from-literal=AZURE_OPENAI_KEY="$AZURE_OPENAI_KEY" \
  --from-literal=AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  --from-literal=AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
  --from-literal=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="$AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT" \
  --from-literal=GOOGLE_VISION_API_KEY="$GOOGLE_VISION_API_KEY" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  -n choreo-ai-assistant

print_info "✓ Secret created successfully!"

# Restart deployments if they exist
if kubectl get deployment choreo-ai-backend -n choreo-ai-assistant &> /dev/null; then
    print_info "Restarting backend deployment to apply new secrets..."
    kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
    kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant --timeout=120s
    print_info "✓ Backend deployment restarted."
fi

echo ""
print_info "Secrets management completed!"
print_info "You can verify the secret with:"
echo "  kubectl get secret choreo-ai-secrets -n choreo-ai-assistant"
echo "  kubectl describe secret choreo-ai-secrets -n choreo-ai-assistant"

