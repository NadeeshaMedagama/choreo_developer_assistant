# DevChoreo (Choreo AI Assistant)

Minimal RAG assistant that ingests a GitHub repo into Milvus and answers with Azure OpenAI. Frontend is a ChatGPT-like UI built with React + Vite + Tailwind.

## 🚀 Quick Start (Local Development)

```bash
# 1. Clone and setup
cd choreo-ai-assistant

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Install dependencies
cd frontend && npm install && cd ..

# 4. Start the application
./docs/scripts/start_local.sh
```

That's it! Open http://localhost:5173 to use the application.

**Troubleshooting?** See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) or [CONNECTIVITY_FIX.md](./CONNECTIVITY_FIX.md)

---

> 📚 **All documentation is now centralized in [`docs/readmes/`](./docs/readmes/INDEX.md)**  
> See [Documentation Index](./docs/readmes/INDEX.md) for complete guides on setup, features, and deployment.

> 🚀 **NEW: Choreo Platform Support**  
> Now fully optimized for Choreo deployment! See [CHOREO_DEPLOYMENT.md](./CHOREO_DEPLOYMENT.md) for deployment guide.

## Stack
- Backend: FastAPI, Azure OpenAI, Milvus, LangChain, LangGraph
- Frontend: React, Vite, Tailwind CSS, Mermaid.js (diagrams)
- Monitoring: Prometheus, Grafana, Alertmanager, Structured Logging
- Deployment: Docker, Choreo Platform
- Advanced Features: Conversation Memory with Smart Summarization, Progressive Streaming Responses, Context-Aware Retrieval, Automatic Diagram Generation

## ✨ Key Features

### 🧠 Intelligent Conversation Memory
- **Automatic Summarization**: LLM-powered summaries when conversations exceed token limits
- **Smart Context Management**: Keeps recent messages (last 6) fully detailed while summarizing older ones
- **Metadata Extraction**: Tracks topics, key questions, and important decisions
- **Token Tracking**: Real-time monitoring of conversation size
- **Graceful Fallback**: Simple summaries if LLM is unavailable during peak times

### ⚡ Progressive Streaming Responses
- **Real-time Streaming**: Answers appear word-by-word like ChatGPT/Gemini
- **Visual Feedback**: Blinking cursor indicator during streaming
- **Automatic Fallback**: Switches to standard API if streaming fails
- **Better UX**: First token in 1-2 seconds vs 3-5 for full response

### 🔍 Context-Aware Retrieval
- **Enhanced Query Enrichment**: Uses conversation history to improve database searches
- **Better Results**: Retrieves more relevant chunks from Milvus
- **Summary Integration**: Includes conversation summary in retrieval context
- **Quality Filtering**: Score-based filtering to ensure high-quality results

### 🚫 Intelligent Content Filtering
- **OpenChoreo Exclusion**: Automatically filters out non-Choreo platform content
- **Multi-stage Filtering**: Applied to retrieval, context, and source display
- **Clean Answers**: Ensures responses are based only on WSO2 Choreo platform

### 🔗 URL Validation
- **Automatic Validation**: Validates all URLs in answers and sources before displaying
- **404 Prevention**: Removes broken or inaccessible URLs from responses
- **Concurrent Checks**: Validates multiple URLs in parallel for performance
- **Smart Caching**: Caches validation results to avoid redundant checks
- **Configurable**: Enable/disable validation and adjust timeout settings

### 🎨 Mermaid Diagram Generation
- **Automatic Diagram Detection**: AI detects when users ask about architecture, flows, or processes
- **Multiple Diagram Types**: Flowcharts, sequence diagrams, architecture graphs, state diagrams
- **Context-Aware**: Generates diagrams based on actual knowledge base content
- **Interactive Rendering**: Beautiful, theme-aware diagrams with dark/light mode support
- **Real-time Display**: Diagrams render instantly after streaming completes
- **Error Handling**: Clear error messages with diagram code preview if rendering fails

### 📊 Production Monitoring
- **23+ Metrics**: Infrastructure, application, AI, vector DB, and ingestion metrics
- **Pre-built Dashboard**: Grafana dashboard with 8 key panels
- **Smart Alerts**: 7 alert rules for proactive issue detection
- **Structured Logging**: JSON logs with automatic rotation
- **One-click Access**: Monitoring button integrated into UI

### 🔄 Incremental Ingestion
- **Smart Chunking**: Avoids re-processing already ingested files
- **Change Detection**: Only processes new or modified content
- **Performance**: Significantly faster re-ingestion of large repositories
- **Metadata Tracking**: Stores ingestion status and timestamps

### 🎨 Modern UI/UX
- **ChatGPT-like Interface**: Familiar chat experience
- **Multiple Chats**: Create, switch, rename, and delete conversations
- **Persistent History**: Conversations saved in localStorage
- **Source Citations**: View document sources with relevance scores
- **Edit & Copy**: Edit questions and copy responses easily

## Quick Start

1. Open http://localhost:5173
2. Type a question: "What is Choreo?"
3. Get AI-powered answers with context!
4. Enjoy progressive streaming responses (like ChatGPT)
5. Experience intelligent conversation memory across long chats

