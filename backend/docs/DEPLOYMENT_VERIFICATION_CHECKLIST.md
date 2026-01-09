# Deployment Verification Checklist

## Pre-Deployment
- [x] Enhanced exception logging in metrics middleware
- [x] Added service initialization check in streaming endpoint
- [x] Improved error handling in async generator
- [x] Changed top-level exception handler to return JSON response
- [x] Added progress logging throughout streaming pipeline
- [x] No syntax errors detected

## Post-Deployment Steps

### 1. Verify Application Starts Successfully
```bash
# Check logs for successful initialization
# Look for: "Application startup complete" or similar
```

### 2. Test Streaming Endpoint
```bash
# Make a test request to the streaming endpoint
curl -X POST https://your-choreo-url/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'
```

### 3. Monitor Logs for New Error Details

**What to look for:**
- Exception type names (e.g., `AttributeError`, `TypeError`)
- "Unhandled exception in request processing: [ExceptionType]:"
- "Streaming generator failed - [ExceptionType]:"
- Stack traces with full context

**Example of what you should now see:**
```
ERROR: Unhandled exception in request processing: AttributeError: 'NoneType' object has no attribute 'client'
  method=POST
  path=/api/ask/stream
  error_type=AttributeError
  [Full stack trace follows]
```

### 4. Common Error Patterns and Solutions

#### If logs show: `RuntimeError: Services not initialized`
**Solution:** Check environment variables are set correctly:
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `MILVUS_URI`
- `MILVUS_TOKEN`

#### If logs show: `AttributeError: 'NoneType' object has no attribute 'client'`
**Solution:** LLM service failed to initialize - verify Azure OpenAI credentials

#### If logs show: `ConnectionError` or `Timeout`
**Solution:** Network connectivity issue - check:
- Azure OpenAI endpoint reachability
- Milvus connection
- Firewall/security group rules

#### If logs show: `KeyError` or `ValueError`
**Solution:** Data validation issue - check request payload format

### 5. Specific Tests

#### Test 1: Basic Question
```json
{
  "question": "What is Choreo?"
}
```
Expected: Successful streaming response

#### Test 2: With Conversation History
```json
{
  "question": "Tell me more",
  "conversation_history": [
    {"role": "user", "content": "What is Choreo?"},
    {"role": "assistant", "content": "Choreo is..."}
  ]
}
```
Expected: Successful streaming with context

#### Test 3: Invalid Request (Error Handling)
```json
{
  "question": ""
}
```
Expected: Proper error response with details

### 6. Log Analysis Commands

```bash
# Filter for streaming endpoint errors
grep "Streaming.*failed" /path/to/logs

# Look for exception types
grep "error_type=" /path/to/logs

# Check for initialization errors
grep "Services not initialized" /path/to/logs

# View full error context
grep -A 20 "Unhandled exception" /path/to/logs
```

## Success Criteria

✅ Application starts without errors  
✅ Health endpoint responds with 200  
✅ Streaming endpoint returns responses OR clear error messages  
✅ Logs now show exception types and full stack traces  
✅ Error responses are JSON formatted with proper status codes  

## Rollback Plan

If issues persist after deployment:

1. The changes are backward compatible - they only enhance logging
2. No breaking changes to API contracts
3. Can safely revert by restoring previous versions of:
   - `monitoring/middleware/metrics_middleware.py`
   - `app.py`

## Additional Monitoring

Monitor Choreo metrics for:
- Error rate on `/api/ask/stream`
- Response times
- 5xx error codes
- Memory usage (ensure no memory leaks from exception handling)

