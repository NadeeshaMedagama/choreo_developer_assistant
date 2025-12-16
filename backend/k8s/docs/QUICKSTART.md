# Choreo AI Assistant - Kubernetes Quick Start
- Check pod status: `./status.sh`
- View application logs: `kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend`
- Check the full README: `backend/k8s/README.md`
For issues and questions:

## Support

5. **Configure backups**: Set up backup strategy for data
4. **Set up CI/CD**: Automate builds and deployments
3. **Enable persistence**: Configure proper storage class for PVCs
2. **Configure ingress**: Set up proper domain and TLS certificates
1. **Set up monitoring**: Deploy Prometheus and Grafana

## Next Steps

```
kubectl get events -n choreo-ai-assistant --sort-by='.lastTimestamp'
```bash
### View Events

```
  curl http://choreo-ai-backend-service:9090/health
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n choreo-ai-assistant -- \
# Test backend from within cluster
```bash
### Connection Issues

```
kind load docker-image choreo-ai-frontend:latest
kind load docker-image choreo-ai-backend:latest
```bash
For Kind:

```
./build-images.sh
eval $(minikube docker-env)
```bash
For Minikube:
### Image Pull Errors

```
kubectl logs <pod-name> -n choreo-ai-assistant
kubectl describe pod <pod-name> -n choreo-ai-assistant
```bash
### Pods Not Starting

## Troubleshooting

```
kubectl delete namespace choreo-ai-assistant
```bash
Or manually:

```
./cleanup.sh
```bash
### Remove Everything

## Cleanup

```
kubectl describe hpa choreo-ai-backend-hpa -n choreo-ai-assistant
kubectl get hpa -n choreo-ai-assistant
```bash
### Check Auto-Scaling

```
kubectl rollout restart deployment/choreo-ai-frontend -n choreo-ai-assistant
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
```bash
### Restart Deployment

```
./update-secrets.sh
```bash
### Update Secrets

```
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=3
```bash
### Scale Manually

```
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-frontend -f
# Frontend logs

kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f
# Backend logs
```bash
### View Logs

## Common Tasks

```
curl http://localhost:9090/metrics
```bash
### View Metrics

```
curl -X POST "http://localhost:9090/api/ingest/github?repo_url=https://github.com/wso2/docs-choreo-dev.git&branch=main"
```bash
### Ingest a GitHub Repository

```
curl -X POST "http://localhost:9090/api/ask?question=What%20is%20Choreo?"
```bash
### Ask a Question

## Using the Application

```
}
  }
    "application": "healthy"
    "pinecone": "healthy",
  "checks": {
  "timestamp": "...",
  "status": "healthy",
{
```json
Expected response:

```
curl http://localhost:9090/health
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
```bash
### Health Check

```
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend
kubectl get pods -n choreo-ai-assistant
kubectl get all -n choreo-ai-assistant
```bash
Or manually:

```
./status.sh
```bash
### Check Status

## Verify Deployment

```
kubectl apply -k backend/k8s/environments/production/
```bash
### Production

```
kubectl apply -k backend/k8s/environments/dev/
```bash
### Development

## Option 3: Environment-Specific Deploy

```
kubectl apply -f backend/k8s/hpa.yaml
# Then apply HPA

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# Install metrics server first
```bash
### 7. Enable Auto-Scaling (Optional)

```
kubectl apply -f backend/k8s/ingress.yaml
# Then apply ingress

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
# Install nginx ingress controller first
```bash
### 6. Setup Ingress (Optional)

```
kubectl apply -f backend/k8s/frontend-service.yaml
kubectl apply -f backend/k8s/frontend-deployment.yaml
```bash
### 5. Deploy Frontend

```
kubectl apply -f backend/k8s/backend-service.yaml
kubectl apply -f backend/k8s/backend-deployment.yaml
```bash
### 4. Deploy Backend

```
kubectl apply -f backend/k8s/secret.yaml
kubectl apply -f backend/k8s/configmap.yaml
```bash
### 3. Create ConfigMap and Secrets

```
kubectl apply -f backend/k8s/namespace.yaml
```bash
### 2. Create Namespace

```
docker build -t choreo-ai-frontend:latest -f frontend/Dockerfile ./frontend
docker build -t choreo-ai-backend:latest -f Dockerfile .
cd ../../  # Go to project root
```bash
### 1. Build Images

## Option 2: Step-by-Step Deploy

- Metrics: http://localhost:9090/metrics
- Health Check: http://localhost:9090/health
- Backend API: http://localhost:9090
- Frontend: http://localhost:8080
Then open:

```
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80
# Frontend

kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
# Backend API
```bash
### 5. Access Your Application

```
./deploy.sh
```bash
### 4. Deploy Everything

```
./update-secrets.sh
# Make sure you have a .env file in the project root
```bash
Or use the helper script:

```
nano secret.yaml
```bash
Edit `secret.yaml` and replace placeholder values with your actual API keys:
### 3. Update Secrets

```
kind load docker-image choreo-ai-frontend:latest
kind load docker-image choreo-ai-backend:latest
./build-images.sh
```bash
For Kind users:

```
./build-images.sh
eval $(minikube docker-env)
```bash
For Minikube users:

```
./build-images.sh
```bash
### 2. Build Docker Images

```
cd choreo-ai-assistant/backend/k8s
```bash
### 1. Clone and Navigate

## Option 1: Quick Deploy (5 minutes)

  - GitHub token (optional but recommended)
  - Azure OpenAI credentials (or OpenAI API key)
  - Pinecone API key
- Your API keys ready:
- Docker installed
- `kubectl` installed and configured
- Kubernetes cluster (Minikube, Kind, or cloud provider)

## Prerequisites

Get your Choreo AI Assistant running on Kubernetes in minutes!


