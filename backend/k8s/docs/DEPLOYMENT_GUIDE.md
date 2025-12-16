# Quick Start Guide - Fixed and Ready to Deploy

## ✅ Issues Fixed

1. ✅ Fixed corrupted `resource-quota.yaml` file
2. ✅ Fixed `deploy.sh` script with missing functions
3. ✅ Fixed `build-images.sh` to find Dockerfile correctly
4. ✅ Created `deploy-auto.sh` for automated deployment (no prompts)

## 🚀 Step-by-Step Deployment

### Step 1: Build Docker Images

```bash
cd backend/k8s/scripts
./build-images.sh
```

**For Minikube users:**
```bash
eval $(minikube docker-env)
cd backend/k8s/scripts
./build-images.sh
```

**For Kind users:**
```bash
cd backend/k8s/scripts
./build-images.sh
cd ..
kind load docker-image choreo-ai-backend:latest
kind load docker-image choreo-ai-frontend:latest
```

### Step 2: Update Secrets (IMPORTANT!)

Edit the secret file with your actual API keys:

```bash
cd backend/k8s
nano base/config/secret.yaml
```

Replace these values:
- `PINECONE_API_KEY` - Your Pinecone API key
- `AZURE_OPENAI_KEY` - Your Azure OpenAI key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT` - Your deployment name
- `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` - Your embeddings deployment
- `GITHUB_TOKEN` - Your GitHub token (optional)

### Step 3: Deploy to Kubernetes

**Option A: Automatic deployment (recommended for first-time)**
```bash
cd backend/k8s
./scripts/deploy-auto.sh
```

**Option B: Interactive deployment**
```bash
cd backend/k8s
./scripts/deploy.sh
# Answer 'y' when prompted about secrets
```

**Option C: Manual kubectl**
```bash
cd backend/k8s
kubectl apply -k .
```

### Step 4: Check Deployment Status

```bash
cd backend/k8s
./scripts/status.sh
```

Or manually:
```bash
kubectl get pods -n choreo-ai-assistant
kubectl get all -n choreo-ai-assistant
```

Wait until pods show `Running` status:
```
NAME                                  READY   STATUS    RESTARTS   AGE
choreo-ai-backend-xxxxx-xxxxx         1/1     Running   0          2m
choreo-ai-frontend-xxxxx-xxxxx        1/1     Running   0          2m
```

### Step 5: Access the Application

**Port forward the services:**
```bash
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80 &
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &
```

**Then access:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:9090
- Health Check: http://localhost:9090/health

### Step 6: View Logs (if needed)

```bash
# Backend logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f

# Frontend logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-frontend -f
```

## 🔧 Troubleshooting

### ⚠️ IMPORTANT: After Building Images, Restart Pods!

**If you rebuilt the Docker images but pods are still crashing**, Kubernetes is still using the old images. You MUST delete the pods:

```bash
# Delete backend pods to force restart with new image
kubectl delete pods -n choreo-ai-assistant -l app=choreo-ai-backend

# Wait and check status
sleep 10
kubectl get pods -n choreo-ai-assistant
```

**OR use the automated fix script:**
```bash
cd backend/k8s
./scripts/fix-pods.sh
```

### Pods Not Starting

Check pod details:
```bash
kubectl describe pod -n choreo-ai-assistant <pod-name>
kubectl logs -n choreo-ai-assistant <pod-name>
```

### Image Pull Errors

**For Minikube:**
```bash
eval $(minikube docker-env)
cd backend/k8s/scripts
./build-images.sh
```

**For Kind:**
```bash
kind load docker-image choreo-ai-backend:latest
kind load docker-image choreo-ai-frontend:latest
```

### Check if images exist:
```bash
docker images | grep choreo-ai
```

### Pods in CrashLoopBackOff

Check logs for errors:
```bash
kubectl logs -n choreo-ai-assistant <pod-name> --previous
```

Common issues:
- Missing or invalid API keys in secrets
- Backend can't connect to Pinecone
- Azure OpenAI credentials incorrect

## 🧹 Clean Up

To remove everything:
```bash
cd backend/k8s
./scripts/cleanup.sh
```

Or manually:
```bash
kubectl delete namespace choreo-ai-assistant
```

## 📝 Quick Command Reference

```bash
# Build images
cd backend/k8s/scripts && ./build-images.sh

# Deploy
cd backend/k8s && ./scripts/deploy-auto.sh

# Check status
cd backend/k8s && ./scripts/status.sh

# View logs
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f

# Port forward
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

# Restart deployment
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

# Delete everything
cd backend/k8s && ./scripts/cleanup.sh
```

## ✅ Verification Checklist

- [ ] Docker images built successfully
- [ ] Secrets updated with real API keys
- [ ] Kubernetes cluster accessible (kubectl cluster-info works)
- [ ] Deployment successful (all pods Running)
- [ ] Services created
- [ ] Port-forward working
- [ ] Can access frontend at http://localhost:8080
- [ ] Can access backend at http://localhost:9090

---

**Ready to deploy!** Start with Step 1 above. 🚀

