# Choreo Deployment Fix - Port Binding Issue

## Problem
The application was getting "Upstream connection timeout" (error 102504) because it was binding to a hardcoded port instead of using Choreo's `PORT` environment variable.

## Solution Applied

### 1. Created Startup Scripts
- **`start.py`** (Python-based, recommended): Reads `PORT` environment variable and starts uvicorn
- **`start.sh`** (Bash-based, alternative): Shell script version

### 2. Updated Dockerfile
The main `Dockerfile` now:
- Uses `start.py` to launch the application
- Binds to `0.0.0.0:${PORT}` instead of hardcoded `0.0.0.0:9090`
- Makes the application compatible with Choreo's dynamic port assignment

### 3. Created Choreo Configuration
- **`.choreo/component.yaml`**: Tells Choreo how to deploy the service

## Key Changes

### Before (Incorrect):
```dockerfile
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
```

### After (Correct):
```dockerfile
CMD ["python3", "/app/start.py"]
```

Where `start.py` reads the `PORT` environment variable:
```python
port = os.environ.get('PORT', '9090')
cmd = ['uvicorn', 'backend.app:app', '--host', '0.0.0.0', '--port', port]
```

## How It Works

1. **Choreo sets PORT**: When deployed, Choreo injects a `PORT` environment variable
2. **start.py reads PORT**: The startup script reads this variable
3. **Binds to 0.0.0.0:PORT**: uvicorn starts on the correct host and port
4. **Choreo routes traffic**: Choreo can now successfully route traffic to your service

## Deployment Steps

### 1. Commit Changes
```bash
git add .
git commit -m "Fix: Use PORT env variable for Choreo deployment"
git push
```

### 2. Deploy to Choreo
- Go to your Choreo console
- Trigger a new deployment or redeploy
- The service should now start successfully on Choreo's assigned port

### 3. Verify Deployment
Check the following:
- ✅ Container starts without errors
- ✅ Health check passes (`/api/health`)
- ✅ No more "upstream connection timeout" errors
- ✅ Application is accessible through Choreo's endpoint

## Testing Locally

To test the PORT environment variable locally:

```bash
# Test with default port (9090)
python3 start.py

# Test with custom port
PORT=8080 python3 start.py

# Test with Docker
docker build -t choreo-ai-assistant .
docker run -e PORT=8080 -p 8080:8080 choreo-ai-assistant
```

## Important Notes

1. **Host Binding**: Always bind to `0.0.0.0` (not `localhost` or `127.0.0.1`)
   - `0.0.0.0` allows external connections
   - `localhost` only allows connections from within the container

2. **Port Environment Variable**: Use `${PORT}` environment variable
   - Choreo dynamically assigns ports
   - Hardcoded ports will fail in Choreo

3. **Health Checks**: Ensure health check endpoint works
   - Path: `/api/health`
   - Must respond within timeout (30s)
   - Should return 200 OK

4. **Startup Time**: The application has a 90s startup period
   - Services are initialized lazily
   - Health checks only start after 90s

## Troubleshooting

### Issue: Still getting timeout errors
**Solution**: Check Choreo logs to verify:
1. PORT environment variable is set
2. Application is starting on correct port
3. Health check is passing

### Issue: Health check fails
**Solution**: 
1. Increase `start-period` in Dockerfile if initialization takes longer
2. Check `/api/health` endpoint is working
3. Verify services initialize properly

### Issue: Application crashes on startup
**Solution**: Check logs for:
1. Missing environment variables (Milvus, Azure OpenAI, etc.)
2. Permission issues
3. Dependency errors

## Environment Variables Required for Choreo

Make sure these are configured in Choreo:
- `MILVUS_URI`
- `MILVUS_TOKEN`
- `MILVUS_COLLECTION_NAME`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `GITHUB_TOKEN` (optional)

## Files Changed
- ✅ `Dockerfile` - Updated CMD to use start.py
- ✅ `start.py` - New Python startup script
- ✅ `start.sh` - New Bash startup script (alternative)
- ✅ `.choreo/component.yaml` - Choreo configuration
- ✅ `CHOREO_DEPLOYMENT_FIX.md` - This documentation

## Success Criteria
✅ Application binds to `0.0.0.0:${PORT}`
✅ Port is read from environment variable
✅ No hardcoded ports in CMD
✅ Health check passes
✅ No upstream timeout errors
✅ Application accessible via Choreo endpoint

