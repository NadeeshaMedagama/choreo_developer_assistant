# ✅ FIXED: Server Startup Issue

## Problem
```
IndentationError: unindent does not match any outer indentation level
```

## Root Cause
There was **duplicate content** in `app.py` after the system prompt string. Old monorepo references were left in the file after editing.

## Solution
- ✅ Removed duplicate lines (335-346 in app.py)
- ✅ Fixed system prompt to use **wso2-enterprise** organization
- ✅ Updated all references from wso2 to wso2-enterprise
- ✅ Cleaned up indentation errors

## Files Fixed
1. ✅ `backend/app.py` - Removed duplicate content, fixed syntax
2. ✅ `backend/services/llm_service.py` - Updated to wso2-enterprise
3. ✅ `backend/services/choreo_repo_registry.py` - Updated to wso2-enterprise

## Verified
- No more Python syntax errors
- Server should start successfully now
- All URLs will use wso2-enterprise organization

## Try Starting Server
```bash
cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Should work now! ✅

