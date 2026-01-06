# Choreo Deployment Guide - Frontend Component

## ✅ Component Configuration Complete

Your frontend component is now ready for Choreo deployment with the following configuration:

## Component Details

### Implementation Type
- **Type**: WebApplication
- **Server**: NGINX
- **Port**: 80
- **Visibility**: Public

### Build Configuration
- **Build Type**: Dockerfile
- **Context**: Frontend directory
- **Multi-stage**: Node.js build → NGINX serve
- **Cache**: BuildKit inline cache enabled

### Resource Allocation
| Resource | Request | Limit |
|----------|---------|-------|
| Memory   | 256Mi   | 512Mi |
| CPU      | 250m    | 500m  |

## Deployment Steps

### Step 1: Prepare Backend
Ensure the backend component is deployed first:

```bash
# In Choreo dashboard:
1. Go to Components
2. Find "choreo-ai-backend" (or your backend component name)
3. Verify it's deployed and has a ServiceURL
4. Note the component name (must match in frontend config)
```

### Step 2: Create Frontend Component
```bash
# In Choreo dashboard:
1. Click "Create" → "Component"
2. Select "Web Application"
3. Connect to your Git repository
4. Select the frontend directory
5. Component name: choreo-ai-frontend (or your choice)
6. Choreo will detect the .choreo/component.yaml file
```

### Step 3: Configure Connection
```bash
# In frontend component settings:
1. Go to "Connections" tab
2. Click "Add Connection"
3. Select your backend component
4. Connection name: "choreo-ai-backend" (must match component.yaml)
5. Save the connection
```

### Step 4: Review Environment Variables
The following variables will be auto-configured:

#### API_URL (Auto-injected)
- **Source**: Backend service connection
- **Value**: Automatically set from backend's ServiceURL
- **Example**: `https://choreo-ai-backend-xxx.choreoapis.dev/`

#### ENVIRONMENT (Optional - Configurable)
- **Default**: production
- **Options**: development, staging, production
- **Can edit in**: Deploy Configurations

#### VERSION (Optional - Configurable)
- **Default**: 1.0.0
- **Can edit in**: Deploy Configurations

### Step 5: Deploy
```bash
# In Choreo dashboard:
1. Go to "Deploy" tab
2. Click "Deploy" button
3. Select deployment environment (Development/Production)
4. Choreo will:
   - Build Docker image from Dockerfile
   - Inject API_URL from backend connection
   - Deploy to Choreo infrastructure
   - Assign public URL
```

### Step 6: Verify Deployment
```bash
# Check deployment status:
1. Wait for build to complete
2. Check "Logs" tab for any errors
3. Once deployed, click the endpoint URL
4. Open browser DevTools console
5. Check: console.log(window.configs)
6. Verify API_URL points to your backend
```

## Configuration Reference

### component.yaml Structure

```yaml
schemaVersion: 1.2
implementation: WebApplication

# Build from Dockerfile
build:
  buildType: dockerfile
  dockerfilePath: Dockerfile
  dockerContext: .

# Resource limits
resources:
  limits:
    memory: 512Mi
    cpu: 500m
  requests:
    memory: 256Mi
    cpu: 250m

# Public endpoint
endpoints:
  - name: choreo-ai-frontend
    service:
      basePath: /
      port: 80
    type: WebApplication
    networkVisibilities:
      - Public

# Backend dependency
dependsOn:
  - name: choreo-ai-backend
    connectionConfig:
      type: REST

# Environment variables
configurations:
  env:
    - name: API_URL
      valueFrom:
        connectionRef:
          name: choreo-ai-backend
          key: ServiceURL
```

## How Runtime Configuration Works

### Build Time
```
1. Choreo builds Docker image
2. Dockerfile copies docker-entrypoint.sh
3. Dockerfile sets ENTRYPOINT to run script
4. Image is stored in Choreo registry
```

### Deploy Time
```
1. Choreo creates container from image
2. Injects environment variables:
   - API_URL from backend connection
   - ENVIRONMENT from config form
   - VERSION from config form
3. Container starts
```

### Container Startup
```
1. docker-entrypoint.sh executes
2. Reads environment variables
3. Generates /usr/share/nginx/html/config.js:
   window.configs = {
     apiUrl: "${API_URL}",
     environment: "${ENVIRONMENT}",
     version: "${VERSION}"
   };
4. Starts nginx
```

### Browser Load
```
1. User requests https://frontend-url.choreoapis.dev/
2. NGINX serves index.html
3. Browser loads <script src="/config.js">
4. window.configs is available
5. React app loads (main.jsx)
6. App.jsx calls getApiUrl()
7. Returns API_URL from window.configs
8. All fetch calls use this dynamic URL
```

## Troubleshooting

### Issue 1: Build Fails

**Error**: "Dockerfile not found"
```bash
Solution:
- Verify Dockerfile exists in frontend directory
- Check component.yaml: dockerfilePath: Dockerfile
- Ensure dockerContext: . (current directory)
```

**Error**: "docker-entrypoint.sh: not found"
```bash
Solution:
- Verify docker-entrypoint.sh exists in frontend root
- Check it's executable: chmod +x docker-entrypoint.sh
- Ensure COPY docker-entrypoint.sh line in Dockerfile
```

