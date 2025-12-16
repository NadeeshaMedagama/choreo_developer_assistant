# Choreo Deployment - Quick Start Summary

## ✅ What I've Done for You

I've prepared your project for Choreo deployment with:

1. **Updated Configuration** (`diagram_processor/utils/__init__.py`)
   - ✅ Now works with Choreo's environment variables
   - ✅ Supports Google credentials as JSON string (Choreo secrets)
   - ✅ Falls back gracefully when `.env` file doesn't exist

2. **Created Choreo Configuration** (`.choreo/component.yaml`)
   - ✅ Defines service type, endpoints, and resources
   - ✅ Lists all required environment variables
   - ✅ Configures health checks and scaling

3. **Created Dockerfile** (`Dockerfile` at root)
   - ✅ Deploys entire project structure
   - ✅ Installs all dependencies
   - ✅ Exposes port 9090 (Choreo standard)
   - ✅ Includes health check

4. **Created Documentation**
   - ✅ `CHOREO_DEPLOYMENT.md` - Complete deployment guide
   - ✅ `GOOGLE_CREDENTIALS_SETUP.md` - How to add Google credentials
   - ✅ `prepare_google_creds.sh` - Script to prepare credentials

## 🚀 Deploy to Choreo in 5 Steps

### Step 1: Prepare Google Credentials
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
./prepare_google_creds.sh
```
This will convert your Google credentials to Choreo-compatible format.

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Prepare for Choreo deployment"
git push origin main
```

### Step 3: Create Component in Choreo

1. Login to Choreo Console
2. Create New Component → Service
3. Connect your GitHub repository
4. Set these values:
   - **Component Directory**: `.` (dot)
   - **Dockerfile Path**: `Dockerfile`
   - **Port**: `9090`

### Step 4: Add Environment Variables

In Choreo Console → DevOps → Configs & Secrets, add:

**Required:**
```
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
PINECONE_API_KEY=<your-key>
PINECONE_INDEX_NAME=choreo-ai-assistant-v2
GITHUB_TOKEN=<your-token>
```

**Optional (for diagram OCR):**
```
GOOGLE_CREDENTIALS_JSON=<single-line-json-from-step-1>
```

### Step 5: Deploy
Click **Deploy** button and wait for build to complete!

## 📝 Important Settings

### Choreo Component Configuration

| Setting | Value |
|---------|-------|
| Component Directory | `.` |
| Dockerfile Path | `Dockerfile` |
| Port | `9090` |
| Build Type | Dockerfile |

### Environment Variables Priority

The app checks for credentials in this order:
1. **Choreo Secrets** (recommended) - `GOOGLE_CREDENTIALS_JSON` as JSON string
2. **Environment File Path** - `GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/file.json`
3. **Local File** - Files in `credentials/` directory (local dev only)

## 🧪 Test Your Deployment

### Health Check
```bash
curl https://your-app.choreo.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "pinecone": "connected"
}
```

### Ask a Question
```bash
curl -X POST https://your-app.choreo.dev/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CHOREO_DEPLOYMENT.md` | Complete deployment guide with troubleshooting |
| `GOOGLE_CREDENTIALS_SETUP.md` | How to add Google Vision credentials |
| `prepare_google_creds.sh` | Script to convert credentials for Choreo |
| `.choreo/component.yaml` | Choreo component configuration |
| `Dockerfile` | Container image for deployment |

## 🔧 Troubleshooting

### Build Fails
- ✅ Check that **Component Directory** is set to `.` (not `backend`)
- ✅ Verify **Dockerfile Path** is `Dockerfile` (not `docker/Dockerfile`)

### Runtime Errors
- ✅ Verify all environment variables are set in Choreo
- ✅ Check that API keys are valid and not expired
- ✅ Look at logs in Choreo Console → Observability → Logs

### Import Errors
- ✅ Ensure `PYTHONPATH=/app` is set
- ✅ Verify entire project structure is deployed (not just `backend/`)

## 🎯 Key Differences from Local Development

| Aspect | Local | Choreo |
|--------|-------|--------|
| Environment | `.env` file | Choreo Configs/Secrets |
| Port | 8000 | 9090 |
| Google Creds | File path | JSON string |
| PYTHONPATH | Auto-detected | Must set to `/app` |
| Deployment | Manual run | Auto-deploy on push |

## 📞 Need Help?

1. Read `CHOREO_DEPLOYMENT.md` for detailed guide
2. Check Choreo logs for error messages
3. Verify environment variables are set correctly
4. Test locally with Docker first: `docker build -t test . && docker run -p 9090:9090 test`

## ✅ Checklist Before Deploying

- [ ] Google credentials converted to single-line JSON
- [ ] All code pushed to GitHub
- [ ] Component created in Choreo
- [ ] Component Directory set to `.`
- [ ] All environment variables added
- [ ] Secrets configured (recommended)
- [ ] Health endpoint tested

---

**You're all set!** 🎉 Follow the 5 steps above to deploy to Choreo.

