# Backend Tests Directory

## Overview
This directory contains all test scripts for the Choreo AI Assistant backend.

## Test Files

| File | Purpose | Usage |
|------|---------|-------|
| `test_backend.py` | Verify backend app initialization | Tests FastAPI app and services |
| `test_github.py` | Test GitHub API connectivity | Validates GitHub token and repo access |
| `test_chunking.py` | Test markdown chunking | Demonstrates chunking functionality |
| `test_chunking_simple.py` | Simple chunking validation | Quick chunking test |
| `test_org_search.py` | Test organization repo search | Search WSO2 org for Choreo repos |
| `test_token.py` | Test GitHub token auth | Validates GitHub token |

## Running Tests

### From Project Root
```bash
# Test backend initialization
python backend/tests/test_backend.py

# Test GitHub connectivity
python backend/tests/test_github.py

# Test chunking functionality
python backend/tests/test_chunking.py
```

### From Backend Directory
```bash
cd backend
python tests/test_github.py
python tests/test_backend.py
```

### From Tests Directory
```bash
cd backend/tests
python test_github.py
python test_backend.py
```

## Migration Notes

**✅ Test files were moved from project root to `backend/tests/` on Nov 10, 2025**

### What Changed:
- All `test_*.py` files moved from root to `backend/tests/`
- Path resolution updated to use relative imports
- Documentation updated to reflect new location

### Why This Change:
1. **Better Organization**: Groups all tests together
2. **Cleaner Project Root**: Reduces clutter in main directory
3. **Deployment Ready**: Test files not needed in production builds
4. **Standard Practice**: Follows Python project conventions

### Updated Files:
- `backend/tests/test_*.py` - All test files updated with correct paths
- `backend/check_setup.py` - Updated reference to test_github.py
- `docs/readmes/SETUP_GUIDE.md` - Updated test commands
- `docs/readmes/DOCKER_README.md` - Updated Docker test commands
- `docs/readmes/DOCKER_QUICK_REFERENCE.md` - Updated quick reference
- `docs/readmes/ENV_FILE_LOCATION.md` - Updated directory structure

## Environment Setup

All tests automatically load environment variables from `backend/.env`:
```python
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)
```

## Expected Results

### test_backend.py
```
Testing backend imports...
✓ Backend app imported successfully!
✓ All services initialized!

Backend is ready to run!
```

### test_github.py
```
🔍 Testing GitHub API Access...
GitHub Token present: Yes

📡 Testing repository access...
Fetching contents from: NadeeshaMedagama/docs-choreo-dev
✓ Repository accessible!
✓ Found 3 items in root

📄 Searching for .md files...
✓ Found 34 markdown files
```

### test_chunking.py
```
CHUNKING REQUIREMENTS
Minimum chunk size:        2000 characters
Maximum chunk size:        4000 characters
Overlap between chunks:    200 characters
```

## Troubleshooting

### Import Errors
**Issue**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Run from project root:
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python backend/tests/test_github.py
```

### Environment Not Loaded
**Issue**: "No GITHUB_TOKEN found"

**Solution**: Ensure `backend/.env` exists with required variables:
```bash
cat backend/.env | grep GITHUB_TOKEN
```

## Future Improvements

- [ ] Add pytest integration
- [ ] Add unit tests for individual services
- [ ] Add integration tests
- [ ] Add test coverage reporting
- [ ] Add CI/CD test automation

