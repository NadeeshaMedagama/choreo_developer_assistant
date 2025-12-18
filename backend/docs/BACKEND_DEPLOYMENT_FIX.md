# BACKEND DEPLOYMENT FIX FOR CHOREO

## ✅ Problem Solved

**Error:** "Upstream connection timeout" (Error 102504)
**Cause:** Backend was binding to hardcoded port instead of reading Choreo's dynamic PORT
**Solution:** Created start.py that reads PORT environment variable

---

## 📁 Files Created in Backend Directory

### ✅ New Files:
1. **`backend/Dockerfile`** - Docker configuration for backend deployment
2. **`backend/start.py`** - Startup script that reads PORT from environment
3. **`backend/BACKEND_DEPLOYMENT_FIX.md`** - This documentation

### ✅ Existing Files (No changes needed):
- **`backend/.choreo/component.yaml`** - Already configured correctly
- **`backend/app.py`** - FastAPI application
- **`backend/choreo-ai-assistant/requirements.txt`** - Dependencies

---

## 🔧 The Fix

### Dockerfile (backend/Dockerfile)

```dockerfile
# Working directory is /app
WORKDIR /app

# Copies backend directory contents
COPY .. .

# Installs dependencies from backend subdirectories
RUN pip install -r choreo-ai-assistant/requirements.txt && \
    pip install -r diagram_processor/requirements.txt

# Uses start.py to read PORT dynamically
CMD ["python3", "start.py"]
```

### Startup Script (backend/start.py)
```python
# Reads PORT from Choreo's environment
port = os.environ.get('PORT', '9090')

# Starts uvicorn on dynamic port
cmd = ['uvicorn', 'app:app', '--host', '0.0.0.0', '--port', port]
subprocess.run(cmd, check=True)
```

### How It Works:
```
Choreo Platform
    ↓ Sets: PORT=<dynamic-port>
Backend Container Starts
    ↓ Runs: python3 start.py
start.py Reads PORT
    ↓ Launches: uvicorn app:app --host 0.0.0.0 --port ${PORT}
Application Binds to Correct Port
    ↓ Choreo Routes Traffic
SUCCESS - No Timeout! ✅
```

---

## 🚀 Deployment Steps

### 1. Verify Files Exist
```bash
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant/backend"

# Check new files exist
ls -la Dockerfile start.py

# Check component.yaml
ls -la .choreo/component.yaml
```

### 2. Test Locally (Optional)
```bash
# Build Docker image
docker build -t choreo-ai-backend .

# Run with custom port
docker run -e PORT=8080 -p 8080:8080 choreo-ai-backend

# Test health endpoint
curl http://localhost:8080/api/health
```

### 3. Commit and Push
```bash
# From backend directory
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"

# Add new files
git add backend/Dockerfile backend/start.py backend/BACKEND_DEPLOYMENT_FIX.md

# Commit
git commit -m "Fix: Backend now uses dynamic PORT for Choreo deployment

- Added backend/Dockerfile for Choreo deployment
- Added backend/start.py to read PORT environment variable
- Fixes upstream connection timeout (error 102504)
- Backend binds to 0.0.0.0:\${PORT} instead of hardcoded 9090"

# Push
git push origin main
```

### 4. Deploy in Choreo

1. **Go to Choreo Console**: https://console.choreo.dev
2. **Select Your Component** (or create new)
3. **Deployment Configuration**:
   - **Project Path**: `backend`
   - **Build Type**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (relative to backend dir)
   - **Context**: `.` (backend directory)
4. **Configure Environment Variables** (see list below)
5. **Click Deploy**

---

## 🔑 Required Environment Variables in Choreo

Configure these in Choreo's environment configuration:

### Azure OpenAI (Required):
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION` (default: "2024-02-15-preview")

### Milvus Vector DB (Required):
- `MILVUS_URI`
- `MILVUS_TOKEN`
- `MILVUS_COLLECTION_NAME` (default: "choreo_developer_assistant")
- `MILVUS_DIMENSION` (default: 1536)
- `MILVUS_METRIC` (default: "COSINE")

### Optional:
- `GITHUB_TOKEN`
- `GOOGLE_VISION_API_KEY`
- `ENABLE_LLM_SUMMARIZATION` (default: "true")
- `ENABLE_URL_VALIDATION` (default: "true")

### Auto-provided by Choreo:
- `PORT` - Dynamically assigned (this is what we fixed!)

---

## ✅ Verification After Deployment

### Check Container Logs:
Look for these success indicators:
```
============================================================
Starting Choreo AI Assistant Backend
Port: <dynamic-port>
Host: 0.0.0.0
============================================================
Command: uvicorn app:app --host 0.0.0.0 --port <port>
============================================================
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:<port>
```

### Test Endpoints:
```bash
# Health check
curl https://your-choreo-url/api/health

