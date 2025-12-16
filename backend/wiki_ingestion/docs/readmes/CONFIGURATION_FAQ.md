# 📝 Wiki Ingestion Configuration - Quick Guide

## ❓ Your Question: Do I need to update the GitHub URL in .env?

**Answer: It depends on what wiki you want to ingest!**

---

## 📋 Current Configuration

Your `.env` file already has:

```bash
# Wiki Ingestion Configuration
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki  ← This is the wiki to ingest
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0  # 0 = no limit, process all linked URLs
```

---

## 🎯 When to Update WIKI_URL

### Scenario 1: Keep Current Wiki (No Change Needed) ✅

If you want to continue ingesting from `wso2/docs-choreo-dev` wiki:

**Action**: Nothing! Just run the script:
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Scenario 2: Ingest a Different Wiki (Update Needed) 🔄

If you want to ingest a **different** GitHub wiki, update the URL:

**Example 1 - Another WSO2 Repo:**
```bash
WIKI_URL=https://github.com/wso2/choreo-docs/wiki
```

**Example 2 - Different Organization:**
```bash
WIKI_URL=https://github.com/microsoft/vscode/wiki
```

**Example 3 - Your Own Repo:**
```bash
WIKI_URL=https://github.com/yourorg/yourrepo/wiki
```

---

## 🛠️ Complete Configuration Options

### Required Settings (Already Set ✅)

```bash
# Which wiki to ingest
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki

# Azure OpenAI (for embeddings)
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=choreo-ai-embedding

# Milvus (for storage)
MILVUS_URI=your-milvus-uri
MILVUS_TOKEN=your-token
MILVUS_COLLECTION_NAME=choreo_developer_assistant
```

### Optional Settings (You Can Adjust)

```bash
# Crawling Settings
WIKI_MAX_DEPTH=2              # How deep to crawl (1-5 recommended)
WIKI_MAX_PAGES=50             # Max wiki pages to fetch
WIKI_FETCH_LINKED=true        # Fetch linked URLs from wiki pages
WIKI_MAX_LINKED_URLS=0        # 0 = unlimited linked URLs

# GitHub Token (optional, for higher rate limits)
GITHUB_TOKEN=your-github-token
```

---

## 🔍 What Each Setting Does

### WIKI_URL
- **What**: The starting point for wiki ingestion
- **Format**: `https://github.com/{owner}/{repo}/wiki`
- **Example**: `https://github.com/wso2/docs-choreo-dev/wiki`
- **When to change**: When you want to ingest a different wiki

### WIKI_MAX_DEPTH
- **What**: How many levels deep to crawl wiki pages
- **Values**: 
  - `0` = Only the home page
  - `1` = Home page + direct links
  - `2` = Home page + 2 levels of links
  - `3+` = Deeper crawling
- **Current**: `2` (good balance)

### WIKI_MAX_PAGES
- **What**: Maximum number of wiki pages to fetch
- **Values**: Any number (e.g., 10, 50, 100, 500)
- **Current**: `50` (reasonable limit)
- **Tip**: Set higher for comprehensive coverage

### WIKI_FETCH_LINKED
- **What**: Whether to fetch external links found on wiki pages
- **Values**: `true` or `false`
- **Current**: `true` (fetches linked content)
- **Impact**: When `true`, you get 2.6x more content!

### WIKI_MAX_LINKED_URLS
- **What**: Limit on how many linked URLs to process
- **Values**: 
  - `0` = No limit (process all)
  - `30` = Process only first 30
  - `100` = Process only first 100
- **Current**: `0` (no limit - processes all URLs)

---

## 📊 Example Configurations

### Conservative (Fast, Limited Content)
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=1
WIKI_MAX_PAGES=10
WIKI_FETCH_LINKED=false
WIKI_MAX_LINKED_URLS=0
```
**Result**: ~5-10 chunks, ~30 seconds

### Balanced (Current Setup)
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0
```
**Result**: ~1,161 chunks, ~4.5 minutes

### Aggressive (Maximum Coverage)
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=3
WIKI_MAX_PAGES=200
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0
```
**Result**: ~3,000+ chunks, ~15-20 minutes

---

## 🎯 Quick Decision Guide

### Question 1: What wiki do I want?

**Same wiki (wso2/docs-choreo-dev)?**
→ ✅ No change needed

**Different wiki?**
→ 🔄 Update `WIKI_URL` in `.env`

### Question 2: How much content do I want?

**Just wiki pages (fast)?**
→ Set `WIKI_FETCH_LINKED=false`

**Maximum coverage (current)?**
→ Keep `WIKI_FETCH_LINKED=true` and `WIKI_MAX_LINKED_URLS=0`

**Limited linked content?**
→ Set `WIKI_MAX_LINKED_URLS=30` (or any number)

---

## 📝 How to Update Configuration

### Step 1: Edit .env file
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
nano .env  # or use any text editor
```

### Step 2: Change the settings
```bash
# Change the wiki URL (example)
WIKI_URL=https://github.com/wso2/choreo-docs/wiki

# Or adjust other settings
WIKI_MAX_PAGES=100
WIKI_MAX_LINKED_URLS=50
```

### Step 3: Save and run ingestion
```bash
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## ✅ Your Current Setup is Ready!

Your `.env` is already configured for:
- ✅ Wiki: `wso2/docs-choreo-dev`
- ✅ Unlimited linked URLs
- ✅ Maximum content coverage
- ✅ All credentials set

**You can run it right now without any changes!**

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## 🔄 Multiple Wikis?

Want to ingest multiple wikis into the same Milvus collection?

**Option 1: Run multiple times**
```bash
# First wiki
export WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
python -m wiki_ingestion.examples.ingest_to_milvus

# Second wiki
export WIKI_URL=https://github.com/wso2/choreo-docs/wiki
python -m wiki_ingestion.examples.ingest_to_milvus

# Third wiki
export WIKI_URL=https://github.com/wso2/api-manager/wiki
python -m wiki_ingestion.examples.ingest_to_milvus
```

**Option 2: Update .env each time**
Edit `.env` and change `WIKI_URL`, then run the script.

All wikis will be stored in the same Milvus collection with proper metadata for filtering.

---

## 💡 Summary

| Question | Answer |
|----------|--------|
| Do I need to update WIKI_URL? | Only if you want a different wiki |
| What's the current wiki? | wso2/docs-choreo-dev |
| Is my config complete? | Yes! ✅ |
| Can I run it now? | Yes! Just run the script |
| How to change wiki? | Edit WIKI_URL in .env |
| How to limit URLs? | Change WIKI_MAX_LINKED_URLS |

---

**Quick Answer to Your Question:**

**NO**, you don't need to update the GitHub URL in `.env` unless you want to ingest a **different** wiki. 

Your current configuration is:
- ✅ Already set to `wso2/docs-choreo-dev/wiki`
- ✅ Configured for unlimited URLs
- ✅ Ready to run

Just run the script and it will work! 🚀

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

