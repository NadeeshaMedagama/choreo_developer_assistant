# GitHub Issues Ingestion System - Documentation Index

Welcome to the GitHub Issues Ingestion System! This index will help you navigate the documentation.

## 🚀 Quick Navigation

### Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** - Start here! Get up and running in 5 minutes
2. **[setup.sh](../scripts/setup.sh)** - Run this script to verify your setup
3. **[examples.py](../examples.py)** - Run interactive examples

### Core Documentation
- **[README.md](../README.md)** - Complete system documentation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Architecture and design overview
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation

### Code
- **[main.py](../main.py)** - Command-line interface
- **[test_system.py](../test_system.py)** - Test suite

## 📚 Documentation Guide

### For First-Time Users

1. Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Run `./setup.sh` to verify installation
3. Run `python examples.py` to see it in action
4. Try: `python main.py wso2/choreo --max-issues 5`

### For Developers

1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture
2. Review [API_REFERENCE.md](API_REFERENCE.md) for API details
3. Check [README.md](../README.md) for comprehensive docs
4. Explore the code:
   - `interfaces/` - Abstract interfaces (SOLID principles)
   - `services/` - Concrete implementations
   - `models/` - Data models
   - `config/` - Configuration

### For Integration

1. Start with [API_REFERENCE.md](API_REFERENCE.md)
2. See `examples.py` for code examples
3. Use the factory function:
   ```python
   from github_issues_ingestion import create_ingestion_pipeline
   orchestrator = create_ingestion_pipeline()
   ```

## 📖 Documentation Files

### Core Documentation

| File | Description | Audience | Reading Time |
|------|-------------|----------|--------------|
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide | Everyone | 5 min |
| [README.md](../README.md) | Complete documentation | Developers | 15 min |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Architecture overview | Developers | 10 min |
| [API_REFERENCE.md](API_REFERENCE.md) | API documentation | Developers | 20 min |

### Code Files

| File | Description | Type |
|------|-------------|------|
| [main.py](../main.py) | CLI entry point | Executable |
| [test_system.py](../test_system.py) | Test suite | Executable |
| [examples.py](../examples.py) | Usage examples | Executable |
| [setup.sh](../scripts/setup.sh) | Setup script | Shell script |

### Package Structure

```
interfaces/     - Abstract interfaces (5 files)
├── issue_fetcher.py
├── text_processor.py
├── chunker.py
├── embedding_service.py
└── vector_store.py

models/         - Data models (2 files)
├── github_issue.py
└── chunk.py

services/       - Implementations (6 files)
├── github_issue_fetcher.py
├── text_processor_service.py
├── chunking_service.py
├── azure_embedding_service.py
├── pinecone_vector_store.py
└── ingestion_orchestrator.py

config/         - Configuration (1 file)
└── settings.py

utils/          - Utilities (1 file)
└── helpers.py
```

## 🎯 Common Tasks

### Task: First Time Setup
**Documents:** [QUICKSTART.md](QUICKSTART.md)  
**Commands:**
```bash
./setup.sh
python test_system.py
```

