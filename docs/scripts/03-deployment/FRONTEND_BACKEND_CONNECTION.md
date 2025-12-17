# Frontend-Backend Connection Guide

## Overview

The DevChoreo project consists of:
- **Backend**: FastAPI (Python) running on port 8000
- **Frontend**: React + Vite running on port 5173

## Connection Architecture

### Development Mode

```
User Browser → http://localhost:5173 (Vite Dev Server)
                      ↓ (proxies /api/*)
                http://localhost:8000 (FastAPI Backend)
```

**How it works:**
1. Frontend makes requests to `/api/health`, `/api/ask`, etc.
2. Vite's proxy intercepts `/api/*` requests
3. Forwards them to `http://localhost:8000/api/*`
4. Backend responds with JSON data
5. Frontend receives and displays the data

### Production Mode

In production, you would typically:
1. Build frontend: `npm run build` (creates `dist` folder)
2. Serve static files from backend or use nginx
3. Configure backend URL via environment variable

## API Endpoints

### Backend Endpoints (with /api prefix)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check & Pinecone status |
| POST | `/api/ask?question=...` | Ask a question (RAG) |
| POST | `/api/ask_graph?question=...` | Ask using LangGraph |
| POST | `/api/ingest/github` | Ingest GitHub repo |
| POST | `/api/webhook/github` | GitHub webhook handler |

**Note**: Legacy endpoints without `/api` prefix are also available for backward compatibility.

## CORS Configuration

The backend has CORS middleware configured to allow:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)

This allows the frontend to make cross-origin requests during development.

## Starting the Application

### Option 1: Easy Start (Recommended)
```bash
./start-dev.sh
```
This script starts both backend and frontend automatically.

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd choreo-ai-assistant
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd choreo-ai-assistant/frontend
npm install  # First time only
npm run dev
```

### Option 3: Docker (Backend Only)

```bash
cd choreo-ai-assistant/docker
docker compose up --build
```

**Note**: This runs only the backend. You'll need to run the frontend separately or access the API directly.

## Environment Variables

### Backend (.env location)

The `.env` file should be in: `backend/.env`

Required variables:
```bash
# Azure OpenAI
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_embeddings_deployment

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=choreo-docs

# GitHub (optional - for higher API rate limits)
GITHUB_TOKEN=your_github_token
```

## Troubleshooting

### Frontend shows "Backend offline"

**Check:**
1. Is backend running? Visit: http://localhost:8000/api/health
2. Check CORS errors in browser console
3. Verify `.env` file exists in `backend/` directory
4. Check if all required API keys are set

**Fix:**
```bash
# Check backend status
curl http://localhost:8000/api/health

# Restart backend with logs
cd choreo-ai-assistant
python -m uvicorn backend.app:app --reload
```

### CORS errors in browser console

**Error**: `Access to fetch at 'http://localhost:8000/api/health' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Fix**: The backend now includes CORS middleware. Make sure you're using the updated `backend/app.py`.

### "Connection refused" errors

**Cause**: Backend is not running or running on wrong port

**Fix**:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Start backend on correct port
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Docker warnings about environment variables

**Warning**: `The "PINECONE_API_KEY" variable is not set`

**Fix**: Export variables before running docker compose:
```bash
# Option 1: Export in current shell
export PINECONE_API_KEY="your_key"
export GITHUB_TOKEN="your_token"
# ... (all other variables)

# Option 2: Use .env file (Docker will read from backend/.env)
cd docker
docker compose up
```

## Testing the Connection

### 1. Test Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "pinecone": "connected"
}
```

### 2. Test Frontend-Backend Communication

1. Open browser: http://localhost:5173
2. Check browser console (F12)
3. Look for "Backend online" indicator in UI
4. Try asking a question

### 3. Test RAG Query
```bash
curl -X POST "http://localhost:8000/api/ask?question=What%20is%20Choreo"
```

## Production Deployment

For production, consider:

1. **Build frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve frontend static files** from:
   - Nginx
   - Backend (FastAPI can serve static files)
   - CDN (e.g., Vercel, Netlify)

3. **Update API URL** in frontend to point to production backend

4. **Use environment-based configuration**:
   ```javascript
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```

5. **Remove development CORS origins** from backend

## Summary

✅ **Fixed Issues:**
- Added `/api` prefix to all backend endpoints
- Added CORS middleware for cross-origin requests
- Created startup script for easy development
- Fixed Docker configuration
- Improved Vite proxy configuration

✅ **Connection is now properly configured!**

The frontend and backend can communicate successfully in development mode.

