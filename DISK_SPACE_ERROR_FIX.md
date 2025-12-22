# Docker Build - Disk Space Error Fix

## ❌ Error Encountered

```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```

## 🔍 Root Cause

The Docker build is running out of disk space because:

1. **PyTorch with CUDA is HUGE** (~2GB+ for GPU version)
2. **ML dependencies are large** (scipy, numpy, transformers, etc.)
3. **Build cache accumulates** during pip install
4. **Choreo buildpack environment** may have disk space limits

### Package Size Breakdown:
- `torch` (CUDA version): ~2.5 GB
- `torch` (CPU version): ~200 MB ✅
- `scipy`: ~35 MB
- `transformers`: ~500 MB with models
- `sentence-transformers`: ~300 MB with models

## ✅ Solutions (3 Options)

### **Option 1: Use CPU-Only PyTorch (RECOMMENDED)**

The optimized Dockerfile installs PyTorch CPU-only version, which is **90% smaller**:

```bash
# Use the optimized Dockerfile
docker build -f Dockerfile.optimized -t choreo-ai-assistant .
```

**Benefits:**
- ✅ Reduces image size by ~2GB
- ✅ Faster builds
- ✅ Sufficient for most inference tasks
- ✅ Works great in cloud environments

### **Option 2: Use Lightweight Requirements**

Use the `requirements-docker.txt` which excludes heavy dependencies:

```bash
# Build with lightweight requirements
docker build -t choreo-ai-assistant .
```

The Dockerfile now uses `backend/requirements-docker.txt` which:
- Uses CPU-only PyTorch
- Excludes unnecessary CUDA dependencies
- Adds aggressive cache purging

### **Option 3: Multi-Stage Build with Shared Layers**

For the smallest possible image, use multi-stage builds:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /tmp
COPY backend/requirements-docker.txt .
RUN pip install --user --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --user --no-cache-dir -r requirements-docker.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
# ... rest of Dockerfile
```

## 📁 Files Created

1. ✅ **`Dockerfile.optimized`** - Optimized Dockerfile with CPU-only PyTorch
2. ✅ **`backend/requirements-docker.txt`** - Lightweight requirements
3. ✅ **`Dockerfile`** - Updated with better caching and cleanup

## 🔧 Quick Fix Instructions

### Step 1: Choose Your Dockerfile

**For Choreo Deployment (Recommended):**
```bash
# Rename optimized version to main Dockerfile
mv Dockerfile Dockerfile.original
mv Dockerfile.optimized Dockerfile
```

**Or keep both and specify:**
```bash
docker build -f Dockerfile.optimized -t choreo-ai-assistant .
```

### Step 2: Update Choreo Configuration

If deploying to Choreo, you may need to update the buildpack or Dockerfile path in your deployment config.

### Step 3: Test the Build

```bash
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"
docker build -t choreo-ai-assistant .
```

## 📊 Expected Results

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| PyTorch Size | ~2.5 GB | ~200 MB | **90%** |
| Total Image | ~4-5 GB | ~1-1.5 GB | **70%** |
| Build Time | ~15 min | ~5 min | **66%** |
| Disk Space Needed | ~10 GB | ~3 GB | **70%** |

## 🎯 Additional Optimizations

### 1. **Aggressive Cache Purging**
Already added to Dockerfiles:
```dockerfile
RUN pip install ... && pip cache purge && rm -rf /root/.cache
```

### 2. **Layer Optimization**
Copy requirements first, then code:
```dockerfile
COPY backend/requirements-docker.txt /tmp/
RUN pip install -r /tmp/requirements-docker.txt
COPY . .  # This layer won't rebuild if only code changes
```

### 3. **Use .dockerignore**
Create `.dockerignore` to exclude:
```
**/__pycache__
**/*.pyc
**/.git
**/logs
**/node_modules
**/.venv
**/venv
```

### 4. **Install Only What You Need**
Review if you really need:
- `sentence-transformers` - Can you use OpenAI embeddings instead?
- `torch` - Do you actually use PyTorch models?
- `google-cloud-vision` - Only if using OCR features

## 🚨 Choreo-Specific Considerations

If deploying to Choreo platform:

1. **Check Disk Quotas:**
   - Choreo may have build environment disk limits
   - Contact support if needed

2. **Use Cloud Build:**
   - Consider building locally and pushing to registry
   - Or use GitHub Actions with larger runners

3. **Registry Size Limits:**
   - Check if Choreo has image size limits
   - Optimize to stay under limits

## ✅ Verification Checklist

After applying fixes:

- [ ] Dockerfile uses CPU-only PyTorch
- [ ] pip cache purge commands are present
- [ ] Unnecessary files are cleaned up
- [ ] .dockerignore file exists
- [ ] Build completes without disk space errors
- [ ] Image size is < 2 GB
- [ ] Application starts successfully

## 📖 Related Documentation

- [PyTorch CPU Installation](https://pytorch.org/get-started/locally/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Reducing Image Size](https://docs.docker.com/build/building/best-practices/)

---

**Status**: ✅ **SOLUTIONS PROVIDED** - Choose Option 1 (CPU-only PyTorch) for best results

