# Makefile for Choreo AI Assistant Kubernetes Deployment
.PHONY: help build deploy status logs clean secrets validate port-forward dev prod
# Default target
help:
@echo "Choreo AI Assistant - Kubernetes Deployment"
@echo ""
@echo "Available targets:"
@echo "  make build          - Build Docker images"
@echo "  make deploy         - Deploy to Kubernetes"
@echo "  make deploy-dev     - Deploy to development environment"
@echo "  make deploy-prod    - Deploy to production environment"
@echo "  make status         - Check deployment status"
@echo "  make logs           - View application logs"
@echo "  make logs-backend   - View backend logs"
@echo "  make logs-frontend  - View frontend logs"
@echo "  make secrets        - Update secrets"
@echo "  make validate       - Validate manifests"
@echo "  make port-forward   - Port forward services"
@echo "  make scale-up       - Scale up deployments"
@echo "  make scale-down     - Scale down deployments"
@echo "  make restart        - Restart deployments"
@echo "  make clean          - Delete all resources"
@echo "  make shell-backend  - Open shell in backend pod"
@echo "  make test-health    - Test health endpoints"
@echo ""
# Build Docker images
build:
@echo "Building Docker images..."
./scripts/build-images.sh
# Deploy to Kubernetes (default namespace)
deploy:
@echo "Deploying to Kubernetes..."
./scripts/deploy.sh
# Deploy to development environment
deploy-dev:
@echo "Deploying to development environment..."
kubectl apply -k environments/dev/
# Deploy to production environment
deploy-prod:
@echo "Deploying to production environment..."
kubectl apply -k environments/production/
# Check status
status:
@echo "Checking deployment status..."
./scripts/status.sh
# View logs
logs:
@echo "Viewing application logs (Ctrl+C to exit)..."
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f --tail=100
logs-backend:
@echo "Viewing backend logs (Ctrl+C to exit)..."
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f --tail=100
logs-frontend:
@echo "Viewing frontend logs (Ctrl+C to exit)..."
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-frontend -f --tail=100
# Update secrets
secrets:
@echo "Updating secrets..."
./scripts/update-secrets.sh
# Validate manifests
validate:
@echo "Validating Kubernetes manifests..."
kubectl apply --dry-run=client -k .
@echo "✓ All manifests are valid"
# Port forward services
port-forward:
@echo "Port forwarding services..."
@echo "Backend: http://localhost:9090"
@echo "Frontend: http://localhost:8080"
@echo "Press Ctrl+C to stop"
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 & \
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80
# Scale up deployments
scale-up:
@echo "Scaling up deployments..."
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=5
kubectl scale deployment choreo-ai-frontend -n choreo-ai-assistant --replicas=3
@echo "✓ Scaled up"
# Scale down deployments
scale-down:
@echo "Scaling down deployments..."
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=1
kubectl scale deployment choreo-ai-frontend -n choreo-ai-assistant --replicas=1
@echo "✓ Scaled down"
# Restart deployments
restart:
@echo "Restarting deployments..."
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
kubectl rollout restart deployment/choreo-ai-frontend -n choreo-ai-assistant
@echo "Waiting for rollout to complete..."
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant
kubectl rollout status deployment/choreo-ai-frontend -n choreo-ai-assistant
@echo "✓ Deployments restarted"
# Clean up all resources
clean:
@echo "Cleaning up all resources..."
./scripts/cleanup.sh
# Open shell in backend pod
shell-backend:
@echo "Opening shell in backend pod..."
kubectl exec -it -n choreo-ai-assistant $$(kubectl get pod -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}') -- /bin/bash
# Test health endpoints
test-health:
@echo "Testing health endpoints..."
kubectl run -it --rm curl-test --image=curlimages/curl --restart=Never -n choreo-ai-assistant -- \
curl -s http://choreo-ai-backend-service:9090/health | jq .
# Development helpers
dev: build deploy-dev status
# Production deployment
prod: validate deploy-prod status
# Quick restart
quick-restart:
kubectl delete pod -n choreo-ai-assistant -l app=choreo-ai-backend
kubectl delete pod -n choreo-ai-assistant -l app=choreo-ai-frontend
