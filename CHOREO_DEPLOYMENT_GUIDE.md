# Choreo Deployment Guide

## ✅ Answer: Deploy the COMPLETE DIRECTORY

You need to deploy the **entire project root directory** (`choreo-ai-assistant/`), NOT just the `backend/` folder.

## Why Deploy the Complete Directory?

Your project has this structure:

```
choreo-ai-assistant/              ← Deploy THIS (project root)
├── .choreo/
│   ├── component.yaml           ← Choreo config (dockerContext: .)
│   └── openapi.yaml
├── Dockerfile                   ← Builds from project root
├── backend/                     ← Backend code
│   ├── app.py
│   ├── choreo-ai-assistant/
│   │   └── requirements.txt     ← Dependencies HERE (inside backend/)
│   └── diagram_processor/
│       └── requirements.txt
```

### Key Reasons:

1. **Dockerfile Context**: Your `Dockerfile` has `COPY . .` which copies the entire project
2. **Requirements Location**: `requirements.txt` files are now in `backend/choreo-ai-assistant/` and `backend/diagram_processor/` subfolders
3. **Python Imports**: Backend uses relative imports like `from .services import ...` which require the full structure
4. **Multiple Components**: You have `backend/` with nested `diagram_processor/` and other modules that depend on each other

## Step-by-Step Deployment to Choreo

### Step 1: Create Component in Choreo

1. Log in to [Choreo Console](https://console.choreo.dev)
2. Click **Create** → **Service**
3. Connect your GitHub repository

### Step 2: Configure Component

When prompted for configuration:

| Setting | Value |
|---------|-------|
| **Component Name** | `choreo-ai-assistant` |
| **Build Preset** | Dockerfile |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Context Path** | `.` (root directory) |
| **Port** | `9090` |

**IMPORTANT**: Set Docker Context Path to `.` (dot) - this means the project root!

### Step 3: Repository Path Selection

When Choreo asks "Which directory contains your service?":

**Select**: `/` or `./` (root of repository)

**DO NOT select**: `/backend/` ❌

### Step 4: Verify Configuration

Your `.choreo/component.yaml` should show:

```yaml
build:
  buildType: dockerfile
  dockerfilePath: Dockerfile
  dockerContext: .              # ← This means project root!
```

This is already correct in your project! ✅

### Step 5: Deploy

1. Click **Deploy**
2. Choreo will:
   - Clone the entire repository
   - Use the project root as build context
   - Find `Dockerfile` at the root
   - Copy everything with `COPY . .`
   - Install dependencies from `backend/choreo-ai-assistant/requirements.txt`
   - Run the backend server

## How the Build Process Works

### Dockerfile Build Flow:

```dockerfile
# 1. Set working directory
WORKDIR /app

# 2. Copy ENTIRE project (this needs project root as context!)
COPY . .

# 3. Install dependencies (tries both locations)
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r backend/choreo-ai-assistant/requirements.txt

# 4. Install diagram processor dependencies
RUN pip install --no-cache-dir -r backend/diagram_processor/requirements.txt

# 5. Set Python path to project root
ENV PYTHONPATH=/app

# 6. Run backend server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Selecting /backend/ directory
```
Component Path: /backend/  ← WRONG!
```
**Problem**: Won't find `requirements.txt` or other dependencies

### ❌ Mistake 2: Wrong Dockerfile path
```
Dockerfile Path: backend/Dockerfile  ← WRONG!
```
**Problem**: Dockerfile is at project root, not in backend/

### ❌ Mistake 3: Creating requirements.txt in backend/
```
backend/requirements.txt  ← Don't do this!
```
**Problem**: Creates duplicate dependencies, breaks existing structure

## ✅ Correct Configuration

```yaml
# In .choreo/component.yaml (already configured!)
build:
  buildType: dockerfile
  dockerfilePath: Dockerfile      # At project root
  dockerContext: .                # Project root as context
```

## Environment Variables Setup

After deployment, configure these in Choreo Console:

### Required Variables:

1. **AZURE_OPENAI_KEY** - Azure OpenAI API key
2. **AZURE_OPENAI_ENDPOINT** - Azure OpenAI endpoint URL
3. **AZURE_OPENAI_API_VERSION** - API version (e.g., "2024-02-15-preview")
4. **AZURE_OPENAI_DEPLOYMENT_NAME** - Deployment name
5. **MILVUS_HOST** - Milvus database host
6. **MILVUS_PORT** - Milvus port (default: 19530)
7. **MILVUS_USER** - Milvus username
8. **MILVUS_PASSWORD** - Milvus password
9. **GITHUB_TOKEN** - GitHub personal access token (for ingestion)

### Optional Variables:

- **GOOGLE_APPLICATION_CREDENTIALS** - Path to Google Cloud credentials
- **LOG_LEVEL** - Logging level (default: INFO)

## Testing After Deployment

### 1. Health Check

```bash
curl https://your-component-url.choreo.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "milvus": "connected"
}
```

### 2. Test Query Endpoint

```bash
curl -X POST "https://your-component-url.choreo.dev/api/ask?question=What%20is%20Choreo%3F"
```

### 3. View API Documentation

Navigate to: `https://your-component-url.choreo.dev/docs`

## Troubleshooting

### Issue: "npm ci" error - package-lock.json not found

**Error Message**:
```
npm error The `npm ci` command can only install with an existing package-lock.json or
npm error npm-shrinkwrap.json with lockfileVersion >= 1.
```

**Root Cause**: The `.gitignore` file has `*.json` which ignores all JSON files including `package-lock.json`

**Solution**: Update `.gitignore` to exclude `package-lock.json` from being ignored:

```gitignore
# Credentials and API Keys
credentials/
*.json
!package.json
!package-lock.json  # ← Add this line
!tsconfig.json
```

Then commit and push:
```bash
git add .gitignore frontend/package-lock.json
git commit -m "fix: ensure package-lock.json is tracked by git"
git push
```

**This fix has already been applied to your project!** ✅

### Issue: "requirements.txt not found"

**Solution**: Ensure Docker Context is set to `.` (project root), not `/backend/`

### Issue: "Module 'backend' not found"

**Solution**: Check that `ENV PYTHONPATH=/app` is set in Dockerfile (already done ✅)

### Issue: "Cannot connect to Milvus"

**Solution**: Configure Milvus environment variables in Choreo Console

### Issue: Build fails with "COPY failed"

**Solution**: Verify that `dockerContext: .` in component.yaml points to project root

## Summary

### What to Deploy: 
**Complete directory** (project root: `choreo-ai-assistant/`)

### Why:
- ✅ Dockerfile expects full project structure
- ✅ requirements.txt is outside backend/
- ✅ Multiple interdependent components
- ✅ Python imports need full structure

### Configuration:
- ✅ Docker Context: `.` (already configured)
- ✅ Dockerfile Path: `Dockerfile` (already configured)
- ✅ Port: `9090` (already configured)

Your project is **already correctly configured** for Choreo deployment! Just point Choreo to the project root when creating the component. 🚀

