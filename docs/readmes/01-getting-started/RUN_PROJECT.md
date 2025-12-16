# 🚀 How to Run the DevChoreo Project Successfully

## Complete Step-by-Step Guide

---

## Prerequisites Check ✅

Before running, ensure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ and npm installed
- ✅ `.env` file configured in `backend/.env` (already done ✓)

---

## Method 1: Quick Start (Recommended) 🎯

### Step 1: Install Dependencies

```bash
# Navigate to project root
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Install Python dependencies
pip install -r choreo-ai-assistant/requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Run the Application

**Option A: Use the startup script (easiest)**
```bash
./start-dev.sh
```

**Option B: Manual startup (if script doesn't work)**

Open TWO terminal windows:

**Terminal 1 - Backend:**
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/frontend"
npm run dev
```

### Step 3: Verify Everything Works

1. **Backend Health Check:**
   - Open: http://localhost:8000/api/health
   - Should see: `{"status":"healthy","pinecone":"connected"}`

2. **Frontend:**
   - Open: http://localhost:5173
   - Should see DevChoreo chat interface
   - Status indicator should show "Backend online" (green dot)

---

## Method 2: Docker (Alternative) 🐳

### Option A: Backend Only in Docker

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Build and run backend
cd docker
docker compose up --build

# In another terminal, run frontend locally
cd ../frontend
npm install
npm run dev
```

**Access:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Option B: Export env vars before Docker (to avoid warnings)

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"

# Export environment variables
export $(cat backend/.env | xargs)

# Run docker
cd docker
docker compose up --build
```

---

## Step 4: Ingest GitHub Documentation 📚

Before you can ask questions, you need to ingest the documentation into Pinecone:

### Method 1: Using the API endpoint

```bash
curl -X POST "http://localhost:8000/api/ingest/github?repo_url=https://github.com/NadeeshaMedagama/docs-choreo-dev&branch=main"
```

### Method 2: Using the ingestion script

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python backend/run_ingestion.py
```

**What this does:**
1. ✅ Fetches all `.md` files from the GitHub repo using GitHub API
2. ✅ Chunks the content into smaller pieces
3. ✅ Creates embeddings using Azure OpenAI
4. ✅ Stores everything in Pinecone vector database

**This may take several minutes depending on the repo size.**

---

## Step 5: Test the Application 🧪

### Test 1: Ask a Question via UI
1. Go to http://localhost:5173
2. Type a question: "What is Choreo?"
3. Should get an AI-generated answer based on the docs

### Test 2: Ask via API
```bash
curl -X POST "http://localhost:8000/api/ask?question=What%20is%20Choreo"
```

### Test 3: Check Pinecone Connection
```bash
curl http://localhost:8000/api/health
```

---

## Troubleshooting 🔧

### Problem: "Backend offline" in UI

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# If not, start backend:
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Problem: Python module errors

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r choreo-ai-assistant/requirements.txt

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install -r choreo-ai-assistant/requirements.txt
```

### Problem: Port already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>

# Or use different port
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8001
```

### Problem: Frontend build/npm errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Problem: Pinecone connection failed

**Check:**
1. ✅ PINECONE_API_KEY is correct in backend/.env
2. ✅ PINECONE_INDEX_NAME exists (or will be auto-created)
3. ✅ Internet connection is working

### Problem: Azure OpenAI errors

**Check:**
1. ✅ AZURE_OPENAI_KEY is valid
2. ✅ AZURE_OPENAI_ENDPOINT is correct
3. ✅ Deployment names match your Azure setup:
   - AZURE_OPENAI_CHAT_DEPLOYMENT
   - AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT

---

## Project Structure 📁

```
choreo-ai-assistant/
├── backend/                    # FastAPI backend
│   ├── .env                   # ✅ Your API keys (configured)
│   ├── app.py                 # Main API server
│   ├── run_ingestion.py       # Ingestion script
│   ├── services/              # Business logic
│   │   ├── ingestion.py       # GitHub ingestion
│   │   ├── llm_service.py     # Azure OpenAI
│   │   ├── rag_graph.py       # LangGraph RAG
│   │   └── context_manager.py # Vector search
│   └── db/
│       └── vector_client.py   # Pinecone client
├── frontend/                   # React UI
│   ├── src/
│   │   ├── App.jsx            # Main app
│   │   └── components/        # UI components
│   └── package.json
├── docker/                     # Docker configs
│   ├── Dockerfile
│   └── docker-compose.yml
└── start-dev.sh               # ✅ Quick start script
```

---

## Environment Variables Reference 📋

Your `backend/.env` is already configured with:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=***
AZURE_OPENAI_ENDPOINT=https://ai-copilot-test-cogsvc.openai.azure.com/
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=choreo-ai-embedding
AZURE_OPENAI_CHAT_DEPLOYMENT=architect-agent-development
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Pinecone
PINECONE_API_KEY=***
PINECONE_INDEX_NAME=choreo-ai-assistant
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# GitHub
GITHUB_TOKEN=***
```

---

## Quick Command Reference 📝

```bash
# Start everything (recommended)
./start-dev.sh

# Backend only
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Frontend only
cd frontend && npm run dev

# Ingest docs
curl -X POST "http://localhost:8000/api/ingest/github?repo_url=https://github.com/NadeeshaMedagama/docs-choreo-dev"

# Health check
curl http://localhost:8000/api/health

# Ask question
curl -X POST "http://localhost:8000/api/ask?question=What%20is%20Choreo"

# Docker
cd docker && docker compose up --build
```

---

## Success Checklist ✅

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] Health check returns "healthy" status
- [ ] UI shows "Backend online" (green dot)
- [ ] Documentation ingested successfully
- [ ] Can ask questions and get answers
- [ ] Responses are relevant to the ingested docs

---

## Next Steps 🎯

1. ✅ Run the project using Method 1 (Quick Start)
2. ✅ Ingest the GitHub documentation
3. ✅ Test by asking questions
4. 🔄 Set up GitHub webhook (optional) for auto-updates
5. 🚀 Deploy to production (when ready)

---

## Support & Resources 📚

- **Frontend-Backend Connection:** See `FRONTEND_BACKEND_CONNECTION.md`
- **Architecture:** See `docs/architecture.md`
- **Main README:** See `README.md`
- **Setup Guide:** See `SETUP_GUIDE.md`

---

**You're all set! 🎉**

Run `./start-dev.sh` and you should have a fully working DevChoreo AI Assistant!

