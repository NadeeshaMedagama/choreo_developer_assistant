# 🚨 QUICK FIX: Azure OpenAI 429 Errors

## Problem
```
Error code: 429 - NoCapacity
```

## Immediate Solution (Choose One)

### ⚡ Option 1: Disable LLM Summarization (RECOMMENDED)

**In terminal:**
```bash
export ENABLE_LLM_SUMMARIZATION=false
cd backend
python app.py
```

**Result:** ✅ No more 429 errors, uses simple text summaries

---

### ⚡ Option 2: Quick Code Change

**Edit `backend/app.py` line ~80:**
```python
enable_llm_summarization = False  # Changed from True
```

**Restart backend**

---

### ⚡ Option 3: Reduce Retries

**In terminal:**
```bash
export MAX_SUMMARIZATION_RETRIES=1
cd backend  
python app.py
```

**Result:** ✅ Fails faster, less waiting

---

## What These Fixes Do

| Fix | 429 Errors | Summary Quality | Setup Time |
|-----|------------|-----------------|------------|
| **Disable LLM** | ✅ Eliminated | ⭐⭐ Basic | 30 seconds |
| **Reduce Retries** | ⚠️ Reduced | ⭐⭐⭐ Good | 30 seconds |
| **Keep Current** | ❌ May occur | ⭐⭐⭐⭐⭐ Excellent | 0 |

---

## Test It Works

1. Start backend
2. Ask 10+ questions in UI
3. Check logs - should see:
   ```
   "Creating fallback summary"
   ```
4. No 429 errors! ✅

---

## Revert Back Later

When Azure capacity is better:
```bash
export ENABLE_LLM_SUMMARIZATION=true
# Restart backend
```

---

## Full Details

See: `TROUBLESHOOTING_429_ERRORS.md`

