# 🚀 Backend Kubernetes Deployment Guide

This guide will help you deploy the Choreo AI Assistant backend to Kubernetes.

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] **Kubernetes cluster** running (Minikube, Kind, Docker Desktop, or cloud provider)
- [ ] **kubectl** installed and configured
- [ ] **Docker** installed and running
- [ ] **Backend Docker image** built
- [ ] **Secrets configured** (API keys, tokens)

## Step 1: Verify Prerequisites

### 1.1 Check Kubernetes Cluster

```bash
# Check if kubectl is installed
kubectl version --client

# Check cluster connection
kubectl cluster-info

# Check cluster nodes
kubectl get nodes
```

**If you don't have a cluster running:**

#### Option A: Using Minikube
```bash
# Install Minikube (if not installed)
# See: https://minikube.sigs.k8s.io/docs/start/

# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable metrics server (for autoscaling)
minikube addons enable metrics-server
```

#### Option B: Using Kind (Kubernetes in Docker)
```bash
# Install Kind (if not installed)
# See: https://kind.sigs.k8s.io/docs/user/quick-start/

# Create a cluster
kind create cluster --name choreo-cluster

# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### Option C: Using Docker Desktop
```bash
# Enable Kubernetes in Docker Desktop settings
# Settings → Kubernetes → Enable Kubernetes
```

### 1.2 Check Docker

```bash
# Verify Docker is running
docker ps

# Check available images
docker images | grep choreo
```

## Step 2: Build Backend Docker Image

```bash
# Navigate to project root
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Build the backend image
docker build -t choreo-ai-backend:latest -f docker/Dockerfile .

# Verify the image was created
docker images | grep choreo-ai-backend
```

**For Minikube users:**
```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build the image again in Minikube's Docker
docker build -t choreo-ai-backend:latest -f docker/Dockerfile .
```

**For Kind users:**
```bash
# Build the image
docker build -t choreo-ai-backend:latest -f docker/Dockerfile .

# Load the image into Kind
kind load docker-image choreo-ai-backend:latest --name choreo-cluster
```

## Step 3: Configure Secrets

### 3.1 Create Environment File (for reference)

```bash
# Navigate to backend k8s directory
cd backend/k8s

# Create a .env file with your actual secrets
cat > .env.local << EOF
PINECONE_API_KEY=your_actual_pinecone_api_key
GITHUB_TOKEN=your_actual_github_token
AZURE_OPENAI_KEY=your_actual_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your-embeddings-deployment
GOOGLE_VISION_API_KEY=your_google_vision_api_key
OPENAI_API_KEY=your_openai_api_key
EOF
```

### 3.2 Update Kubernetes Secret

**Option A: Edit the secret.yaml file directly**
```bash
# Edit the secret file
nano base/config/secret.yaml

# Replace placeholder values with actual secrets
```

**Option B: Create secret from .env file (recommended)**
```bash
# Create the secret from environment variables
kubectl create namespace choreo-ai-assistant --dry-run=client -o yaml | kubectl apply -f -

# Load .env file and create secret
source .env.local
kubectl create secret generic choreo-ai-secrets \
  --from-literal=PINECONE_API_KEY="$PINECONE_API_KEY" \
  --from-literal=GITHUB_TOKEN="$GITHUB_TOKEN" \
  --from-literal=AZURE_OPENAI_KEY="$AZURE_OPENAI_KEY" \
  --from-literal=AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  --from-literal=AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
  --from-literal=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="$AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT" \
  --from-literal=GOOGLE_VISION_API_KEY="$GOOGLE_VISION_API_KEY" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  -n choreo-ai-assistant \
  --dry-run=client -o yaml > base/config/secret-generated.yaml

# Apply the generated secret
kubectl apply -f base/config/secret-generated.yaml
```

## Step 4: Deploy Backend to Kubernetes

### 4.1 Using Make (Recommended)

```bash
cd backend/k8s

# Deploy everything
make deploy

# Check status
make status

# View logs
make logs-backend
```

### 4.2 Using kubectl directly

```bash
cd backend/k8s

# Apply all resources
kubectl apply -k .

# Wait for deployment
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant

# Check pod status
kubectl get pods -n choreo-ai-assistant
```

### 4.3 Using the deployment script

```bash
cd backend/k8s

# Make script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## Step 5: Verify Deployment

### 5.1 Check Pod Status

```bash
# Get all pods
kubectl get pods -n choreo-ai-assistant

# Get detailed pod info
kubectl describe pod -n choreo-ai-assistant -l app=choreo-ai-backend

# Check pod logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f
```

### 5.2 Check Services

```bash
# Get services
kubectl get svc -n choreo-ai-assistant

# Get detailed service info
kubectl describe svc choreo-ai-backend-service -n choreo-ai-assistant
```

### 5.3 Test Backend Health

```bash
# Port forward to access backend locally
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &

# Test health endpoint
curl http://localhost:9090/health

# Test metrics endpoint
curl http://localhost:9090/metrics
```

## Step 6: Troubleshooting Common Issues

### Issue 1: Pods in CrashLoopBackOff or Error state

```bash
# Check pod logs
kubectl logs -n choreo-ai-assistant <pod-name>

# Check previous container logs (if pod restarted)
kubectl logs -n choreo-ai-assistant <pod-name> --previous

# Describe pod to see events
kubectl describe pod -n choreo-ai-assistant <pod-name>
```

