# Choreo Platform Deployment Guide

## Overview
This guide covers deploying the Choreo AI Assistant to the WSO2 Choreo platform.

## Prerequisites
- Access to Choreo platform
- GitHub repository with this project
- Required API keys (Azure OpenAI, Pinecone, GitHub, Google Vision)

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository structure looks like this:
```
choreo-ai-assistant/
├── Dockerfile                  # Root-level Dockerfile for Choreo
├── .choreo/
│   └── component.yaml         # Choreo configuration
├── backend/                   # FastAPI backend
├── diagram_processor/         # Processing logic
├── data/                      # Data files
├── credentials/               # (Optional - use secrets instead)
└── requirements.txt
```

### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Choreo deployment"
git push origin main
```

### 3. Create Component in Choreo

1. **Login to Choreo Console**: https://console.choreo.dev/
2. **Create New Project** or select existing project
3. **Create New Component**:
   - Component Type: **Service**
   - Build Pack: **Dockerfile**
   - Repository: Select your GitHub repository
   - Branch: `main` (or your default branch)

### 4. Configure Build Settings

In the Choreo component configuration:

| Setting | Value |
|---------|-------|
| **Dockerfile Path** | `Dockerfile` |
| **Docker Context** | `.` |
| **Component Directory** | `.` (root directory) |
| **Port** | `9090` |

### 5. Add Environment Variables

Go to **Component Settings > Configs** and add these environment variables:

#### Required Variables:

**Azure OpenAI:**
```
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Pinecone:**
```
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=choreo-ai-assistant-v2
PINECONE_ENVIRONMENT=us-east-1-aws
```

**GitHub:**
```
GITHUB_TOKEN=ghp_...
```

#### Optional Variables:

**Google Vision (for diagram OCR):**
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"..."}
```
*Note: Paste the entire JSON file contents as a single-line string*

**Configuration:**
```
PYTHONPATH=/app
CHUNK_SIZE=3000
CHUNK_OVERLAP=200
MAX_FILE_SIZE=52428800
```

### 6. Configure Secrets (Recommended)

Instead of using environment variables for sensitive data, use Choreo's **Secret Store**:

1. Go to **Component Settings > Secrets**
2. Create secrets for:
   - `AZURE_OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `GITHUB_TOKEN`
   - `GOOGLE_CREDENTIALS_JSON`
3. Mount secrets as environment variables

### 7. Deploy

1. Click **Deploy** button
2. Select environment (Dev/Staging/Prod)
3. Wait for build to complete
4. Monitor logs for any issues

### 8. Test Deployment

Once deployed, test the endpoints:

**Health Check:**
```bash
curl https://your-component-url.choreo.dev/health
```

**API Test:**
```bash
curl -X POST https://your-component-url.choreo.dev/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Choreo?",
    "conversationId": "test-123"
  }'
```

## Troubleshooting

### Build Fails

**Issue**: `requirements.txt not found`
**Solution**: Make sure you have `requirements.txt` at the root level or update Dockerfile path

**Issue**: Import errors for `diagram_processor`
**Solution**: Ensure `PYTHONPATH=/app` is set and entire project is copied in Dockerfile

### Runtime Errors

**Issue**: `GOOGLE_APPLICATION_CREDENTIALS not found`
**Solution**: Use `GOOGLE_CREDENTIALS_JSON` environment variable with JSON string instead

**Issue**: Port binding errors
**Solution**: Ensure your app uses `PORT` environment variable: `--port ${PORT:-9090}`

### API Key Errors

**Issue**: `401 Unauthorized` from Azure OpenAI
**Solution**: Verify your Azure OpenAI API key and endpoint in Choreo secrets/configs

**Issue**: Pinecone connection fails
**Solution**: Check Pinecone API key and ensure index exists

## Environment-Specific Configuration

### Development
```yaml
# Minimal resources for testing
resources:
  memory: 512Mi
  cpu: 500m
```

### Production
```yaml
# Higher resources for production workload
resources:
  memory: 2Gi
  cpu: 2000m
replicas: 2  # For high availability
```

## Monitoring

### Health Endpoint
The application exposes a health check at `/health`:
```bash
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T12:00:00Z",
  "services": {
    "pinecone": "connected",
    "openai": "connected"
  }
}
```

### Logs
View logs in Choreo Console:
1. Go to **Observability > Logs**
2. Filter by component name
3. Monitor for errors or warnings

### Metrics
Monitor key metrics:
- Request rate
- Response time
- Error rate
- Memory usage
- CPU usage

## Scaling

Choreo auto-scales based on:
- CPU utilization (default: 70%)
- Memory utilization (default: 80%)
- Request rate

Configure scaling in **Component Settings > Scaling**:
```yaml
scaling:
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilization: 70
  targetMemoryUtilization: 80
```

## CI/CD Integration

### Auto-Deploy on Push

1. Go to **Component Settings > Deployments**
2. Enable **Auto Deploy**
3. Select branch (e.g., `main`)
4. Choose environment

Every push to the branch will trigger automatic deployment.

### Manual Deploy

Use Choreo CLI:
```bash
# Install Choreo CLI
npm install -g @wso2/choreo-cli

# Login
choreo login

# Deploy
choreo deploy --component choreo-ai-assistant --env prod
```

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use Choreo Secrets Store** for sensitive data
3. **Enable HTTPS** for all endpoints (automatic in Choreo)
4. **Implement rate limiting** to prevent abuse
5. **Regular security updates** for dependencies

## Cost Optimization

1. **Right-size resources**: Don't over-provision memory/CPU
2. **Use auto-scaling**: Scale down during low traffic
3. **Monitor API usage**: Track Azure OpenAI and Pinecone costs
4. **Implement caching**: Cache frequently requested queries

## Support

For Choreo platform issues:
- Documentation: https://wso2.com/choreo/docs/
- Support: Contact WSO2 support team
- Community: WSO2 Discord/Slack channels

For application issues:
- Check logs in Choreo Console
- Review error messages
- Validate environment variables
- Test locally with same configuration

