# Troubleshooting & Fixes

This directory contains solutions to common problems and known issues with DevChoreo.

## 🔥 Common Issues

### Azure OpenAI Errors

#### 429 - Rate Limit / NoCapacity Errors
- **[TROUBLESHOOTING_429_ERRORS.md](./TROUBLESHOOTING_429_ERRORS.md)** - Complete guide for handling Azure OpenAI rate limits
- **[QUICK_FIX_429.md](./QUICK_FIX_429.md)** - Quick fixes for 429 errors

**Quick Fix:**
```bash
# Disable LLM summarization during peak times
export ENABLE_LLM_SUMMARIZATION=false
```

#### 422 - Validation Errors
- **[FIX_422_ERROR.md](./FIX_422_ERROR.md)** - Fix for 422 validation errors

### Application Errors

#### Memory Issues
- **[MEMORY_FIX_SUMMARY.md](./MEMORY_FIX_SUMMARY.md)** - Memory-related fixes
- **[MEMORY_LAG_FIX.md](./MEMORY_LAG_FIX.md)** - Fixing memory lag issues
- **[OVERFLOW_FIXES.md](./OVERFLOW_FIXES.md)** - Buffer overflow and memory overflow fixes

#### Crashes
- **[CRASH_ANALYSIS_AND_FIXES.md](./CRASH_ANALYSIS_AND_FIXES.md)** - Analysis and solutions for application crashes

### Feature-Specific Issues

#### Source Citations
- **[FIX_SOURCES_NOT_SHOWING.md](./FIX_SOURCES_NOT_SHOWING.md)** - Fix when sources don't appear

#### Content Filtering
- **[FIX_OPENCHOREO_FILTERING.md](./FIX_OPENCHOREO_FILTERING.md)** - Fix OpenChoreo content appearing in results
- **[CHANGES_OPENCHOREO_FIX.md](./CHANGES_OPENCHOREO_FIX.md)** - Changes made to fix OpenChoreo filtering

## 🔍 Troubleshooting by Symptom

### "Sources not showing"
→ See [FIX_SOURCES_NOT_SHOWING.md](./FIX_SOURCES_NOT_SHOWING.md)

### "Error 429 - NoCapacity"
→ See [TROUBLESHOOTING_429_ERRORS.md](./TROUBLESHOOTING_429_ERRORS.md) or [QUICK_FIX_429.md](./QUICK_FIX_429.md)

### "OpenChoreo content in results"
→ See [FIX_OPENCHOREO_FILTERING.md](./FIX_OPENCHOREO_FILTERING.md)

### "Application crashes"
→ See [CRASH_ANALYSIS_AND_FIXES.md](./CRASH_ANALYSIS_AND_FIXES.md)

### "Memory issues / lag"
→ See [MEMORY_FIX_SUMMARY.md](./MEMORY_FIX_SUMMARY.md) or [MEMORY_LAG_FIX.md](./MEMORY_LAG_FIX.md)

### "Validation error 422"
→ See [FIX_422_ERROR.md](./FIX_422_ERROR.md)

### "Buffer overflow"
→ See [OVERFLOW_FIXES.md](./OVERFLOW_FIXES.md)

## 🛠️ Quick Diagnostic Steps

### 1. Check Logs
```bash
# Application logs
tail -f logs/app.log

# Error logs only
tail -f logs/error.log

# AI operations
tail -f logs/ai.log
```

### 2. Check Health Endpoints
```bash
# Backend health
curl http://localhost:8000/api/health

# Metrics
curl http://localhost:8000/metrics
```

### 3. Check Environment Variables
```bash
# Verify critical env vars are set
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_KEY
echo $MILVUS_URI
```

### 4. Check Dependencies
```bash
# Backend
pip list | grep -E "(openai|pymilvus|fastapi)"

# Frontend
npm list react vite
```

## 📊 Common Error Codes

| Error Code | Issue | Solution |
|------------|-------|----------|
| 429 | Rate limit / NoCapacity | [TROUBLESHOOTING_429_ERRORS.md](./TROUBLESHOOTING_429_ERRORS.md) |
| 422 | Validation error | [FIX_422_ERROR.md](./FIX_422_ERROR.md) |
| 500 | Server error | Check logs, [CRASH_ANALYSIS_AND_FIXES.md](./CRASH_ANALYSIS_AND_FIXES.md) |
| CORS | CORS error | Check [FRONTEND_BACKEND_CONNECTION.md](../03-deployment/FRONTEND_BACKEND_CONNECTION.md) |

## 🔧 Performance Issues

### Slow Responses
1. Check Azure OpenAI quota
2. Verify Pinecone index health
3. Reduce `top_k` in retrieval
4. Disable summarization temporarily
5. Check network latency

### High Memory Usage
1. Check conversation history size
2. Enable summarization
3. Lower `max_history_tokens`
4. Clear old conversations
5. See [MEMORY_FIX_SUMMARY.md](./MEMORY_FIX_SUMMARY.md)

### Streaming Not Working
1. Check `/api/ask/stream` endpoint
2. Verify frontend uses streaming
3. Check for CORS issues
4. Fall back to standard `/api/ask`
5. See [STREAMING_IMPLEMENTATION.md](../02-features/STREAMING_IMPLEMENTATION.md)

## 🆘 Getting Help

### Before Asking for Help
1. Check this troubleshooting directory
2. Review logs for error messages
3. Test with minimal configuration
4. Verify environment variables
5. Check the main [INDEX.md](../INDEX.md)

### When Reporting Issues
Include:
- Error message (from logs)
- Steps to reproduce
- Environment details
- Configuration (without secrets)
- What you've already tried

## 🔗 Related Documentation

- **Getting Started**: See [../01-getting-started/](../01-getting-started/)
- **Features**: See [../02-features/](../02-features/)
- **Deployment**: See [../03-deployment/](../03-deployment/)
- **Implementation Notes**: See [../05-implementation-notes/](../05-implementation-notes/)

---

**Last Updated**: December 2, 2025