### Task: Ingest a Repository
**Documents:** [README.md](../README.md#usage), [QUICKSTART.md](QUICKSTART.md#3-ingest-your-first-repository)  
**Command:**
```bash
python main.py owner/repo --max-issues 10
```

### Task: Query Issues
**Documents:** [README.md](../README.md#usage), [API_REFERENCE.md](API_REFERENCE.md#ingestionorchestrator)  
**Command:**
```bash
python main.py owner/repo --query "search term"
```

### Task: Integrate into Code
**Documents:** [API_REFERENCE.md](API_REFERENCE.md), [examples.py](../examples.py)  
**Example:**
```python
from github_issues_ingestion import create_ingestion_pipeline
orchestrator = create_ingestion_pipeline()
stats = orchestrator.ingest_repository("owner", "repo")
```

### Task: Understand Architecture
**Documents:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#-solid-principles-implementation)  
**Focus Areas:**
- SOLID principles
- Clean architecture
- Dependency injection

### Task: Custom Configuration
**Documents:** [API_REFERENCE.md](API_REFERENCE.md#services), [examples.py](../examples.py)  
**Example:**
```python
from github_issues_ingestion import (
    GitHubIssueFetcher,
    IngestionOrchestrator,
    # ... other imports
)
# Create custom components
```

### Task: Troubleshooting
**Documents:** [QUICKSTART.md](QUICKSTART.md#6-common-issues-and-solutions)  
**Steps:**
1. Check `.env` file
2. Run `python test_system.py`
3. Review error messages
4. Check API keys and quotas

## 🔍 Finding Information

### By Topic

| Topic | Document | Section |
|-------|----------|---------|
| Installation | [QUICKSTART.md](QUICKSTART.md) | Steps 1-2 |
| CLI Usage | [README.md](../README.md) | Command Line Interface |
| Python API | [API_REFERENCE.md](API_REFERENCE.md) | Complete Reference |
| Architecture | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | SOLID Principles |
| Configuration | [README.md](../README.md) | Configuration |
| Examples | [examples.py](../examples.py) | All Examples |
| Testing | [test_system.py](../test_system.py) | Test Suite |
| Troubleshooting | [QUICKSTART.md](QUICKSTART.md) | Common Issues |

### By Skill Level

**Beginner:**
1. [QUICKSTART.md](QUICKSTART.md) - Get started quickly
2. [examples.py](../examples.py) - See it in action
3. [README.md](../README.md#examples) - Basic examples

**Intermediate:**
1. [README.md](../README.md) - Full documentation
2. [API_REFERENCE.md](API_REFERENCE.md) - API details
3. Service implementations in `services/`

**Advanced:**
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture
2. [API_REFERENCE.md](API_REFERENCE.md) - Full API
3. Interface definitions in `interfaces/`
4. Custom implementations

## 📝 Document Contents

### QUICKSTART.md
- Prerequisites check
- First ingestion
- Querying
- Code integration
- Common issues
- Best practices
- Examples

### README.md
- Complete overview
- Architecture diagram
- Installation
- Configuration
- CLI usage
- Python API
- Examples
- Performance
- Contributing

### PROJECT_SUMMARY.md
- Project statistics
- SOLID principles
- Architecture
- Data flow
- Features
- Usage examples
- Testing
- Extensibility

### API_REFERENCE.md
- Factory functions
- All interfaces
- All services
- All models
- Configuration
- Utilities
- Error handling
- Complete examples

## 🎓 Learning Path

### Path 1: Quick User
1. **[QUICKSTART.md](QUICKSTART.md)** - Setup and first use
2. **[examples.py](../examples.py)** - Run examples
3. **Done!**

### Path 2: Developer
1. **[QUICKSTART.md](QUICKSTART.md)** - Setup
2. **[README.md](../README.md)** - Understand features
3. **[API_REFERENCE.md](API_REFERENCE.md)** - Learn API
4. **[examples.py](../examples.py)** - Study examples
5. **Code exploration** - Read implementations

### Path 3: Architect
1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Architecture overview
2. **Interface definitions** - Study abstractions
3. **Service implementations** - Study concrete classes
4. **[README.md](../README.md)** - Full documentation
5. **[API_REFERENCE.md](API_REFERENCE.md)** - API details

## 🆘 Getting Help

1. **Setup issues?** → [QUICKSTART.md](QUICKSTART.md#6-common-issues-and-solutions)
2. **Usage questions?** → [README.md](../README.md#usage)
3. **API questions?** → [API_REFERENCE.md](API_REFERENCE.md)
4. **Architecture questions?** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
5. **Bug or error?** → Run `python test_system.py`

## ✅ Checklist

Before you start:
- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Run `./setup.sh`
- [ ] Test with `python test_system.py`
- [ ] Try `python examples.py`
- [ ] Ingest test data
- [ ] Query test data

For development:
- [ ] Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- [ ] Review [API_REFERENCE.md](API_REFERENCE.md)
- [ ] Study `interfaces/`
- [ ] Study `services/`
- [ ] Run all examples
- [ ] Understand SOLID principles

## 📞 Quick Reference

**Start here:** [QUICKSTART.md](QUICKSTART.md)  
**Full docs:** [README.md](../README.md)  
**API docs:** [API_REFERENCE.md](API_REFERENCE.md)  
**Architecture:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)  

**Run setup:** `./setup.sh`  
**Run tests:** `python test_system.py`  
**Run examples:** `python examples.py`  
**CLI help:** `python main.py --help`

---

**Ready to get started?** → [QUICKSTART.md](QUICKSTART.md)

**Need the full picture?** → [README.md](../README.md)

**Want to dive deep?** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

