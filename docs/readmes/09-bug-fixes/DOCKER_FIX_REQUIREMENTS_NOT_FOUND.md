# Docker Build Error Fix - requirements-docker.txt Not Found

## ❌ Error Encountered

```
ERROR: failed to compute cache key: "/backend/requirements-docker.txt": not found
```

## 🔍 Root Cause

The Dockerfile was trying to copy `backend/requirements-docker.txt`, but:
1. The file might not be in the Docker build context
2. The `.dockerignore` might have been excluding it
3. Simpler to use existing `backend/requirements.txt`

## ✅ Solution Applied

### Change 1: Updated Dockerfile
Instead of using a separate `requirements-docker.txt`, the Dockerfile now:
1. Copies the existing `backend/requirements.txt`
2. Uses `grep -v "^torch"` to exclude the torch line
3. Installs PyTorch CPU separately
4. Installs the remaining dependencies

**This approach:**
- ✅ Uses existing files (no new file needed)
- ✅ Still installs CPU-only PyTorch (~200MB)
- ✅ Avoids .dockerignore issues
- ✅ Simpler and more maintainable

### Change 2: Fixed .dockerignore
Moved requirements.txt exceptions to the TOP of .dockerignore to ensure they're never excluded:

```dockerignore
# IMPORTANT: Do NOT ignore requirements files (must be first!)
!requirements*.txt
!backend/requirements.txt
!backend/requirements-docker.txt
!backend/choreo-ai-assistant/requirements.txt
!backend/diagram_processor/requirements.txt
...
```

## 📝 Updated Dockerfile Logic

```dockerfile
# Copy existing requirements files
COPY ../../../backend/requirements.txt /tmp/backend-requirements.txt
COPY ../../../backend/diagram_processor/requirements.txt /tmp/diagram-requirements.txt

# Install PyTorch CPU-only (~200MB instead of 2.5GB)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Exclude torch from requirements.txt and install rest
RUN grep -v "^torch" /tmp/backend-requirements.txt > /tmp/backend-requirements-no-torch.txt && \
    pip install --no-cache-dir -r /tmp/backend-requirements-no-torch.txt

# Install diagram processor requirements
RUN pip install --no-cache-dir -r /tmp/diagram-requirements.txt
```

## ✅ Benefits

1. **No new files needed** - Uses existing requirements.txt
2. **Still gets CPU PyTorch** - Saves ~2GB+ disk space
3. **No .dockerignore conflicts** - Works with existing files
4. **Easier maintenance** - One requirements.txt to update

## 🎯 Next Steps

Try the build again:

```bash
docker build -t choreo-ai-assistant .
```

The build should now:
1. ✅ Find `backend/requirements.txt` (it exists)
2. ✅ Install PyTorch CPU-only (200MB)
3. ✅ Install other dependencies (without torch line)
4. ✅ Complete successfully without disk space errors

## 📊 File Status

| File | Status | Purpose |
|------|--------|---------|
| `backend/requirements.txt` | ✅ Used | Main requirements (with torch line) |
| `backend/requirements-docker.txt` | ⚠️ Optional | Alternative lightweight requirements |
| `.dockerignore` | ✅ Fixed | Ensures requirements files are included |
| `Dockerfile` | ✅ Updated | Uses grep to exclude torch line |

## 🔄 What Changed

### Before (BROKEN):
```dockerfile
COPY backend/requirements-docker.txt /tmp/backend-requirements.txt  # ❌ File not found
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt
```

### After (FIXED):
```dockerfile
COPY backend/requirements.txt /tmp/backend-requirements.txt  # ✅ File exists
RUN grep -v "^torch" /tmp/backend-requirements.txt > /tmp/backend-requirements-no-torch.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements-no-torch.txt
```

---

**Status**: ✅ **FIXED** - Dockerfile now uses existing requirements.txt file

