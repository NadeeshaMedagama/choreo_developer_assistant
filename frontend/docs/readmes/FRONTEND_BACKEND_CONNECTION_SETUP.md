# Frontend-Backend Connection Configuration

## ✅ Implementation Complete

This document describes the implementation of Choreo-compatible runtime configuration for the DevChoreo AI Assistant.

## 🎯 What Was Implemented

### 1. Runtime Configuration System
- **Purpose**: Allow API URL to be configured at deployment time without rebuilding
- **Method**: JavaScript configuration file loaded before React app starts

### 2. Files Created/Modified

#### ✅ Created Files
1. **`frontend/public/config.js`**
   - Template configuration file
   - Sets `window.configs` with default values
   - Overwritten at runtime by docker-entrypoint.sh

2. **`frontend/src/config.js`**
   - Utility functions to access configuration
   - `getApiUrl()` - Returns API base URL
   - `getApiEndpoint(endpoint)` - Builds full endpoint URLs
   - Type-safe configuration access

3. **`frontend/docker-entrypoint.sh`**
   - Shell script that runs when container starts
   - Generates `config.js` from environment variables
   - Supports `API_URL`, `ENVIRONMENT`, `VERSION` env vars

4. **`docs/CHOREO_CONFIG_GUIDE.md`**
   - Complete documentation for Choreo deployment
   - Troubleshooting guide
   - Configuration examples

#### ✅ Modified Files
1. **`frontend/index.html`**
   - Added `<script src="/config.js"></script>` before app loads
   - Ensures config is available to React app

2. **`frontend/Dockerfile`**
   - Copies `public/` directory to nginx
   - Adds `docker-entrypoint.sh` as entrypoint
   - Generates config.js dynamically on startup

3. **`frontend/src/App.jsx`**
   - Imported `getApiUrl` from `./config`
   - Updated ALL 7 fetch calls to use dynamic API URL:
     - Line ~119: Health check
     - Line ~262: Main streaming chat
     - Line ~356: Fallback chat
     - Line ~433: Regenerate streaming
     - Line ~524: Regenerate fallback
     - Line ~606: Edit message streaming
     - Line ~680: Edit message fallback

4. **`frontend/src/components/MonitoringButton.jsx`**
   - Imported `getApiUrl` from `../config`
   - Updated metrics and health endpoints to use dynamic URL
   - Maintained localhost URLs for Grafana/Prometheus (dev tools)

## 🔧 How It Works

### Step-by-Step Flow

```
1. Container Starts
   ↓
2. docker-entrypoint.sh runs
   ↓
3. Reads API_URL environment variable
   ↓
4. Generates /usr/share/nginx/html/config.js
   ↓
5. Starts nginx
   ↓
6. Browser loads index.html
   ↓
7. <script src="/config.js"> loads configuration
   ↓
8. window.configs is available globally
   ↓
9. React app starts (main.jsx)
   ↓
10. App.jsx imports getApiUrl()
    ↓
11. All fetch calls use dynamic API URL
```

## 🚀 Usage Examples

### Local Development
```bash
# No config needed - uses Vite proxy
cd frontend
npm run dev
# API calls proxied to http://localhost:8000
```

### Docker Local Testing
```bash
# Build frontend
cd frontend
docker build -t choreo-frontend .

# Run with custom API URL
docker run -p 8080:80 \
  -e API_URL="http://localhost:8000/" \
  choreo-frontend

# Open browser
open http://localhost:8080
```

### Choreo Deployment

#### Frontend Component Configuration
```yaml
# In Choreo dashboard - Frontend Component
environment:
  - name: API_URL
    value: "https://your-backend-service.choreoapis.dev/"
  - name: ENVIRONMENT
    value: "production"
  - name: VERSION
    value: "1.0.0"
```

#### Backend Component Configuration
```yaml
# In Choreo dashboard - Backend Component
environment:
  - name: PORT
    value: "9090"
  - name: AZURE_OPENAI_KEY
    value: "xxx"
  # ... other backend env vars
```

## 🔍 Verification

