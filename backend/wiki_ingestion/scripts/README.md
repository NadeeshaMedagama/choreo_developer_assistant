# Wiki Ingestion Scripts

Utility scripts for debugging, testing, and exploring wiki ingestion capabilities.

## 📁 Available Scripts

### 🔐 test_auth.py
Test GitHub token authentication and repository access.

```bash
python test_auth.py
```

**What it does:**
- Validates GitHub token
- Tests access to repositories
- Checks wiki availability
- Shows user permissions

**Output:**
- ✅ Token valid/invalid
- ✅ Repository accessible/not accessible
- ✅ Wiki exists/doesn't exist

---

### 🔍 debug_wiki_url.py
Debug wiki URL accessibility and find correct URLs.

```bash
python debug_wiki_url.py
```

**What it does:**
- Tests different URL formats
- Checks repository accessibility
- Finds working wiki URLs
- Suggests alternatives

**Use when:**
- Getting 404 errors
- Wiki URL unclear
- Need to find correct format

---

### 🔎 search_choreo.py
Search for Choreo-related repositories via GitHub API.

```bash
python search_choreo.py
```

**What it does:**
- Searches GitHub for Choreo repos
- Lists repos with wikis
- Shows public/private status
- Provides wiki URLs

**Output:**
- All Choreo repositories found
- Which ones have wikis
- Access URLs

---

## 🚀 Quick Examples

### Test if you can access a private repo
```bash
cd backend/wiki_ingestion/scripts
python test_auth.py
```

### Find the correct wiki URL
```bash
python debug_wiki_url.py
```

### Search for all Choreo documentation
```bash
python search_choreo.py
```

---

## 📝 Notes

- All scripts use credentials from `backend/.env`
- Scripts are standalone and can be run independently
- Safe to run - they only read, never write to GitHub

## 🔙 Back to Main

See [../README.md](../README.md) for main documentation.