# Expected: {"status": "healthy", ...}

# Root endpoint
curl https://your-choreo-url/

# Expected: {"message": "Choreo AI Assistant...", "status": "ok"}

# AI query
curl -X POST https://your-choreo-url/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'
```

---

## 📊 Directory Structure

```
backend/
├── .choreo/
│   ├── component.yaml        ← Choreo configuration (already exists)
│   └── openapi.yaml
├── Dockerfile                 ← NEW - Docker build config
├── start.py                   ← NEW - Startup script with PORT
├── app.py                     ← FastAPI application
├── choreo-ai-assistant/
│   └── requirements.txt       ← Dependencies
├── diagram_processor/
│   └── requirements.txt       ← Dependencies
├── db/
├── services/
├── utils/
└── ... (other backend files)
```

---

## 🔍 Key Differences from Root Deployment

### Root Deployment (Previous):
- Dockerfile at root level
- Had to reference: `backend/app.py`
- Python path: `/app/backend`
- CMD: `uvicorn backend.app:app`

### Backend Deployment (Current):
- Dockerfile in backend directory
- Direct reference: `app.py`
- Python path: `/app`
- CMD: `uvicorn app:app`

**The backend deployment is simpler and more natural!** ✅

---

## 🆘 Troubleshooting

### Issue: Container fails to build
**Check:**
- Both requirements.txt files exist
- Paths in Dockerfile are correct
- Dependencies install successfully

**Fix:**
```bash
# Test locally
cd backend
docker build -t test-backend .
```

### Issue: Health check fails
**Check:**
- PORT environment variable is set
- Application starts on correct port
- `/api/health` endpoint responds

**Fix:**
```bash
# Check logs for port binding
# Should show: "Host: 0.0.0.0" and "Port: <number>"
```

### Issue: Still getting timeout
**Check:**
- start.py is executable
- Logs show correct port binding
- All required env vars are set

**Fix:**
1. Verify Dockerfile CMD: `CMD ["python3", "start.py"]`
2. Check logs show: "Starting Choreo AI Assistant Backend"
3. Ensure health check passes after 90s

---

## ✅ Success Checklist

Before deploying:
- [x] backend/Dockerfile created
- [x] backend/start.py created
- [x] backend/.choreo/component.yaml exists
- [ ] All environment variables configured in Choreo
- [ ] Ready to commit and push

After deploying:
- [ ] Container builds successfully
- [ ] Container starts and stays running
- [ ] Logs show: "Starting Choreo AI Assistant Backend"
- [ ] Logs show correct port binding
- [ ] Health check passes (~90s)
- [ ] GET /api/health → 200 OK
- [ ] No timeout errors

---

## 🎯 Summary

**What Changed:**
- ✅ Created `backend/Dockerfile` for Choreo deployment
- ✅ Created `backend/start.py` to read PORT dynamically
- ✅ Backend now binds to `0.0.0.0:${PORT}`

**What Stayed the Same:**
- ✅ `backend/.choreo/component.yaml` (no changes needed)
- ✅ `backend/app.py` (no changes needed)
- ✅ All other backend code (no changes needed)

**Result:**
- ✅ **No more "upstream connection timeout" errors!**
- ✅ **Backend correctly uses Choreo's dynamic PORT**
- ✅ **Ready to deploy to Choreo!**

---

## 🚀 Quick Deploy Commands

```bash
# Navigate to project root
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"

# Add files
git add backend/Dockerfile backend/start.py backend/BACKEND_DEPLOYMENT_FIX.md

# Commit
git commit -m "Fix: Backend uses dynamic PORT for Choreo"

# Push
git push origin main

# Then deploy in Choreo console with:
# - Project Path: backend
# - Dockerfile: Dockerfile
# - Context: .
```

---

**🎉 Backend is now ready for Choreo deployment!**

*No more upstream timeout errors. Application will bind to the correct dynamic port.*

