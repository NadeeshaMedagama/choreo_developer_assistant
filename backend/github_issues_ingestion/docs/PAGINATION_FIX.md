# GitHub API Pagination Fix

## Problem
The ingestion pipeline was crashing with a `422 Unprocessable Entity` error when trying to fetch issues from repositories with more than 1000 issues (like `wso2-enterprise/choreo`).

**Error:**
```
422 Client Error: Unprocessable Entity for url: 
https://api.github.com/repos/wso2-enterprise/choreo/issues?state=all&per_page=100&page=100
```

## Root Cause
GitHub's REST API has a hard limit on pagination:
- Maximum of **1000 results** can be fetched through standard pagination
- This equals 10 pages × 100 items per page
- Attempting to access page 11 or higher results in a 422 error

The code was trying to fetch all issues without checking this limit, causing it to crash when it reached page 100.

## Solution
Implemented a two-tier fix in `github_issue_fetcher.py`:

### 1. Pagination Limit Guard
Added checks in `_make_paginated_request()` to:
- Stop at page 10 (1000 items) to respect GitHub's limit
- Catch and handle 422 errors gracefully
- Log warnings when limits are reached instead of crashing

```python
# GitHub API has a hard limit of 1000 results (10 pages of 100 items)
max_pages = 10

while True:
    # Check if we've hit GitHub's pagination limit
    if page > max_pages:
        print(f"Warning: Reached GitHub's pagination limit...")
        break
    
    try:
        items = self._make_request(url, params)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print(f"Warning: Pagination limit reached...")
            break
        raise  # Re-raise other errors
```

### 2. Search API Fallback (Optional Enhancement)
Added `_fetch_issues_via_search()` method that:
- Uses GitHub's Search API for repositories with >1000 issues
- Provides an alternative way to fetch additional issues
- Automatically merges results while avoiding duplicates
- Handles search-specific rate limits

## Benefits
1. **No More Crashes**: The pipeline completes successfully even with large repositories
2. **Graceful Degradation**: Fetches up to 1000 issues and logs a warning instead of failing
3. **Extensibility**: Search API method provides a path to fetch more issues in the future
4. **Better Error Handling**: Catches 422 errors specifically and handles them appropriately

## Testing
Created `test_pagination_fix.py` to verify the fix works with the problematic repository.

Run test:
```bash
cd backend
GITHUB_TOKEN=your_token python github_issues_ingestion/test_pagination_fix.py
```

## Recommendations
For production use with repositories having >1000 issues, consider:
1. Using incremental updates with the `since` parameter to fetch only recent issues
2. Implementing the Search API fallback for comprehensive coverage
3. Setting a reasonable `max_issues` limit based on your needs
4. Using issue labels to filter and reduce the total count

## Files Modified
- `backend/github_issues_ingestion/services/github_issue_fetcher.py`
  - Updated `_make_paginated_request()` with limit checks
  - Added `_fetch_issues_via_search()` for Search API fallback
  - Enhanced `fetch_issues()` to use both methods intelligently

## Files Created
- `backend/github_issues_ingestion/test_pagination_fix.py` - Test script
- `backend/github_issues_ingestion/PAGINATION_FIX.md` - This document