**Key Features:**
- 🎯 **Smart Conversation Memory**: Automatic summarization when conversations get long
- ⚡ **Progressive Streaming**: Answers appear word-by-word in real-time
- 🔍 **Context-Aware Retrieval**: Uses conversation history to improve search results
- 🚫 **Content Filtering**: Automatically excludes OpenChoreo content
- 🎨 **Mermaid Diagrams**: Automatically generates visual diagrams for architecture and flows
- 📊 **Memory Stats**: See token usage and summarization status

**Using the API:**
```bash
# Standard RAG query with conversation history
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy a service?",
    "conversation_history": [
      {"role": "user", "content": "What is Choreo?"},
      {"role": "assistant", "content": "Choreo is..."}
    ],
    "enable_summarization": true
  }'

# Streaming responses (progressive like ChatGPT)
curl -X POST "http://localhost:8000/api/ask/stream?question=What%20is%20Choreo%3F"

# Ask for diagrams (automatically generates Mermaid diagrams)
curl -X POST "http://localhost:8000/api/ask/stream" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me the Choreo deployment architecture"}'

# LangGraph-based query (advanced)
curl -X POST "http://localhost:8000/api/ask_graph?question=What%20is%20Choreo%3F"
```

**Example Diagram Queries:**
- "Show me the Choreo deployment architecture"
- "Explain how the CI/CD pipeline works"
- "What's the authentication flow in Choreo?"
- "Diagram the observability system components"

## 🚀 Deployment for Multiple Users

### ⚡ Quick Deploy (Easiest Method)

```bash
# One-command deployment
./quick-deploy.sh
```

**Access Points:**
- Frontend UI: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 📖 Full Deployment Guide

**Want to deploy for your team?** See **[EASY_DEPLOYMENT_GUIDE.md](./EASY_DEPLOYMENT_GUIDE.md)** for:

1. **Docker Compose** (5 min) - Easiest, full control
2. **Cloud Platforms** (15 min) - Railway, Render, Fly.io
3. **Choreo Platform** (20 min) - Enterprise deployment

The guide includes:
- ✅ Step-by-step instructions
- 🔒 Security checklist
- 📊 Comparison table
- 🆘 Troubleshooting tips
- 💡 Scaling recommendations

### 🐳 Docker Deployment

```bash
cd docker

# Create .env file with your credentials
cp ../backend/.env.example ../backend/.env
# Edit backend/.env with your API keys

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

**See [Docker Guide](./docs/readmes/03-deployment/DOCKER_README.md) for details.**

## 🚢 Choreo Platform Deployment

**✅ Fully optimized for Choreo with no gateway timeouts!**

### Quick Deploy to Choreo

```bash
# 1. Test locally first
./test-choreo-deployment.sh

# 2. Review deployment configuration
cat .choreo/component.yaml
cat .choreo/openapi.yaml

# 3. Commit and push to GitHub
git add .
git commit -m "Deploy to Choreo"
git push origin main

# 4. Deploy in Choreo Console
# - Create Service component
# - Connect to GitHub
# - Configure environment variables
# - Deploy!
```

### Documentation

- 📖 **[Complete Deployment Guide](./CHOREO_DEPLOYMENT.md)** - Step-by-step instructions
- 📋 **[Deployment Checklist](docs/readmes/12-choreo-deployment/CHOREO_CHECKLIST.md)** - Ensure nothing is missed
- 🔧 **[Technical Fix Details](docs/readmes/12-choreo-deployment/CHOREO_DEPLOYMENT_FIX.md)** - How we solved 504 errors
- 📝 **[Environment Variables](./.env.choreo.example)** - Configuration reference

### Key Features for Choreo

- ⚡ **Fast Startup**: < 5 seconds (no gateway timeouts)
- 🔄 **Lazy Initialization**: Services initialize on first request
- 💚 **Quick Health Checks**: Immediate response for platform probes
- 📊 **Production Ready**: Prometheus metrics, structured logging
- 🔒 **Secure**: Environment-based secrets management
# - Create new component
# - Connect GitHub repository
# - Component Directory: . (root)
# - Add environment variables from Choreo Secrets
- **[Test Files](./backend/tests/README.md)** - Testing documentation
- **[Scripts Documentation](./backend/scripts/README.md)** - Development scripts
**Complete guides:**
- [Choreo Deployment Guide](./docs/readmes/CHOREO_DEPLOYMENT.md)
- [Choreo Quick Start](./CHOREO_QUICK_START.md)
- [OpenAPI Specification](./.choreo/README.md)

#### Security & Compliance
- **[Security Audit Report](docs/implementation/SECURITY_AUDIT_REPORT.md)** - Security verification

---

## 🧠 Conversation Memory System

DevChoreo includes an intelligent **Conversation Memory Management System** that maintains context across long conversations while staying within token limits.

### How It Works

1. **Normal Conversations** (Below token limit)
   - All conversation history sent to LLM
   - Full context preserved

2. **Long Conversations** (Exceeding limits)
   - Older messages automatically summarized by LLM
   - Recent messages (last 6) kept fully detailed
   - Summary + recent messages sent to LLM
   - Enhanced context for better answers

### Key Features

- ✅ **Automatic Summarization**: LLM creates intelligent summaries when needed
- ✅ **Token Management**: Tracks conversation size in real-time
- ✅ **Metadata Extraction**: Captures topics, key questions, and decisions
- ✅ **Context-Aware Retrieval**: Uses history to improve database searches
- ✅ **Configurable**: Control limits and enable/disable per request
- ✅ **Graceful Fallback**: Simple summaries if LLM unavailable

### Configuration

**Environment Variables:**
```bash
# Enable/disable LLM summarization (useful during peak times)
ENABLE_LLM_SUMMARIZATION=true

