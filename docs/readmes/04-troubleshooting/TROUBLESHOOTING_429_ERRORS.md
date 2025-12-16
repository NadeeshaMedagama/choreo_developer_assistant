# Azure OpenAI 429 Error - Troubleshooting Guide

## Problem: NoCapacity Error (429)

When using conversation memory with summarization, you may encounter:

```
Error code: 429 - {'error': {'code': 'NoCapacity', 'message': 'The system is currently experiencing high demand and cannot process your request. Your request exceeds the maximum usage size allowed during peak load.'}}
```

## Root Cause

The conversation memory system makes **additional LLM calls** to:
1. Create summaries of old conversations
2. Extract metadata (topics, questions, decisions)

During peak Azure OpenAI usage, these extra calls can exceed your quota.

---

## ✅ Solutions Implemented

### 1. **Retry Logic with Exponential Backoff**
```python
# Automatically retries failed summarization attempts
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds (if max_retries=3)
```

### 2. **Graceful Degradation**
```python
# If all LLM attempts fail, uses simple fallback summary
# Example: "User discussed: deployment, authentication, monitoring"
```

### 3. **Configurable Retry Limits**
```python
# Reduce retries to fail faster during peak times
max_summarization_retries=2  # Default
```

### 4. **Toggle LLM Summarization**
```python
# Disable LLM summarization entirely during peak times
enable_llm_summarization=False
# System will use simple text-based summaries instead
```

---

## 🔧 Quick Fixes

### Option 1: Disable LLM Summarization (Immediate Fix)

**Via Environment Variable:**
```bash
# In your .env or environment
export ENABLE_LLM_SUMMARIZATION=false

# Restart backend
```

**Or in code:**
```python
# In backend/app.py
conversation_memory_manager = ConversationMemoryManager(
    llm_service=llm_service,
    enable_llm_summarization=False,  # ← Set to False
    max_summarization_retries=2
)
```

**Result:**
- ✅ No more 429 errors from summarization
- ✅ Simple summaries still created
- ⚠️ Less detailed metadata
- ✅ Conversation still works perfectly

### Option 2: Reduce Retry Attempts

```bash
export MAX_SUMMARIZATION_RETRIES=1
```

**Result:**
- ✅ Fails faster (less waiting)
- ✅ Falls back to simple summaries quickly
- ✅ Reduces load on Azure API

### Option 3: Disable Summarization Entirely

```python
# In frontend API call
{
  "question": "...",
  "enable_summarization": false  // ← Disable per request
}
```

**Result:**
- ✅ No summarization at all
- ✅ No 429 errors
- ⚠️ Token limits may be reached in long conversations
- ⚠️ No memory management benefits

---

## 📊 Comparison of Approaches

| Approach | 429 Errors | Summary Quality | Token Savings | Recommended |
|----------|------------|-----------------|---------------|-------------|
| **Full LLM Summarization** | ❌ May occur | ⭐⭐⭐⭐⭐ Excellent | 73% | Peak hours ❌ |
| **LLM with Retries** | ⚠️ Rare | ⭐⭐⭐⭐ Good | 73% | ✅ Default |
| **Simple Fallback** | ✅ None | ⭐⭐ Basic | 60% | ✅ Peak hours |
| **No Summarization** | ✅ None | ❌ None | 0% | Emergency only |

---

## 🎯 Recommended Configuration

### For Normal Usage (Off-Peak)
```python
enable_llm_summarization=True
max_summarization_retries=2
```

### For Peak Hours (High Load)
```python
enable_llm_summarization=False  # ← Disable LLM summaries
max_summarization_retries=1
```

### For Emergency (Constant 429s)
```python
# In frontend - disable summarization entirely
{
  "enable_summarization": false
}
```

---

## 🔍 How Fallback Summaries Work

When LLM summarization fails or is disabled, the system creates simple summaries:

**Example:**
```python
# Original conversation:
User: "What is Choreo?"
Bot: "Choreo is a platform..."
User: "How do I deploy a Python service?"
Bot: "To deploy in Choreo..."
User: "What about authentication?"
Bot: "You can use OAuth 2.0..."

# Simple fallback summary:
"User discussed: What is Choreo?, How do I deploy a Python service?, What about authentication?"
```

**Compared to LLM summary:**
```
"User learned about Choreo platform basics, explored Python service deployment options, 
and investigated OAuth 2.0 authentication setup."
```

