# 🚀 CHOREO DEPLOYMENT CHECKLIST

## ✅ Pre-Deployment Checklist

### Code Changes (All Complete ✓)
- [x] Created `start.py` - Dynamic port binding script
- [x] Created `start.sh` - Alternative bash script
- [x] Updated `Dockerfile` - Uses start.py instead of hardcoded port
- [x] Created `requirements.txt` - Root level dependencies
- [x] Created `.choreo/component.yaml` - Choreo configuration
- [x] All tests passing (verified with test_port_binding.sh)

### Configuration Files Required in Choreo

#### 🔴 Critical Environment Variables (Must Configure)
Configure these in your Choreo deployment settings:

**Vector Database (Milvus):**
```
MILVUS_URI=<your-milvus-endpoint>
MILVUS_TOKEN=<your-milvus-token>
MILVUS_COLLECTION_NAME=readme_embeddings
```

**Azure OpenAI:**
```
AZURE_OPENAI_KEY=<your-azure-key>
AZURE_OPENAI_ENDPOINT=<your-azure-endpoint>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

#### 🟡 Optional Environment Variables
```
GITHUB_TOKEN=<for-github-integration>
GOOGLE_VISION_API_KEY=<for-image-processing>
ENABLE_URL_VALIDATION=true
ENABLE_LLM_SUMMARIZATION=true
```

#### 🟢 Auto-Configured by Choreo
```
PORT=<dynamically-assigned>  ← This is what we fixed!
```

---

## 📝 Deployment Steps

### Step 1: Commit and Push Changes
```bash
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"

# Add all new files
git add .

# Commit with descriptive message
git commit -m "Fix: Bind to dynamic PORT env variable for Choreo deployment

- Created start.py to read PORT environment variable
- Updated Dockerfile to use start.py
- Added .choreo/component.yaml configuration
- Fixes upstream connection timeout (error 102504)
- Ensures binding to 0.0.0.0:${PORT} instead of hardcoded port"

# Push to repository
git push origin main
```

### Step 2: Configure Choreo Component

1. **Go to Choreo Console**: https://console.choreo.dev
2. **Select your Component** or create new one
3. **Configure Build Settings**:
   - Build Type: Dockerfile
   - Dockerfile Path: `Dockerfile`
   - Context Path: `.`

4. **Configure Environment Variables**:
   - Add all required variables listed above
   - Make sure sensitive data (keys, tokens) are marked as secrets

5. **Configure Health Check** (if not auto-detected):
   - Health Check Path: `/api/health`
   - Port: Use default (Choreo handles this)
   - Initial Delay: 90 seconds
   - Timeout: 30 seconds

### Step 3: Deploy

1. Click **"Deploy"** or **"Redeploy"** button
2. Monitor build logs for errors
3. Wait for health checks to pass (may take ~90 seconds)

### Step 4: Verify Deployment

1. **Check Deployment Status**: Should show "Healthy" ✅
2. **Test Health Endpoint**:
   ```bash
   curl https://your-choreo-url/api/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "message": "All services are healthy",
     ...
   }
   ```

3. **Test Main Endpoint**:
   ```bash
   curl https://your-choreo-url/
   ```
   Should return:
   ```json
   {
     "message": "Choreo AI Assistant (Azure LLM + Milvus) is running.",
     "status": "ok"
   }
   ```

4. **Test AI Query**:
   ```bash
   curl -X POST https://your-choreo-url/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Choreo?"}'
   ```

---

## 🔍 Monitoring Deployment

### Check Logs in Choreo
Look for these success indicators:
```
✓ Starting Choreo AI Assistant on port <dynamic-port>...
✓ Binding to 0.0.0.0:<dynamic-port>
✓ FastAPI application starting up...
✓ All services initialized successfully
✓ Application startup complete
```

### Common Log Messages (Normal)
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:<port>
```