# Maximum summarization retries before fallback
MAX_SUMMARIZATION_RETRIES=2
```

**Per-Request Control:**
```json
{
  "question": "How do I deploy?",
  "conversation_history": [...],
  "enable_summarization": true,
  "max_history_tokens": 4000
}
```

**Response Includes:**
```json
{
  "answer": "...",
  "memory_stats": {
    "total_tokens": 3200,
    "summarized_count": 2,
    "summary_created": true
  },
  "summary": {
    "content": "User learned about...",
    "topics_covered": ["deployment", "APIs"],
    "key_questions": ["How to deploy?"],
    "important_decisions": ["Use GitHub integration"]
  }
}
```

### Documentation

- **[Implementation Guide](./docs/readmes/CONVERSATION_MEMORY_IMPLEMENTATION.md)**
- **[Quick Start](./docs/readmes/QUICK_START_CONVERSATION_MEMORY.md)**
- **[Visual Guide](./docs/readmes/VISUAL_GUIDE.md)**
- **[Service Documentation](./backend/services/CONVERSATION_MEMORY_README.md)**
- **[Troubleshooting 429 Errors](./docs/readmes/TROUBLESHOOTING_429_ERRORS.md)**

---

## ⚡ Progressive Streaming Responses

DevChoreo delivers answers progressively, like ChatGPT and Gemini, for better user experience.

### Features

- ✅ **Real-time Streaming**: Answers appear word-by-word as generated
- ✅ **Streaming Cursor**: Blinking indicator shows active streaming
- ✅ **Graceful Fallback**: Auto-switches to regular API if streaming fails
- ✅ **Works Everywhere**: New messages, regenerate, and conversation history

### How to Use

**Frontend (Automatic):**
- Just ask a question - streaming is enabled by default
- Watch the answer appear progressively with blinking cursor

**API (Manual):**
```bash
# Streaming endpoint
curl -N -X POST "http://localhost:8000/api/ask/stream?question=What%20is%20Choreo%3F"

