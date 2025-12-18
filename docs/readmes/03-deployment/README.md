# Deployment Documentation

This directory contains all documentation related to deploying DevChoreo in various environments.

## 🚀 Deployment Guides

### Platform Deployment
- **[CHOREO_DEPLOYMENT.md](CHOREO_DEPLOYMENT.md)** - Deploy to WSO2 Choreo platform
- **[CHOREO_RUN_COMMAND.md](CHOREO_RUN_COMMAND.md)** - Running on Choreo with proper commands

### Docker Deployment
- **[DOCKER_README.md](DOCKER_README.md)** - Complete Docker setup and deployment guide
- **[DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md)** - Quick Docker commands reference

### Frontend Deployment
- **[FRONTEND_DIST_DEPLOYMENT.md](FRONTEND_DIST_DEPLOYMENT.md)** - Building and deploying frontend distribution
- **[FRONTEND_BACKEND_CONNECTION.md](FRONTEND_BACKEND_CONNECTION.md)** - Connecting frontend to backend

## 📦 Deployment Options

### 1. Local Development
```bash
# Backend
cd backend
uvicorn app:app --reload

# Frontend
cd frontend
npm run dev
```
See: [RUN_PROJECT.md](../01-getting-started/RUN_PROJECT.md)

### 2. Docker Compose
```bash
cd docker
docker-compose up
```
See: [DOCKER_README.md](DOCKER_README.md)

### 3. Choreo Platform
Deploy to WSO2 Choreo using `.choreo/component.yaml`
See: [CHOREO_DEPLOYMENT.md](CHOREO_DEPLOYMENT.md)

### 4. Production
- Build frontend: `npm run build`
- Containerize: Use provided Dockerfile
- Deploy: Kubernetes, AWS, Azure, etc.

## 🔧 Configuration for Deployment

### Environment Variables
See: [ENV_FILE_LOCATION.md](../01-getting-started/ENV_FILE_LOCATION.md)

Required:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`

Optional:
- `GITHUB_TOKEN`
- `GOOGLE_VISION_API_KEY`
- `ENABLE_LLM_SUMMARIZATION`
- `MAX_SUMMARIZATION_RETRIES`

### Frontend-Backend Connection
- Development: `http://localhost:8000`
- Production: Configure in `vite.config.js` and environment variables

See: [FRONTEND_BACKEND_CONNECTION.md](FRONTEND_BACKEND_CONNECTION.md)

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Set all required environment variables
- [ ] Test locally first
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging
- [ ] Review security settings

### Deployment
- [ ] Build frontend (`npm run build`)
- [ ] Test backend endpoints
- [ ] Verify database connections (Milvus)
- [ ] Check health endpoints
- [ ] Validate CORS settings

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Test all features
- [ ] Verify source citations work
- [ ] Check conversation memory
- [ ] Validate streaming responses
- [ ] Set up alerts

## 🔒 Security Considerations

- Use environment variables for secrets (never hardcode)
- Configure CORS properly for production
- Enable HTTPS in production
- Rotate API keys regularly
- Monitor for unusual activity

## 📊 Monitoring in Production

- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert notifications
- **Logs**: Structured JSON logging

See: [MONITORING.md](../02-features/MONITORING.md)

## ✅ Ready to Deploy

- **[READY_TO_PUSH.md](READY_TO_PUSH.md)** - Pre-deployment verification checklist

## 🔗 Related Documentation

- **Getting Started**: See [../01-getting-started/](../01-getting-started/)
- **Troubleshooting**: See [../04-troubleshooting/](../04-troubleshooting/)
- **Features**: See [../02-features/](../02-features/)

---

**Last Updated**: December 2, 2025

