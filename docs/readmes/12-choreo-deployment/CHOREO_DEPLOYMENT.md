# Choreo Deployment Guide

This guide explains how to deploy the Choreo AI Assistant to the Choreo platform.

## Overview

The Choreo AI Assistant is now **fully optimized for Choreo deployment** with the following improvements:

### ✅ Fixed Gateway Timeout Issues

The previous **504 Gateway Timeout** errors have been resolved through:

1. **Lazy Service Initialization**: Services are initialized on first request, not at startup
2. **Fast Health Checks**: Health endpoints respond immediately without waiting for full initialization
3. **Optimized Startup**: Docker health checks use longer timeouts and startup periods
4. **Async Architecture**: Proper FastAPI lifespan management for cloud deployments

## Prerequisites

Before deploying to Choreo, ensure you have:

1. **Azure OpenAI Resources**
   - Azure OpenAI endpoint URL
   - API key
   - Chat deployment name (e.g., `gpt-4`)
   - Embeddings deployment name (e.g., `text-embedding-ada-002`)

2. **Milvus Vector Database**
   - Milvus Cloud URI or self-hosted endpoint
   - Authentication token
   - Collection name (default: `choreo_developer_assistant`)

3. **GitHub Token** (Optional)
   - Personal Access Token for ingesting private repositories
   - Required scopes: `repo`, `read:org`

4. **Google Vision API** (Optional)
   - API key for image/diagram processing

## Deployment Steps

### 1. Create a New Component in Choreo