# Returns Server-Sent Events (SSE)
data: {"content": "Choreo "}
data: {"content": "is "}
data: {"content": "a "}
...
data: [DONE]
```

### Performance

- **First Token**: 1-2 seconds (vs 3-5 for full response)
- **Perceived Speed**: Much faster user experience
- **Total Time**: Similar to non-streaming
- **Network**: More efficient with progressive data

### Documentation

- **[Streaming Implementation](./docs/readmes/STREAMING_IMPLEMENTATION.md)**
- **[Streaming Responses Guide](./docs/readmes/STREAMING_RESPONSES.md)**
- **[URL Validation](./docs/readmes/URL_VALIDATION.md)**

---

## 🚫 Content Filtering

DevChoreo automatically filters out non-Choreo content to ensure accurate answers.

### What's Filtered

- ❌ **OpenChoreo repositories** - Excluded from context and sources
- ✅ **WSO2 Choreo only** - Answers based exclusively on Choreo platform

### Where Filtering Applies

1. **Vector DB Retrieval**: OpenChoreo content excluded from search results
2. **LLM Context**: Filtered content never sent to AI
3. **Source Display**: Only Choreo sources shown to users
4. **System Prompts**: Clear instructions to avoid non-Choreo info

### Configuration

Filtering is automatic and enabled by default. The system:
- Checks repository metadata for "openchoreo" references
- Excludes matching content at multiple pipeline stages
- Ensures clean, relevant answers

**See:** [Content Filtering Guide](./docs/readmes/FIX_OPENCHOREO_FILTERING.md)

---

## 🔄 How It All Works Together

DevChoreo uses a sophisticated pipeline that combines conversation memory, context-aware retrieval, and intelligent filtering to deliver accurate answers.

### Complete Query Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. User asks: "How do I monitor my deployment?"                     │
│    + Conversation history (previous 10 messages)                     │
│    + Existing summary (if conversation is long)                      │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. CONVERSATION MEMORY MANAGER                                       │
│    ├─ Estimate tokens in history: 3,500 tokens                      │
│    ├─ Check if > 75% of limit (4,000): YES                          │
│    ├─ Split: Older messages (4) + Recent messages (6)               │
│    ├─ Summarize older messages with LLM                             │
│    │  "User learned about Choreo basics, created a project,         │
│    │   deployed a service, and discussed authentication."           │
│    └─ Output: Summary + Recent Messages                             │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. QUERY ENRICHMENT                                                  │
│    Build enriched query for better retrieval:                        │
│    ├─ Summary: "User learned about Choreo basics..."                │
│    ├─ Recent context: [last 4 messages]                             │
│    └─ Current question: "How do I monitor my deployment?"           │
│    Result: "Summary: User learned... Recent: [context]              │
│            Current question: How do I monitor my deployment?"        │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. VECTOR DB RETRIEVAL (Milvus Cloud)                               │
│    ├─ Convert enriched query to embeddings (Azure OpenAI)           │
│    ├─ Search Milvus for similar chunks (top 10)                     │
│    ├─ Filter out OpenChoreo content                                 │
│    ├─ Apply quality filtering (score > 0.7)                         │
│    └─ Return: 5-10 high-quality context chunks                      │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. BUILD LLM CONTEXT                                                 │
│    Combine all context for the LLM:                                  │
│    ├─ System Prompt: "You are DevChoreo, assistant for Choreo..."   │
│    ├─ Conversation Summary (if exists): "User learned about..."     │
│    ├─ Knowledge Base Context: [5-10 relevant chunks from Milvus]    │
│    ├─ Recent Messages: [last 6 messages fully detailed]             │
│    └─ Current Question: "How do I monitor my deployment?"           │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. LLM PROCESSING (Azure OpenAI)                                    │
│    ├─ Stream response word-by-word (if using /api/ask/stream)       │
│    ├─ OR return complete answer (if using /api/ask)                 │
│    └─ Generate answer based on full context                         │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. RESPONSE TO USER                                                  │
│    ├─ Answer: "To monitor your deployment in Choreo..."             │
│    ├─ Sources: [Filtered Choreo docs with scores]                   │
│    ├─ Memory Stats: {total_tokens: 3200, summarized: 4}            │
│    └─ Updated Summary: [For next question]                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Benefits of This Architecture

1. **Better Context Understanding**
   - Summary preserves conversation history without token bloat
   - Recent messages ensure precision for follow-ups
   - Enriched queries improve retrieval relevance

2. **Accurate Answers**
   - Multi-stage filtering ensures quality
   - Conversation-aware retrieval finds better chunks
   - LLM has full context (summary + recent + knowledge base)

3. **Token Efficiency**
   - Automatic summarization when limits approached
   - Only recent messages kept in full detail
   - Graceful degradation during peak times

4. **User Experience**
   - Progressive streaming for faster perceived response
   - Memory stats show token usage
   - Transparent source citations

### Example Conversation Flow

**Turn 1:**
- User: "What is Choreo?"
- System: Full answer + saves to history
- Memory: 1 message, 150 tokens

**Turn 2-6:**
- User asks about projects, deployment, APIs, etc.
- System: Uses full history for context
- Memory: 12 messages, 2,800 tokens

**Turn 7 (Trigger summarization):**
- User: "How do I monitor my deployment?"
- System: Detects 3,500 tokens (>75% limit)
- Action: Summarizes messages 1-6, keeps 7-12 recent
- Memory: Summary (200 tokens) + 6 messages (1,500 tokens) = 1,700 tokens
- Result: Accurate answer with 50% token reduction

**Turn 8+:**
- System continues with summary + recent messages
- Can handle much longer conversations efficiently

---

## 📡 API Reference

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check (legacy) |
| `/api/health` | GET | Health check with Milvus status |

### AI Query Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ask` | POST | Ask question (standard RAG) |
| `/api/ask/stream` | POST | Ask question with progressive streaming |
| `/api/ask_graph` | POST | Ask question (LangGraph RAG) |
| `/ask` | POST | Legacy ask endpoint |
| `/ask_graph` | POST | Legacy graph endpoint |

### Data Ingestion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest/github` | POST | Ingest single repository |
| `/api/ingest/github/with-images` | POST | Ingest with image processing |
| `/api/ingest/org` | POST | Bulk ingest organization repos |
| `/ingest/github` | POST | Legacy ingest endpoint |

### Webhooks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/webhook/github` | POST | GitHub push webhook handler |

**Complete API Documentation:**
- Interactive Docs: http://localhost:8000/docs
- OpenAPI Spec: [.choreo/openapi.yaml](./.choreo/openapi.yaml)
- API Guide: [.choreo/README.md](./.choreo/README.md)
### Backend
- **FastAPI** - High-performance async API framework
- **Azure OpenAI** - GPT-4 for chat, text-embedding-ada-002 for embeddings
- **Milvus Cloud** - Serverless vector database for semantic search
- **LangChain** - LLM orchestration framework
- **LangGraph** - Advanced graph-based RAG workflows
- **Python 3.12+** - Modern Python with type hints

### Frontend
- **React 18** - Modern component-based UI
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
## 📁 Project Structure