**Common causes:**
- Missing or incorrect secrets
- Image pull errors
- Application startup errors
- Resource limits too low

### Issue 2: Image Pull Errors (ErrImagePull, ImagePullBackOff)

```bash
# Check the image name in deployment
kubectl get deployment choreo-ai-backend -n choreo-ai-assistant -o yaml | grep image:

# For Minikube: Make sure you built the image in Minikube's Docker
eval $(minikube docker-env)
docker images | grep choreo-ai-backend

# For Kind: Make sure you loaded the image
kind load docker-image choreo-ai-backend:latest --name choreo-cluster
```

**Fix: Update imagePullPolicy**
```bash
# Edit deployment to use imagePullPolicy: Never (for local images)
kubectl edit deployment choreo-ai-backend -n choreo-ai-assistant
# Change imagePullPolicy: IfNotPresent to imagePullPolicy: Never
```

### Issue 3: Secrets Not Found

```bash
# Check if secrets exist
kubectl get secrets -n choreo-ai-assistant

# View secret (base64 encoded)
kubectl get secret choreo-ai-secrets -n choreo-ai-assistant -o yaml

# Recreate secrets
kubectl delete secret choreo-ai-secrets -n choreo-ai-assistant
# Then follow Step 3.2 to create secrets again
```

### Issue 4: Health Check Failures

```bash
# Check if app is running on correct port
kubectl exec -n choreo-ai-assistant <pod-name> -- netstat -tuln | grep 9090

# Test health endpoint from within pod
kubectl exec -n choreo-ai-assistant <pod-name> -- curl -v http://localhost:9090/health

# Check readiness/liveness probe configuration
kubectl describe pod -n choreo-ai-assistant <pod-name> | grep -A 10 Liveness
```

### Issue 5: Backend Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n choreo-ai-assistant

# Check if pods are ready
kubectl get pods -n choreo-ai-assistant -o wide

# Port forward and test
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
curl http://localhost:9090/health
```

## Step 7: Accessing the Backend

### Option 1: Port Forward (Development)

```bash
# Port forward backend service
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

# Access backend
curl http://localhost:9090/health
# Open http://localhost:9090/docs in browser for API docs
```

### Option 2: Ingress (Production)

```bash
# Check ingress
kubectl get ingress -n choreo-ai-assistant

# Add to /etc/hosts (get ingress IP first)
INGRESS_IP=$(kubectl get ingress -n choreo-ai-assistant -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
echo "$INGRESS_IP choreo-ai.local" | sudo tee -a /etc/hosts

# Access via domain
curl http://choreo-ai.local/api/health
```

### Option 3: NodePort (Minikube)

```bash
# Get Minikube service URL
minikube service choreo-ai-backend-service -n choreo-ai-assistant --url

# Access the backend
curl $(minikube service choreo-ai-backend-service -n choreo-ai-assistant --url)/health
```

## Step 8: Scaling and Management

### Scale Backend

```bash
# Scale to 5 replicas
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=5

# Check scaling
kubectl get pods -n choreo-ai-assistant -w
```

### Update Deployment

```bash
# Edit deployment
kubectl edit deployment choreo-ai-backend -n choreo-ai-assistant

# Or update image
kubectl set image deployment/choreo-ai-backend backend=choreo-ai-backend:v2 -n choreo-ai-assistant

# Check rollout status
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant
```

### Restart Deployment

```bash
# Restart all pods
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
```

## Step 9: Monitoring

### View Metrics

```bash
# Check HPA (Horizontal Pod Autoscaler)
kubectl get hpa -n choreo-ai-assistant

# View resource usage (requires metrics-server)
kubectl top pods -n choreo-ai-assistant
kubectl top nodes
```

### Access Prometheus (if monitoring is enabled)

```bash
# See MONITORING_GUIDE.md for detailed instructions

# Quick access via port-forward
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9091:9090
# Open http://localhost:9091
```

## Step 10: Cleanup

### Remove Backend Deployment Only

```bash
# Delete backend deployment
kubectl delete deployment choreo-ai-backend -n choreo-ai-assistant

# Keep namespace and other resources
```

### Remove Everything

```bash
# Using Make
make clean

# Using kubectl
kubectl delete namespace choreo-ai-assistant

# Using script
./scripts/cleanup.sh
```

## Quick Reference Commands

```bash
# Check everything
kubectl get all -n choreo-ai-assistant

# Watch pods
kubectl get pods -n choreo-ai-assistant -w

# Tail logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f --tail=100

# Execute command in pod
kubectl exec -it -n choreo-ai-assistant <pod-name> -- bash

# Port forward
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

# Restart deployment
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

# Check events
kubectl get events -n choreo-ai-assistant --sort-by='.lastTimestamp'
```

## Next Steps

1. ✅ Deploy backend to Kubernetes
2. ✅ Verify backend is running
3. ✅ Test backend endpoints
4. 📊 Set up monitoring (see MONITORING_GUIDE.md)
5. 🔒 Configure ingress and SSL
6. 📈 Enable autoscaling
7. 🔄 Set up CI/CD pipeline

## Additional Resources

- **Makefile Commands**: `make help`
- **Deployment Scripts**: `backend/k8s/scripts/`
- **Monitoring Guide**: `backend/MONITORING_GUIDE.md`
- **Quick Reference**: `backend/k8s/QUICK_REFERENCE.txt`
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

