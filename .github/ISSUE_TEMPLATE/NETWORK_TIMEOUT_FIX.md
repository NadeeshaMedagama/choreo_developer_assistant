# 🔧 GitHub Actions Network Timeout Fix

## 🐛 Problem

GitHub Actions failing with network timeout errors:

```
Error: fatal: unable to access 'https://github.com/NadeeshaMedagama/choreo_developer_assistant/': 
Failed to connect to github.com port 443 after 135841 ms: Couldn't connect to server
The process '/usr/bin/git' failed with exit code 128
```

**Root Cause**: GitHub Actions runners experiencing network connectivity issues when trying to checkout the repository.

---

## ✅ Solutions Implemented

### 1. **Added Timeout Controls**

Added job-level and step-level timeouts to fail faster instead of waiting indefinitely:

```yaml
jobs:
  backend-test:
    timeout-minutes: 30  # Job-level timeout
    steps:
      - name: Checkout code
        timeout-minutes: 10  # Step-level timeout
```

**Benefits**:
- ⏱️ Fails after 10 minutes instead of 135+ seconds per retry
- 🔄 Allows GitHub Actions to retry or assign a different runner
- 💰 Saves CI/CD minutes

### 2. **Optimized Checkout Settings**

Added efficient checkout configuration:

```yaml
- name: Checkout code
  uses: actions/checkout@v4
  timeout-minutes: 10
  with:
    fetch-depth: 1              # Shallow clone (faster)
    persist-credentials: false  # Don't store credentials
  env:
    GIT_TERMINAL_PROMPT: 0     # Non-interactive mode
```

**Benefits**:
- 📦 Smaller download size (shallow clone)
- 🔒 Better security (no credential persistence)
- 🚫 No interactive prompts hanging

### 3. **Job Timeouts Added**

| Job | Timeout | Reason |
|-----|---------|--------|
| backend-test | 30 min | Tests should complete quickly |
| frontend-test | 30 min | Build and tests |
| docker-build | 60 min | Docker builds can be slow |
| security-scan | 30 min | Scanning time |
| deploy-choreo | 20 min | Deployment steps |

---

## 🚀 Alternative Solutions

If the problem persists, try these alternatives:

### Option 1: Use GitHub-Hosted Runners in Different Regions

Modify workflow to use different runner types:

```yaml
jobs:
  backend-test:
    runs-on: ubuntu-latest
    # OR try:
    # runs-on: ubuntu-22.04
    # runs-on: ubuntu-20.04
```

### Option 2: Add Network Diagnostics

Add before checkout to diagnose issues:

```yaml
- name: Network diagnostics
  run: |
    echo "🌐 Testing network connectivity..."
    ping -c 3 github.com || echo "Cannot ping github.com"
    curl -I https://github.com || echo "Cannot reach github.com via HTTPS"
    nslookup github.com || echo "DNS resolution failed"
```

### Option 3: Use Actions Retry

Install retry action wrapper:

```yaml
- name: Checkout code with retry
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      git clone --depth=1 https://github.com/${{ github.repository }} .
```

### Option 4: Mirror Repository

If network issues are persistent, set up a repository mirror:

```yaml
- name: Checkout from mirror
  run: |
    git clone --depth=1 \
      https://your-mirror-url.com/repo.git .
```

### Option 5: Use Self-Hosted Runners

For enterprise setups with network restrictions:

```yaml
jobs:
  backend-test:
    runs-on: self-hosted  # Use your own infrastructure
```

---

## 🔍 Troubleshooting Guide

### Check GitHub Status

1. Visit: https://www.githubstatus.com/
2. Check if there are any ongoing incidents affecting:
   - Git Operations
   - API Requests
   - Actions

### Check Workflow Logs

1. Go to **Actions** tab in your repository
2. Click on the failed workflow run
3. Expand the "Checkout code" step
4. Look for specific error patterns:

**Pattern 1: Connection Timeout**
```
Failed to connect to github.com port 443 after XXXXX ms
```
**Solution**: Network issue, retry or wait

**Pattern 2: DNS Resolution**
```
Could not resolve host: github.com
```
**Solution**: DNS issue on runner, retry

**Pattern 3: SSL/TLS Error**
```
SSL certificate problem
```
**Solution**: Clock skew or certificate issue

### Manual Retry

If a run fails:
1. Click **Re-run failed jobs** in GitHub Actions UI
2. OR push an empty commit:
   ```bash
   git commit --allow-empty -m "Retry CI/CD pipeline"
   git push
   ```

---

## 📊 Expected Behavior After Fix

### ✅ Success Case:

```
✓ Checkout code (completed in 5s)
✓ Set up Python
✓ Install dependencies
✓ Run tests
✓ Build Docker image
```

### ⏱️ Timeout Case (Better):