```
choreo-ai-assistant/
├── .choreo/                    # Choreo deployment configuration
│   ├── component.yaml         # Component specification
│   ├── openapi.yaml           # API documentation
│   └── README.md              # OpenAPI guide
├── backend/                   # FastAPI backend
│   ├── app.py                 # Main application
│   ├── services/              # Business logic
│   │   ├── llm_service.py     # Azure OpenAI service
│   │   ├── context_manager.py # Vector DB context management
│   │   ├── conversation_memory_manager.py  # ⭐ Smart summarization
│   │   ├── github_service.py  # GitHub integration
│   │   ├── image_service.py   # Google Vision API
│   │   ├── ingestion.py       # Data ingestion
│   │   ├── rag_graph.py       # LangGraph workflows
│   │   └── CONVERSATION_MEMORY_README.md  # Memory system docs
│   ├── db/                    # Database clients
│   │   └── vector_client.py   # Milvus client
│   ├── utils/                 # Utilities
│   ├── diagram_processor/     # Diagram/image processing
│   ├── choreo-ai-assistant/   # Additional requirements
│   ├── monitoring/            # Monitoring system ⭐
│   │   ├── metrics.py         # Prometheus metrics
│   │   ├── logging_config.py  # Logging setup
│   │   ├── alerts.py          # Alert rules
│   │   ├── prometheus.yml     # Prometheus config
│   │   ├── grafana_dashboard.json  # Pre-built dashboard
│   │   ├── docker-compose.yml # Monitoring stack
│   │   ├── install.sh         # Installation script
│   │   ├── start.sh           # Start all services
│   │   ├── stop.sh            # Stop all services
│   │   └── docs/              # Monitoring guides
│   ├── tests/                 # Test files
│   └── scripts/               # Development scripts
│       ├── debug/             # Debug tools
│       ├── fetch/             # Data fetching
│       └── ingest/            # Data ingestion
├── frontend/                  # React frontend
│   ├── src/                   # Source code
│   │   ├── App.jsx            # Main app with streaming support
│   │   └── components/        # UI components
│   └── public/                # Static assets
├── data/                      # Data files
├── docs/                      # Documentation
│   └── readmes/               # ⭐ Detailed guides
│       ├── CONVERSATION_MEMORY_IMPLEMENTATION.md
│       ├── STREAMING_IMPLEMENTATION.md
│       ├── TROUBLESHOOTING_429_ERRORS.md
│       ├── FIX_OPENCHOREO_FILTERING.md
│       └── INDEX.md           # Documentation index
├── docker/                    # Docker configuration
├── logs/                      # Application logs (auto-generated)
│   ├── app.log                # All logs
│   ├── error.log              # Errors only
│   ├── ai.log                 # AI operations
│   └── ingestion.log          # Ingestion logs
├── Dockerfile                 # Production container
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🧪 Testing

### Run Backend Tests

```bash
# Test backend initialization
python backend/tests/test_backend.py

# Test GitHub connectivity
python backend/tests/test_github.py

# Test chunking functionality
python backend/tests/test_chunking.py
```

### Run Debug Scripts

```bash
# Debug GitHub access
python backend/scripts/debug/debug_github_access.py

# Check repository visibility
python backend/scripts/debug/debug_github_repos.py
```

**See [Testing Guide](./backend/tests/README.md) for comprehensive testing documentation.**

---

## 🔒 Security Best Practices

### ✅ What's Protected

- ✅ All credentials in `.gitignore` (never committed)
- ✅ Environment variables in `backend/.env` (gitignored)
- ✅ API keys managed through Choreo Secrets in production
- ✅ No hardcoded credentials in source code
- ✅ Security audit completed (see [SECURITY_AUDIT_REPORT.md](docs/implementation/SECURITY_AUDIT_REPORT.md))

### ⚠️ Important Security Notes

1. **Never commit** `backend/.env` or credential files
2. **Use Choreo Secrets** for production deployment
3. **Rotate API keys** regularly
4. **Limit API permissions** to minimum required
5. **Review changes** before pushing to GitHub

**Security Audit:** [SECURITY_AUDIT_REPORT.md](docs/implementation/SECURITY_AUDIT_REPORT.md)

---

## 🔧 Troubleshooting

### Azure OpenAI Errors

**Issue:** `401 Unauthorized` or `Invalid API key`
- ✅ Verify `AZURE_OPENAI_API_KEY` is correct
- ✅ Check `AZURE_OPENAI_ENDPOINT` URL format
- ✅ Ensure deployment names match your Azure resources
- ✅ Confirm API version is supported

### Milvus Connection Issues

**Issue:** `Milvus: disconnected` in health check
- ✅ Verify `MILVUS_URI` is valid and accessible
- ✅ Check `MILVUS_TOKEN` is correct
- ✅ Ensure collection name exists: `MILVUS_COLLECTION_NAME`
- ✅ Verify network connectivity to Milvus Cloud
- ✅ Check dimension settings match your embedding model

### Frontend API Errors

**Issue:** `Network Error` or `Failed to fetch`
- ✅ Confirm backend is running on port 8000
- ✅ Check Vite proxy configuration in `vite.config.js`
- ✅ Verify CORS settings in `backend/app.py`
- ✅ Ensure both frontend and backend are running

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'backend'`
- ✅ Activate virtual environment: `source .venv/bin/activate`
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Run from project root directory
- ✅ Check `PYTHONPATH` if using custom setup

### Google Vision API Issues

