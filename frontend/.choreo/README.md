# Choreo Frontend Component Configuration

This directory contains the Choreo platform configuration for the DevChoreo AI Assistant frontend component.

## Files

### component.yaml
Defines the Choreo component configuration including:
- **Implementation Type**: WebApplication (static frontend with nginx)
- **Build**: Dockerfile-based build
- **Endpoints**: Public web application on port 80
- **Dependencies**: Connects to `choreo-ai-backend` service
- **Environment Variables**: Runtime configuration

## Configuration Overview

### Build Configuration
- **Build Type**: Dockerfile
- **Context**: Current directory (frontend/)
- **Multi-stage build**: Node.js for build, nginx for serving

### Resources
- **Memory**: 256Mi-512Mi
- **CPU**: 250m-500m

### Endpoints
- **Name**: choreo-ai-frontend
- **Port**: 80 (nginx)
- **Base Path**: /
- **Visibility**: Public
- **Type**: WebApplication

### Dependencies
The frontend depends on the backend service:
- **Component**: choreo-ai-backend
- **Type**: REST connection
- **Usage**: API_URL is injected from backend's ServiceURL

## Environment Variables

### 1. API_URL (Required)
- **Source**: Connection reference to backend service
- **Injected From**: `choreo-ai-backend.ServiceURL`
- **Purpose**: Backend API base URL
- **Example**: `https://choreo-ai-backend-xxx.choreoapis.dev/`

### 2. ENVIRONMENT (Optional)
- **Type**: String
- **Default**: "production"
- **Purpose**: Environment identifier
- **Values**: development, staging, production

### 3. VERSION (Optional)
- **Type**: String
- **Default**: "1.0.0"
- **Purpose**: Application version

## Runtime Configuration

The frontend uses a dynamic configuration system:

1. **docker-entrypoint.sh** generates `/usr/share/nginx/html/config.js` at startup
2. Environment variables (API_URL, ENVIRONMENT, VERSION) are injected into config.js
3. Frontend loads config.js before React app starts
4. React app uses `getApiUrl()` to fetch the dynamic backend URL

## Deployment Steps

### 1. Deploy Backend First
```bash
# Deploy the backend service to get the ServiceURL
choreo deploy --component choreo-ai-backend
```

### 2. Create Connection
In Choreo dashboard:
- Go to Frontend component > Connections
- Add connection to `choreo-ai-backend`
- Connection name must match `dependsOn.name` in component.yaml

### 3. Deploy Frontend
```bash
choreo deploy --component choreo-ai-frontend
```

### 4. Verify Configuration
The API_URL will be automatically injected from the backend connection.

## Connection Configuration

The `dependsOn` section creates a connection to the backend:

```yaml
dependsOn:
  - name: choreo-ai-backend
    connectionConfig:
      type: REST
```

And the API_URL references this connection:

```yaml
- name: API_URL
  valueFrom:
    connectionRef:
      name: choreo-ai-backend  # Must match dependsOn.name
      key: ServiceURL          # Uses backend's service URL
```

## Troubleshooting

### Issue: API_URL not injected
**Check:**
- Backend service is deployed and running
- Connection to backend is created in Choreo dashboard
- Connection name matches `choreo-ai-backend`

### Issue: Frontend can't reach backend
**Check:**
- Backend endpoint is accessible (Public visibility)
- CORS is configured in backend to allow frontend origin
- API_URL has trailing slash if needed

### Issue: Build fails
**Check:**
- Dockerfile exists in frontend directory
- docker-entrypoint.sh exists and is executable
- public/config.js exists
- All npm dependencies are correct

## Testing Locally

To test the configuration locally:

```bash
# Build the image
docker build -t choreo-frontend .

# Run with environment variables
docker run -p 8080:80 \
  -e API_URL="https://your-backend.choreoapis.dev/" \
  -e ENVIRONMENT="staging" \
  -e VERSION="1.0.0" \
  choreo-frontend

# Access at http://localhost:8080
```

## Component Schema

This configuration uses Choreo schema version 1.2, which supports:
- ✅ WebApplication implementation type
- ✅ Connection references for environment variables
- ✅ Config forms for user-input variables
- ✅ Resource limits and requests
- ✅ Dependency declarations

## Notes

- The frontend is a **stateless** web application
- Configuration is injected at **runtime** (no rebuild needed)
- Backend URL is **dynamically** obtained from Choreo service mesh
- NGINX serves the built React app and proxies API requests (in dev only)
- In production, all API calls go directly to the backend ServiceURL

## References

- [Choreo Component Documentation](https://wso2.com/choreo/docs/)
- [WebApplication Implementation](https://wso2.com/choreo/docs/develop-components/develop-a-web-application/)
- Frontend Setup: `../docs/CHOREO_CONFIG_GUIDE.md`

