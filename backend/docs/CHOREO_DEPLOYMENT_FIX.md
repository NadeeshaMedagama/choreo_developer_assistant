# Choreo Deployment Build Size Fix

## Problem
The application was failing to deploy on Choreo platform with error code 51 during the buildpack phase. The logs showed installation of CUDA/GPU packages (nvidia-cuda-*, nvidia-nccl-cu12, etc.) which caused:

1. **Massive image size** - CUDA wheels add ~8GB vs ~200MB for CPU-only PyTorch
2. **Buildpack limits exceeded** - Google Cloud Buildpacks have stricter size/time limits
3. **Unnecessary dependencies** - Choreo doesn't provide GPU support

## Root Cause
- `sentence-transformers` and other ML libraries were pulling PyTorch with CUDA support by default
- Without explicit CPU-only PyTorch installation, pip installs the full CUDA version

## Solution Applied

### 1. Modified Dockerfile
**File**: `/backend/Dockerfile`

Added explicit CPU-only PyTorch installation BEFORE installing other dependencies:

```dockerfile
# Install CPU-only PyTorch FIRST to prevent CUDA dependencies
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
```

### 2. Updated requirements.txt
**File**: `/backend/requirements.txt`

Added clear documentation that torch is handled separately to avoid confusion.

## Expected Results
- **Image size reduction**: ~6-8GB smaller
- **Faster builds**: Less data to download and unpack
- **Build success**: Within Choreo platform limits
- **Same functionality**: CPU-only PyTorch is sufficient for inference workloads

## Additional Optimizations (Optional)

### A. Multi-stage Build Cleanup
The Dockerfile already uses multi-stage builds. Consider also removing build tools from the final image if needed.

### B. Reduce Layer Count
Combine RUN commands where possible:
```dockerfile
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge || true
```

### C. Use .dockerignore
Create `/backend/.dockerignore` to exclude unnecessary files:
```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov
.git
.gitignore
*.md
docs/
tests/
logs/
```

### D. Pin PyTorch Version (Recommended)
For production stability, consider pinning the torch version:
```dockerfile
RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu
```

## Verification Steps

1. **Local build test**:
   ```bash
   cd backend
   docker build -t choreo-ai-assistant:test .
   ```

2. **Check image size**:
   ```bash
   docker images choreo-ai-assistant:test
   ```
   - Expected: ~1.5-2GB (was ~8-10GB with CUDA)

3. **Verify no CUDA packages**:
   ```bash
   docker run --rm choreo-ai-assistant:test pip list | grep cuda
   ```
   - Expected: No results

4. **Test application runs**:
   ```bash
   docker run --rm -p 9090:9090 choreo-ai-assistant:test
   ```

## Deployment to Choreo

After these changes, the build should succeed on Choreo platform. If you still encounter issues:

1. **Check Choreo build logs** for specific errors
2. **Verify memory limits** in your Choreo component configuration
3. **Consider reducing dependencies** if image is still too large
4. **Use Choreo's build configuration** to increase timeout if needed

## Impact on Performance

**No negative impact expected:**
- CPU inference is standard for most production ML workloads
- Sentence transformers work perfectly with CPU-only PyTorch
- GPU support is typically not available in serverless/container platforms anyway

## References
- [PyTorch CPU Installation](https://pytorch.org/get-started/locally/)
- [Google Cloud Buildpacks Limits](https://cloud.google.com/docs/buildpacks/build-application)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

