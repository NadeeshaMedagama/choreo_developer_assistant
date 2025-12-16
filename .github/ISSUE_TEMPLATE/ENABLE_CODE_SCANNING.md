# 🔐 GitHub Code Scanning Setup Required

## ⚠️ Issue Detected

**Error Message:**
```
Warning: Code scanning is not enabled for this repository.
Please enable code scanning in the repository settings.
Error: Please verify that the necessary features are enabled
```

**What Happened:**
The CodeQL security workflow ran successfully and scanned your code, but it couldn't upload the results because Code Scanning is not enabled in your repository settings.

---

## ✅ Solution: Enable Code Scanning

### Option 1: Enable via GitHub UI (Recommended - 2 Minutes)

#### Step-by-Step Instructions:

1. **Go to your repository:**
   ```
   https://github.com/NadeeshaMedagama/choreo_ai_assistant
   ```

2. **Click on "Settings" tab** (top right)

3. **Navigate to Security Settings:**
   - In the left sidebar, scroll down to **"Code security and analysis"**
   - Click on it

4. **Enable Required Features:**

   **✅ Dependency graph**
   - Click **"Enable"** if not already enabled
   - (Usually enabled by default for public repos)

   **✅ Dependabot alerts**
   - Click **"Enable"**
   - Alerts you about vulnerable dependencies

   **✅ Dependabot security updates**
   - Click **"Enable"**
   - Automatically creates PRs to fix vulnerabilities

   **✅ Code scanning** ← **MOST IMPORTANT**
   - Click **"Set up"** or **"Enable"**
   - Select **"Default"** setup
   - Or choose **"Advanced"** if you want to customize
   - Click **"Enable CodeQL"**

   **✅ Secret scanning**
   - Click **"Enable"**
   - Detects accidentally committed secrets

5. **Verify Setup:**
   - All features should show "Enabled" with green checkmarks
   - You should see the Security tab become active

---

### Option 2: Enable via GitHub API (Advanced)

If you prefer automation:

```bash
# Using GitHub CLI (gh)
gh api -X PATCH /repos/NadeeshaMedagama/choreo_ai_assistant \
  -f security_and_analysis[advanced_security][status]=enabled \
  -f security_and_analysis[secret_scanning][status]=enabled

# Or using curl with a Personal Access Token
curl -X PATCH \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/NadeeshaMedagama/choreo_ai_assistant \
  -d '{
    "security_and_analysis": {
      "advanced_security": {"status": "enabled"},
      "secret_scanning": {"status": "enabled"}
    }
  }'
```

---

## 📋 Complete Security Setup Checklist

Once you're in **Settings → Code security and analysis**, enable all these:

### Essential Features

- [ ] ✅ **Dependency graph** → Track dependencies
- [ ] ✅ **Dependabot alerts** → Get notified of vulnerabilities
- [ ] ✅ **Dependabot security updates** → Auto-fix vulnerabilities
- [ ] ✅ **Code scanning (CodeQL)** → Find security issues in code
- [ ] ✅ **Secret scanning** → Detect committed secrets

### Optional but Recommended

- [ ] 🔐 **Push protection** → Block secrets from being pushed
- [ ] 📊 **Dependency review** → Review dependency changes in PRs

---

## 🎯 After Enabling Code Scanning

### What Will Happen Automatically:

1. **CodeQL Analysis Runs:**
   - On every push to main/develop
   - On every pull request
   - Daily scheduled scan at 6 AM UTC

2. **Results Upload:**
   - Security findings appear in the **Security** tab
   - Alerts categorized by severity (Critical, High, Medium, Low)
   - Detailed explanations and fix suggestions

3. **PR Checks:**
   - Code scanning results shown on pull requests
   - Blocks merge if critical issues found (optional)

4. **Notifications:**
   - Email alerts for new security issues
   - GitHub notifications for vulnerabilities

---

## 🔍 Verify Everything Works

### Step 1: Enable Features (2 minutes)
Follow the instructions above to enable Code Scanning

### Step 2: Trigger a Workflow
```bash
# Option 1: Make any commit
git commit --allow-empty -m "test: trigger code scanning"
git push origin main

# Option 2: Manually trigger from GitHub UI
# Go to Actions → Security Analysis → Run workflow
```

### Step 3: Check Results

**After ~2-3 minutes:**

1. **Go to Security Tab:**
   ```
   https://github.com/NadeeshaMedagama/choreo_ai_assistant/security
   ```

2. **Look for:**
   - ✅ Code scanning alerts section
   - ✅ Dependabot alerts section
   - ✅ Secret scanning alerts section

3. **Check Actions Tab:**
   ```
   https://github.com/NadeeshaMedagama/choreo_ai_assistant/actions
   ```
   - ✅ CodeQL workflow should complete successfully
   - ✅ No more "Code scanning not enabled" errors

---

## ⚡ Quick Visual Guide

### Before (Current State)
```
Settings → Code security and analysis

❌ Code scanning: Not enabled
⚠️  Secret scanning: Not enabled
⚠️  Dependabot: Partially enabled
```

