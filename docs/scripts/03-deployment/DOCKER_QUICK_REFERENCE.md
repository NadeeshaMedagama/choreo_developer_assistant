# Docker Quick Reference

## From the project root directory

### Build
```bash
cd docker
docker-compose build
```

### Run ingestion (one-time)
```bash
cd docker
docker-compose run --rm choreo-ingestion
```

### Run in background
```bash
cd docker
docker-compose up -d
```

### View logs
```bash
cd docker
docker-compose logs -f
```

### Stop
```bash
cd docker
docker-compose down
```

## Alternative: Direct Docker Commands

### Build image directly
```bash
docker build -f docker/Dockerfile -t choreo-ingestion:latest .
```

### Run directly
```bash
docker run --rm --env-file backend/.env choreo-ingestion:latest
```

## Test Commands

```bash
# Test GitHub connection
cd docker
docker-compose run --rm choreo-ingestion python backend/tests/test_github.py

# Check environment setup
cd docker
docker-compose run --rm choreo-ingestion python backend/check_setup.py

# Interactive shell
cd docker
docker-compose run --rm choreo-ingestion bash
```

## Build Time

First build takes 5-10 minutes due to:
- PyTorch installation (~2GB)
- Sentence-transformers (~700MB)
- Other dependencies

Subsequent builds use cache and are much faster!

