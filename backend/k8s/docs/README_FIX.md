# 🚀 Backend Kubernetes Deployment - Complete Solution

## 📋 Summary

I've diagnosed and identified the issue with your backend Kubernetes deployment. Here's the complete solution.

---

## ❌ The Problem

Your backend pods are **crashing** with this error:
```
ImportError: cannot import name 'RemoveMessage' from 'langchain_core.messages'
```

**Root Cause**: Version incompatibility between `langgraph` and `langchain-core` packages.

---

## ✅ The Solution

### What I Fixed

**Updated** `/choreo-ai-assistant/requirements.txt`:

| Package | Old Version | New Version |
|---------|-------------|-------------|
| langchain | >=0.2.14 | >=0.3.0 |
| langchain-core | >=0.2.30 | >=0.3.0 |
| langgraph | >=0.1.43 | >=0.2.0 |

These updated versions are compatible and include the `RemoveMessage` class.

---

## 🛠️ What You Need to Do

Since the Docker image needs to be rebuilt with the fixed dependencies, follow these steps:

### Quick Start (Recommended)

```bash
# 1. Navigate to project root
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# 2. Rebuild Docker image (takes 5-10 minutes)
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .

# 3. Load image into Minikube
minikube image load choreo-ai-backend:v2-fixed

# 4. Restart deployment
kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

# 5. Watch the rollout (wait for success)
kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant

# 6. Verify pods are running
kubectl get pods -n choreo-ai-assistant
```

### Expected Result

After following the steps above, you should see:

```
NAME                                  READY   STATUS    RESTARTS   AGE
choreo-ai-backend-xxx                 1/1     Running   0          2m
choreo-ai-backend-yyy                 1/1     Running   0          2m
choreo-ai-backend-zzz                 1/1     Running   0          2m
choreo-ai-frontend-...                1/1     Running   ...        3d
```

All backend pods should show `1/1 Running` status (not CrashLoopBackOff).

---

## 📁 Resources I Created

To help you deploy and troubleshoot, I created these files:

### Scripts (in `backend/k8s/scripts/`)

1. **`quick-fix.sh`** - Automated rebuild and redeploy script
2. **`deploy-backend-auto.sh`** - Full auto-deployment with diagnostics  
3. **`diagnose-backend.sh`** - Diagnostic tool to check deployment status
4. **`monitor-build.sh`** - Monitor Docker build progress
5. **`STEP_BY_STEP.sh`** - Step-by-step guide with all commands

### Documentation (in `backend/k8s/`)

1. **`FIX_SUMMARY.md`** - Detailed fix summary (this file)
2. **`BACKEND_DEPLOYMENT_GUIDE.md`** - Complete deployment guide
3. **`QUICK_REFERENCE.txt`** - Quick reference commands (already existed)

---

## 🧪 Verification Steps

After the rebuild and restart:

### 1. Check Pod Status
```bash
kubectl get pods -n choreo-ai-assistant
```
✅ All backend pods should be `Running` with `1/1` ready

### 2. Check Logs
```bash
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend --tail=50
```
✅ Should show application startup logs  
❌ Should NOT show `ImportError` or `RemoveMessage` errors

### 3. Test Health Endpoint
```bash
# Start port forwarding
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &

# Test endpoint
curl http://localhost:9090/health
```
Expected response: `{"status":"healthy",...}`

### 4. Access API Docs
Open in browser: http://localhost:9090/docs

You should see the FastAPI Swagger UI.

---

## 🔍 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Cluster | ✅ Running | Minikube |
| Namespace | ✅ Created | choreo-ai-assistant |
| Frontend | ✅ Running | 3/3 pods healthy |
| **Backend** | **❌ Failing** | **CrashLoopBackOff (dependency issue)** |
| Services | ✅ Created | All K8s services exist |
| ConfigMaps | ✅ Created | Configuration ready |
| Secrets | ✅ Created | API keys configured |
| **Fix** | **✅ Applied** | **requirements.txt updated** |
| **Action Needed** | **⏳ Rebuild** | **Docker image rebuild required** |

---

## 📝 How to Use the Helper Scripts

### Option 1: Display Step-by-Step Guide
```bash
cd backend/k8s
./STEP_BY_STEP.sh
```
This will show you all the commands with explanations.

### Option 2: Run Diagnostics
```bash
cd backend/k8s
./scripts/diagnose-backend.sh
```
This shows the current status of all backend components.

### Option 3: Monitor Build Progress
```bash
# In one terminal, start the build:
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile . > /tmp/docker-build.log 2>&1 &

# In another terminal, monitor progress:
cd backend/k8s
./scripts/monitor-build.sh
```

---

## 🆘 Troubleshooting

### If pods still crash after rebuild:
```bash
# Check logs
kubectl logs -n choreo-ai-assistant <pod-name>

# Check events
kubectl describe pod -n choreo-ai-assistant <pod-name>

# Force delete old pods
kubectl delete pod -n choreo-ai-assistant -l app=choreo-ai-backend
```

### If Docker build fails:
```bash
# Check disk space
df -h

# Clean Docker cache
docker system prune -a

# Try build again
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .
```

### If image not found in Minikube:
```bash
# Option 1: Load existing image
minikube image load choreo-ai-backend:v2-fixed

# Option 2: Build directly in Minikube's Docker
eval $(minikube docker-env)
docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .
eval $(minikube docker-env -u)
```

---

## 🎯 Next Steps

1. **Run the Docker build** (this is the key step)
   ```bash
   cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
   docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .
   ```

2. **Load into Minikube**
   ```bash
   minikube image load choreo-ai-backend:v2-fixed
   ```

3. **Restart deployment**
   ```bash
   kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant
   kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant
   ```

4. **Verify everything is working**
   ```bash
   kubectl get pods -n choreo-ai-assistant
   kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
   curl http://localhost:9090/health
   ```

5. **Access your services**
   - Frontend: http://localhost:8080 (port-forward svc/choreo-ai-frontend-service 8080:80)
   - Backend: http://localhost:9090/docs (port-forward svc/choreo-ai-backend-service 9090:9090)

---

## ⏱️ Time Estimate

- Docker build: **5-10 minutes** (first time, faster on subsequent builds)
- Load into Minikube: **30-60 seconds**
- Deployment restart: **2-3 minutes**
- **Total: ~10-15 minutes**

---

## ✨ Summary

**Problem**: LangChain/LangGraph version incompatibility causing ImportError  
**Fix Applied**: Updated requirements.txt with compatible versions  
**Action Required**: Rebuild Docker image and restart K8s deployment  
**Estimated Time**: 10-15 minutes  
**Success Indicator**: All pods show `1/1 Running`, health endpoint responds

---

**Created**: November 18, 2025  
**Issue**: Backend CrashLoopBackOff - dependency version mismatch  
**Status**: Fix ready - requires Docker rebuild and deployment restart