### After (Target State)
```
Settings → Code security and analysis

✅ Dependency graph: Enabled
✅ Dependabot alerts: Enabled
✅ Dependabot security updates: Enabled
✅ Code scanning: Enabled (CodeQL)
✅ Secret scanning: Enabled
```

---

## 🎓 What Each Feature Does

### 1. Code Scanning (CodeQL)
**What it does:**
- Analyzes your code for security vulnerabilities
- Finds common coding mistakes
- Detects potential security flaws
- Supports Python, JavaScript, and more

**When it runs:**
- Every push to main/develop
- Every pull request
- Daily at 6 AM UTC

**Example findings:**
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Hardcoded credentials
- Insecure cryptography

### 2. Secret Scanning
**What it does:**
- Detects accidentally committed secrets
- Finds API keys, passwords, tokens
- Alerts you before they're exploited

**Example detections:**
- AWS access keys
- GitHub personal access tokens
- Database passwords
- Private keys

### 3. Dependabot Alerts
**What it does:**
- Monitors your dependencies
- Alerts about known vulnerabilities
- Can automatically create PRs to update

**Example alerts:**
- npm packages with CVEs
- Python packages with security issues
- Outdated dependencies with fixes available

---

## 🐛 Troubleshooting

### Issue: "Enable" button is grayed out

**Cause:** You might not have admin permissions on the repository

**Solution:**
- Ask the repository owner to enable these features
- Or request admin access to the repository

### Issue: "This feature requires GitHub Advanced Security"

**Cause:** Your repository might be private and on a plan without Advanced Security

**Solutions:**
1. Make the repository public (free features)
2. Upgrade to GitHub Enterprise plan
3. Request Advanced Security from your organization admin

### Issue: Code scanning still fails after enabling

**Wait 2-3 minutes** then:
1. Go to Actions tab
2. Find the failed workflow
3. Click "Re-run all jobs"
4. Should succeed now

---

## 📊 Expected Workflow After Fix

### Current Workflow (Failing)
```
Run CodeQL Analysis
  ✓ Scan code (successful)
  ✓ Generate SARIF file (successful)
  ❌ Upload results (FAILED - not enabled)
```

### Fixed Workflow (After Enabling)
```
Run CodeQL Analysis
  ✓ Scan code (successful)
  ✓ Generate SARIF file (successful)
  ✓ Upload results (successful)
  ✓ Display in Security tab
  ✓ Check PR for issues
```

---

## ✅ Action Items

### Do This Right Now (5 minutes):

1. ✅ **Go to repository settings**
   ```
   https://github.com/NadeeshaMedagama/choreo_ai_assistant/settings/security_analysis
   ```

2. ✅ **Enable these features:**
   - Dependency graph
   - Dependabot alerts
   - Dependabot security updates
   - **Code scanning (CodeQL)** ← Most important
   - Secret scanning

3. ✅ **Wait for next workflow run** or trigger manually:
   ```bash
   git commit --allow-empty -m "test: verify code scanning"
   git push origin main
   ```

4. ✅ **Verify in Security tab:**
   - Check that CodeQL results appear
   - Review any security findings
   - Enable notifications for alerts

---

## 🎉 Benefits After Enabling

### Security Improvements
- 🔐 Automatic vulnerability detection
- 🚨 Real-time security alerts
- 🛡️ Protection against common attacks
- 📊 Security dashboard in GitHub

### Developer Experience
- ✅ PR checks for security issues
- 🤖 Automated dependency updates
- 📧 Email notifications for vulnerabilities
- 🎯 Clear fix recommendations

### Compliance
- 📋 Security audit trail
- 📈 Compliance reporting
- 🏆 Security best practices enforced
- ✅ Industry-standard security scanning

---

## 📚 Documentation Links

- [Enabling Code Scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning-for-a-repository)
- [About CodeQL](https://codeql.github.com/docs/)
- [SARIF Support](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

## 🎯 Summary

**Problem:** Code scanning not enabled in repository  
**Solution:** Enable via Settings → Code security and analysis  
**Time Required:** 2-5 minutes  
**Difficulty:** Easy (just click Enable buttons)  
**Impact:** Major security improvement  

---

## ✨ Next Steps

1. **Enable the features now** (2 minutes)
2. **Wait for workflow to run** (automatic)
3. **Check Security tab** for results
4. **Review any findings** and fix critical issues
5. **Enjoy automated security scanning!** 🎊

---

**Status:** ⚠️ Action Required  
**Blocker:** Code scanning not enabled  
**Fix Time:** 2-5 minutes  
**Fix Difficulty:** ⭐ Easy (just enable in settings)  

---

## 🚀 Ready to Enable?

**Click here to go directly to settings:**
```
https://github.com/NadeeshaMedagama/choreo_ai_assistant/settings/security_analysis
```

**Then click "Enable" on:**
1. Code scanning
2. Secret scanning
3. Dependabot alerts

**That's it! Your security scanning will work perfectly after that!** ✅

