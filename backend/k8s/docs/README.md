# Kubernetes Deployment for Choreo AI Assistant

This directory contains Kubernetes manifests for deploying the Choreo AI Assistant application.

## Architecture

The deployment includes:
- **Backend**: FastAPI application running on port 9090
- **Frontend**: Nginx-served React/Vue application on port 80
- **Monitoring**: Prometheus metrics endpoint at `/metrics`
- **Health Checks**: Health endpoint at `/health`
- **Auto-scaling**: Horizontal Pod Autoscaler (HPA) for both frontend and backend
- **Persistent Storage**: PVCs for logs and diagram outputs
- **Network Policies**: Security policies for pod communication

## Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Minikube, Kind, or cloud provider (GKE, EKS, AKS)
   
2. **kubectl** configured and connected to your cluster

3. **Ingress Controller** (nginx-ingress recommended)
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

4. **Metrics Server** (for HPA)
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

5. **Docker Images** built and available:
   ```bash
   # Build backend image
   docker build -t choreo-ai-backend:latest -f Dockerfile .
   
   # Build frontend image
   docker build -t choreo-ai-frontend:latest -f frontend/Dockerfile ./frontend
   ```

## Quick Start

### 1. Update Secrets

**IMPORTANT**: Before deploying, update `secret.yaml` with your actual API keys:

```bash
# Edit the secret file
nano k8s/secret.yaml

# Or use kubectl to create the secret directly (recommended for production)
kubectl create secret generic choreo-ai-secrets \
  --from-literal=PINECONE_API_KEY=your_key \
  --from-literal=GITHUB_TOKEN=your_token \
  --from-literal=AZURE_OPENAI_KEY=your_key \
  --from-literal=AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/ \
  --from-literal=AZURE_OPENAI_DEPLOYMENT=your-deployment \
  --from-literal=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your-embeddings \
  --from-literal=GOOGLE_VISION_API_KEY=your_key \
  --from-literal=OPENAI_API_KEY=your_key \
  -n choreo-ai-assistant
```

### 2. Deploy Using Kustomize (Recommended)

```bash
# Deploy all resources
kubectl apply -k backend/k8s/

# Verify deployment
kubectl get all -n choreo-ai-assistant
```

### 3. Deploy Individually

```bash
# Deploy in order
kubectl apply -f backend/k8s/namespace.yaml
kubectl apply -f backend/k8s/configmap.yaml
kubectl apply -f backend/k8s/secret.yaml
kubectl apply -f backend/k8s/pvc.yaml
kubectl apply -f backend/k8s/backend-deployment.yaml
kubectl apply -f backend/k8s/backend-service.yaml
kubectl apply -f backend/k8s/frontend-deployment.yaml
kubectl apply -f backend/k8s/frontend-service.yaml
kubectl apply -f backend/k8s/ingress.yaml
kubectl apply -f backend/k8s/hpa.yaml
kubectl apply -f backend/k8s/networkpolicy.yaml
kubectl apply -f backend/k8s/prometheus-servicemonitor.yaml
```

## Access the Application

### Local Development (Minikube/Kind)

```bash
# Get the ingress IP
kubectl get ingress -n choreo-ai-assistant

# Add to /etc/hosts
echo "$(minikube ip) choreo-ai.local" | sudo tee -a /etc/hosts

# Access application
# Frontend: http://choreo-ai.local
# Backend API: http://choreo-ai.local/api
```

### Port Forwarding (Alternative)

```bash
# Forward backend
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

# Forward frontend
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80

# Access:
# Backend: http://localhost:9090
# Frontend: http://localhost:8080
```

### Load Balancer (Cloud Providers)

```bash
# Change service type to LoadBalancer in frontend-service.yaml
kubectl patch svc choreo-ai-frontend-service -n choreo-ai-assistant -p '{"spec": {"type": "LoadBalancer"}}'

# Get external IP
kubectl get svc -n choreo-ai-assistant -w
```

## Monitoring

### Health Checks

```bash
# Check pod health
kubectl get pods -n choreo-ai-assistant

# Check backend health
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
curl http://localhost:9090/health
```

