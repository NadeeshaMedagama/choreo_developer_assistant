# Wiki Ingestion - Directory Structure

## 📁 Directory Organization

```
backend/wiki_ingestion/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration management
├── main.py                     # Main entry point
├── ingest_via_git.py          # Primary ingestion script (Git-based)
├── test_system.py             # System tests
├── requirements.txt            # Python dependencies
├── quickstart.sh              # Quick start script
├── .env.example               # Environment template
│
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide  
├── SUMMARY.md                # System overview
├── START_HERE.md             # Getting started
│
├── 📁 interfaces/            # SOLID: Interface definitions
│   ├── web_crawler.py
│   ├── content_extractor.py
│   └── url_fetcher.py
│
├── 📁 models/                # Data models
│   ├── wiki_page.py
│   └── wiki_chunk.py
│
├── 📁 services/              # Service implementations
│   ├── url_fetcher_service.py
│   ├── content_extractor_service.py
│   ├── web_crawler_service.py
│   ├── wiki_chunking_service.py
│   └── wiki_ingestion_orchestrator.py
│
├── 📁 examples/              # Usage examples
│   ├── simple_crawl.py
│   ├── ingest_to_vector_db.py
│   ├── ingest_choreo_complete.py
│   └── ingest_choreo_wiki.py
│
├── 📁 scripts/               # Utility scripts
│   ├── debug_wiki_url.py     # Debug URL accessibility
│   ├── search_choreo.py      # Search for Choreo repos
│   └── test_auth.py          # Test GitHub authentication
│
├── 📁 logs/                  # Log files
│   ├── final_ingestion.log
│   ├── ingestion_complete.log
│   └── ingestion_output.log
│
└── 📁 docs/                  # Documentation
    ├── guides/
    │   └── TROUBLESHOOTING.md
    └── architecture/
```

## 🎯 Quick Reference

### Main Scripts

- **`ingest_via_git.py`** - ✅ **RECOMMENDED** - Complete ingestion via Git clone
- **`main.py`** - Basic wiki crawl and chunk (web-based)
- **`test_system.py`** - Run system tests

### Utility Scripts (scripts/)

- **`test_auth.py`** - Test GitHub token authentication
- **`debug_wiki_url.py`** - Debug wiki URL accessibility
- **`search_choreo.py`** - Search for Choreo repositories

### Examples (examples/)

- **`simple_crawl.py`** - Basic crawl without vector DB
- **`ingest_to_vector_db.py`** - Full pipeline with Pinecone
- **`ingest_choreo_complete.py`** - Complete Choreo ingestion
- **`ingest_choreo_wiki.py`** - Alternative Choreo script

## 🚀 Usage

### Quick Test
```bash
python test_system.py
```

### Full Ingestion (Recommended)
```bash
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
python ingest_via_git.py
```

### Debug Authentication
```bash
python scripts/test_auth.py
```

### Search for Repos
```bash
python scripts/search_choreo.py
```

## 📝 Documentation

- **README.md** - Complete system documentation
- **QUICKSTART.md** - 5-minute quick start
- **SUMMARY.md** - Architecture overview
- **START_HERE.md** - Getting started guide
- **docs/guides/TROUBLESHOOTING.md** - Troubleshooting guide

## 🗂️ Organization Principles

1. **Core files** in root - Main scripts and configuration
2. **interfaces/** - Abstract interfaces (SOLID principle)
3. **models/** - Data models
4. **services/** - Service implementations
5. **examples/** - Usage examples
6. **scripts/** - Utility and debug scripts
7. **logs/** - Log files (auto-generated)
8. **docs/** - Additional documentation

---

**See individual README files in each directory for more details.**

