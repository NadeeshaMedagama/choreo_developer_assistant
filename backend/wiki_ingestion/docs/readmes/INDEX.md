# 🗂️ Wiki Ingestion System - Complete File Index

## 📍 Quick Navigation

| Category | Location | Description |
|----------|----------|-------------|
| **Main Scripts** | Root directory | Primary ingestion scripts |
| **Core Architecture** | `interfaces/`, `models/`, `services/` | SOLID architecture components |
| **Examples** | `examples/` | Working usage examples |
| **Utilities** | `scripts/` | Debug and testing tools |
| **Documentation** | `docs/` | Guides and references |
| **Logs** | `logs/` | Ingestion log files |

---

## 📁 Complete File Structure

```
backend/wiki_ingestion/
│
├── 📄 Core Files (Root)
│   ├── __init__.py                 Package initialization
│   ├── config.py                   Configuration management
│   ├── main.py                     Basic web-based ingestion
│   ├── ingest_via_git.py          ⭐ PRIMARY: Git-based ingestion
│   ├── test_system.py             System tests
│   ├── requirements.txt            Dependencies
│   ├── quickstart.sh              Quick start script
│   └── .env.example               Environment template
│
├── 📚 Documentation
│   ├── README.md                   Complete documentation
│   ├── QUICKSTART.md              5-minute quick start
│   ├── SUMMARY.md                 System overview
│   ├── START_HERE.md              Getting started
│   ├── STRUCTURE.md               This file
│   ├── .gitignore                 Git ignore rules
│   └── docs/
│       ├── guides/
│       │   └── TROUBLESHOOTING.md  Troubleshooting guide
│       └── architecture/           (For future architecture docs)
│
├── 🏗️ Architecture (SOLID)
│   ├── interfaces/                 Abstract interfaces
│   │   ├── __init__.py
│   │   ├── web_crawler.py         IWebCrawler interface
│   │   ├── content_extractor.py   IContentExtractor interface
│   │   └── url_fetcher.py         IUrlFetcher interface
│   │
│   ├── models/                     Data models
│   │   ├── __init__.py
│   │   ├── wiki_page.py           WikiPage model
│   │   └── wiki_chunk.py          WikiChunk model
│   │
│   └── services/                   Implementations
│       ├── __init__.py
│       ├── url_fetcher_service.py              HTTP fetching
│       ├── content_extractor_service.py        HTML extraction
│       ├── web_crawler_service.py              Web crawling
│       ├── wiki_chunking_service.py            Content chunking
│       └── wiki_ingestion_orchestrator.py      Main coordinator
│
├── 📦 Examples & Scripts
│   ├── examples/                   Usage examples
│   │   ├── README.md
│   │   ├── simple_crawl.py        Basic crawl → JSON
│   │   ├── ingest_to_vector_db.py Full pipeline
│   │   ├── ingest_choreo_complete.py  Choreo ingestion
│   │   └── ingest_choreo_wiki.py  Alternative Choreo
│   │
│   └── scripts/                    Utility scripts
│       ├── README.md
│       ├── __init__.py
│       ├── test_auth.py           Test GitHub auth
│       ├── debug_wiki_url.py      Debug URLs
│       └── search_choreo.py       Search repos
│
└── 📊 Output & Logs
    └── logs/                       Log files
        ├── README.md
        ├── __init__.py
        ├── final_ingestion.log
        ├── ingestion_complete.log
        └── ingestion_output.log
```

---

## 🎯 Usage Guide by File

### 🚀 Primary Scripts

#### **ingest_via_git.py** ⭐ RECOMMENDED
Complete ingestion via Git clone (works with private repos).

```bash
cd backend
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
python -m backend.wiki_ingestion.ingest_via_git
```

**When to use:** Production ingestion, private wikis, complete wiki access.

---

#### **main.py**
Basic web-based ingestion (for public wikis).

```bash
cd backend
export WIKI_URL="https://github.com/wso2/docs-apim/wiki"
python -m wiki_ingestion.main
```

**When to use:** Quick tests, public wikis, exploration.

---

#### **test_system.py**
System validation tests.

```bash
cd backend
python -m wiki_ingestion.test_system
```

**When to use:** Verify installation, check if system works.

---

### 📦 Example Scripts

Located in `examples/` - see [examples/README.md](../../examples/README.md)

| File | Purpose | Use Case |
|------|---------|----------|
| `simple_crawl.py` | Basic crawl → JSON | Testing, exploration |
| `ingest_to_vector_db.py` | Full pipeline | Production (public wikis) |
| `ingest_choreo_complete.py` | Choreo-specific | Alternative approach |
| `ingest_choreo_wiki.py` | Choreo variant | Different config |

