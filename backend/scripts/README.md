# Backend Scripts

This directory contains utility scripts for development, debugging, data fetching, and ingestion operations.

## Directory Structure

```
backend/scripts/
├── debug/          # Debugging and diagnostic scripts
├── fetch/          # Data fetching scripts
├── ingest/         # Data ingestion scripts
└── README.md       # This file
```

## Script Categories

### 1. Debug Scripts (`debug/`)
Scripts for debugging GitHub API access and troubleshooting issues.

| Script | Purpose | Usage |
|--------|---------|-------|
| `debug_github_access.py` | Test GitHub org access and find repos | `python backend/scripts/debug/debug_github_access.py` |
| `debug_github_repos.py` | Check GitHub API and repo visibility | `python backend/scripts/debug/debug_github_repos.py` |

### 2. Fetch Scripts (`fetch/`)
Scripts for fetching README and documentation files from GitHub.

| Script | Purpose | Usage |
|--------|---------|-------|
| `fetch_all_choreo_readmes.py` | Fetch all READMEs from Choreo repos | `python backend/scripts/fetch/fetch_all_choreo_readmes.py` |
| `fetch_choreo_readmes_standalone.py` | Standalone fetcher (no dependencies) | `python backend/scripts/fetch/fetch_choreo_readmes_standalone.py` |

### 3. Ingest Scripts (`ingest/`)
Scripts for ingesting markdown files into Pinecone vector database.

| Script | Purpose | Usage |
|--------|---------|-------|
| `ingest_wso2_choreo_repos.py` | Ingest from WSO2 org repos | `python backend/scripts/ingest/ingest_wso2_choreo_repos.py` |
| `ingest_choreo_readmes.py` | Ingest downloaded READMEs | `python backend/scripts/ingest/ingest_choreo_readmes.py` |
| `ingest_choreo_readmes_standalone.py` | Standalone ingestion | `python backend/scripts/ingest/ingest_choreo_readmes_standalone.py` |

## Usage Examples

### Debug GitHub Access
```bash
# Test GitHub organization access
python backend/scripts/debug/debug_github_access.py

# Check specific repository visibility
python backend/scripts/debug/debug_github_repos.py
```

### Fetch Documentation
```bash
# Fetch all Choreo READMEs
python backend/scripts/fetch/fetch_all_choreo_readmes.py
```

### Ingest into Vector Database
```bash
# Ingest from WSO2 organization (with options)
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --max-repos 5

# Ingest previously fetched READMEs
python backend/scripts/ingest/ingest_choreo_readmes.py
```

## Migration Notes

**✅ Scripts moved from project root on Nov 10, 2025**

### Previous Locations → New Locations
```
debug_github_access.py    → backend/scripts/debug/debug_github_access.py
debug_github_repos.py     → backend/scripts/debug/debug_github_repos.py
fetch_*.py                → backend/scripts/fetch/fetch_*.py
ingest_*.py               → backend/scripts/ingest/ingest_*.py
```

### What Changed
- All scripts now use relative path resolution
- Updated imports to work from new locations
- Documentation updated to reflect new paths
- Environment loading adjusted for new directory structure

### Why This Change
1. **Better Organization** - Scripts grouped by function
2. **Cleaner Root** - Reduces clutter in main directory
3. **Professional Structure** - Follows Python best practices
4. **Easier Maintenance** - Related scripts together

## Environment Setup

All scripts automatically load environment variables from `backend/.env`:
```python
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent.parent.parent
env_path = project_root / 'backend' / '.env'
load_dotenv(env_path)
```

## Requirements

Ensure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

Required environment variables in `backend/.env`:
```
GITHUB_TOKEN=ghp_...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
MILVUS_URI=...
MILVUS_TOKEN=...
MILVUS_COLLECTION_NAME=choreo_developer_assistant
```

## Common Issues

### Import Errors
**Issue**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Always run from project root:
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python backend/scripts/ingest/ingest_wso2_choreo_repos.py
```

### Environment Not Loaded
**Issue**: "GITHUB_TOKEN not found"

**Solution**: Ensure `backend/.env` exists:
```bash
cat backend/.env | grep GITHUB_TOKEN
```

## Development

### Adding New Scripts

1. Choose appropriate directory (debug/fetch/ingest)
2. Create script with proper imports:
```python
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.github_service import GitHubService
```

3. Update this README with script details

### Testing Scripts

Test that scripts work from new location:
```bash
python backend/scripts/debug/debug_github_access.py
python backend/scripts/fetch/fetch_all_choreo_readmes.py
python backend/scripts/ingest/ingest_wso2_choreo_repos.py
```

## See Also

- [Test Scripts](../tests/README.md) - Test and validation scripts
- [Main Documentation](../../docs/readmes/) - Full project documentation

