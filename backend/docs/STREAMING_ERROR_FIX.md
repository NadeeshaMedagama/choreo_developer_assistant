# Streaming Endpoint Error Fix

## Problem Analysis

The `/api/ask/stream` endpoint was failing with unhandled exceptions that weren't being properly logged, making debugging difficult.

### Root Causes Identified:

1. **Insufficient Exception Logging**: The middleware and endpoint weren't logging the exception type, only the message
2. **Silent Failures in Async Generator**: Exceptions inside the streaming generator weren't being caught with full details
3. **Poor Error Propagation**: The streaming response could fail during generation without proper error reporting
4. **No Service Initialization Check**: The endpoint didn't verify services were initialized before attempting to use them

## Fixes Applied

### 1. Enhanced Metrics Middleware (`monitoring/middleware/metrics_middleware.py`)

**Changes:**
- Added exception type logging: `error_type=type(e).__name__`
- Improved error message to include exception class name
- Full traceback logging with `exc_info=True`

```python
self._monitoring.log_error(
    f"Unhandled exception in request processing: {type(e).__name__}: {str(e)}",
    logger_type='app',
    exc_info=True,
    method=request.method,
    path=request.url.path,
    error_type=type(e).__name__
)
```

### 2. Streaming Endpoint Improvements (`app.py`)

#### A. Service Initialization Check
Added explicit check at function entry:
```python
if not services_initialized:
    monitoring.log_error(
        "Services not initialized when streaming endpoint called",
        logger_type='ai'
    )
    raise RuntimeError("Services not initialized. Please check application startup.")
```

#### B. Enhanced Generator Exception Handling
- Added logging at key points (Azure OpenAI request start, response collected)
- Included exception type in error logging
- Better error details in streaming error response

```python
except Exception as e:
    monitoring.log_error(
        f"Streaming generator failed - {type(e).__name__}: {str(e)}",
        logger_type='ai',
        exc_info=True,
        error_type=type(e).__name__,
        error_details=str(e)
    )
    yield f"data: {json.dumps({{'error': f'{type(e).__name__}: {str(e)}'}})}}\n\n"
```

#### C. Top-Level Exception Handler
Changed from `raise` to returning a proper JSON error response:
```python
from fastapi.responses import JSONResponse
return JSONResponse(
    status_code=500,
    content={
        "error": type(e).__name__,
        "message": str(e),
        "detail": "Failed to process streaming request. Check server logs for details."
    }
)
```

## Benefits

1. **Better Debugging**: Exception type and full stack traces are now logged
2. **Clearer Error Messages**: Users see the actual error type, not just generic messages
3. **Graceful Degradation**: Errors return proper HTTP 500 with JSON instead of raw exceptions
4. **Early Failure Detection**: Service initialization is checked before attempting operations
5. **Progress Tracking**: Added logging at key points in the streaming pipeline

## Testing Recommendations

After deployment, monitor logs for:
1. Exception type names appearing in logs (e.g., `AttributeError`, `TypeError`, `ValueError`)
2. Service initialization errors at startup
3. Azure OpenAI connection issues
4. URL validation failures

## Common Issues to Watch For

### If you see:
- **`AttributeError`**: Likely accessing a property that doesn't exist (check llm_service, context_manager initialization)
- **`TypeError`**: Argument mismatch or None value where object expected (check Azure OpenAI client)
- **`RuntimeError: Services not initialized`**: Application startup failed, check environment variables
- **`ConnectionError`**: Network issues with Azure OpenAI or Milvus

## Next Steps

1. Deploy the changes to development environment
2. Monitor application logs for the specific exception types
3. Test the streaming endpoint with various inputs
4. If errors persist, the logs will now show the exact exception type and location

