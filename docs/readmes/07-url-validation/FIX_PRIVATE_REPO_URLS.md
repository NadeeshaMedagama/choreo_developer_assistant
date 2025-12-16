# Fix: Private Repository URLs Now Included

## Problem

URLs to private GitHub repositories (like `wso2-enterprise/choreo-console`) were being removed from answers because they return 404 when accessed without authentication.

**Example:**
```
Component: Choreo Console (UI)
Location: [URL removed - not accessible]
```

## Root Cause

The URL validator was checking if URLs are accessible by making HTTP requests. Private GitHub repositories return 404 unless you're authenticated, so they were marked as invalid and removed.

## Solution

Added a **trusted domains whitelist** that bypasses URL validation for known internal/private sources.

### Default Trusted Domains

The following domains are now automatically trusted and their URLs will **always** be included in responses:

1. `github.com/wso2-enterprise` - WSO2 Enterprise private repositories
2. `github.com/wso2` - WSO2 public repositories  
3. `wso2.com` - Official WSO2 website
4. `console.choreo.dev` - Choreo console
5. `docs.choreo.dev` - Choreo documentation

### How It Works

```python
# Before: All URLs validated
https://github.com/wso2-enterprise/choreo-console
    ↓
HTTP HEAD request → 404 (requires auth)
    ↓
❌ Marked as invalid → Removed

# After: Trusted domains bypass validation
https://github.com/wso2-enterprise/choreo-console
    ↓
Check if from trusted domain → YES
    ↓
✅ Marked as valid → Kept in response
```

## Changes Made

### 1. Updated `url_validator.py`

**Added trusted domains list:**
```python
class URLValidator:
    TRUSTED_DOMAINS = [
        'github.com/wso2-enterprise',
        'github.com/wso2',
        'wso2.com',
        'console.choreo.dev',
        'docs.choreo.dev',
    ]
```

**Added validation bypass:**
```python
async def validate_url(self, url: str, session: ClientSession) -> bool:
    # Trusted domains bypass validation
    if self.is_trusted_url(url):
        logger.debug(f"URL is from trusted domain, marking as valid: {url}")
        self._cache[url] = True
        return True
    # ... rest of validation
```

### 2. Updated `app.py`

**Added environment variable support:**
```python
# Parse trusted domains from environment (comma-separated list)
trusted_domains_env = os.getenv("URL_VALIDATION_TRUSTED_DOMAINS", "")
trusted_domains = [d.strip() for d in trusted_domains_env.split(",") if d.strip()]

url_validator = get_url_validator(
    timeout=url_validation_timeout,
    max_concurrent=10,
    enable_validation=enable_url_validation,
    trusted_domains=trusted_domains  # Pass additional trusted domains
)
```

## Configuration

### Use Default Trusted Domains (Recommended)

No configuration needed! Default trusted domains are built-in:

```bash
# Just enable URL validation (already default)
ENABLE_URL_VALIDATION=true
URL_VALIDATION_TIMEOUT=5
```

### Add Additional Trusted Domains

If you have other internal domains to trust:

```bash
# Add to .env
URL_VALIDATION_TRUSTED_DOMAINS=internal.example.com,private-docs.company.com
```

Multiple domains are comma-separated.

## Testing

### Before Fix

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Where is Choreo Console repository?"}'
```

**Response:**
```
Component: Choreo Console (UI)
Location: [URL removed - not accessible]
```

### After Fix

**Response:**
```
Component: Choreo Console (UI)
Location: https://github.com/wso2-enterprise/choreo-console
```

✅ **Private repository URLs are now preserved!**

## Logs

You'll see these log messages on startup:

```
[APP] URL validation enabled (timeout: 5s)
[APP] Trusted domains (bypass validation): github.com/wso2-enterprise, github.com/wso2, wso2.com, console.choreo.dev, docs.choreo.dev
```

When validating URLs:

```
[DEBUG] URL is from trusted domain, marking as valid: https://github.com/wso2-enterprise/choreo-console
```

## Files Modified

1. ✅ `backend/services/url_validator.py`
   - Added `TRUSTED_DOMAINS` class constant
   - Added `is_trusted_url()` method
   - Updated `validate_url()` to bypass validation for trusted domains
   - Updated `get_url_validator()` to accept `trusted_domains` parameter

2. ✅ `backend/app.py`
   - Added parsing of `URL_VALIDATION_TRUSTED_DOMAINS` environment variable
   - Pass trusted domains to `get_url_validator()`
   - Added logging of trusted domains on startup

## How Validation Works Now

### Flow Diagram

```
URL in response
    ↓
Is from trusted domain?
    ├─ YES → ✅ Keep URL (bypass validation)
    └─ NO → Continue to HTTP validation
              ↓
         Make HTTP request
              ↓
         Status < 400?
              ├─ YES → ✅ Keep URL
              └─ NO → ❌ Remove URL
```

### Validation Priority

1. **Trusted Domain Check** (fast, no network request)
   - If URL contains any trusted domain → Mark as valid
   
2. **HTTP Validation** (slower, network request)
   - Only for non-trusted URLs
   - HEAD request first, GET fallback
   - Status < 400 → Valid

## Benefits

✅ **Private repos preserved** - Internal GitHub repositories now show correctly
✅ **No false positives** - Trusted internal URLs won't be removed
✅ **Faster validation** - Trusted domains skip HTTP requests
✅ **Configurable** - Can add more trusted domains via env var
✅ **Backward compatible** - Existing behavior for external URLs unchanged

## Security Note

URLs from trusted domains bypass validation because they are **known internal/private resources**. This is safe for:

- Internal tools (like this AI assistant for WSO2 developers)
- Private GitHub repositories (wso2-enterprise)
- Company documentation sites

For **public-facing applications**, review the trusted domains list to ensure only appropriate domains are whitelisted.

## Summary

🎯 **Problem Solved**: Private repository URLs like `github.com/wso2-enterprise/choreo-console` are now included in responses instead of being marked as "[URL removed - not accessible]".

The URL validator now has two modes:
1. **Trusted domains** → Always valid (bypass HTTP check)
2. **Other URLs** → Validate via HTTP request

This gives you the best of both worlds:
- ✅ Keep internal/private URLs that users need
- ✅ Filter out genuinely broken external URLs

**Restart your application to apply the fix!**

