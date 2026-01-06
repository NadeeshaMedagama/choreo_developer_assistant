# How to Run the Backend Server

## The Problem You Just Hit

When you run `python -m uvicorn backend.app:app` from the **project root**, Python looks for modules inside the `backend` package. But the code uses absolute imports like `from services.llm_service`, which expects to run from the `backend` directory.

## ✅ Correct Ways to Run

### Option 1: Use the Helper Scripts (EASIEST)

From the **project root** directory:

```bash
# Development mode (with auto-reload)
./dev-start.sh

# Production mode (no auto-reload)
./prod-start.sh
```

### Option 2: Manual Command from Backend Directory

```bash
# Navigate to backend first
cd backend

# Then run uvicorn
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Use the backend/start.py Script

```bash
cd backend
python start.py
```

## ❌ What NOT to Do

```bash
# DON'T run this from project root:
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
# This fails with: ModuleNotFoundError: No module named 'services.llm_service'
```

## Why This Happens

The backend code uses **absolute imports** without the `backend.` prefix:
```python
from services.llm_service import LLMService  # Not: from backend.services...
from db.vector_client import VectorClient     # Not: from backend.db...
from utils.logger import get_logger          # Not: from backend.utils...
```

This matches the Choreo deployment environment where `/workspace` is the root, and `services/`, `utils/`, `db/` are top-level packages.

## Directory Structure

```
choreo-ai-assistant/           ← Project root
├── dev-start.sh              ← Use this for development
├── prod-start.sh             ← Use this for production testing
└── backend/                  ← Run uvicorn from HERE
    ├── app.py
    ├── start.py
    ├── services/
    ├── utils/
    └── db/
```

## Quick Reference

| Command | Directory | Use Case |
|---------|-----------|----------|
| `./dev-start.sh` | Project root | Development with auto-reload |
| `./prod-start.sh` | Project root | Production testing |
| `cd backend && python start.py` | Backend dir | Choreo-like environment |
| `cd backend && python -m uvicorn app:app --reload` | Backend dir | Manual development |

## Ports

- **Development**: Port 8000 (with auto-reload)
- **Production**: Port 9090 (matches Choreo deployment)

## Health Check

After starting the server:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","milvus":"initializing"}
```

---
Last Updated: January 5, 2026

