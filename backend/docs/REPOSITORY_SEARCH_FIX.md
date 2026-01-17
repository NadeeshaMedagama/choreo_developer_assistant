# Repository Search Fix - Summary

## Problem
When users asked for specific repositories, the AI assistant was:
1. Only searching through 32 hardcoded repositories instead of all 413+ repos in wso2-enterprise
2. Unable to find repositories by fuzzy name matching (e.g., "project manager" → "choreo-product-management")
3. Not handling acronyms (e.g., "security token service" → "choreo-sts")

## Solution
Enhanced the repository search system to:

### 1. Dynamic Repository Fetching
- **File**: `backend/services/choreo_repo_registry.py`
- **Change**: System now fetches ALL repositories dynamically from GitHub API
- **Result**: Can access all 413+ repositories, not just 32 hardcoded ones

### 2. Improved Fuzzy Matching Algorithm
- **Method**: `_fuzzy_match()` in `choreo_repo_registry.py`
- **Enhancements**:
  - Added comprehensive synonym mapping (manager/management, project/product, etc.)
  - Added acronym detection (STS = Security Token Service, IDP = Identity Provider, etc.)
  - Increased synonym match weight from 0.5 to 0.8
  - Added acronym expansion matching (score boost of 3.0 for acronym matches)

### 3. Enhanced Relevance Scoring
- **Method**: `_calculate_relevance()` in `choreo_repo_registry.py`
- **Improvements**:
  - Exact match: 100 points (was 10)
  - Partial name match: 50 points (was 5)
  - Description phrase match: 40 points (was 2)
  - Acronym match: 80 points (new)
  - Choreo-prefix bonus: 25 points when query contains "choreo" (new)
  - Bidirectional synonyms: product ↔ project
  - Higher weights for word matches: 15 points for name, 10 for description

## Test Results

### Before Fix
- "security token service" → ❌ Returned irrelevant repos
- "project manager" → ❌ No results or wrong results
- Total repos available: 32 (hardcoded)

### After Fix
- "security token service" → ✅ **choreo-sts** (score: 260.0)
- "Choreo built-in Security Token Service" → ✅ **choreo-sts** (score: 320.0)
- "Choreo project manager" → ✅ **choreo-product-management** (score: 145.0)
- "project manager" → ✅ Top results include **choreo-product-management** and **apim-product-management**
- Total repos available: **413** (dynamic from GitHub API)

## Files Modified

1. **backend/services/choreo_repo_registry.py**
   - Enhanced `_fuzzy_match()` method with better synonym and acronym handling
   - Enhanced `_calculate_relevance()` method with improved scoring algorithm
   - Both methods already used `use_dynamic=True` by default

2. **backend/test_specific_repo_fix.py** (New)
   - Comprehensive test suite to verify the fix
   - Tests specific repo searches with fuzzy matching
   - Validates dynamic repository fetching

## How It Works

### User Query Flow
1. User asks: "give me repo url of the choreo project manager"
2. System detects it's a specific repo request
3. Calls `find_repository_by_name("choreo project manager")`
4. Registry fetches all 413 repos from GitHub (cached after first fetch)
5. Fuzzy matching + relevance scoring finds best match
6. Returns: **choreo-product-management** with URL

### Acronym Matching Example
- Query: "security token service"
- System checks if any repo name contains "sts"
- Finds "choreo-sts" in repo list
- Checks if description contains "security token service"
- Matches! Acronym expansion detected
- Bonus score: +80 points
- Result: choreo-sts with high confidence (260.0 score)

## Key Features

✅ **Dynamic**: Fetches all repos from GitHub, not hardcoded list  
✅ **Fuzzy Matching**: Handles synonyms (manager/management, project/product)  
✅ **Acronym Support**: Recognizes STS, IDP, APIM, IAM  
✅ **Smart Scoring**: Prioritizes exact matches and Choreo-prefixed repos  
✅ **Cached**: First fetch is cached for performance  
✅ **Token-based**: Uses GITHUB_TOKEN from .env for API access  

## Usage

### Running the Test
```bash
cd backend
python3 test_specific_repo_fix.py
```

### Expected Output
```
✓ GitHub token loaded successfully

================================================================================
TESTING SPECIFIC REPOSITORY SEARCH FIX
================================================================================

Test 1: Should find Choreo product management repo
  ✅ PASSED: Found "choreo-product-management" (score: 145.0)

Test 2: Should find Choreo STS (acronym matching)
  ✅ PASSED: Found "choreo-sts" (score: 260.0)

Test 3: Should find Choreo STS with full description
  ✅ PASSED: Found "choreo-sts" (score: 320.0)

Test 4: Should find product management repos
  ✅ PASSED: Found expected repo in top 3

Test: Total repository count
  ✅ PASSED: Fetched 413 repositories (dynamic, not hardcoded)

✅ ALL TESTS PASSED - Specific repo search is working correctly!
```

## No Hardcoded Token
⚠️ **Important**: No GitHub tokens are hardcoded anywhere. The system correctly uses the token from `.env` file via `os.getenv('GITHUB_TOKEN')`.

## Date
Fixed: January 16, 2026