### Metrics

```bash
# View Prometheus metrics
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
curl http://localhost:9090/metrics
```

### Logs

```bash
# View backend logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f

# View frontend logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-frontend -f
```

### Horizontal Pod Autoscaler

```bash
# Check HPA status
kubectl get hpa -n choreo-ai-assistant

# Describe HPA
kubectl describe hpa choreo-ai-backend-hpa -n choreo-ai-assistant
```

## Configuration Updates

### Update ConfigMap

```bash
# Edit configmap
kubectl edit configmap choreo-ai-config -n choreo-ai-assistant

# Restart pods to apply changes
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
```

### Update Secrets

```bash
# Update secret
kubectl edit secret choreo-ai-secrets -n choreo-ai-assistant

# Or recreate
kubectl delete secret choreo-ai-secrets -n choreo-ai-assistant
kubectl create secret generic choreo-ai-secrets --from-literal=... -n choreo-ai-assistant

# Restart pods
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=5

# Scale frontend
kubectl scale deployment choreo-ai-frontend -n choreo-ai-assistant --replicas=3
```

### Auto-scaling

The HPA automatically scales based on:
- CPU utilization (70% threshold)
- Memory utilization (80% threshold)

Modify `hpa.yaml` to adjust thresholds and replica counts.

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n choreo-ai-assistant

# Describe pod
kubectl describe pod <pod-name> -n choreo-ai-assistant

# Check events
kubectl get events -n choreo-ai-assistant --sort-by='.lastTimestamp'
```

### Image Pull Errors

```bash
# For local images in Minikube
eval $(minikube docker-env)
docker build -t choreo-ai-backend:latest .
docker build -t choreo-ai-frontend:latest -f frontend/Dockerfile ./frontend

# For Kind, load images
kind load docker-image choreo-ai-backend:latest
kind load docker-image choreo-ai-frontend:latest
```

### Service Connection Issues

```bash
# Test backend service
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n choreo-ai-assistant -- \
  curl http://choreo-ai-backend-service:9090/health

# Test frontend to backend
kubectl exec -it <frontend-pod> -n choreo-ai-assistant -- \
  curl http://choreo-ai-backend-service:9090/health
```

### DNS Resolution

```bash
# Test DNS
kubectl run -it --rm debug --image=busybox --restart=Never -n choreo-ai-assistant -- \
  nslookup choreo-ai-backend-service
```

## Production Checklist

- [ ] Replace placeholder secrets with actual values
- [ ] Configure proper ingress domain and TLS certificates
- [ ] Set up external secret management (e.g., Sealed Secrets, Vault)
- [ ] Configure resource limits based on actual usage
- [ ] Set up log aggregation (e.g., ELK, Loki)
- [ ] Configure backup strategy for PVCs
- [ ] Enable pod security policies
- [ ] Set up monitoring and alerting
- [ ] Configure proper storage class
- [ ] Review and adjust HPA settings
- [ ] Enable network policies
- [ ] Configure RBAC
- [ ] Set up CI/CD pipeline

## Cleanup

```bash
# Delete all resources using kustomize
kubectl delete -k backend/k8s/

# Or delete namespace (removes everything)
kubectl delete namespace choreo-ai-assistant
```

## Directory Structure

```
k8s/
├── README.md                        # This file
├── namespace.yaml                   # Namespace definition
├── configmap.yaml                   # Application configuration
├── secret.yaml                      # Secrets (API keys, tokens)
├── backend-deployment.yaml          # Backend deployment
├── backend-service.yaml             # Backend service
├── frontend-deployment.yaml         # Frontend deployment
├── frontend-service.yaml            # Frontend service
├── ingress.yaml                     # Ingress rules
├── hpa.yaml                         # Horizontal Pod Autoscaler
├── pvc.yaml                         # Persistent Volume Claims
├── prometheus-servicemonitor.yaml   # Prometheus monitoring
├── networkpolicy.yaml               # Network security policies
└── kustomization.yaml               # Kustomize configuration
```

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)