```
✗ Checkout code (failed after 10m timeout)
→ Job cancelled after 10 minutes
→ GitHub Actions will retry or you can manually retry
```

### ❌ Before Fix (Worse):

```
✗ Checkout code (hangs for 135+ seconds per attempt)
✗ Retries 3 times (taking 6+ minutes total)
✗ Eventually fails with no useful feedback
```

---

## 🧪 Testing the Fix

### Test 1: Push a Small Change

```bash
git add .
git commit -m "test: Verify network timeout fix"
git push origin main
```

Watch the Actions tab - checkout should complete in <1 minute or timeout in exactly 10 minutes.

### Test 2: Check Timeout Behavior

If checkout hangs:
- Old behavior: Would hang for 135+ seconds × 3 retries
- New behavior: Fails after exactly 10 minutes

### Test 3: Verify All Jobs

Ensure all jobs respect their timeouts:
- Backend tests: Max 30 min
- Frontend tests: Max 30 min
- Docker build: Max 60 min

---

## 📝 Configuration Summary

### What Changed:

| Component | Before | After |
|-----------|--------|-------|
| Job timeout | None (6 hours default) | 30-60 minutes |
| Checkout timeout | None | 10 minutes |
| Fetch depth | Full history | Shallow (depth=1) |
| Credentials | Persisted | Not persisted |
| Interactive mode | Enabled | Disabled |

### Files Modified:

- ✅ `.github/workflows/ci-cd.yml` - Added timeouts and optimizations
- ✅ `.github/NETWORK_TIMEOUT_FIX.md` - This documentation
- ✅ `.github/ISSUE_TEMPLATE/DOCKER_FIX_SUMMARY.md` - Updated with network fix notes

---

## 🆘 If Problem Persists

### Step 1: Verify GitHub Status
Check https://www.githubstatus.com/ for ongoing incidents

### Step 2: Try Different Times
Network issues can be time-dependent. Try:
- Different time of day
- Different day of week
- Wait 1-2 hours and retry

### Step 3: Check Repository Settings
1. Go to **Settings** → **Actions** → **General**
2. Verify "Actions permissions" are enabled
3. Check "Workflow permissions" are set correctly

### Step 4: Contact GitHub Support
If issue persists for >24 hours:
1. Collect workflow run URLs
2. Note timestamps of failures
3. Contact GitHub Support with details

### Step 5: Emergency Workaround
Temporarily disable CI/CD and deploy manually:
1. Build locally: `docker build -t choreo-ai-assistant .`
2. Push to container registry manually
3. Deploy to Choreo from registry

---

## 📈 Monitoring

After implementing the fix, monitor for 1-2 weeks:

### Success Metrics:
- ✅ Checkout completes in <1 minute
- ✅ Jobs complete within timeout windows
- ✅ No more 135-second hangs
- ✅ Reduced CI/CD costs (less hanging time)

### Warning Signs:
- ⚠️ Frequent timeouts at exactly 10 minutes
- ⚠️ Multiple retries needed
- ⚠️ Consistent failures at specific times

If you see warning signs, consider:
- Using self-hosted runners
- Setting up repository mirrors
- Contacting GitHub Support

---

## 🎯 Quick Reference

### To retry a failed workflow:
```bash
# Option 1: Via GitHub UI
Actions → Failed Run → Re-run failed jobs

# Option 2: Empty commit
git commit --allow-empty -m "retry: CI/CD pipeline"
git push
```

### To check if fix is working:
```bash
# Look at recent workflow runs
gh run list --limit 5

# View specific run logs
gh run view <run-id> --log
```

### To test network before push:
```bash
# Check GitHub connectivity
curl -I https://github.com
ping -c 3 github.com

# Check repo access
git ls-remote https://github.com/$USER/$REPO
```

---

## ✅ Checklist

Completed fixes:
- [x] ✅ Added job-level timeouts (30-60 min)
- [x] ✅ Added step-level timeouts (10 min for checkout)
- [x] ✅ Optimized checkout (shallow clone)
- [x] ✅ Disabled credential persistence
- [x] ✅ Added non-interactive mode
- [x] ✅ Updated all jobs (5 jobs total)
- [x] ✅ Created documentation

Next steps:
- [ ] 🔲 Push changes to GitHub
- [ ] 🔲 Monitor first workflow run
- [ ] 🔲 Verify checkout completes quickly
- [ ] 🔲 Check all jobs respect timeouts
- [ ] 🔲 Update team on changes

---

**Last Updated**: December 19, 2024  
**Author**: GitHub Copilot  
**Status**: Ready for testing 🚀

**Related Documentation**:
- `.github/DOCKER_BUILD_FIX.md` - Docker build fixes
- `.github/QUICK_REFERENCE.md` - Quick start guide
- `.github/workflows/ci-cd.yml` - Main workflow file

