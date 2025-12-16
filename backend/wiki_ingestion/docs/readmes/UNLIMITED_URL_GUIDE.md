# 🚀 Unlimited URL Ingestion - Configuration Guide

## ✅ Changes Made

The URL limitation has been **removed**! You can now ingest **ALL** linked URLs from the wiki page.

---

## 🔧 What Was Updated

### 1. **Script Updated**: `examples/ingest_to_milvus.py`

**Changed:**
- ❌ Before: `max_linked_urls=30` (hardcoded)
- ✅ After: `max_linked_urls=MAX_LINKED_URLS` (configurable)

**New Configuration Variable:**
```python
MAX_LINKED_URLS = int(os.getenv('WIKI_MAX_LINKED_URLS', '0'))  # 0 = no limit
```

### 2. **Environment File Updated**: `backend/.env`

**Added New Configuration:**
```bash
# Wiki Ingestion Configuration
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0  # 0 = no limit, process all linked URLs
```

---

## 🎯 Configuration Options

### Option 1: No Limit (Default - Process ALL URLs)

```bash
WIKI_MAX_LINKED_URLS=0
```
- Processes **all** linked URLs found on wiki pages
- Can take longer depending on number of URLs
- Generates maximum content coverage

### Option 2: Custom Limit

```bash
WIKI_MAX_LINKED_URLS=100
```
- Processes up to 100 linked URLs
- Good for testing or when you want partial coverage
- Faster processing

### Option 3: Skip Linked Content

```bash
WIKI_FETCH_LINKED=false
```
- Only processes wiki pages, no external links
- Fastest option
- Minimal content

---

## 📊 Expected Results with No Limit

Based on your last run, the wiki homepage had **84 linked URLs**. With the limit removed:

### Before (with limit=30):
- ✅ Crawled: 1 wiki page
- ✅ Linked URLs: 30 (limited from 84)
- ✅ Total chunks: 440
- ⏱️ Duration: ~2 minutes

### After (with limit=0):
- ✅ Crawled: 1 wiki page
- ✅ Linked URLs: **~84** (all URLs)
- ✅ Total chunks: **~1,200-1,500** (estimated)
- ⏱️ Duration: **~5-7 minutes** (estimated)

---

## 🚀 How to Run with No Limit

### Quick Start (Easiest)

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend/wiki_ingestion
./quickstart_milvus.sh
```

The script will automatically use `WIKI_MAX_LINKED_URLS=0` from your `.env` file.

### Direct Command

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

### With Custom Limit (Optional)

```bash
# Temporarily set a different limit
export WIKI_MAX_LINKED_URLS=100
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## ⏱️ Processing Time Estimates

Based on batching (10 chunks at a time) and API rate limits:

| Linked URLs | Chunks (Est.) | Time (Est.) |
|-------------|---------------|-------------|
| 30 (old limit) | ~440 | ~2 min |
| 50 | ~700 | ~3.5 min |
| 84 (all from homepage) | ~1,400 | ~7 min |
| 100 | ~1,600 | ~8 min |

**Note**: Actual time depends on:
- Size of linked pages
- Azure OpenAI API response time
- Network speed
- Milvus write speed

---

## 📋 Monitoring Progress

The script shows real-time progress:

```
================================================================================
STEP 4: FETCHING AND CHUNKING LINKED CONTENT
================================================================================
  [1/84] Fetching: https://github.com/features/copilot...
     ✓ 12 chunks created
  [2/84] Fetching: https://github.com/...
     ✓ 13 chunks created
  ...
  [84/84] Fetching: https://docs.github.com/...
     ✓ 84 chunks created
✅ Created 1,234 chunks from linked content
```

Then embedding progress:

```
📦 Embedding and storing 1,234 chunks in Milvus...
================================================================================

📦 Processing batch 1/124 (10 chunks)...
   🔄 Creating embeddings...
   💾 Storing in Milvus...
   ✅ Batch complete (10/1,234 total)
...
```

---

## 🎛️ Advanced Configuration

### Full Control via .env

Edit `backend/.env`:

```bash
# Wiki Ingestion Configuration
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=3                # Crawl depth (0-5 recommended)
WIKI_MAX_PAGES=100              # Max wiki pages to crawl
WIKI_FETCH_LINKED=true          # Fetch external links
WIKI_MAX_LINKED_URLS=0          # 0 = no limit
```

### Performance Tuning

**For Fast Testing:**
```bash
WIKI_MAX_DEPTH=1
WIKI_MAX_PAGES=5
WIKI_FETCH_LINKED=false
```

**For Maximum Coverage:**
```bash
WIKI_MAX_DEPTH=3
WIKI_MAX_PAGES=200
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0
```

**For Balanced Approach:**
```bash
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=50
```

---

## 💡 Best Practices

### 1. Start with a Test Run

Before processing all URLs, test with a small number:

```bash
export WIKI_MAX_LINKED_URLS=10
python -m wiki_ingestion.examples.ingest_to_milvus
```

### 2. Monitor API Limits

Azure OpenAI has rate limits. If you hit them:
- The script includes retry logic
- You can reduce batch size in the script
- Or add delays between batches

### 3. Check Milvus Storage

After ingestion, verify:

```bash
python -m wiki_ingestion.examples.verify_milvus_data
```

### 4. Incremental Updates

Re-running the script will:
- Update existing chunks (if content changed)
- Add new chunks (if new URLs found)
- Keep old chunks (if URLs still exist)

---

## 🔍 Troubleshooting

### Issue: Taking too long

**Solution**: Set a limit temporarily
```bash
export WIKI_MAX_LINKED_URLS=50
```

### Issue: Rate limit errors

**Solution**: The script handles retries automatically. If persistent:
1. Check your Azure OpenAI quota
2. Reduce batch size (edit script: `batch_size = 5`)
3. Add delays between batches

### Issue: Some URLs fail to fetch

**Expected**: Some URLs may be:
- Private/requiring authentication
- Temporarily unavailable
- Invalid/broken links

The script continues processing other URLs.

### Issue: Out of memory

**Solution**: Process in smaller batches:
```bash
# First run
export WIKI_MAX_LINKED_URLS=30
python -m wiki_ingestion.examples.ingest_to_milvus

# Second run
export WIKI_MAX_LINKED_URLS=60
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## 📊 What Gets Stored

Each chunk from linked URLs includes:

```python
{
    'id': 'unique-id',
    'vector': [0.1, 0.2, ...],          # 1536 dimensions
    'content': 'actual text content',
    'source_url': 'https://...',        # The linked URL
    'source_title': 'Page Title',
    'source_type': 'linked_content',    # Marked as linked content
    'repository': 'wso2/docs-choreo-dev',
    'owner': 'wso2',
    'chunk_index': 0,
    'chunk_size': 1024,
    'total_chunks': 5,
}
```

You can filter by `source_type`:
- `wiki_page` - Direct wiki content
- `linked_content` - Content from linked URLs

---

## 🚀 Ready to Process All URLs!

**Current Configuration:**
- ✅ No URL limit (`WIKI_MAX_LINKED_URLS=0`)
- ✅ All URLs will be processed
- ✅ Maximum content coverage
- ✅ Estimated ~1,400 chunks from 84 URLs

**Run it:**

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend/wiki_ingestion
./quickstart_milvus.sh
```

Or:

```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

**Expected Output:**
```
Configuration:
  📚 Wiki URL: https://github.com/wso2/docs-choreo-dev/wiki
  🔍 Max Depth: 2
  📄 Max Pages: 50
  🔗 Fetch Linked Content: True
  📎 Max Linked URLs: No limit  ← NEW!
  
  🗄️  Milvus Collection: choreo_developer_assistant
  📏 Embedding Dimension: 1536
  🤖 Embedding Model: choreo-ai-embedding
```

---

## 📝 Summary of Changes

| Setting | Before | After |
|---------|--------|-------|
| Max Linked URLs | 30 (hardcoded) | 0 (no limit, configurable) |
| Configuration | Not available | Via `WIKI_MAX_LINKED_URLS` in `.env` |
| Flexibility | Fixed | Fully configurable |
| Expected Chunks | ~440 | ~1,400+ |
| Processing Time | ~2 min | ~5-7 min |

---

**The system is now configured to process ALL linked URLs! 🎉**

_Updated: December 9, 2025_