**Issue:** `Google Vision API not configured`
- ✅ Add `GOOGLE_CREDENTIALS_JSON` to `backend/.env`
- ✅ See [Google Credentials Setup](./docs/readmes/GOOGLE_CREDENTIALS_SETUP.md)
- ✅ Verify service account has Vision API permissions
- ✅ Check JSON format is valid

**More Help:**
- [Setup Guide](./docs/readmes/SETUP_GUIDE.md)
- [Troubleshooting Guide](./docs/readmes/CRASH_ANALYSIS_AND_FIXES.md)
- [Documentation Index](./docs/readmes/INDEX.md)
- **GitHub Integration** - Webhook-based auto-updates
- **Docker** - Containerized deployment

## 📊 Performance & Monitoring

### 🎯 Comprehensive Monitoring System

DevChoreo includes a **complete production-ready monitoring stack** with Prometheus, Grafana, and structured logging. Get real-time insights into your application's performance, health, and resource usage.

#### Quick Start

```bash
# Install monitoring tools (Prometheus + Grafana)
cd backend/monitoring
./install.sh

# Start all monitoring services
./start.sh

# Run load test to generate metrics
./load_test.sh

# Access monitoring dashboard
# Click the monitoring icon (📊) in the bottom-right corner of DevChoreo UI
# OR visit: http://localhost:3000 (Grafana - admin/admin)
```

#### Features

- ✅ **23+ Metrics Types**: Infrastructure, application, AI-specific, vector DB, and GitHub ingestion metrics
- ✅ **Pre-configured Dashboard**: Beautiful Grafana dashboard with 8 key panels
- ✅ **Smart Alerting**: 7 alert rules for proactive issue detection
- ✅ **Structured Logging**: JSON logs with rotation (app, errors, AI ops, ingestion)
- ✅ **One-Click Access**: Monitoring button integrated into DevChoreo UI
- ✅ **Docker Support**: Full stack deployable via docker-compose
- ✅ **Production Ready**: Environment-aware configuration for local/Choreo deployment

#### Metrics Collected

**Infrastructure (8 metrics)**
- CPU, memory, disk usage
- Process count and system health

**Application (4 metrics)**
- HTTP requests (by method, endpoint, status)
- Request duration and active requests
- Error tracking by type

**AI-Specific (4 metrics)**
- Inference duration and success rate
- Token usage (input/output)
- Payload sizes

**Vector Database (3 metrics)**
- Search duration and operations
- Results count distribution

**GitHub/Ingestion (3 metrics)**
- Ingestion duration and success rate
- Files processed by type

**Health (1 metric)**
- Component health status

#### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Metrics Endpoint** | http://localhost:8000/metrics | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana Dashboard** | http://localhost:3000 | admin/admin |
| **Alertmanager** | http://localhost:9093 | - |

#### Monitoring Documentation

- **[Setup Guide](./backend/monitoring/docs/SETUP_GUIDE.md)** - Detailed installation and configuration
- **[Quick Reference](./backend/monitoring/docs/QUICK_REFERENCE.md)** - Commands and queries cheat sheet
- **[Implementation Summary](./backend/monitoring/docs/IMPLEMENTATION_SUMMARY.md)** - Complete feature overview
- **[Main README](./backend/monitoring/README.md)** - Overview and architecture

#### Pre-configured Alerts

The system includes 7 alert rules:
- 🚨 High response time (>2s)
- 🚨 High error rate (>5%)
- 🚨 High CPU usage (>80%)
- 🚨 Critical memory usage (>95%)
- 🚨 Slow AI inference (>5s)
- 🚨 Service health failures
- 🚨 Request rate anomalies

#### Production Deployment

**Using Docker:**
```bash
cd backend/monitoring
docker-compose up -d
```

**For Choreo/Cloud:**
1. FastAPI automatically exposes `/metrics` endpoint
2. Deploy Prometheus to scrape metrics
3. Import Grafana dashboard (`grafana_dashboard.json`)
4. Configure Alertmanager for notifications (email/Slack)

#### Log Files

Logs are automatically created in `logs/` directory:
- `app.log` - All application logs
- `error.log` - Errors only
- `ai.log` - AI operations
- `ingestion.log` - GitHub ingestion

#### Useful Commands

```bash
# View real-time metrics
curl http://localhost:8000/metrics

# Check Prometheus targets
open http://localhost:9090/targets

# View live logs
tail -f logs/app.log

# Stop all monitoring services
cd backend/monitoring && ./stop.sh
```

### Built-in Monitoring Features

- **Health Checks**: `/api/health` endpoint with component status
- **Request Logging**: Automatic request/response logging with correlation IDs
- **Error Tracking**: Comprehensive error messages with stack traces
- **Performance Metrics**: Response time tracking via Prometheus
- **Distributed Tracing**: Ready for OpenTelemetry integration

### Additional Monitoring Options (Production)

- **Application Monitoring**: Azure Application Insights
- **Log Aggregation**: ELK Stack or Choreo Observability
- **Uptime Monitoring**: Pingdom or UptimeRobot
- **API Analytics**: Choreo API Management

---

## 🤝 Contributing

This is an internal project for WSO2 Choreo. For questions or issues:

