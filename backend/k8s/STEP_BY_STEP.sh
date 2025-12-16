#!/bin/bash

# STEP-BY-STEP: Fix Backend Deployment
# Follow these commands one by one

cat << 'EOF'

╔════════════════════════════════════════════════════════════╗
║          STEP-BY-STEP BACKEND FIX GUIDE                    ║
╚════════════════════════════════════════════════════════════╝

✅ STEP 1: Verify you're in the right directory
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
pwd

Expected output: /home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant


✅ STEP 2: Start Docker build (this takes 5-10 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .

⏳ Wait for: "Successfully built" and "Successfully tagged choreo-ai-backend:v2-fixed"

Note: This may take several minutes. You'll see output like:
  Step 1/15 : FROM python:3.11-slim as builder
  Step 2/15 : WORKDIR /app
  ... (many more steps)
  Successfully built abc123def456
  Successfully tagged choreo-ai-backend:v2-fixed


✅ STEP 3: Verify the image was built
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docker images | grep choreo-ai-backend

Expected output:
  choreo-ai-backend   v2-fixed   <image-id>   Just now   ~9GB


✅ STEP 4: Load image into Minikube
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

minikube image load choreo-ai-backend:v2-fixed

⏳ Wait for completion (usually 30-60 seconds)


✅ STEP 5: Verify image is in Minikube
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

minikube image ls | grep choreo-ai-backend

Expected output should include: choreo-ai-backend:v2-fixed


✅ STEP 6: Restart the backend deployment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant

Expected output:
  deployment.apps/choreo-ai-backend restarted


✅ STEP 7: Watch the rollout (wait for completion)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kubectl rollout status deployment/choreo-ai-backend -n choreo-ai-assistant

⏳ Wait for: "deployment "choreo-ai-backend" successfully rolled out"

This may take 2-3 minutes as:
  1. Old pods terminate
  2. New pods start
  3. New pods become ready


✅ STEP 8: Check pod status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kubectl get pods -n choreo-ai-assistant

Expected output (all backend pods should show Running and 1/1 READY):
  NAME                                  READY   STATUS    RESTARTS   AGE
  choreo-ai-backend-xxx                 1/1     Running   0          2m
  choreo-ai-backend-yyy                 1/1     Running   0          2m
  choreo-ai-backend-zzz                 1/1     Running   0          2m
  choreo-ai-frontend-...                1/1     Running   ...        3d

If you see "CrashLoopBackOff" or "Error", go to TROUBLESHOOTING below.


✅ STEP 9: Check backend logs (verify no errors)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend --tail=20

✅ You should see application startup logs
❌ You should NOT see ImportError or RemoveMessage errors


✅ STEP 10: Test the backend health endpoint
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# In one terminal, start port forwarding:
kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

# In another terminal, test the endpoint:
curl http://localhost:9090/health

Expected response:
  {"status":"healthy",...}


✅ STEP 11: Access the API documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Keep port-forward running from Step 10
# Open in browser:

  http://localhost:9090/docs

You should see the FastAPI Swagger UI with all endpoints documented.


🎉 SUCCESS! Your backend is now running!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To access your services:

  Frontend:  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80
             http://localhost:8080

  Backend:   kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090
             http://localhost:9090/docs


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: Pods still in CrashLoopBackOff after rebuild
Solution:
  1. Check logs: kubectl logs -n choreo-ai-assistant <pod-name>
  2. Check events: kubectl describe pod -n choreo-ai-assistant <pod-name>
  3. Verify image was loaded: minikube image ls | grep v2-fixed
  4. Force delete old pods: kubectl delete pod -n choreo-ai-assistant -l app=choreo-ai-backend

Problem: Docker build fails
Solution:
  1. Check disk space: df -h
  2. Clean Docker: docker system prune -a
  3. Try again: docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .

Problem: Image not found in Minikube
Solution:
  1. Use Minikube's Docker: eval $(minikube docker-env)
  2. Rebuild: docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile .
  3. Exit Minikube Docker: eval $(minikube docker-env -u)

Problem: Port forward fails
Solution:
  1. Kill existing port forwards: pkill -f "port-forward"
  2. Try again: kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090

Problem: Need to start fresh
Solution:
  # Delete the deployment
  kubectl delete deployment choreo-ai-backend -n choreo-ai-assistant

  # Reapply from scratch
  kubectl apply -f backend/k8s/base/deployments/backend-deployment.yaml


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USEFUL COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Watch pods continuously
kubectl get pods -n choreo-ai-assistant -w

# Stream logs from all backend pods
kubectl logs -n choreo-ai-assistant -l app=choreo-ai-backend -f

# Get detailed pod info
kubectl describe pod -n choreo-ai-assistant <pod-name>

# Execute command in pod
kubectl exec -it -n choreo-ai-assistant <pod-name> -- bash

# Check events
kubectl get events -n choreo-ai-assistant --sort-by='.lastTimestamp' | tail -20

# Scale deployment
kubectl scale deployment choreo-ai-backend -n choreo-ai-assistant --replicas=1

# Check service endpoints
kubectl get endpoints -n choreo-ai-assistant

# Full cluster status
cd backend/k8s && ./scripts/diagnose-backend.sh


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For more help, see:
  - backend/k8s/FIX_SUMMARY.md
  - backend/k8s/BACKEND_DEPLOYMENT_GUIDE.md
  - backend/k8s/QUICK_REFERENCE.txt

EOF

