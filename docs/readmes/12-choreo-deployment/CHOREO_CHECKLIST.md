# Choreo Deployment Checklist

Use this checklist when deploying to Choreo platform.

## Pre-Deployment ☑️

- [ ] Azure OpenAI credentials available
  - [ ] Endpoint URL
  - [ ] API Key
  - [ ] Chat deployment name
  - [ ] Embeddings deployment name

- [ ] Milvus database setup
  - [ ] Milvus URI
  - [ ] Authentication token
  - [ ] Collection created (or auto-create enabled)

- [ ] Optional services (if needed)
  - [ ] GitHub token for private repos
  - [ ] Google Vision API key for images

## Code Preparation ☑️

- [ ] Latest code pulled from repository
- [ ] `.choreo/component.yaml` exists and is configured
- [ ] `.choreo/openapi.yaml` exists
- [ ] `Dockerfile` has updated health check configuration
- [ ] `backend/app.py` has lazy initialization

## Choreo Console Setup ☑️

- [ ] Create new Service component in Choreo
- [ ] Connect to GitHub repository
- [ ] Select correct branch
- [ ] Build configuration set:
  - [ ] Build Type: `dockerfile`
  - [ ] Dockerfile Path: `Dockerfile`
  - [ ] Docker Context: `.`

## Environment Variables ☑️

### Required
- [ ] `AZURE_OPENAI_KEY`
- [ ] `AZURE_OPENAI_ENDPOINT`
- [ ] `AZURE_OPENAI_DEPLOYMENT`
- [ ] `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`
- [ ] `MILVUS_URI`
- [ ] `MILVUS_TOKEN`

### Optional (configure if needed)
- [ ] `AZURE_OPENAI_API_VERSION`
- [ ] `MILVUS_COLLECTION_NAME`
- [ ] `MILVUS_DIMENSION`
- [ ] `GITHUB_TOKEN`
- [ ] `GOOGLE_VISION_API_KEY`
- [ ] `ENABLE_LLM_SUMMARIZATION`
- [ ] `ENABLE_URL_VALIDATION`

## Deployment ☑️

- [ ] Click "Deploy" in Choreo Console
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Check deployment logs for errors
- [ ] Verify deployment status shows "Running"

## Post-Deployment Verification ☑️

### Health Checks
- [ ] Test root endpoint: `curl https://your-app.choreo.dev/`
- [ ] Test health endpoint: `curl https://your-app.choreo.dev/health`
- [ ] Test detailed health: `curl https://your-app.choreo.dev/api/health`

### API Testing
- [ ] Test AI query endpoint:
  ```bash
  curl -X POST https://your-app.choreo.dev/api/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "What is Choreo?"}'
  ```

### Monitoring
- [ ] Check application logs in Choreo Console
- [ ] Verify no error messages
- [ ] Confirm "All services initialized successfully" message

### Performance
- [ ] Health check responds in < 5 seconds
- [ ] First API request completes (may take 10-30s)
- [ ] Subsequent requests respond quickly (< 2s)

## Troubleshooting ☑️

If deployment fails, check:

- [ ] All required environment variables are set
- [ ] Environment variables are correctly formatted
- [ ] Milvus URI is accessible from Choreo
- [ ] Azure OpenAI endpoint is accessible
- [ ] Deployment logs for specific errors
- [ ] Health check endpoint responds

## Common Issues & Solutions

### ❌ 504 Gateway Timeout
**Solution**: ✅ Already fixed with lazy initialization

### ❌ Service unhealthy after deployment
**Check**:
- Environment variables (especially API keys)
- Milvus connection (URI and token)
- Azure OpenAI connection (endpoint and key)
- View logs in Choreo Console

### ❌ First request times out
**Expected**: First request may take 10-30s to initialize services
**Solution**: Subsequent requests will be fast

### ❌ Vector search returns no results
**Check**:
- Milvus collection has data ingested
- Collection name in env vars matches actual collection
- Run ingestion endpoint to populate data

## Next Steps After Successful Deployment

- [ ] Ingest initial data using `/api/ingest/github` endpoint
- [ ] Configure frontend to use Choreo API URL
- [ ] Set up monitoring and alerts
- [ ] Configure auto-scaling if needed
- [ ] Set up CI/CD for automatic deployments
- [ ] Document the deployment URL for team

## Support Resources

- 📖 [CHOREO_DEPLOYMENT.md](CHOREO_DEPLOYMENT.md) - Full deployment guide
- 📖 [CHOREO_DEPLOYMENT_FIX.md](CHOREO_DEPLOYMENT_FIX.md) - Technical details of fixes
- 📋 [.env.choreo.example](../../../.env.choreo.example) - Environment variables reference
- 🔗 [Choreo Documentation](https://wso2.com/choreo/docs/)

---

**Date**: _________________
**Deployed By**: _________________
**Deployment URL**: _________________
**Status**: ☐ Success ☐ Failed ☐ In Progress

