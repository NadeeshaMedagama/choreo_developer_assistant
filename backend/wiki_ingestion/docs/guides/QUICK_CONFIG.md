# 🚀 Wiki Ingestion - Quick Configuration Guide

## ⚡ Quick Options

### Option 1: FAST - Wiki Pages Only (CURRENT SETTING)
**Time**: ~30 seconds  
**Chunks**: ~5-10  
**Use when**: You only want wiki content, no external links

```bash
WIKI_FETCH_LINKED=false  # ← Currently set to this
```

Run:
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

### Option 2: BALANCED - Limited Linked Content
**Time**: ~2-3 minutes  
**Chunks**: ~200-400  
**Use when**: You want some external content but not everything

```bash
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=20  # Process only first 20 URLs
```

---

### Option 3: COMPREHENSIVE - All Content
**Time**: ~4-5 minutes  
**Chunks**: ~1,100+  
**Use when**: You want maximum coverage

```bash
WIKI_FETCH_LINKED=true
WIKI_MAX_LINKED_URLS=0  # No limit
```

---

## 📝 How to Change Settings

### Edit .env file:
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
nano .env  # or use your editor
```

### Find this section:
```bash
# Wiki Ingestion Configuration
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=false  # ← Change this
WIKI_MAX_LINKED_URLS=0   # ← Or this
```

---

## 🎯 Current Configuration

Your `.env` is now set to:
- ✅ **WIKI_FETCH_LINKED=false** (fast mode)
- ✅ Wiki pages only
- ✅ No external links
- ⏱️ Takes ~30 seconds

---

## 🔄 Quick Commands

### Run ingestion with current settings:
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Or override for this run only:
```bash
# Fast (wiki only)
export WIKI_FETCH_LINKED=false
python -m wiki_ingestion.examples.ingest_to_milvus

# Medium (20 URLs)
export WIKI_FETCH_LINKED=true
export WIKI_MAX_LINKED_URLS=20
python -m wiki_ingestion.examples.ingest_to_milvus

# All content (84 URLs)
export WIKI_FETCH_LINKED=true
export WIKI_MAX_LINKED_URLS=0
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## ⚙️ All Configuration Options

| Setting | What It Does | Values |
|---------|-------------|--------|
| `WIKI_URL` | Which wiki to ingest | Any GitHub wiki URL |
| `WIKI_MAX_DEPTH` | How deep to crawl | 0-5 (2 recommended) |
| `WIKI_MAX_PAGES` | Max wiki pages | Any number (50 default) |
| `WIKI_FETCH_LINKED` | Fetch external links | true/false |
| `WIKI_MAX_LINKED_URLS` | Limit external links | 0=unlimited, N=limit |

---

## 📊 Speed vs Coverage

| Mode | FETCH_LINKED | MAX_LINKED_URLS | Time | Chunks |
|------|--------------|-----------------|------|--------|
| Fast | false | - | ~30s | ~5-10 |
| Medium | true | 20 | ~2min | ~300 |
| Full | true | 0 | ~5min | ~1,200 |

---

## ✅ Recommended: Start with Fast Mode

1. Run in fast mode first to test:
   ```bash
   # .env already set to WIKI_FETCH_LINKED=false
   python -m wiki_ingestion.examples.ingest_to_milvus
   ```

2. If you want more content, change to medium or full:
   ```bash
   # Edit .env
   WIKI_FETCH_LINKED=true
   WIKI_MAX_LINKED_URLS=20
   ```

3. Run again to add more content:
   ```bash
   python -m wiki_ingestion.examples.ingest_to_milvus
   ```

---

## 🎉 Current Setup - Ready to Run!

✅ Fast mode enabled (WIKI_FETCH_LINKED=false)  
✅ Will ingest wiki pages only  
✅ Should complete in ~30 seconds  
✅ No interruptions from slow external URLs  

**Run it now:**
```bash
cd ~/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