1. Check existing documentation in `docs/readmes/`
2. Review [troubleshooting section](#-troubleshooting)
3. Contact the development team

---

## 📜 License

Internal/example use for WSO2. Add your preferred license if publishing publicly.

---

## 🙏 Acknowledgments

- **WSO2 Choreo Team** - Platform and requirements
- **Azure OpenAI** - Language model capabilities
- **Milvus/Zilliz** - Vector database infrastructure
- **LangChain** - RAG framework and tools

---

## ⚙️ Performance & Best Practices

### Conversation Memory Optimization

**Token Limits**
```python
# Recommended settings for different use cases

# Default (balanced)
max_total_tokens=8000
max_history_tokens=4000
summarization_trigger_ratio=0.75

# High-volume production (aggressive summarization)
max_total_tokens=6000
max_history_tokens=3000
summarization_trigger_ratio=0.6

# Development/testing (minimal summarization)
max_total_tokens=12000
max_history_tokens=8000
summarization_trigger_ratio=0.9
```

**Reducing Azure OpenAI Costs**
- Enable summarization to reduce token usage by 40-60%
- Set lower `max_history_tokens` for frequent, short conversations
- Use `enable_summarization: false` for single-turn questions
- Monitor token usage via `memory_stats` in responses

**Handling Peak Times**
```bash
# Temporarily disable LLM summarization during peak hours
export ENABLE_LLM_SUMMARIZATION=false

# Reduce retries to fail faster
export MAX_SUMMARIZATION_RETRIES=1
```

### Retrieval Optimization

**Quality vs Speed Trade-offs**
```python
# Current settings (balanced)
top_k=10  # Retrieve 10 candidates
score_threshold=0.7  # High quality filter

# For faster responses (lower quality)
top_k=5
score_threshold=0.6

# For best quality (slower)
top_k=15
score_threshold=0.75
```

**Query Enrichment**
- Conversation summary is limited to 300 characters for retrieval
- Only last 4 messages included in enriched query
- Balances context vs retrieval speed

### Streaming Performance

**First Token Time**
- Streaming: 1-2 seconds
- Non-streaming: 3-5 seconds
- Network overhead: ~200ms

**When to Use Streaming**
- ✅ User-facing chat interfaces
- ✅ Long responses (>500 tokens)
- ✅ Better perceived performance
- ❌ Batch processing
- ❌ API integrations requiring full response

### Caching Strategies

**Frontend**
```javascript
// Conversations cached in localStorage
// Summary cached with each conversation
// No expiration (manual clear only)
```

**Backend**
```python
# No caching by default
# Consider adding:
# - Redis for conversation summaries
# - LRU cache for frequent queries
# - Milvus metadata cache
```

### Monitoring Performance

**Key Metrics to Watch**
```bash
# Visit http://localhost:8000/metrics

# Response time
http_request_duration_seconds

# Token usage
ai_tokens_total{type="input"}
ai_tokens_total{type="output"}

# Summarization
conversation_summary_created_total
conversation_summary_failed_total

# Vector search
vector_search_duration_seconds
```

**Performance Targets**
| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Response Time | <2s | >3s | >5s |
| First Token | <1.5s | >2s | >3s |
| Vector Search | <500ms | >1s | >2s |
| Summarization | <3s | >5s | >10s |
| Error Rate | <1% | >3% | >5% |

### Scaling Recommendations

**Small Deployments (<100 users)**
- Current configuration works well
- Single backend instance sufficient
- Local monitoring adequate

**Medium Deployments (100-1000 users)**
- Add Redis for conversation caching
- Multiple backend instances (3-5)
- Dedicated Prometheus/Grafana
- Consider Azure OpenAI Provisioned Throughput

**Large Deployments (1000+ users)**
- Kubernetes deployment
- Auto-scaling based on metrics
- Distributed caching (Redis Cluster)
- CDN for frontend assets
- Azure OpenAI Provisioned Throughput required
- Separate monitoring infrastructure

---

## ❓ Frequently Asked Questions

### Conversation Memory

**Q: Where is the conversation history stored?**
- A: In the frontend's localStorage for persistence across sessions. Each chat has its own history array.

**Q: Where is the summary stored?**
- A: The summary is returned in each API response and stored in the frontend alongside the conversation. It's updated automatically when needed.

**Q: When is a summary created?**
- A: Automatically when conversation history exceeds 75% of the token limit (default: 3,000 tokens out of 4,000 max).

**Q: Can I disable summarization?**
- A: Yes, set `ENABLE_LLM_SUMMARIZATION=false` in environment or `enable_summarization: false` in the request.

**Q: What happens if summarization fails (429 error)?**
- A: The system falls back to simple text-based summaries and continues working. See [Troubleshooting 429 Errors](./docs/readmes/TROUBLESHOOTING_429_ERRORS.md).

### Retrieval & Context

**Q: Does the system use conversation history for retrieval?**
- A: Yes! The query is enriched with conversation summary and recent messages before searching Milvus.

**Q: Are chunks from Milvus sent to the LLM?**
- A: Yes, the top 5-10 high-quality chunks are included in the LLM context along with the conversation.

**Q: How does the filtering work?**
- A: OpenChoreo content is filtered at multiple stages: during retrieval, before sending to LLM, and when displaying sources.

### Streaming

**Q: Is streaming enabled by default?**
- A: Yes, the frontend automatically uses the streaming endpoint (`/api/ask/stream`).

**Q: What if streaming fails?**
- A: The frontend automatically falls back to the standard `/api/ask` endpoint.

**Q: Can I use streaming via API?**
- A: Yes, use `POST /api/ask/stream?question=Your+question` with curl's `-N` flag.

### Performance

**Q: Does conversation memory slow down responses?**
- A: No, it actually improves speed by reducing tokens sent to the LLM. Summarization only happens when needed.

**Q: How many conversations can I have?**
- A: Unlimited! Each conversation is stored separately in localStorage.

**Q: What's the maximum conversation length?**
- A: Practically unlimited due to automatic summarization. Very long conversations are compressed efficiently.

### Private Repository Information

**Q: Why does the assistant refuse to share internal/private details?**
- A: This was a previous configuration. The system now shares ALL information from the knowledge base, including private repositories, as it's designed for internal WSO2 Choreo developers.

**Q: Can I see internal API endpoints like Rudder?**
- A: Yes! If this information is in the ingested repositories, DevChoreo will share it. The system is configured to provide complete technical details.

**Q: How do I ensure private repo data is included?**
- A: Make sure private repositories are ingested using the `/api/ingest/github` endpoint with proper GitHub token authentication.

---

## 📞 Support & Resources

- **Documentation**: [docs/readmes/INDEX.md](./docs/readmes/INDEX.md)
- **API Docs**: http://localhost:8000/docs
- **Choreo Platform**: https://console.choreo.dev/
- **Security Audit**: [SECURITY_AUDIT_REPORT.md](docs/implementation/SECURITY_AUDIT_REPORT.md)

---

**Last Updated:** December 2, 2025  
**Version:** 2.0.0  
**Status:** Production Ready ✅

## 📋 Recent Updates (v2.0.0)

### November-December 2025

**🧠 Conversation Memory System**
- ✅ Intelligent LLM-powered summarization
- ✅ Token tracking and management
- ✅ Metadata extraction (topics, questions, decisions)
- ✅ Graceful fallback for peak times
- ✅ Per-request configuration options

**⚡ Progressive Streaming**
- ✅ ChatGPT-like word-by-word responses
- ✅ Streaming cursor indicator
- ✅ Server-Sent Events (SSE) implementation
- ✅ Automatic fallback to standard API

**🔍 Enhanced Retrieval**
- ✅ Context-aware query enrichment
- ✅ Conversation history integration
- ✅ Quality-based filtering
- ✅ OpenChoreo content exclusion

**🛡️ Reliability Improvements**
- ✅ Azure OpenAI 429 error handling
- ✅ Retry logic with exponential backoff
- ✅ Environment-based feature toggles
- ✅ Comprehensive error logging

**📊 Monitoring & Observability**
- ✅ 23+ Prometheus metrics
- ✅ Pre-built Grafana dashboard
- ✅ Smart alerting rules
- ✅ Structured JSON logging

**📚 Documentation**
- ✅ Comprehensive feature guides
- ✅ Visual diagrams and flowcharts
- ✅ Troubleshooting guides
- ✅ Quick start examples

---

## Quick Start

For detailed instructions, see:
- **[Setup Guide](./docs/readmes/SETUP_GUIDE.md)** - Complete setup instructions
- **[Run Project](./docs/readmes/RUN_PROJECT.md)** - How to run the application
- **[Docker Guide](./docs/readmes/DOCKER_README.md)** - Docker deployment
- **[Incremental Ingestion](./docs/readmes/INCREMENTAL_INGESTION.md)** - Smart chunking feature

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Accounts/keys for:
  - Azure OpenAI (chat + embeddings deployments)
  - Milvus (vector database instance)

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

# Milvus
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION_NAME="choreo_docs"
export MILVUS_USER=""
export MILVUS_PASSWORD=""
export MILVUS_DB_NAME="default"
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
Run once to populate Milvus:

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
# (same variables as above for Azure OpenAI + Milvus)
docker compose up --build
```

Backend will be available on http://localhost:8000.

---

## API quick reference
- `GET /health` — Health check (Milvus connectivity)
- `POST /ask?question=...` — Ask a question (RAG using similarity from Milvus)
- `POST /ask_graph?question=...` — Ask via LangGraph pipeline
- `POST /ingest/github` — Body: `{ "repo_url": "...", "branch": "main" }`
- `POST /webhook/github` — Basic push webhook; re-ingests repo from payload

---

## Troubleshooting
- Azure OpenAI errors: verify endpoint URL, API key, and deployment names; set `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` if using a separate embeddings model.
- Milvus connection errors: verify Milvus host, port, and credentials are correct; ensure Milvus is running and accessible.
- Frontend API errors: confirm the backend is running on port 8000 and the Vite proxy is active (run `npm run dev`).

---

## License
Internal/example use. Add your preferred license if publishing.
