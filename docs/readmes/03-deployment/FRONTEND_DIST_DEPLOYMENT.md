# Frontend Build and Deployment Guide

## Overview

The `frontend/dist/` directory contains the **production build** of the React frontend application. This directory **must be committed to Git** for deployment to work correctly on Choreo and other platforms.

---

## 🏗️ Building the Frontend

### Option 1: Using the Build Script (Recommended)

```bash
./docs/scripts/build-frontend.sh
```

### Option 2: Manual Build

```bash
cd frontend
npm install
npm run build
```

### Option 3: Build in Docker

The Dockerfile automatically handles this, but you can test it:

```bash
docker build -t choreo-ai-assistant .
```

---

## 📁 Directory Structure

After building, the `frontend/dist/` directory will contain:

```
frontend/dist/
├── index.html              # Main HTML file
├── assets/                 # Static assets
│   ├── index-[hash].js    # Bundled JavaScript
│   ├── index-[hash].css   # Bundled CSS
│   └── ...                # Other assets
└── .gitkeep               # Ensures directory is tracked
```

---

## ✅ Why dist/ Must Be in Git

### For Choreo Deployment

Choreo builds the Docker image which serves the pre-built frontend. The dist directory must be present in the repository because:

1. **Dockerfile copies it**: `COPY . .` includes `frontend/dist/`
2. **Backend serves it**: The backend can optionally serve static files
3. **No build step in Choreo**: Choreo doesn't run `npm build` - it uses the committed files

### Alternative Approaches

If you prefer NOT to commit dist/, you can:

1. **Build in Dockerfile** (slower builds):
   ```dockerfile
   # Install Node.js
   RUN apt-get install -y nodejs npm
   # Build frontend
   RUN cd frontend && npm install && npm run build
   ```

2. **Use CI/CD** to build and deploy separately

---

## 🔧 .gitignore Configuration

### Root .gitignore

The root `.gitignore` has been updated to:
```gitignore
# Python dist is ignored, but NOT frontend/dist/
# Note: frontend/dist/ is NOT ignored - we need it for deployment
```

### Frontend .gitignore

Created `frontend/.gitignore` with:
```gitignore
# Dependencies
node_modules/

# dist/ is NOT ignored - we need it for production deployment

# Logs and temporary files
*.log
.env.local
```

---

## 🚀 Deployment Workflow

### 1. Build Frontend

```bash
cd frontend
npm run build
```

### 2. Verify Build

```bash
ls -la frontend/dist/
# Should show index.html and assets/
```

### 3. Commit Changes

```bash
git add frontend/dist
git add frontend/.gitignore
git commit -m "Add production frontend build"
```

### 4. Push to GitHub

```bash
git push origin main
```

### 5. Deploy to Choreo

Choreo will:
1. Pull the repository
2. Build Docker image (includes frontend/dist/)
3. Start the backend server
4. Frontend is accessible via the backend or separate hosting

---

## 🧪 Testing the Build

### Local Testing

After building, test with a simple HTTP server:

```bash
cd frontend/dist
python -m http.server 8080
# Visit http://localhost:8080
```

### Docker Testing

```bash
docker build -t choreo-test .
docker run -p 9090:9090 choreo-test
# Backend runs on http://localhost:9090
```

---

## 📊 Build Artifacts

### What's Included in dist/

| File/Directory | Purpose | Size (typical) |
|----------------|---------|----------------|
| `index.html` | Entry point | ~2 KB |
| `assets/*.js` | Bundled React app | ~200-500 KB |
| `assets/*.css` | Compiled Tailwind CSS | ~50-100 KB |
| `assets/fonts/` | Font files (if any) | Varies |
| `assets/images/` | Optimized images | Varies |

### Build Optimization

Vite automatically:
- ✅ Minifies JavaScript and CSS
- ✅ Tree-shakes unused code
- ✅ Generates content hashes for caching
- ✅ Optimizes images
- ✅ Code splits for lazy loading

---

## 🔍 Troubleshooting

### Issue: dist/ Directory is Empty

**Cause:** Build hasn't been run or failed

**Solution:**
```bash
cd frontend
npm install
npm run build
# Check for errors in output
```

### Issue: dist/ Not in Git

**Cause:** .gitignore is blocking it

**Solution:**
```bash
# Force add the directory
git add -f frontend/dist
git commit -m "Add frontend dist directory"
```

### Issue: Build Fails

**Cause:** Missing dependencies or syntax errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
# Check error messages
```

### Issue: Choreo Deployment Fails

**Cause:** dist/ not committed or Dockerfile misconfigured

**Solution:**
1. Verify dist/ is in repository:
   ```bash
   git ls-files frontend/dist
   ```
2. Check Dockerfile copies frontend:
   ```bash
   grep "COPY" Dockerfile
   ```

---

## 🎯 Best Practices

### Development

1. **Don't commit every build** - Only commit when:
   - Making a production release
   - Deploying to Choreo
   - Tagging a version

2. **Keep builds fresh** - Rebuild before deployment:
   ```bash
   npm run build
   git add frontend/dist
   git commit -m "Update frontend build"
   ```

### Production

1. **Version builds** - Tag commits with builds:
   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0 with frontend build"
   git push origin v1.0.0
   ```

2. **Verify before push** - Always test the build locally

3. **Document changes** - Note frontend changes in commit messages

---

## 📝 CI/CD Integration

### GitHub Actions (Optional)

Create `.github/workflows/build-frontend.yml`:

```yaml
name: Build Frontend

on:
  push:
    branches: [ main ]
    paths:
      - 'frontend/src/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Build
        run: |
          cd frontend
          npm install
          npm run build
      - name: Commit
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add frontend/dist
          git commit -m "Auto-build frontend [skip ci]" || exit 0
          git push
```

---

## 🔐 Security Considerations

### What to NOT Commit

- ❌ `.env` files
- ❌ API keys in source code
- ❌ `node_modules/`
- ❌ Development builds with source maps

### What to Commit

- ✅ Production `dist/` directory
- ✅ `package.json` and `package-lock.json`
- ✅ Source code in `src/`
- ✅ Vite configuration

---

## 📚 Related Documentation

- [Frontend README](../FRONTEND_README.md)
- [Choreo Deployment Guide](CHOREO_DEPLOYMENT.md)
- [Docker Guide](DOCKER_README.md)
- [Build Scripts](../../docs/scripts/)

---

## Summary

✅ **frontend/dist/** directory is committed to Git  
✅ **Build script** available: `./docs/scripts/build-frontend.sh`  
✅ **.gitignore** configured correctly  
✅ **Ready for Choreo deployment**  

**To rebuild and commit:**
```bash
npm run build                    # Build frontend
git add frontend/dist            # Stage changes
git commit -m "Update frontend"  # Commit
git push origin main             # Push to GitHub
```

---

**Last Updated:** November 10, 2025  
**Status:** ✅ Configured for deployment

