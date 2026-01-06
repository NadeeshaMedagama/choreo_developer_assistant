# Build Optimization Guide

## Overview
This document explains the optimizations made to reduce build size and resolve disk space issues during deployment.

## Problems Addressed

### 1. GitHub Actions Pipeline Failure
**Error:** `Username and password required`
**Solution:** Removed Docker Hub login/push from workflow. GitHub Actions now only builds and tests the image locally. Deployment to Choreo is done through Choreo's native build process.

### 2. Disk Space Issues During Build
**Error:** `[Errno 28] No space left on device`
**Solutions:**
- Use CPU-only PyTorch (~80% space savings vs CUDA version)
- Single RUN command for pip install (reduces layer duplication)
- Aggressive cleanup after installation
- Remove test files, __pycache__, and .pyc files

### 3. Dependency Resolution Conflicts
**Error:** `ResolutionImpossible`
**Solution:** Use loose version constraints in requirements.txt to allow pip to resolve compatible versions.

## Optimizations Implemented

### Dockerfile Optimizations

1. **CPU-Only PyTorch**: 
   ```dockerfile
   torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 \
   --index-url https://download.pytorch.org/whl/cpu
   ```
   Saves ~2GB compared to CUDA version.

2. **Single Layer Installation**:
   All pip packages installed in one RUN command to minimize layer overhead.

3. **Aggressive Cleanup**:
   ```dockerfile
   pip cache purge && \
   rm -rf /root/.cache/pip/* /root/.cache/huggingface /tmp/* && \
   find /usr/local/lib/python3.11 -type d -name "__pycache__" -delete && \
   find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete && \
   find /usr/local/lib/python3.11 -type d -name "tests" -exec rm -rf {} +
   ```

### File Exclusions

#### .dockerignore
- Excludes: tests, docs, notebooks, venv, logs, output files, model binaries
- Keeps: source code, requirements.txt, credentials

#### .gcloudignore
- Same exclusions as .dockerignore
- Specific to Google Cloud builds (used by Choreo)

### Removed Files

1. **Documentation .txt files**:
   - All files in `docs/notes/`
   - Quick reference guides
   - Deployment guides (moved to .md format)

2. **Output files**:
   - All files in `backend/diagram_processor/output/`
   - Processing reports
   - Generated summaries

3. **Duplicate requirements**:
   - `backend/choreo-ai-assistant/requirements.txt`
   - `backend/monitoring/configs/requirements.txt`

## Requirements Structure

### Main Requirements
- **Root**: `requirements.txt` - References backend requirements
- **Backend**: `backend/requirements.txt` - Core dependencies with loose constraints
- **Diagram Processor**: `backend/diagram_processor/requirements.txt` - Optional dependencies
- **GitHub Ingestion**: `backend/github_issues_ingestion/requirements.txt` - Optional dependencies

### Version Constraints Philosophy
Use loose constraints (`>=`) instead of pinned versions (`==`) to allow pip to resolve conflicts:
```python
# Good
fastapi>=0.100.0,<1.0.0
openai>=1.0.0

# Avoid (causes conflicts)
fastapi==0.100.0
openai==1.0.0
```

## GitHub Actions Workflow

The workflow now:
1. ✅ Builds the Docker image locally
2. ✅ Tests that the build succeeds
3. ✅ Shows image size
4. ❌ Does NOT push to Docker Hub (Choreo builds from source)

## Deployment to Choreo

Choreo will:
1. Clone the repository
2. Use `.gcloudignore` to exclude unnecessary files
3. Build the Docker image using the `Dockerfile`
4. Deploy to Choreo infrastructure

## Estimated Space Savings

- CPU-only PyTorch: ~2GB
- Removed test files: ~500MB
- Removed docs/output: ~200MB
- Cache cleanup: ~1GB
- **Total savings: ~3.7GB**

## Troubleshooting

### If build still fails with disk space error:

1. **Check Choreo build logs** for specific package causing issues
2. **Remove heavy optional dependencies**:
   - sentence-transformers (large)
   - opencv-python-headless (can use opencv-python-headless-minimal)
   - google-cloud-vision (if not using vision features)

3. **Use multi-stage build** (future enhancement):
   ```dockerfile
   FROM python:3.11-slim AS builder
   # Install dependencies
   
   FROM python:3.11-slim
   # Copy only necessary files from builder
   ```

### If dependency resolution fails:

1. Check the specific packages in conflict
2. Loosen version constraints further
3. Remove version constraints entirely for non-critical packages

## Maintenance

- **Don't commit** output files, logs, or temporary files
- **Keep** .dockerignore and .gcloudignore up to date
- **Test** builds locally before pushing to ensure they work

