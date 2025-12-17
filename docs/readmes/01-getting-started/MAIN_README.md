# DevChoreo (Choreo AI Assistant)

Minimal RAG assistant that ingests a GitHub repo into Pinecone and answers with Azure OpenAI. Frontend is a ChatGPT-like UI built with React + Vite + Tailwind.

## Stack
- Backend: FastAPI, Azure OpenAI, Pinecone, LangChain, LangGraph
- Frontend: React, Vite, Tailwind CSS

---

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Accounts/keys for:
  - Azure OpenAI (chat + embeddings deployments)
  - Pinecone (serverless index)

---

## 1) Backend setup

1. Export environment variables (or create a `backend/.env`). Example:

```bash
# Azure OpenAI
export AZURE_OPENAI_KEY="your_azure_openai_key"
export AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="your_chat_deployment_name"
# Optional: separate embeddings deployment (recommended)
export AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="your_embeddings_deployment_name"
# Optional: API version (the code has a default)
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Pinecone (serverless)
export PINECONE_API_KEY="your_pinecone_key"
export PINECONE_CLOUD="aws"
export PINECONE_REGION="us-east-1"
export PINECONE_INDEX_NAME="choreo-assistant-index"
# Optional: explicitly set dimension if index is created automatically
# export PINECONE_DIMENSION="1536"
```

2. Install Python dependencies and run the API:

```bash
cd "choreo-ai-assistant"
python -m pip install --upgrade pip
python -m pip install -r backend/choreo-ai-assistant/requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

3. Health check:

- Visit http://localhost:8000/health
- If keys are not valid or network is restricted, health may show "unhealthy"; the server can still start.

### Ingest the GitHub repo (wso2/docs-choreo-dev)
Run once to populate Pinecone:

```bash
curl -X POST "http://localhost:8000/ingest/github" \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/wso2/docs-choreo-dev.git","branch":"main"}'
```

### GitHub Webhook (optional, to auto-update on push)
- In your GitHub repo: Settings → Webhooks → Add webhook
  - Payload URL: `http://YOUR_HOST:8000/webhook/github`
  - Content type: `application/json`
  - Events: `Just the push event`
  - Secret: optional (current endpoint does not verify signatures)

---

## 2) Frontend setup

1. Install and start the dev server:

```bash
cd "choreo-ai-assistant/frontend"
npm install
npm run dev
```

2. Open http://localhost:5173

- The dev server proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.js`).
- UI features: New chat, list/switch chats, rename, delete, persistent chat history via localStorage.

---

## Docker (optional: backend only)

```bash
cd "choreo-ai-assistant/docker"
# Ensure env vars are exported in your shell before this step
# (same variables as above for Azure OpenAI + Pinecone)
docker compose up --build
```

Backend will be available on http://localhost:8000.

---

## API quick reference
- `GET /health` — Health check (Pinecone connectivity)
- `POST /ask?question=...` — Ask a question (RAG using similarity from Pinecone)
- `POST /ask_graph?question=...` — Ask via LangGraph pipeline
- `POST /ingest/github` — Body: `{ "repo_url": "...", "branch": "main" }`
- `POST /webhook/github` — Basic push webhook; re-ingests repo from payload

---

## Troubleshooting
- Azure OpenAI errors: verify endpoint URL, API key, and deployment names; set `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` if using a separate embeddings model.
- Pinecone index creation: if the index does not exist and `PINECONE_DIMENSION` is not provided, the client infers dimension on first upsert; ensure at least one upsert occurs.
- Frontend API errors: confirm the backend is running on port 8000 and the Vite proxy is active (run `npm run dev`).

---

## License
Internal/example use. Add your preferred license if publishing.

