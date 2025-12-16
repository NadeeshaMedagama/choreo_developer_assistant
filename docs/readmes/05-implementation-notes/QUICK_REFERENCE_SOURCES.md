# Quick Reference: Intelligent Source Filtering

## 🎯 What's New

Your Choreo AI Assistant now shows **only the most relevant sources** for every question!

---

## ✅ Two Major Fixes

### 1. No More OpenChoreo Sources
- **Before**: OpenChoreo repos sometimes appeared
- **After**: 100% WSO2 Choreo sources only

### 2. Only Highly Relevant Sources
- **Before**: Mixed quality (48%-96% relevance)
- **After**: High quality only (75%-100% relevance)

---

## 🔢 The Numbers

### Thresholds:
- **75%** = Minimum relevance for sources shown to users
- **70%** = Minimum relevance for context (what AI uses)
- **60%** = Fallback threshold if limited docs available

### Limits:
- **10** candidates retrieved initially
- **5** high-quality docs used for AI context
- **3** best sources displayed to users

---

## 📊 Quality Guarantee

Every source you see is:
- ✅ ≥75% relevant to your question
- ✅ From WSO2 Choreo only (no OpenChoreo)
- ✅ In top 3 most relevant
- ✅ Sorted by relevance

---

## 🚀 How to Apply

```bash
# Just restart the backend
python -m uvicorn backend.app:app --reload
```

That's it! No other changes needed.

---

## 🧪 How to Test

### Test 1: Ask a Question
```
Question: "How do I deploy a service?"

Check:
✅ Sources shown: 1-3 (not more)
✅ All sources ≥75% relevant
✅ No OpenChoreo sources
✅ All directly about deployment
```

### Test 2: Check Relevance Scores
```
Look at the percentage under each source:

✅ Good: 75% or higher
❌ Should never see: Below 75%
```

### Test 3: Platform Check
```
Look at repository names:

✅ Good: wso2/*, wso2-enterprise/*
❌ Should never see: openchoreo/*
```

---

## 💡 What Changed in Code

### Before:
```python
# Get 5 documents, show all
docs = retrieve(query, top_k=5)
sources = filter_openchoreo(docs)
```

### After:
```python
# Get 10 candidates
docs = retrieve(query, top_k=10)

# Filter OpenChoreo
filtered = filter_openchoreo(docs)

# Use high-quality for context (70%+)
context = [d for d in filtered if d.score > 0.7][:5]

# Show best to users (75%+)
sources = [d for d in filtered if d.score >= 0.75][:3]
```

---

## 🎯 Benefits

1. **Better Answers**
   - AI uses only high-quality context
   - More accurate responses

2. **Cleaner Sources**
   - Max 3 sources
   - All highly relevant

3. **Higher Trust**
   - Every source is verified relevant
   - No confusion with OpenChoreo

4. **Better UX**
   - Easy to find right info
   - No wasted time on irrelevant docs

---

## 📝 Examples

### Deployment Question:
```
Before: 5 sources (only 1 truly relevant)
After:  3 sources (all deployment-focused)
```

### OAuth Question:
```
Before: 5 sources (2 relevant, 3 general)
After:  3 sources (all OAuth-specific)
```

### Conceptual Question:
```
Before: 5 sources (mixed relevance)
After:  3 sources (all highly relevant)
```

---

## ✨ Summary

**File Changed**: `backend/app.py`  
**Lines Modified**: ~50 lines  
**Breaking Changes**: None  
**Frontend Changes**: None  
**Config Changes**: None  

**Result**: Smarter, more relevant sources for every question!

---

## 📚 Full Documentation

- `docs/FIX_OPENCHOREO_FILTERING.md` - OpenChoreo fix details
- `docs/INTELLIGENT_SOURCE_FILTERING.md` - Technical docs
- `docs/SOURCE_QUALITY_VISUAL_GUIDE.md` - Visual examples

---

**Just restart and enjoy smarter sources!** 🎉

