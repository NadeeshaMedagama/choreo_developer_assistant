# 🐳 Docker Setup Guide

## Quick Start

### 1. Build the Docker Image

```bash
cd /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant/docker
docker-compose build
```

### 2. Run the Ingestion

```bash
docker-compose up
```

Or run in detached mode:

```bash
docker-compose up -d
```

## Available Commands

### Build Only
```bash
docker-compose build
```

### Run Ingestion (One-time)
```bash
docker-compose run --rm choreo-ingestion
```

### Run and View Logs
```bash
docker-compose up
```

### Run in Background
```bash
docker-compose up -d
docker-compose logs -f  # Follow logs
```

### Stop the Service
```bash
docker-compose down
```

### Rebuild and Run
```bash
docker-compose up --build
```

## Configuration

### Environment Variables

The docker-compose.yml automatically loads from `backend/.env`. Make sure you have:

```bash
# Required
PINECONE_API_KEY=your_key_here

# Recommended
GITHUB_TOKEN=your_token_here
```

### Override Configuration

You can override any environment variable:

```bash
docker-compose run --rm \
  -e CHUNK_SIZE=500 \
  -e CHUNK_OVERLAP=100 \
  choreo-ingestion
```

## Different Use Cases

### 1. Run Ingestion Script (Default)
```bash
docker-compose run --rm choreo-ingestion
```

### 2. Run GitHub Test
```bash
docker-compose run --rm choreo-ingestion python backend/tests/test_github.py
```

### 3. Check Setup
```bash
docker-compose run --rm choreo-ingestion python backend/check_setup.py
```

### 4. Interactive Shell
```bash
docker-compose run --rm choreo-ingestion bash
```

### 5. Run with Custom Python Script
```bash
docker-compose run --rm choreo-ingestion python your_script.py
```

## Building for Production

### Build Optimized Image
```bash
docker build -f docker/Dockerfile -t choreo-ingestion:latest .
```

### Run Production Container
```bash
docker run --rm \
  --env-file backend/.env \
  choreo-ingestion:latest
```

## Resource Management

The docker-compose.yml includes resource limits:
- **CPU Limit**: 2 cores
- **Memory Limit**: 4GB
- **CPU Reservation**: 1 core
- **Memory Reservation**: 2GB

Adjust these in `docker-compose.yml` based on your needs:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Increase for faster processing
      memory: 8G     # Increase if loading large models
```

## Development Mode

For development, the compose file mounts your local code:

```yaml
volumes:
  - ../choreo-ai-assistant/backend:/app/backend
```

This means changes to your code are reflected immediately without rebuilding.

**For production**, comment out the volumes section to bake the code into the image.

## Troubleshooting

### Issue: "Cannot connect to Pinecone"
**Solution**: Check that `PINECONE_API_KEY` is set in `backend/.env`

### Issue: "GitHub rate limit exceeded"
**Solution**: Add `GITHUB_TOKEN` to `backend/.env`

### Issue: "Out of memory"
**Solution**: Increase memory limit in docker-compose.yml or reduce `CHUNK_SIZE`

### Issue: "Model download fails"
**Solution**: Ensure the container has internet access and sufficient disk space

### View Container Logs
```bash
docker-compose logs choreo-ingestion
```

### Check Container Status
```bash
docker-compose ps
```

### Enter Running Container
```bash
docker-compose exec choreo-ingestion bash
```

## Advanced Usage

### Run with Different Embedding Models

```bash
docker-compose run --rm \
  -e EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2 \
  -e PINECONE_DIMENSION=768 \
  choreo-ingestion
```

### Run with OpenAI Embeddings

```bash
docker-compose run --rm \
  -e OPENAI_API_KEY=your_key \
  -e PINECONE_DIMENSION=1536 \
  choreo-ingestion
```

### Schedule with Cron

Add to your crontab to run daily at 2 AM:

```bash
0 2 * * * cd /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant/docker && docker-compose run --rm choreo-ingestion
```

## Image Size

The multi-stage build produces an optimized image:
- **Builder stage**: ~2GB (includes build tools)
- **Final stage**: ~800MB (runtime only)

## Security

The Dockerfile:
- ✅ Runs as non-root user (`appuser`)
- ✅ Uses slim base image (fewer vulnerabilities)
- ✅ No secrets baked into image
- ✅ Minimal attack surface

## Container Registry

### Tag and Push to Registry

```bash
# Tag the image
docker tag choreo-ingestion:latest your-registry.com/choreo-ingestion:latest

# Push to registry
docker push your-registry.com/choreo-ingestion:latest
```

### Pull and Run from Registry

```bash
docker pull your-registry.com/choreo-ingestion:latest
docker run --rm --env-file backend/.env your-registry.com/choreo-ingestion:latest
```

## Cleanup

### Remove All Containers and Images
```bash
docker-compose down --rmi all --volumes
```

### Remove Unused Docker Resources
```bash
docker system prune -a
```

## Summary

✅ **Multi-stage build** - Optimized image size  
✅ **Environment variables** - Easy configuration  
✅ **Non-root user** - Security best practice  
✅ **Development mode** - Live code reload  
✅ **Resource limits** - Prevent resource exhaustion  
✅ **Docker Compose** - Simple orchestration  

Your project is now fully dockerized! 🚀

