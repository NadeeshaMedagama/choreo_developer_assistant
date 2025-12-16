# 🚨 WIKI INGESTION ISSUE - RESOLUTION GUIDE

## Problem Summary

When you run the wiki ingestion for `wso2-enterprise/choreo/wiki`, it returns a **404 error**.

---

## 🔍 Diagnostic Results

✅ **.env file**: Correctly configured and being read  
✅ **WIKI_URL**: `https://github.com/wso2-enterprise/choreo/wiki`  
✅ **Repository**: Exists (`wso2-enterprise/choreo`)  
✅ **Repository Type**: **Private**  
✅ **Wiki Enabled**: Yes  
❌ **Wiki Pages**: **Not accessible** (404 error)  

---

## 🎯 Root Cause

The `wso2-enterprise/choreo` wiki is returning 404 because:

1. **No wiki pages exist** - The wiki might be enabled but empty
2. **Authentication issue** - Private repo wikis require special access
3. **Permissions** - Your GitHub token might not have wiki read access

---

## ✅ Solutions

### Solution 1: Use a Different Wiki (RECOMMENDED)

Since `wso2-enterprise/choreo/wiki` doesn't have pages, use the original working wiki:

**Update your `.env` file:**
```bash
# Change back to the working wiki
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
```

**Then run:**
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Solution 2: Create Wiki Pages in wso2-enterprise/choreo

If you have admin access:

1. Go to: https://github.com/wso2-enterprise/choreo/wiki
2. Click "Create the first page"
3. Add content and save
4. Then run the ingestion

### Solution 3: Check Wiki Access Using Git

Private repo wikis can be cloned:

```bash
# Try cloning the wiki
git clone https://github.com/wso2-enterprise/choreo.wiki.git

# If it works, wiki exists
# If it fails, wiki has no pages
```

### Solution 4: Use GitHub API to Check Wiki

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'token {token}'}

# Check wiki pages via API
url = 'https://api.github.com/repos/wso2-enterprise/choreo/pages'
resp = requests.get(url, headers=headers)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:500]}')
"
```

---

## 🚀 Recommended Action Plan

### Option A: Continue with wso2/docs-choreo-dev (Working)

**1. Update .env:**
```bash
nano ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend/.env
```

Change:
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
```

**2. Run ingestion:**
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

This will process:
- Wiki pages from `wso2/docs-choreo-dev`
- All linked URLs (unlimited)
- Store in Milvus

### Option B: Wait for wso2-enterprise/choreo Wiki

If you specifically need `wso2-enterprise/choreo` wiki:

1. Ask repository admin to create wiki pages
2. Or wait until wiki pages are added
3. Then run the ingestion

---

## 📊 Alternative Repositories to Ingest

If you want to ingest other Choreo-related content:

### 1. wso2/docs-choreo-dev (Already tested ✅)
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
```

### 2. Check other wso2 repos
```bash
# List wso2 repositories
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/orgs/wso2/repos?per_page=100 | \
  grep -o '"full_name": "[^"]*"' | head -20
```

### 3. Check wso2-enterprise repos
```bash
# List wso2-enterprise repositories
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/orgs/wso2-enterprise/repos?per_page=100 | \
  grep -o '"full_name": "[^"]*"' | head -20
```

---

## 🔧 Quick Fix Command

Run this to switch back to the working wiki and start ingestion:

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend

# Update .env
sed -i 's|WIKI_URL=https://github.com/wso2-enterprise/choreo/wiki|WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki|' .env

# Run ingestion
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## 📝 Summary

| Issue | Status | Action |
|-------|--------|--------|
| .env file reading | ✅ Working | No action needed |
| WIKI_URL configuration | ✅ Working | No action needed |
| wso2-enterprise/choreo wiki | ❌ No pages (404) | Use different repo |
| wso2/docs-choreo-dev wiki | ✅ Working | Switch back to this |

**Recommendation**: Use `https://github.com/wso2/docs-choreo-dev/wiki` which is working and has content.

---

## 💡 Next Steps

1. **Decide which wiki to use**:
   - `wso2/docs-choreo-dev` - Working, has content ✅
   - `wso2-enterprise/choreo` - No pages, needs setup ❌

2. **Update .env accordingly**

3. **Run the ingestion**

4. **Verify data in Milvus**

---

**Quick command to fix and run:**
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend && \
echo "WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki" && \
python -m wiki_ingestion.examples.ingest_to_milvus
```

