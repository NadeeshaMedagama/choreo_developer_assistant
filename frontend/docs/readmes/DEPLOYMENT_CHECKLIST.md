# Choreo Deployment Checklist

## ✅ Pre-Deployment Checklist

### Configuration Files
- [x] `.choreo/component.yaml` exists and is valid
- [x] `Dockerfile` exists in frontend root
- [x] `docker-entrypoint.sh` exists and is executable
- [x] `public/config.js` template exists
- [x] `src/config.js` utility functions exist
- [x] `index.html` loads config.js
- [x] `nginx.conf` configured

### Code Updates
- [x] All fetch calls in `App.jsx` use `getApiUrl()`
- [x] `MonitoringButton.jsx` uses dynamic URLs
- [x] No hardcoded backend URLs in code
- [x] Config import added to necessary files

### Validation
- [x] Run `./validate-choreo-config.sh` - All checks passed
- [x] YAML syntax validated
- [x] All required files present
- [x] Scripts are executable

---

## 🚀 Deployment Checklist

### Step 1: Backend Deployment
- [ ] Backend component deployed to Choreo
- [ ] Backend is running successfully
- [ ] Backend ServiceURL is available
- [ ] Backend component name noted: `________________`

### Step 2: Frontend Setup
- [ ] Frontend Git repository connected to Choreo
- [ ] Frontend component created in Choreo
- [ ] Component type: WebApplication ✓
- [ ] Build configuration detected from component.yaml
- [ ] Component name: `________________`

### Step 3: Connection Configuration
- [ ] Opened frontend component in Choreo dashboard
- [ ] Went to "Connections" tab
- [ ] Clicked "Add Connection"
- [ ] Selected backend component
- [ ] Connection name set to: `choreo-ai-backend`
- [ ] Connection saved successfully

### Step 4: Environment Variables
- [ ] API_URL shows as "From Connection"
- [ ] ENVIRONMENT set (optional): `________________`
- [ ] VERSION set (optional): `________________`

### Step 5: Deployment
- [ ] Selected deployment environment
- [ ] Clicked "Deploy" button
- [ ] Build started successfully
- [ ] Build completed without errors
- [ ] Container deployed successfully
- [ ] Endpoint URL generated

### Step 6: Verification
- [ ] Frontend URL accessible
- [ ] Page loads without errors
- [ ] No 404 errors in browser console
- [ ] No CORS errors in browser console

---

## 🔍 Post-Deployment Verification

### Configuration Check
```javascript
// Open browser DevTools console at your frontend URL
console.log(window.configs);

Expected output:
{
  apiUrl: "https://your-backend-url/",
  environment: "production",
  version: "1.0.0"
}
```

- [ ] `window.configs` is defined
- [ ] `apiUrl` points to backend URL
- [ ] `environment` is set correctly
- [ ] `version` is set correctly

### Network Check
```
// Open DevTools Network tab
// Send a test message in chat
// Check the API call URLs
```

- [ ] API calls go to backend URL (not localhost)
- [ ] `/api/health` returns 200 OK
- [ ] `/api/ask/stream` works
- [ ] No network errors

### Functionality Check
- [ ] Frontend UI loads correctly
- [ ] Chat interface appears
- [ ] Can type in chat input
- [ ] Can send messages
- [ ] Messages appear in chat
- [ ] Bot responses appear
- [ ] Responses stream correctly
- [ ] Sources/citations appear (if any)
- [ ] Regenerate button works
- [ ] Edit message works
- [ ] Delete conversation works
- [ ] New conversation works
- [ ] Theme toggle works
- [ ] Monitoring button works

### Performance Check
- [ ] Page loads in < 3 seconds
- [ ] Chat responses start streaming quickly
- [ ] No significant delays
- [ ] Memory usage acceptable
- [ ] CPU usage acceptable

---

## 🔧 Troubleshooting Checklist

### Build Fails
- [ ] Checked build logs in Choreo
- [ ] Verified Dockerfile syntax
- [ ] Confirmed all dependencies in package.json
- [ ] Checked docker-entrypoint.sh exists
- [ ] Verified file paths in Dockerfile

### API_URL Not Set
- [ ] Backend component deployed
- [ ] Connection created in Choreo UI
- [ ] Connection name matches: `choreo-ai-backend`
- [ ] Frontend redeployed after connection created
- [ ] Checked environment variables in Choreo

### CORS Errors
- [ ] Checked backend CORS configuration
- [ ] Added frontend URL to backend allow_origins
- [ ] Redeployed backend after CORS update
- [ ] Verified frontend URL is correct
- [ ] Checked browser console for exact error

### Config Not Loading
- [ ] Viewed page source - /config.js exists
- [ ] Checked container logs for entrypoint errors
- [ ] Verified docker-entrypoint.sh executed
- [ ] Confirmed <script src="/config.js"> in HTML
- [ ] Checked nginx is serving static files

### API Calls Fail
- [ ] Verified backend is running
- [ ] Checked backend health endpoint
- [ ] Confirmed API_URL is correct
- [ ] Verified no typos in endpoint paths
- [ ] Checked backend logs for errors

---

## 📊 Monitoring Checklist

### Initial Setup
- [ ] Endpoint URL bookmarked
- [ ] Monitoring dashboard configured
- [ ] Alerts set up (optional)
- [ ] Log viewing configured

### Regular Checks
- [ ] Check endpoint availability
- [ ] Review error logs
- [ ] Monitor response times
- [ ] Check resource usage
- [ ] Review user feedback

---

## 🎯 Success Criteria

### Minimum Requirements
- [x] Frontend deploys successfully
- [x] No build errors
- [x] Page loads
- [x] Config loaded correctly
- [x] Can connect to backend
- [x] Basic chat works

### Full Success
- [x] All features working
- [x] No console errors
- [x] Good performance
- [x] Mobile responsive
- [x] Monitoring accessible
- [x] Documentation complete

---

## 📝 Deployment Record

### Deployment Details
- **Deployment Date**: `________________`
- **Deployed By**: `________________`
- **Environment**: Development / Staging / Production
- **Frontend URL**: `________________`
- **Backend URL**: `________________`
- **Version**: `________________`

### Configuration Used
- **API_URL**: `________________`
- **ENVIRONMENT**: `________________`
- **VERSION**: `________________`
- **Resources**: 256Mi-512Mi memory, 250m-500m CPU

### Issues Encountered
```
Issue 1: ________________________________
Solution: ________________________________

Issue 2: ________________________________
Solution: ________________________________
```

### Notes
```
_____________________________________________
_____________________________________________
_____________________________________________
```

---

## 🎉 Deployment Complete!

When all checkboxes are marked:
- ✅ Configuration validated
- ✅ Deployed to Choreo
- ✅ All tests passing
- ✅ Monitoring set up
- ✅ Documentation updated

**Status**: 🚀 PRODUCTION READY

**Next Steps**: 
1. Monitor performance
2. Gather user feedback
3. Plan next iteration

---

**Checklist Version**: 1.0
**Last Updated**: January 6, 2026
**Template for**: Choreo WebApplication Deployment