**Error**: "npm ci failed"
```bash
Solution:
- Check package.json and package-lock.json are in sync
- Verify Node.js version in Dockerfile (node:18-alpine)
- Check for package installation errors in build logs
```

### Issue 2: Connection Not Working

**Error**: API_URL not injected
```bash
Solution:
1. Check backend component is deployed
2. Verify connection created in frontend component
3. Connection name must match: "choreo-ai-backend"
4. Redeploy frontend after creating connection
```

**Error**: API_URL is empty or undefined
```bash
Solution:
1. Check backend endpoint has ServiceURL
2. Verify backend is running (not stopped)
3. Check connection reference in component.yaml:
   - name must match connection name
   - key must be "ServiceURL"
```

### Issue 3: Frontend Can't Reach Backend

**Error**: CORS errors in browser
```bash
Solution:
1. Check backend app.py CORS configuration
2. Add frontend URL to allow_origins:
   app.add_middleware(
     CORSMiddleware,
     allow_origins=["https://frontend-url.choreoapis.dev"],
     ...
   )
3. Redeploy backend
```

**Error**: 404 on /api/health
```bash
Solution:
1. Verify API_URL in browser console
2. Check backend endpoints are accessible
3. Test: curl https://backend-url/api/health
4. Verify backend is running
```

### Issue 4: Configuration Not Loading

**Error**: window.configs is undefined
```bash
Solution:
1. Check config.js loads: View source → /config.js
2. Verify docker-entrypoint.sh executed
3. Check container logs for entrypoint errors
4. Ensure <script src="/config.js"> in index.html
```

**Error**: API calls go to wrong URL
```bash
Solution:
1. Check window.configs.apiUrl value
2. Verify API_URL environment variable set
3. Check all fetch calls use getApiUrl()
4. Look for hardcoded URLs in code
```

## Verification Checklist

Before deployment:
- [ ] Dockerfile exists in frontend root
- [ ] docker-entrypoint.sh exists in frontend root
- [ ] docker-entrypoint.sh is executable
- [ ] public/config.js template exists
- [ ] index.html loads config.js
- [ ] All fetch calls use getApiUrl()
- [ ] component.yaml is valid YAML
- [ ] Backend component name matches in component.yaml

After deployment:
- [ ] Build completed successfully
- [ ] Container is running
- [ ] Endpoint URL is accessible
- [ ] window.configs loaded in browser
- [ ] API_URL points to backend
- [ ] Health check works
- [ ] Chat functionality works
- [ ] No CORS errors

## Advanced Configuration

### Custom Environment Variables

Add more variables in component.yaml:

```yaml
configurations:
  env:
    - name: CUSTOM_VAR
      valueFrom:
        configForm:
          displayName: Custom Variable
          required: false
          type: string
          default: "value"
```

Then update docker-entrypoint.sh:

```bash
CUSTOM_VAR="${CUSTOM_VAR:-default}"
cat > /usr/share/nginx/html/config.js <<EOF
window.configs = {
  apiUrl: "${API_URL}",
  customVar: "${CUSTOM_VAR}",
  ...
};
EOF
```

### Multiple Environments

Deploy to different environments:

```bash
Development Environment:
- Smaller resources (128Mi memory)
- DEBUG mode enabled
- Shorter cache times

Production Environment:
- Full resources (512Mi memory)
- Optimized caching
- CDN enabled
```

### Scaling

Adjust in component.yaml:

```yaml
resources:
  limits:
    memory: 1Gi      # Increase for high traffic
    cpu: 1000m
  requests:
    memory: 512Mi
    cpu: 500m
```

## Monitoring

### Health Check
Frontend doesn't need health check (static content), but you can monitor:
- Endpoint availability
- Response times
- Error rates

### Logs
View container logs in Choreo dashboard:
```bash
# NGINX access logs
# NGINX error logs
# docker-entrypoint.sh execution logs
```

### Metrics
Monitor in Choreo observability:
- Request rate
- Error rate
- Response time
- Memory usage
- CPU usage

## Best Practices

1. **Always deploy backend first** before frontend
2. **Use connection references** for API_URL (don't hardcode)
3. **Keep resources modest** for static content (256Mi-512Mi)
4. **Enable BuildKit cache** for faster builds
5. **Test locally first** with Docker before Choreo deployment
6. **Verify config.js generation** in local Docker container
7. **Check browser console** for config after deployment
8. **Monitor CORS** settings when URLs change

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
   - Add custom domain in Choreo
   - Configure DNS
   - SSL automatically provisioned

2. **Configure monitoring** (optional)
   - Set up alerts for downtime
   - Monitor error rates
   - Track performance metrics

3. **Set up CI/CD** (optional)
   - Auto-deploy on Git push
   - Run tests before deployment
   - Automated rollbacks

4. **Scale if needed**
   - Increase resources
   - Add replicas
   - Configure load balancing

---

**Your frontend component is ready for Choreo deployment!** 🚀

Follow the deployment steps above to get your DevChoreo AI Assistant frontend live on Choreo.

