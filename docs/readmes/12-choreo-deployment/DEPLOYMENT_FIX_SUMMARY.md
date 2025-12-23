# Choreo Deployment Fix Guide

## Problem Summary

The deployment was failing due to:

1. **Disk space exhaustion** - "No space left on device"
2. **Dependency conflicts** - ResolutionImpossible errors
3. **Large package sizes** - torch with CUDA dependencies (~2.8GB extra)
4. **Build context bloat** - Unnecessary files included in builds

## Solutions Implemented

### 1. Disk Space Optimization

#### Root Dockerfile (`/choreo-ai-assistant/Dockerfile`)
- ✅ Use CPU-only PyTorch: `torch==2.2.0` with `--index-url https://download.pytorch.org/whl/cpu`
- ✅ Install dependencies in separate steps with aggressive cleanup after each
- ✅ Use `--no-cache-dir` for all pip installs
- ✅ Run `pip cache purge` after each installation step
- ✅ Remove `__pycache__`, test directories, and temporary files

#### Backend Dockerfile (`/backend/Dockerfile`)
- ✅ Same optimizations as root Dockerfile
- ✅ Properly configured for Choreo with user ID 10014

### 2. Build Context Reduction

#### .dockerignore
```
*.txt (except requirements.txt)
docs/
tests/
logs/
*.log
notebooks/
*.ipynb
data/
monitoring/
k8s/
```

#### .gcloudignore (NEW)
Created to exclude files from Google Cloud builds used by Choreo:
- Documentation files
- Test files
- Large data directories
- IDE files
- Build artifacts

### 3. Requirements Optimization

#### Created `/backend/requirements.txt` (was missing!)
Consolidated core dependencies with loose version constraints to allow pip to resolve conflicts.

#### Updated module-specific requirements:
- **choreo-ai-assistant/requirements.txt** - Added `python-dateutil`
- **wiki_ingestion/requirements.txt** - Removed dev dependencies (pytest, black, flake8, mypy)
- **github_issues_ingestion/requirements.txt** - Kept minimal

#### Created `requirements-consolidated.txt`
Single file with all dependencies properly organized and commented.

### 4. Component Configuration

#### Updated `/backend/.choreo/component.yaml`
Added resource limits:
```yaml
resources:
  limits:
    memory: 2Gi
    cpu: 1000m
  requests:
    memory: 1Gi
    cpu: 500m
```

### 5. GitHub Actions Workflow

#### Created `.github/workflows/docker-build.yml`
- Disk space cleanup before build
- Efficient Docker buildx caching
- Multi-tag support
- Automatic release creation

### 6. Cleanup Script

Created `cleanup-before-build.sh` to manually clean up before deployment:
```bash
./cleanup-before-build.sh
```

Removes:
- Test files
- Python cache
- Logs
- Data directories
- Notebooks
- Large model files
- Backup files
- Documentation TXT files

## Deployment Steps for Choreo

### Option 1: Using Choreo UI

1. **Run cleanup** (optional but recommended):
   ```bash
   ./cleanup-before-build.sh
   ```

2. **Commit and push** changes:
   ```bash
   git add .
   git commit -m "fix: Optimize build for Choreo deployment"
   git push
   ```

3. **In Choreo Console**:
   - Navigate to your component
   - Trigger a new deployment
   - The build should now succeed with optimized disk usage

### Option 2: Using Docker Hub

1. **Build locally** (if you have enough space):
   ```bash
   docker build -t yourusername/choreo-ai-assistant:latest .
   docker push yourusername/choreo-ai-assistant:latest
   ```

2. **Or use GitHub Actions**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   This triggers the workflow to build and push to Docker Hub.

3. **In Choreo**: Configure to pull from Docker Hub

## Key Changes Made

### Files Created
- ✅ `/backend/requirements.txt` - Missing core requirements file
- ✅ `/.gcloudignore` - Exclude files from Google Cloud builds
- ✅ `/requirements-consolidated.txt` - All dependencies in one file
- ✅ `/cleanup-before-build.sh` - Pre-deployment cleanup script
- ✅ `/.github/workflows/docker-build.yml` - CI/CD pipeline

### Files Modified
- ✅ `/Dockerfile` - CPU-only torch, aggressive cleanup
- ✅ `/backend/Dockerfile` - Same optimizations
- ✅ `/.dockerignore` - Added *.txt exclusion
- ✅ `/backend/.dockerignore` - Added *.txt exclusion
- ✅ `/backend/.choreo/component.yaml` - Added resource limits
- ✅ `/backend/choreo-ai-assistant/requirements.txt` - Added python-dateutil
- ✅ `/backend/wiki_ingestion/requirements.txt` - Removed dev dependencies

### Files to Remove (if not needed)
These documentation files increase build context:
- `/backend/k8s/QUICK_FIX.txt`
- `/backend/k8s/QUICK_REFERENCE.txt`
- `/backend/docs/QUICK_DEPLOY_GUIDE.txt`
- `/docs/notes/*.txt` (multiple files)

They're already excluded via .dockerignore and .gcloudignore.

## Verification

After deployment, verify:

1. **Build completes successfully** - No disk space errors
2. **Container starts** - Check Choreo logs
3. **Health check passes** - `/` endpoint returns 200
4. **API works** - Test `/chat` endpoint

## Troubleshooting

### Still getting disk space errors?
1. Run `cleanup-before-build.sh`
2. Check if large files exist in your repo: `find . -type f -size +50M`
3. Remove any large model files or data

### Dependency conflicts?
1. Check the consolidated requirements file
2. Try loosening version constraints further
3. Let pip resolve automatically by removing upper bounds

### Build timeout?
1. Use pre-built Docker image from Docker Hub
2. Or increase Choreo build timeout if possible

## Next Steps

1. Monitor first deployment closely
2. Check memory usage in production
3. Adjust resource limits if needed
4. Consider splitting into microservices if size is still an issue

## Summary

The main issues were:
- **Missing backend/requirements.txt** causing build failures
- **CUDA-enabled torch** adding 2.8GB unnecessarily
- **No build cleanup** leaving temporary files
- **Large build context** including unnecessary documentation

All have been fixed. The deployment should now succeed! 🚀

