# Tests Directory

This directory contains all test files and verification scripts for the Choreo AI Assistant.

## Test Files

### URL Validation & Repository Tests
- **test_separate_repos.py** - Tests for separate repository structure (wso2-enterprise)
- **test_choreo_monorepo.py** - Tests for monorepo structure validation
- **test_choreo_registry_simple.py** - Simple registry tests
- **test_registry_direct.py** - Direct registry import tests
- **test_choreo_url_validation.py** - URL validation tests
- **test_url_validation.py** - General URL validation

### Feature Tests
- **test_conversation_memory.py** - Conversation memory functionality tests

### Verification Scripts
- **verify_asyncio_fix.py** - Asyncio implementation verification
- **verify_milvus_migration.py** - Milvus migration verification

### Utility Scripts
- **search_wso2_choreo_repos.py** - Script to search WSO2 Choreo repositories

## Running Tests

### Run all tests:
```bash
cd tests
python -m pytest
```

### Run specific test:
```bash
python test_separate_repos.py
```

### Run with verbose output:
```bash
python -m pytest -v
```

## Test Coverage

Tests cover:
- ✅ URL validation and correction
- ✅ Repository registry functionality
- ✅ Conversation memory management
- ✅ Database migrations
- ✅ Async operations

## Notes

- All tests should pass before deploying
- Run verification scripts after major changes
- Keep test data separate from production data

