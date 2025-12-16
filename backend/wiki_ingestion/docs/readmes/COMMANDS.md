# 🚀 Wiki Ingestion - Quick Command Reference

## ⚡ Most Used Commands

### 1. Main Ingestion (Choreo Wiki)
```bash
cd backend
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
python -m backend.wiki_ingestion.ingest_via_git
```

### 2. Test System
```bash
cd backend
python -m wiki_ingestion.test_system
```

### 3. Test GitHub Authentication
```bash
cd backend/wiki_ingestion
python scripts/test_auth.py
```

---

## 📁 Directory Navigation

### Core Scripts (Root)
```bash
cd backend/wiki_ingestion

# Main ingestion
python ingest_via_git.py

# Basic web crawl
python main.py

# System tests
python test_system.py
```

### Examples
```bash
cd backend/wiki_ingestion/examples

# Simple crawl
python simple_crawl.py

# Full pipeline with vector DB
python ingest_to_vector_db.py
```

### Utilities
```bash
cd backend/wiki_ingestion/scripts

# Test authentication
python test_auth.py

# Debug wiki URL
python debug_wiki_url.py

# Search for repos
python search_choreo.py
```

---

## 🔧 Common Tasks

### Ingest Any Wiki
```bash
cd backend
export WIKI_URL="https://github.com/owner/repo/wiki"
python -m backend.wiki_ingestion.ingest_via_git
```

### Debug Connection Issues
```bash
cd backend/wiki_ingestion
python scripts/test_auth.py
python scripts/debug_wiki_url.py
```

### View Logs
```bash
cd backend/wiki_ingestion/logs
tail -f final_ingestion.log
```

### Clean Logs
```bash
cd backend/wiki_ingestion
rm logs/*.log
```

---

## 📖 Documentation

### Read Documentation
```bash
cd backend/wiki_ingestion

# Navigation guide
cat INDEX.md

# Quick start
cat QUICKSTART.md

# Full documentation
cat README.md
```

---

## 🎯 File Locations

| File | Path |
|------|------|
| Main script | `ingest_via_git.py` |
| System tests | `test_system.py` |
| Config | `config.py` |
| Examples | `examples/*.py` |
| Utilities | `scripts/*.py` |
| Logs | `logs/*.log` |
| Docs | `*.md`, `docs/guides/` |

---

## ✅ Quick Validation

```bash
# Check if everything works
cd backend
python -m wiki_ingestion.test_system

# Should see:
# ✅ URL fetching works
# ✅ Content extraction works
# ✅ Chunking works
# ✅ Integration test complete
```

---

**See INDEX.md for complete navigation guide**