---

### 🔧 Utility Scripts

Located in `scripts/` - see [scripts/README.md](../../scripts/README.md)

| File | Purpose | Command |
|------|---------|---------|
| `test_auth.py` | Test GitHub token | `python scripts/test_auth.py` |
| `debug_wiki_url.py` | Debug URL issues | `python scripts/debug_wiki_url.py` |
| `search_choreo.py` | Find Choreo repos | `python scripts/search_choreo.py` |

---

### 🏗️ Architecture Files

#### Interfaces (SOLID: Dependency Inversion)

| File | Interface | Purpose |
|------|-----------|---------|
| `web_crawler.py` | `IWebCrawler` | Define crawling contract |
| `content_extractor.py` | `IContentExtractor` | Define extraction contract |
| `url_fetcher.py` | `IUrlFetcher` | Define fetching contract |

#### Models

| File | Model | Purpose |
|------|-------|---------|
| `wiki_page.py` | `WikiPage` | Represents a wiki page |
| `wiki_chunk.py` | `WikiChunk` | Represents a content chunk |

#### Services (Implementations)

| File | Service | Implements |
|------|---------|------------|
| `url_fetcher_service.py` | `UrlFetcherService` | `IUrlFetcher` |
| `content_extractor_service.py` | `ContentExtractorService` | `IContentExtractor` |
| `web_crawler_service.py` | `WebCrawlerService` | `IWebCrawler` |
| `wiki_chunking_service.py` | `WikiChunkingService` | Chunking logic |
| `wiki_ingestion_orchestrator.py` | `WikiIngestionOrchestrator` | Coordinates workflow |

---

## 📖 Documentation Files

| File | Content | When to Read |
|------|---------|--------------|
| `README.md` | Complete documentation | First time setup |
| `QUICKSTART.md` | 5-minute guide | Quick start |
| `START_HERE.md` | Getting started | New users |
| `SUMMARY.md` | System overview | Understanding architecture |
| `STRUCTURE.md` | This file | Finding files |
| `docs/guides/TROUBLESHOOTING.md` | Problem solving | When issues occur |

---

## 🎓 Learning Path

### Beginner
1. Read `START_HERE.md`
2. Read `QUICKSTART.md`
3. Run `test_system.py`
4. Try `examples/simple_crawl.py`

### Intermediate
1. Read `README.md`
2. Study `SUMMARY.md` (architecture)
3. Use `ingest_via_git.py` for real ingestion
4. Explore `scripts/` utilities

### Advanced
1. Study `interfaces/` (SOLID design)
2. Read `services/` implementations
3. Create custom implementations
4. Extend the system

---

## 🔍 Finding What You Need

### I want to...

**...ingest a wiki**
→ Use `ingest_via_git.py` (primary) or `main.py` (basic)

**...test the system**
→ Run `test_system.py`

**...debug authentication**
→ Use `scripts/test_auth.py`

**...find correct wiki URL**
→ Use `scripts/debug_wiki_url.py`

**...see examples**
→ Check `examples/` directory

**...understand architecture**
→ Read `SUMMARY.md` and study `interfaces/`

**...troubleshoot issues**
→ Read `docs/guides/TROUBLESHOOTING.md`

**...customize behavior**
→ Study `services/` and create custom implementations

---

## 📊 Statistics

- **Total Files:** 37+
- **Python Files:** 25+
- **Documentation Files:** 10+
- **Directories:** 11
- **Lines of Code:** ~3,500+
- **Test Coverage:** Core functionality tested

---

## 🎯 Quick Commands Reference

```bash
# Test system
python -m wiki_ingestion.test_system

# Full ingestion (Git-based)
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
python -m backend.wiki_ingestion.ingest_via_git

# Test authentication
python -m wiki_ingestion.scripts.test_auth

# Debug URL
python -m wiki_ingestion.scripts.debug_wiki_url

# Simple example
python -m wiki_ingestion.examples.simple_crawl
```

---

## 📝 Notes

- All imports work from `backend/` directory
- Scripts use environment variables from `backend/.env`
- Logs automatically created in `logs/`
- Temporary files cleaned automatically
- See individual README files for detailed documentation

---

**Last Updated:** December 3, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

---

**Navigation:**
- [📖 Main README](../../README.md)
- [🚀 Quick Start](../guides/QUICKSTART.md)  
- [📊 Summary](SUMMARY.md)
- [🏁 Start Here](../guides/START_HERE.md)

