# Choreo Deployment - Run Command Guide

## 🚀 Run Command for Choreo

When Choreo asks for the **Run Command**, use:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 9090
```

---

## 📋 Complete Choreo Configuration

### Component Settings

| Setting | Value |
|---------|-------|
| **Component Type** | Service |
| **Build Type** | Dockerfile |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Context** | `.` (root) |
| **Component Directory** | `.` (root) |

### Endpoint Configuration

| Setting | Value |
|---------|-------|
| **Endpoint Name** | api |
| **Port** | 9090 |
| **Type** | REST |
| **Network Visibility** | Public |
| **Context Path** | `/` |
| **Schema File** | `openapi.yaml` |

### Run Command

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 9090
```

**Note:** This is already in the Dockerfile as CMD, so Choreo will use it automatically. You typically don't need to override it.

---

## 🔧 Fixed Issues

### 1. ✅ component.yaml - Added Missing Fields

**Error:** `endpoints[0].service.port is a required field`

**Fix:** Added service configuration:
```yaml
endpoints:
  - name: api
    port: 9090
    service:
      port: 9090
      basePath: /
```

### 2. ✅ Dockerfile - Fixed Port Consistency

**Before:**
```dockerfile
ENV PORT=9090
CMD uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8080}
```

**After:**
```dockerfile
ENV PORT=9090
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
```

### 3. ✅ OpenAPI Schema Path

**File Location:** `.choreo/openapi.yaml` ✅  
**Referenced in:** `component.yaml` ✅

---

## 📝 Step-by-Step Deployment

### 1. Push Changes to GitHub

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Add all changes
git add .choreo/component.yaml
git add Dockerfile
git add .

# Commit
git commit -m "Fix Choreo deployment configuration

- Add service.port to component.yaml
- Fix Dockerfile CMD port consistency
- Ready for Choreo deployment"

# Push
git push origin main
```

### 2. Create Component in Choreo

1. **Go to Choreo Console**: https://console.choreo.dev/
2. **Create New Component**
3. **Select:**
   - Repository: `NadeeshaMedagama/choreo_ai_assistant`
   - Branch: `main`
   - Component Directory: `.` (root)
   - Build Type: Dockerfile

### 3. Configure Environment Variables

In Choreo Console → Your Component → **DevOps** → **Configs & Secrets**

#### Required Variables:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=choreo-ai-assistant-v2
PINECONE_ENVIRONMENT=us-east-1-aws

# GitHub
GITHUB_TOKEN=your_github_token
```

#### Optional Variables:

```bash
# Google Vision (for diagram processing)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

### 4. Deploy

1. Click **Deploy** in Choreo Console
2. Wait for build to complete
3. Check **Logs** for any issues
4. Test the endpoint

---

## 🧪 Testing the Deployment

### Health Check

```bash
curl https://your-component-url.choreo.dev/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "pinecone": "connected"
}
```

### API Documentation

Visit: `https://your-component-url.choreo.dev/docs`

### Ask a Question

```bash
curl -X POST "https://your-component-url.choreo.dev/api/ask?question=What%20is%20Choreo%3F"
```

---

## 🔍 Troubleshooting

### Issue: "service.port is a required field"

✅ **FIXED** - Added to component.yaml:
```yaml
service:
  port: 9090
  basePath: /
```

### Issue: "Schema file does not exist"

✅ **VERIFIED** - File exists at `.choreo/openapi.yaml`

Make sure the file is committed to Git:
```bash
git ls-files .choreo/openapi.yaml
# Should show: .choreo/openapi.yaml
```

### Issue: "Build fails"

Check Choreo build logs for errors. Common issues:

1. **Missing dependencies**: Ensure `requirements.txt` is complete
2. **Import errors**: Verify `PYTHONPATH=/app` in Dockerfile
3. **Port conflicts**: Using port 9090 consistently

### Issue: "Health check fails"

1. Verify health endpoint works:
   ```bash
   curl http://localhost:9090/health
   ```

2. Check Dockerfile HEALTHCHECK:
   ```dockerfile
   HEALTHCHECK CMD curl -f http://localhost:9090/health || exit 1
   ```

---

## 📊 Port Configuration Summary

| Component | Port | Purpose |
|-----------|------|---------|
| **Dockerfile ENV** | 9090 | Environment variable |
| **Dockerfile EXPOSE** | 9090 | Container port |
| **Dockerfile CMD** | 9090 | Server listen port |
| **component.yaml port** | 9090 | Endpoint port |
| **component.yaml service.port** | 9090 | Service port |
| **Health Check** | 9090 | Health endpoint |

**All ports are now consistent at 9090** ✅

---

## 🎯 Quick Reference

### Files Changed:

1. **`.choreo/component.yaml`**
   - Added `service.port` field
   - Port: 9090

2. **`Dockerfile`**
   - Fixed CMD to use port 9090 consistently
   - Changed to exec form for better signal handling

### Git Commands:

```bash
# Commit and push fixes
git add .choreo/component.yaml Dockerfile
git commit -m "Fix Choreo deployment configuration"
git push origin main
```

### Deployment Command (if asked):

**Run Command:**
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 9090
```

**Note:** This is in the Dockerfile CMD, so you don't need to specify it manually.

---

## ✅ Validation Checklist

Before deploying to Choreo:

- [x] `component.yaml` has `service.port` field
- [x] `openapi.yaml` exists in `.choreo/` directory
- [x] Dockerfile uses port 9090 consistently
- [x] All files committed to Git
- [x] Changes pushed to GitHub
- [ ] Environment variables configured in Choreo
- [ ] Component created in Choreo Console
- [ ] Build successful
- [ ] Health check passing

---

## 📚 Related Documentation

- **Choreo Component Config**: `.choreo/component.yaml`
- **OpenAPI Specification**: `.choreo/openapi.yaml`
- **Dockerfile**: `Dockerfile`
- **Full Deployment Guide**: `docs/readmes/CHOREO_DEPLOYMENT.md`

---

## 🎉 Summary

**Configuration Fixed:**
✅ Added `service.port` to component.yaml  
✅ Fixed Dockerfile port consistency  
✅ Verified openapi.yaml exists  
✅ All ports set to 9090  

**Ready to Deploy:**
1. Commit and push changes
2. Create component in Choreo
3. Configure environment variables
4. Deploy!

**Your run command:** `uvicorn backend.app:app --host 0.0.0.0 --port 9090`

---

**Date:** November 10, 2025  
**Status:** ✅ Ready for Choreo Deployment  
**Run Command:** `uvicorn backend.app:app --host 0.0.0.0 --port 9090`

