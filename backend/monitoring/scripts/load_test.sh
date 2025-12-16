#!/bin/bash
# Load testing script for Choreo AI Assistant monitoring
set -e
echo "🧪 Load Testing Choreo AI Assistant"
echo ""
BASE_URL="${BASE_URL:-http://localhost:8000}"
NUM_REQUESTS="${NUM_REQUESTS:-50}"
echo "Base URL: $BASE_URL"
echo "Number of requests: $NUM_REQUESTS"
echo ""
# Check if service is running
echo "Checking if service is running..."
if ! curl -s "$BASE_URL/api/health" > /dev/null 2>&1; then
    echo "⚠️  Service is not running at $BASE_URL"
    echo "Please start the service first: ./start.sh"
    exit 1
fi
echo "✅ Service is running"
echo ""
# Test questions
questions=(
    "What is Choreo?"
    "How do I deploy an application?"
    "What are the key features?"
)
echo "🔥 Starting load test..."
start_time=$(date +%s)
for i in $(seq 1 $NUM_REQUESTS); do
    idx=$((i % ${#questions[@]}))
    question="${questions[$idx]}"
    curl -s -X POST "$BASE_URL/api/ask?question=$(echo "$question" | sed 's/ /%20/g')" > /dev/null 2>&1 &
    if (( i % 10 == 0 )); then
        wait
        echo "  Progress: $i/$NUM_REQUESTS"
    fi
done
wait
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ Load test completed"
echo "  Duration: ${duration}s"
echo ""
echo "Check metrics at: http://localhost:8000/metrics"
echo "View dashboard at: http://localhost:3000"
