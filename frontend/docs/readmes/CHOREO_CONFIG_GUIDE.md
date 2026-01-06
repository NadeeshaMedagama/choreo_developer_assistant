# Choreo Deployment Configuration Guide

## Overview
This application is configured to work with Choreo platform deployment using runtime configuration injection.

## How It Works

### 1. Configuration Loading
- **File**: `public/config.js` contains the runtime configuration
- **Loaded**: Via `<script src="/config.js"></script>` in `index.html` before the app loads
- **Access**: Through `window.configs` object globally available

### 2. API URL Configuration
The frontend uses a dynamic API URL that can be configured at runtime:

```javascript
// In src/config.js
const apiUrl = window?.configs?.apiUrl ? window.configs.apiUrl : "/";
```

### 3. Docker Configuration
The `docker-entrypoint.sh` script generates `config.js` dynamically when the container starts:

```bash
# Set environment variable when running the container
docker run -e API_URL="https://your-backend.choreoapis.dev/api/" your-frontend-image
```

## Choreo Platform Setup

### Step 1: Deploy Backend Service
1. Deploy your backend service to Choreo
2. Note the backend service URL (e.g., `https://your-backend.choreoapis.dev/`)

### Step 2: Configure Frontend Environment
In Choreo, set the following environment variable for your frontend component:

**Environment Variable:**
```
API_URL=https://your-backend.choreoapis.dev/
```

### Step 3: Update nginx.conf (if needed for Choreo internal routing)
If using Choreo's internal service mesh, you might use service names:

```nginx
location /api/ {
    proxy_pass http://backend-service:9090;
}
```

## Local Development

### Option 1: Using Vite Dev Server (Recommended for Development)
```bash
cd frontend
npm install
npm run dev
```

The Vite proxy in `vite.config.js` will handle API routing:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### Option 2: Using Docker Compose
```bash
cd docker
docker-compose up
```

Access at: `http://localhost:8080`

## Production Deployment

### Building the Image
```bash
cd frontend
docker build -t choreo-frontend .
```

### Running with Custom API URL
```bash
docker run -p 8080:80 \
  -e API_URL="https://api.example.com/" \
  -e ENVIRONMENT="production" \
  -e VERSION="1.0.0" \
  choreo-frontend
```

## Configuration Files

### 1. `/frontend/public/config.js`
Template configuration file (overwritten at runtime):
```javascript
window.configs = {
  apiUrl: "/",
  environment: "development",
  version: "1.0.0"
};
```

### 2. `/frontend/src/config.js`
Utility functions to access configuration:
```javascript
import { getApiUrl } from './config';

// Use in fetch calls
const apiUrl = getApiUrl();
fetch(`${apiUrl}api/health`);
```

### 3. `/frontend/docker-entrypoint.sh`
Generates config.js from environment variables at container startup.

### 4. `/frontend/index.html`
Loads config.js before the React app:
```html
<script src="/config.js"></script>
```

## API Endpoints

All API calls in the application use the dynamic API URL:

- Health Check: `${apiUrl}api/health`
- Streaming Chat: `${apiUrl}api/ask/stream`
- Regular Chat: `${apiUrl}api/ask`

## Troubleshooting

### Issue: 404 on /config.js
**Solution**: Ensure `public/config.js` is copied to nginx html directory in Dockerfile

### Issue: API calls to wrong URL
**Solution**: Check the API_URL environment variable is set correctly

### Issue: CORS errors
**Solution**: Update backend CORS settings to allow the frontend origin

### Debug Configuration
Open browser console and check:
```javascript
console.log(window.configs);
// Should show: { apiUrl: "...", environment: "...", version: "..." }
```

## Example Choreo Configuration

### Frontend Component
```yaml
environment:
  - name: API_URL
    value: "https://choreo-ai-backend.choreoapis.dev/"
  - name: ENVIRONMENT
    value: "production"
  - name: VERSION
    value: "1.0.0"
```

### Backend Component
```yaml
environment:
  - name: PORT
    value: "9090"
  # ... other backend env vars
```

## Key Benefits

1. ✅ **No Rebuild Required**: Change API URL without rebuilding the image
2. ✅ **Environment Agnostic**: Same image works in dev, staging, prod
3. ✅ **Choreo Compatible**: Follows Choreo's runtime configuration pattern
4. ✅ **Type Safe**: Utility functions provide consistent API access
5. ✅ **Fallback Safe**: Defaults to relative URLs if config missing

## Files Modified for Choreo Support

- ✅ `frontend/index.html` - Added config.js script tag
- ✅ `frontend/public/config.js` - Created runtime config template
- ✅ `frontend/src/config.js` - Created config utility functions
- ✅ `frontend/src/App.jsx` - Updated all fetch calls to use dynamic URL
- ✅ `frontend/Dockerfile` - Added entrypoint script and public directory copy
- ✅ `frontend/docker-entrypoint.sh` - Created dynamic config generator

## Next Steps

1. Test locally with Docker:
   ```bash
   docker build -t choreo-frontend ./frontend
   docker run -p 8080:80 -e API_URL="http://localhost:8000/" choreo-frontend
   ```

2. Deploy to Choreo and set the API_URL environment variable

3. Verify config.js loads correctly in browser DevTools

4. Test API connectivity from frontend to backend

