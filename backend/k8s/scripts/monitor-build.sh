#!/bin/bash

# Monitor Docker Build Progress
# Run this in a separate terminal to watch the build progress

echo "Monitoring Docker build for choreo-ai-backend:v2-fixed"
echo "This script will check every 5 seconds..."
echo ""

while true; do
    clear
    echo "=== Docker Build Monitor ==="
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # Check if build is running
    if ps aux | grep -q "[d]ocker build.*choreo-ai-backend"; then
        echo "Status: 🔄 BUILD IN PROGRESS"
        echo ""

        # Show recent build output
        if [ -f /tmp/docker-build.log ]; then
            echo "Recent build output:"
            tail -20 /tmp/docker-build.log | grep -E "Step|#|Successfully|Error|FINISHED" || tail -5 /tmp/docker-build.log
        fi
    else
        # Check if image exists
        if docker images | grep -q "choreo-ai-backend.*v2-fixed"; then
            echo "Status: ✅ BUILD COMPLETE"
            echo ""
            docker images | grep "choreo-ai-backend"
            echo ""
            echo "Image is ready! You can now:"
            echo "  1. Load into Minikube: minikube image load choreo-ai-backend:v2-fixed"
            echo "  2. Restart deployment: kubectl rollout restart deployment/choreo-ai-backend -n choreo-ai-assistant"
            break
        else
            echo "Status: ⏸️  BUILD NOT RUNNING"
            echo ""
            echo "To start the build, run:"
            echo "  cd /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant"
            echo "  docker build -t choreo-ai-backend:v2-fixed -f docker/Dockerfile . > /tmp/docker-build.log 2>&1 &"
        fi
    fi

    echo ""
    echo "Press Ctrl+C to stop monitoring"
    sleep 5
done

