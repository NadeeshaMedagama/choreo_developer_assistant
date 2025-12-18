#!/bin/bash
# Local deployment test script
# Tests the application in Docker to verify Choreo deployment readiness

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="choreo-ai-test"
IMAGE_NAME="choreo-ai-assistant:test"
PORT=9090

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Choreo AI Assistant - Local Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# Trap cleanup on exit
trap cleanup EXIT

# Step 1: Check environment variables
echo -e "${BLUE}Step 1: Checking environment variables...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo -e "${YELLOW}Create a .env file with required variables. See .env.choreo.example${NC}"
    exit 1
fi

# Check for required variables
required_vars=("AZURE_OPENAI_KEY" "AZURE_OPENAI_ENDPOINT" "MILVUS_URI" "MILVUS_TOKEN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}✗ Missing required environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

echo -e "${GREEN}✓ Environment variables configured${NC}"
echo ""

# Step 2: Build Docker image
echo -e "${BLUE}Step 2: Building Docker image...${NC}"
docker build -t $IMAGE_NAME . || {
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 3: Start container
echo -e "${BLUE}Step 3: Starting container...${NC}"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --env-file .env \
    $IMAGE_NAME || {
    echo -e "${RED}✗ Failed to start container${NC}"
    exit 1
}
echo -e "${GREEN}✓ Container started${NC}"
echo ""

# Step 4: Wait for container to be ready
echo -e "${BLUE}Step 4: Waiting for service to be ready...${NC}"
sleep 5

# Check if container is still running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}✗ Container stopped unexpectedly${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo -e "${GREEN}✓ Container is running${NC}"
echo ""

# Step 5: Test health endpoint (should be fast)
echo -e "${BLUE}Step 5: Testing fast health check...${NC}"
start_time=$(date +%s)

if curl -f -s --max-time 10 http://localhost:$PORT/health > /dev/null; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo -e "${GREEN}✓ Health check passed in ${duration}s${NC}"

    if [ $duration -gt 5 ]; then
        echo -e "${YELLOW}⚠ Warning: Health check took longer than expected (${duration}s > 5s)${NC}"
    fi
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs $CONTAINER_NAME | tail -20
    exit 1
fi
echo ""

# Step 6: Test root endpoint
echo -e "${BLUE}Step 6: Testing root endpoint...${NC}"
response=$(curl -s http://localhost:$PORT/ || echo "")
if echo "$response" | grep -q "Choreo AI Assistant"; then
    echo -e "${GREEN}✓ Root endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Step 7: Test API health endpoint (triggers initialization)
echo -e "${BLUE}Step 7: Testing detailed health check (may take 10-30s)...${NC}"
echo -e "${YELLOW}This will initialize all services...${NC}"
start_time=$(date +%s)

response=$(curl -s --max-time 60 http://localhost:$PORT/api/health || echo "")
end_time=$(date +%s)
duration=$((end_time - start_time))

if echo "$response" | grep -q "status"; then
    echo -e "${GREEN}✓ Detailed health check passed in ${duration}s${NC}"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo -e "${RED}✗ Detailed health check failed${NC}"
    echo "Response: $response"
fi
echo ""

# Step 8: Test AI endpoint (optional, requires data)
echo -e "${BLUE}Step 8: Testing AI endpoint (optional)...${NC}"
read -p "Do you want to test the AI endpoint? This requires data to be ingested (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    response=$(curl -s --max-time 30 -X POST http://localhost:$PORT/api/ask \
        -H "Content-Type: application/json" \
        -d '{"question": "What is Choreo?"}' || echo "")

    if echo "$response" | grep -q "answer"; then
        echo -e "${GREEN}✓ AI endpoint working${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null | head -20
    else
        echo -e "${YELLOW}⚠ AI endpoint may not have data ingested yet${NC}"
        echo "Response: $response"
    fi
else
    echo -e "${YELLOW}Skipped AI endpoint test${NC}"
fi
echo ""

# Step 9: Show container logs
echo -e "${BLUE}Step 9: Recent container logs...${NC}"
docker logs --tail 30 $CONTAINER_NAME
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Local deployment test completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Container is running at: http://localhost:$PORT"
echo ""
echo "Test endpoints:"
echo "  - Health: curl http://localhost:$PORT/health"
echo "  - API Health: curl http://localhost:$PORT/api/health"
echo "  - Ask AI: curl -X POST http://localhost:$PORT/api/ask -H 'Content-Type: application/json' -d '{\"question\": \"test\"}'"
echo ""
echo "Stop container with: docker stop $CONTAINER_NAME"
echo ""
echo -e "${GREEN}Ready for Choreo deployment!${NC}"