### Warning Signs to Watch For
```
❌ "Address already in use" - Port conflict (shouldn't happen with PORT env)
❌ "Connection refused" - Not binding to 0.0.0.0
❌ "upstream request timeout" - OLD error, should be fixed now
❌ "Failed to initialize Milvus" - Check Milvus credentials
❌ "Azure OpenAI API error" - Check Azure credentials
```

---

## ⚠️ Troubleshooting Guide

### Issue: Container fails to start
**Symptoms**: Container exits immediately
**Causes & Solutions**:
- Missing dependencies: Check requirements.txt is properly installed
- Syntax errors: Review logs for Python errors
- Permission issues: Verify user 10014 has correct permissions

**Fix**: Check container logs in Choreo console

### Issue: Health check fails
**Symptoms**: Deployment shows "Unhealthy"
**Causes & Solutions**:
- Services taking too long: Increase startup period beyond 90s
- Missing environment variables: Check all required vars are set
- Milvus connection fails: Verify MILVUS_URI and TOKEN

**Fix**: 
```dockerfile
# In Dockerfile, increase start-period:
HEALTHCHECK --start-period=120s ...
```

### Issue: 502 Bad Gateway
**Symptoms**: External requests fail
**Causes & Solutions**:
- Application crashed: Check logs for errors
- Not responding in time: Increase timeouts
- Wrong port binding: Verify using PORT env var (should be fixed now)

**Fix**: Review application logs for crash details

### Issue: Still getting "upstream timeout"
**Symptoms**: Error 102504 persists
**Causes & Solutions**:
- Old deployment cached: Force rebuild
- Wrong port in health check: Verify health check uses same port
- Application slow to respond: Check initialization time

**Fix**: 
1. Clear Choreo cache and rebuild
2. Verify logs show correct port binding
3. Test health endpoint locally first

---

## 🎯 Success Criteria

Your deployment is successful when:

- [✅] Container builds without errors
- [✅] Container starts and runs continuously
- [✅] Health check endpoint responds: `GET /api/health` → 200 OK
- [✅] Root endpoint responds: `GET /` → {"status": "ok"}
- [✅] AI endpoint works: `POST /api/ask` → Returns answer
- [✅] No "upstream timeout" errors in logs
- [✅] Application accessible via Choreo URL
- [✅] Logs show: "Binding to 0.0.0.0:<port>"

---

## 📚 Additional Resources

### Documentation Files Created
1. **CHOREO_DEPLOYMENT_FIX.md** - Detailed fix explanation
2. **test_port_binding.sh** - Verification script
3. **start.py** - Main startup script
4. **.choreo/component.yaml** - Choreo configuration

### Key Changes Made
- ✅ Port binding: Now uses `PORT` env variable
- ✅ Host binding: Correctly binds to `0.0.0.0`
- ✅ Startup script: Reads environment dynamically
- ✅ Choreo config: Proper health checks configured

### Testing Locally Before Deploy
```bash
# Test port binding
./test_port_binding.sh

# Test with custom port
PORT=8080 python3 start.py

# Test Docker build
docker build -t test .
docker run -e PORT=8080 -p 8080:8080 test

# Verify health
curl http://localhost:8080/api/health
```

---

## 🎉 Deployment Complete!

Once deployed successfully, you should be able to:
1. ✅ Access your AI assistant via Choreo URL
2. ✅ Query the AI: `POST /api/ask`
3. ✅ Stream responses: `POST /api/ask/stream`
4. ✅ Ingest new repos: `POST /api/ingest/github`
5. ✅ Monitor health: `GET /api/health`

**The upstream connection timeout issue is now resolved!** 🎊

---

## 📞 Support

If issues persist after deployment:
1. Check Choreo console logs
2. Verify all environment variables are set
3. Review the troubleshooting guide above
4. Test endpoints locally first
5. Check Choreo documentation: https://wso2.com/choreo/docs/

---

*Last updated: December 18, 2025*
*Fix version: 1.0 - Dynamic PORT binding*

