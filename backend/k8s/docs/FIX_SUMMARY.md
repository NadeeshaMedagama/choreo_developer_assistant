# 🔧 Backend Deployment Fix - Summary

## Problem Identified

Your backend pods are in **CrashLoopBackOff** status with this error:

```
ImportError: cannot import name 'RemoveMessage' from 'langchain_core.messages'
```

### Root Cause
Version incompatibility between `langgraph` and `langchain-core` packages. The current Docker image was built with:
- `langchain-core>=0.2.30` 
- `langgraph>=0.1.43`

These versions are incompatible because the newer `langgraph` requires `langchain-core>=0.3.0` which includes the `RemoveMessage` class.

## Solution Applied

### 1. Fixed Dependencies  ✅
Updated `/choreo-ai-assistant/requirements.txt`:

**Before:**
```
langchain>=0.2.14
langchain-core>=0.2.30
langgraph>=0.1.43
```

**After:**
```
langchain>=0.3.0
langchain-core>=0.3.0
langgraph>=0.2.0
```

### 2. Need to Rebuild Docker Image
The Docker image needs to be rebuilt with the fixed dependencies and reloaded into Minikube.

## How to Fix (Choose One Method)

### Method 1: Automated Fix (Recommended)

I've created an automated script that will:
1. Rebuild the Docker image with fixed dependencies
2. Load it into Minikube
3. Restart the deployment
4. Wait for pods to be ready

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/k8s"
chmod +x scripts/quick-fix.sh
./scripts/quick-fix.sh
```

### Method 2: Manual Fix

```bash
# 1. Navigate to project root
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# 2. Rebuild Docker image (this will take 5-10 minutes)
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .

# 3. Load image into Minikube
minikube image load choreo-ai-backend:v2-fixed

# 4. Restart the deployment
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

# 5. Watch the rollout
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant

# 6. Check pods
kubectl get pods -n choreo-ai-assistant -l app=choreo-ai-backend
```

### Method 3: Complete Auto-Deployment

Use the full auto-deployment script I created:

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/k8s"
chmod +x scripts/deploy-backend-auto.sh
./scripts/deploy-backend-auto.sh
```

## Verification Steps

After running the fix, verify the deployment:

### 1. Check Pod Status
```bash
kubectl get pods -n choreo-ai-assistant
```

You should see:
```
NAME                                 READY   STATUS    RESTARTS   AGE
choreo-ai-backend-xxx                1/1     Running   0          2m
choreo-ai-frontend-xxx               1/1     Running   0          3d
```

### 2. Check Logs
```bash
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend --tail=50
```

You should NOT see any ImportError messages.

### 3. Test Health Endpoint
```bash
# Port forward the service
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &

# Test health endpoint
curl http://localhost:9090/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

### 4. Access API Documentation
Open http://localhost:9090/docs in your browser to see the FastAPI Swagger UI.

## Current Cluster Status

- **Cluster**: Minikube (running)
- **Namespace**: choreo-ai-assistant (exists)
- **Frontend**: ✅ Running (3/3 pods healthy)
- **Backend**: ❌ CrashLoopBackOff (dependency issue)
- **Services**: ✅ All services created
- **ConfigMaps/Secrets**: ✅ All configured

## Additional Resources Created

I've created several helpful scripts and guides for you:

### Scripts
1. **`backend/k8s/scripts/quick-fix.sh`** - Quick rebuild and redeploy
2. **`backend/k8s/scripts/deploy-backend-auto.sh`** - Full auto-deployment with diagnostics
3. **`backend/k8s/scripts/diagnose-backend.sh`** - Diagnose backend issues

### Documentation
1. **`backend/k8s/BACKEND_DEPLOYMENT_GUIDE.md`** - Complete deployment guide
2. **`backend/MONITORING_GUIDE.md`** - Monitoring setup (already exists)

## Next Steps

1. **Run the quick fix**:
   ```bash
   cd backend/k8s && ./scripts/quick-fix.sh
   ```

2. **Wait for build** (5-10 minutes for first build, faster for subsequent builds)

3. **Verify pods are running**:
   ```bash
   kubectl get pods -n choreo-ai-assistant -w
   ```

4. **Test the backend**:
   ```bash
   kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
   curl http://localhost:9090/health
   ```

5. **Access both frontend and backend**:
   - Frontend: `kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80`
   - Backend API: http://localhost:9090/docs

## Troubleshooting

### If Docker build takes too long
The build might be downloading large dependencies (PyTorch, etc.). You can:
- Let it run in the background
- Check build progress: `docker ps -a`
- Monitor build logs: Check `/tmp/docker-build.log` if using the automated script

### If pods still crash after rebuild
1. Check logs: `kubectl logs -n choreo-ai-assistant <pod-name>`
2. Describe pod: `kubectl describe pod -n choreo-ai-assistant <pod-name>`
3. Run diagnostics: `./scripts/diagnose-backend.sh`

### If image is not found in Minikube
```bash
# Make sure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild in Minikube's Docker
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .

# Or load existing image
minikube image load choreo-ai-backend:v2-fixed
```

## Summary

**Problem**: Dependency version mismatch causing ImportError  
**Solution**: Updated requirements.txt to use compatible versions  
**Action Required**: Rebuild Docker image and restart deployment  
**Estimated Time**: 10-15 minutes total  
**Success Criteria**: All backend pods in Running state, health endpoint responds

---

**Created**: November 18, 2025  
**Issue**: LangChain/LangGraph version incompatibility  
**Status**: Fix applied to requirements.txt, rebuild needed

