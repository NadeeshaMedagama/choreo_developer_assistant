# DevChoreo Frontend (React + Vite + Tailwind)

Minimal ChatGPT-like UI with multiple conversations and localStorage persistence.

## Features
- New Chat button and sidebar listing previous chats
- Click to switch conversations, double-click or click ✎ to rename, and 🗑 to delete
- Titles auto-generate from the first user message (first 48 characters)
- Conversations persist in localStorage across reloads
- Health indicator checks the backend at `/api/health`

## Prerequisites
- Node.js 18+ and npm
- Backend running on http://localhost:8000

## Install & Run
```bash
cd frontend
npm install
npm run dev
```

Vite dev server runs on http://localhost:5173 and proxies `/api` to `http://localhost:8000`.

## Build
```bash
npm run build
npm run preview
```

## Notes
- The frontend sends POST `/api/ask?question=...` as expected by the backend.
- Update the proxy in `vite.config.js` if your backend URL changes.
- Data is stored under `devchoreo_conversations_v1` and `devchoreo_current_id_v1` in localStorage.
