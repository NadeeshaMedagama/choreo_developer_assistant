# 🚀 Choreo Deployment - Command Reference

Quick reference for deploying and testing the Choreo AI Assistant.

---

## 📋 Pre-Deployment

```bash
# Navigate to project
cd /home/nadeeshame/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant

# Check you have all required files
ls -la .choreo/
# Should see: component.yaml, openapi.yaml

# Review deployment docs
cat CHOREO_DEPLOYMENT.md          # Full guide
cat CHOREO_CHECKLIST.md           # Step-by-step
cat .env.choreo.example           # Environment variables
```

---

## 🧪 Local Testing

```bash
# Test with Docker (recommended before Choreo deployment)
./test-choreo-deployment.sh

# Manual Docker test
docker build -t choreo-ai-assistant:test .
docker run -p 9090:9090 --env-file .env choreo-ai-assistant:test

# Test health endpoint
curl http://localhost:9090/health

# Test API endpoint
curl -X POST http://localhost:9090/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'
```

---

## 🔍 Verify Configuration

```bash
# Check Dockerfile health check settings
grep HEALTHCHECK Dockerfile
# Should show: start-period=90s, timeout=30s

# Validate Python syntax
python -m py_compile backend/app.py

# Check for lazy initialization
grep "services_initialized = False" backend/app.py
grep "def initialize_services" backend/app.py
```

---

## 📦 Prepare for Deployment

```bash
# Ensure all files are tracked
git status

# Add new/modified files
git add .choreo/
git add backend/app.py
git add Dockerfile
git add *.md

# Commit changes
git commit -m "Add Choreo deployment support with lazy initialization"

# Push to GitHub
git push origin main
```

---

## 🎯 Deploy to Choreo

### In Choreo Console:

1. **Create Component**
   - Go to your Choreo project
   - Click "Create" → "Service"
   - Select "GitHub" as source

2. **Configure Build**
   - Build Type: `dockerfile`
   - Dockerfile Path: `Dockerfile`
   - Docker Context: `.`
   - Port: `9090`

3. **Set Environment Variables**
   ```
   AZURE_OPENAI_KEY=<your-key>
   AZURE_OPENAI_ENDPOINT=<your-endpoint>
   AZURE_OPENAI_DEPLOYMENT=<deployment-name>
   AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=<embeddings-deployment>
   MILVUS_URI=<milvus-uri>
   MILVUS_TOKEN=<milvus-token>
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build (3-5 minutes)
   - Check logs for "All services initialized successfully"

---

## ✅ Post-Deployment Verification

```bash
# Replace YOUR_URL with your Choreo URL
CHOREO_URL="https://your-component-xyz.choreo.dev"

# Test root endpoint
curl $CHOREO_URL/

# Test health (should be fast, < 5 seconds)
time curl $CHOREO_URL/health

# Test detailed health (initializes services, 10-30s)
time curl $CHOREO_URL/api/health

# Test AI endpoint
curl -X POST $CHOREO_URL/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'

# Test metrics endpoint
curl $CHOREO_URL/metrics
```

---

## 🔧 Troubleshooting

```bash
# Check if health endpoint is fast
time curl https://your-app.choreo.dev/health
# Should be < 5 seconds

# Get detailed status
curl -s https://your-app.choreo.dev/api/health | python3 -m json.tool

# Check if services are initialized
curl -s https://your-app.choreo.dev/health | grep services_initialized

# View container logs (in Choreo Console)
# Look for:
# - "FastAPI application starting up..."
# - "All services initialized successfully"
```

---

## 📊 Monitoring Commands

```bash
CHOREO_URL="https://your-component-xyz.choreo.dev"

# Get Prometheus metrics
curl $CHOREO_URL/metrics

# Check health status
curl $CHOREO_URL/api/health

# Monitor response times
time curl -X POST $CHOREO_URL/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

---

## 🔄 Update Deployment

```bash
# After making changes
git add .
git commit -m "Update deployment configuration"
git push origin main

# In Choreo Console:
# - Navigate to your component
# - Click "Deploy" to redeploy
# - Monitor build logs
```

---

## 📥 Data Ingestion

```bash
CHOREO_URL="https://your-component-xyz.choreo.dev"

# Ingest a GitHub repository
curl -X POST "$CHOREO_URL/api/ingest/github?repo_url=https://github.com/wso2/docs-choreo-dev.git&branch=main"

# Ingest organization repositories
curl -X POST "$CHOREO_URL/api/ingest/org?org=wso2-enterprise&keyword=choreo&max_repos=5"
```

---

## 🎯 Quick Health Check Script

```bash
#!/bin/bash
# Save as: check-choreo-health.sh

CHOREO_URL="${1:-https://your-app.choreo.dev}"

echo "Checking $CHOREO_URL..."

# Basic health
echo -n "Basic health check: "
if curl -s --max-time 5 "$CHOREO_URL/health" | grep -q "healthy"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

# Detailed health
echo -n "Detailed health check: "
if curl -s --max-time 30 "$CHOREO_URL/api/health" | grep -q "status"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

echo "Done!"
```

Usage: `./check-choreo-health.sh https://your-app.choreo.dev`

---

## 📚 Documentation Quick Access

```bash
# View deployment guide
cat CHOREO_DEPLOYMENT.md | less

# View checklist
cat CHOREO_CHECKLIST.md | less

# View technical details
cat CHOREO_DEPLOYMENT_FIX.md | less

# View environment variables
cat .env.choreo.example
```

---

## 🆘 Emergency Commands

```bash
# Stop local Docker container
docker stop choreo-ai-test && docker rm choreo-ai-test

# Check Docker logs
docker logs choreo-ai-test --tail 50

# Test Python compilation
cd backend && python -m py_compile app.py

# Check port availability
lsof -i :9090

# Clean Docker
docker system prune -a
```

---

## ✨ Success Indicators

Look for these in Choreo logs:

```
✅ "FastAPI application starting up..."
✅ "Metrics middleware added"
✅ "Request received, initializing services..."
✅ "Initializing Milvus vector client..."
✅ "Milvus vector client initialized"
✅ "Initializing Azure OpenAI LLM service..."
✅ "LLM service initialized"
✅ "All services initialized successfully"
```

---

## 📞 Support Resources

- 📖 [CHOREO_DEPLOYMENT.md](CHOREO_DEPLOYMENT.md)
- 📋 [CHOREO_CHECKLIST.md](CHOREO_CHECKLIST.md)
- 🔧 [CHOREO_DEPLOYMENT_FIX.md](CHOREO_DEPLOYMENT_FIX.md)
- 📝 [.env.choreo.example](../../../.env.choreo.example)
- 🎯 [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)

---

**Ready to deploy!** 🚀