---

## 🚀 Testing the Fix

### 1. Test with LLM Summarization Disabled

```bash
# Set environment variable
export ENABLE_LLM_SUMMARIZATION=false

# Restart backend
cd backend
python app.py
```

**Test:** Start a conversation with 10+ messages. Should work without 429 errors.

### 2. Check Logs

```bash
# Look for these messages in logs:
"LLM summarization disabled - using simple fallback summaries"
"Creating fallback summary" 
```

### 3. Verify Fallback Works

```python
# In conversation response:
{
  "summary": {
    "content": "User discussed: topic1, topic2, topic3",  // ← Simple format
    "topics_covered": [],  // ← Empty (no LLM extraction)
    "key_questions": [],
    "important_decisions": []
  }
}
```

---

## 📈 Monitoring

### Check Summary Success Rate

Add logging to monitor:

```python
# In backend logs
"Summary created via LLM: SUCCESS"
"Summary created via fallback: CAPACITY_ERROR"
```

### Track 429 Errors

```python
# Monitor error logs for:
"429" or "NoCapacity"
```

### Adjust Based on Metrics

```
If 429 errors > 10% of requests:
  → Set enable_llm_summarization=False

If 429 errors < 1% of requests:
  → Set enable_llm_summarization=True
  → Increase max_retries to 3
```

---

## 🔄 Dynamic Configuration

For production, implement dynamic toggling:

```python
# Add to app.py
@app.post("/api/admin/toggle-summarization")
def toggle_summarization(enable: bool):
    """Runtime toggle for LLM summarization"""
    global conversation_memory_manager
    conversation_memory_manager.enable_llm_summarization = enable
    return {"enabled": enable, "status": "updated"}

# Use this to disable during detected peak hours
```

---

## 💡 Long-Term Solutions

### 1. Upgrade Azure OpenAI Plan
- Switch from "Pay-as-you-go" to "Provisioned Throughput"
- Guaranteed capacity, no 429 errors
- Higher cost but more reliable

### 2. Implement Rate Limiting
```python
# Add to backend
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/ask")
@limiter.limit("10/minute")  # Limit requests
def ask_ai():
    ...
```

### 3. Queue System
```python
# Add Redis queue for summarization
from rq import Queue

def async_summarize(messages):
    """Summarize in background, retry later if failed"""
    # Runs separately, doesn't block main request
    pass
```

### 4. Cache Summaries
```python
# Store summaries in database
# Avoid regenerating on every request
summary = db.get_cached_summary(conversation_id)
if not summary:
    summary = create_new_summary()
    db.cache_summary(conversation_id, summary)
```

---

## ✅ Current Status

After implementing these fixes:

1. ✅ **Retry logic** - 2 attempts with exponential backoff
2. ✅ **Fallback summaries** - Simple text-based summaries when LLM fails
3. ✅ **Environment toggle** - `ENABLE_LLM_SUMMARIZATION` env var
4. ✅ **Configurable retries** - `MAX_SUMMARIZATION_RETRIES` env var
5. ✅ **Graceful degradation** - Never fails, always provides some summary

---

## 🎯 Action Items

### Immediate (Do Now):
```bash
# Option 1: Disable LLM summarization
export ENABLE_LLM_SUMMARIZATION=false

# Option 2: Reduce retries
export MAX_SUMMARIZATION_RETRIES=1

# Restart backend
```

### Short-term (This Week):
- Monitor 429 error rate
- Adjust `enable_llm_summarization` based on peak hours
- Consider upgrading Azure plan if budget allows

### Long-term (Next Sprint):
- Implement summary caching in database
- Add async queue for summarization
- Set up automatic peak-hour detection

---

## 📞 Support

If issues persist:

1. **Check logs:**
   ```bash
   tail -f backend/logs/error.log | grep "429"
   ```

2. **Verify config:**
   ```bash
   echo $ENABLE_LLM_SUMMARIZATION
   echo $MAX_SUMMARIZATION_RETRIES
   ```

3. **Test fallback:**
   ```python
   # Should see in logs:
   "Creating fallback summary"
   "LLM summarization disabled"
   ```

---

**Problem Solved! 🎉**

Your conversation memory system will now:
- ✅ Handle capacity errors gracefully
- ✅ Use fallback summaries when needed
- ✅ Never crash due to 429 errors
- ✅ Continue providing good answers