1. Log in to [Choreo Console](https://console.choreo.dev/)
2. Create a new project or select an existing one
3. Click **Create** → **Service**
4. Choose **GitHub** as the source
5. Connect your repository
6. Select the repository and branch

### 2. Configure Component Settings

During component creation or in settings:

- **Component Name**: `choreo-ai-assistant`
- **Build Type**: Dockerfile
- **Dockerfile Path**: `Dockerfile`
- **Docker Context**: `.` (root directory)
- **Port**: `9090`

### 3. Configure Environment Variables

In the Choreo Console, configure the following environment variables:

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_KEY` | Azure OpenAI API Key | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI Endpoint URL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | Chat model deployment name | `gpt-4` |
| `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` | Embeddings deployment name | `text-embedding-ada-002` |
| `MILVUS_URI` | Milvus database URI | `https://your-cluster.milvus.io:19530` |
| `MILVUS_TOKEN` | Milvus authentication token | `token:xxxxx` |

#### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-02-15-preview` |
| `MILVUS_COLLECTION_NAME` | Milvus collection name | `choreo_developer_assistant` |
| `MILVUS_DIMENSION` | Vector dimension | `1536` |
| `MILVUS_METRIC` | Distance metric | `COSINE` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | - |
| `GOOGLE_VISION_API_KEY` | Google Vision API key | - |
| `ENABLE_LLM_SUMMARIZATION` | Enable conversation summarization | `true` |
| `ENABLE_URL_VALIDATION` | Enable URL validation | `true` |
| `URL_VALIDATION_TIMEOUT` | URL validation timeout (seconds) | `5` |

### 4. Deploy

1. Click **Deploy** in Choreo Console
2. Wait for the build to complete (~3-5 minutes)
3. Once deployed, the service will be available at the Choreo-provided URL

## Verifying Deployment

### Health Check Endpoints

The application provides multiple health check endpoints:

1. **Basic Health Check** (Fast, no initialization required)
   ```bash
   curl https://your-app.choreo.dev/
   # or
   curl https://your-app.choreo.dev/health
   ```

2. **Detailed Health Check** (Initializes services)
   ```bash
   curl https://your-app.choreo.dev/api/health
   ```

3. **Metrics Endpoint** (Prometheus format)
   ```bash
   curl https://your-app.choreo.dev/metrics
   ```

### Test AI Query

```bash
curl -X POST https://your-app.choreo.dev/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Choreo?",
    "enable_summarization": true
  }'
```

## Architecture Changes for Choreo

### Lazy Initialization

Services are now initialized on first request instead of at startup:

```python
# Services start as None
vector_client = None
llm_service = None
# ... other services

def initialize_services():
    """Initialize all services lazily"""
    # Services are created here on first request
    pass

@app.post("/api/ask")
async def ask_ai(request: AskRequest):
    # Initialize services if not already done
    if not services_initialized:
        initialize_services()
    # ... process request
```

### Fast Health Checks

The `/health` endpoint returns immediately without initializing services:

```python
@app.get("/health")
def health_check_legacy():
    """Returns basic status immediately"""
    return {
        "status": "healthy",
        "message": "Service is running",
        "services_initialized": services_initialized
    }
```

### Docker Health Check Configuration

```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:9090/ || exit 1
```

- **start-period**: 90s to allow for image download and container startup
- **timeout**: 30s for health check response
- **retries**: 5 attempts before marking unhealthy

## Troubleshooting

### 504 Gateway Timeout

**Cause**: Gateway timeout before service is ready

**Solutions**:
1. ✅ **Already Fixed**: Lazy initialization ensures fast startup
2. Verify health check endpoint responds quickly: `curl /health`
3. Check Choreo logs for initialization errors

### Service Not Responding

**Check**:
1. Environment variables are correctly configured
2. Milvus URI is accessible from Choreo
3. Azure OpenAI endpoint is accessible
4. View logs in Choreo Console

### Slow First Request

**Expected Behavior**: The first request after deployment initializes all services and may take 10-30 seconds. Subsequent requests are fast.

**Optimization**: Call `/api/health` after deployment to trigger initialization.

## Monitoring

### Prometheus Metrics

The service exposes Prometheus-compatible metrics at `/metrics`:

- Request counts and durations
- Vector search performance
- AI inference metrics
- Error rates
- Health check status

### Logs

View logs in Choreo Console:
- Application logs: Startup, requests, errors
- Access logs: HTTP requests
- Error logs: Exceptions and failures

## Performance Tuning

### For Production

```yaml
# Recommended environment variables
ENABLE_LLM_SUMMARIZATION: "true"  # Better conversation context
ENABLE_URL_VALIDATION: "true"     # Validate URLs in responses
URL_VALIDATION_TIMEOUT: "5"       # 5 seconds per URL
```

### For High Load

```yaml
# Disable expensive operations if needed
ENABLE_LLM_SUMMARIZATION: "false" # Skip AI summarization
ENABLE_URL_VALIDATION: "false"    # Skip URL validation
```

## API Endpoints

### Query Endpoints

- `POST /api/ask` - Ask a question (with conversation history)
- `POST /api/ask_graph` - Ask a question (using graph-based RAG)

### Ingestion Endpoints

- `POST /api/ingest/github` - Ingest GitHub repository
- `POST /api/ingest/github/with-images` - Ingest with image processing
- `POST /api/ingest/org` - Ingest organization repositories

### Webhook Endpoints

- `POST /api/webhook/github` - GitHub webhook for auto-ingestion

## Security Considerations

1. **API Keys**: Store as secrets in Choreo Config
2. **CORS**: Configured to allow Choreo domains
3. **Network Visibility**: Set to `Public` or restrict as needed
4. **Authentication**: Add API authentication if required

## Support

For issues or questions:
1. Check Choreo logs in Console
2. Verify environment variables
3. Test health endpoints
4. Review this deployment guide

## Next Steps

After successful deployment:

1. **Test the API**: Use the test curl commands above
2. **Ingest Data**: Use ingestion endpoints to populate the vector database
3. **Configure Frontend**: Update frontend to use Choreo API URL
4. **Monitor**: Set up monitoring and alerts in Choreo
5. **Scale**: Adjust replicas based on traffic

---

**Note**: This deployment guide is specifically for the Choreo platform. For local development, see the main README.md file.

