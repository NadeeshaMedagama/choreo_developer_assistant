#!/bin/bash

# Wait for v2-fixed image build and deploy

echo "🔨 Building choreo-ai-backend:v2-fixed with --no-cache..."
echo "This will take 10-15 minutes. Please be patient!"
echo ""
echo "⏱️  Started at: $(date)"
echo ""

# The build is already running in the background
# Just wait for it to complete by monitoring the log

echo "Monitoring build progress..."
echo "Press Ctrl+C to stop watching (build will continue in background)"
echo ""

tail -f /tmp/backend-v2-build.log 2>/dev/null &
TAIL_PID=$!

# Wait for build to complete (check every 30 seconds)
while true; do
    sleep 30

    # Check if image exists
    if eval $(minikube docker-env) && docker images | grep -q "choreo-ai-backend.*v2-fixed"; then
        kill $TAIL_PID 2>/dev/null
        echo ""
        echo "✅ Build complete! Image choreo-ai-backend:v2-fixed is ready"
        echo ""
        break
    fi

    echo "Still building... $(date)"
done

echo "📦 Verifying image..."
eval $(minikube docker-env)
docker images | grep choreo-ai-backend
echo ""

echo "🚀 Deploying with new image..."
kubectl delete deployment choreo-ai-backend -n choreo-ai-assistant 2>/dev/null || true
sleep 5

kubectl apply -f "$(dirname "$0")/../base/deployments/backend-deployment.yaml"

echo ""
echo "⏱️  Waiting 45 seconds for pods to start..."
sleep 45

echo ""
echo "📊 Pod Status:"
kubectl get pods -n choreo-ai-assistant

echo ""
echo "📋 Checking logs..."
BACKEND_POD=$(kubectl get pod -n choreo-ai-assistant -l app=choreo-ai-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    echo "Backend pod: $BACKEND_POD"
    echo ""
    kubectl logs -n choreo-ai-assistant $BACKEND_POD --tail=30
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "If pods are Running, access with:"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-backend-service 9090:9090 &"
echo "  kubectl port-forward -n choreo-ai-assistant svc/choreo-ai-frontend-service 8080:80 &"