### Check Config Loaded Correctly
Open browser DevTools console:
```javascript
// Check if config is loaded
console.log(window.configs);
// Expected output:
// {
//   apiUrl: "https://your-backend.choreoapis.dev/",
//   environment: "production",
//   version: "1.0.0"
// }
```

### Check API Calls
In Network tab, verify fetch requests go to correct URL:
- ✅ `https://your-backend.choreoapis.dev/api/health`
- ✅ `https://your-backend.choreoapis.dev/api/ask/stream`
- ❌ NOT `http://localhost:8000/api/health`

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Build frontend Docker image
- [ ] Test locally with different API_URL values
- [ ] Verify config.js generation works
- [ ] Check all API endpoints use dynamic URL

### Choreo Deployment
- [ ] Deploy backend service first
- [ ] Note backend service URL
- [ ] Deploy frontend service
- [ ] Set API_URL environment variable
- [ ] Verify frontend can reach backend
- [ ] Test health check endpoint
- [ ] Test chat functionality

### Post-Deployment
- [ ] Check browser console for config
- [ ] Verify API calls in Network tab
- [ ] Test all features (chat, regenerate, edit)
- [ ] Check monitoring endpoints work

## 🛠️ Troubleshooting

### Problem: Config not loading (window.configs is undefined)
**Solution**: 
- Check if `/config.js` is accessible in browser
- Verify public directory copied in Dockerfile
- Check nginx is serving static files correctly

### Problem: API calls still going to localhost
**Solution**:
- Verify API_URL environment variable is set
- Check docker-entrypoint.sh executed successfully
- View generated config.js: `docker exec <container> cat /usr/share/nginx/html/config.js`

### Problem: CORS errors in browser
**Solution**:
- Update backend CORS settings in `backend/app.py`
- Add frontend URL to `allow_origins` list
- Ensure credentials and headers are allowed

### Problem: 404 on API endpoints
**Solution**:
- Check backend is running and accessible
- Verify API_URL includes trailing slash if needed
- Test backend health: `curl https://backend-url/api/health`

## 🎨 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_URL` | No | `/` | Backend API base URL |
| `ENVIRONMENT` | No | `production` | Environment name |
| `VERSION` | No | `1.0.0` | App version |

### Example Configurations

#### Development (Local)
```bash
API_URL="http://localhost:8000/"
ENVIRONMENT="development"
VERSION="dev"
```

#### Staging
```bash
API_URL="https://staging-backend.choreoapis.dev/"
ENVIRONMENT="staging"
VERSION="1.0.0-rc1"
```

#### Production
```bash
API_URL="https://backend.choreoapis.dev/"
ENVIRONMENT="production"
VERSION="1.0.0"
```

## 📝 Code Snippets

### Using Config in New Components
```javascript
import { getApiUrl } from './config';

function MyComponent() {
  const fetchData = async () => {
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}api/my-endpoint`);
    // ... handle response
  };
}
```

### Using getApiEndpoint Helper
```javascript
import { getApiEndpoint } from './config';

// Automatically handles URL formatting
const url = getApiEndpoint('/api/health');
// Returns: "https://backend.com/api/health" or "/api/health"
```

## ✨ Benefits

1. **No Rebuild Required**: Change API URL without rebuilding Docker image
2. **Environment Agnostic**: Same image works in dev, staging, production
3. **Choreo Compatible**: Follows Choreo's runtime configuration best practices
4. **Developer Friendly**: Clear utilities for accessing config
5. **Type Safe**: Centralized config access with fallbacks
6. **Zero Downtime**: Update config with container restart only

## 🎉 Summary

The frontend-backend connection is now fully configurable for Choreo deployment:

- ✅ Runtime configuration system implemented
- ✅ All 7 fetch calls updated to use dynamic URL
- ✅ Docker entrypoint generates config from env vars
- ✅ Monitoring button uses dynamic URLs
- ✅ Documentation complete
- ✅ Ready for Choreo deployment

**Next Step**: Deploy to Choreo and set the `API_URL` environment variable!

