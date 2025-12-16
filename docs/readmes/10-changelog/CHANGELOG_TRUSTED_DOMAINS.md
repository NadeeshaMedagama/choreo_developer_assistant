# Changelog - Trusted Domains for URL Validation

## [1.5.1] - 2024-12-03

### Fixed - Private Repository URLs Now Preserved

#### Issue
Private GitHub repository URLs (e.g., `github.com/wso2-enterprise/*`) were being removed from responses because they return 404 when accessed without authentication.

**Before:**
```
Component: Choreo Console (UI)
Location: [URL removed - not accessible]
```

**After:**
```
Component: Choreo Console (UI)
Location: https://github.com/wso2-enterprise/choreo-console
```

#### Solution
Added **Trusted Domains Whitelist** that bypasses URL validation for known internal/private sources.

#### Features

1. **Default Trusted Domains** (built-in):
   - `github.com/wso2-enterprise` - WSO2 Enterprise private repositories
   - `github.com/wso2` - WSO2 public repositories
   - `wso2.com` - Official WSO2 website
   - `console.choreo.dev` - Choreo console
   - `docs.choreo.dev` - Choreo documentation

2. **Configurable via Environment Variable**:
   ```bash
   URL_VALIDATION_TRUSTED_DOMAINS=internal.company.com,private-docs.example.com
   ```

3. **Smart Validation**:
   - Trusted domain URLs → Skip HTTP validation (always valid)
   - Other URLs → Validate via HTTP request
   - Faster performance (no HTTP requests for trusted domains)

#### Changes

**Modified Files:**

1. `backend/services/url_validator.py`:
   - Added `TRUSTED_DOMAINS` class constant with default trusted domains
   - Added `is_trusted_url()` method to check if URL is from trusted domain
   - Updated `validate_url()` to bypass HTTP validation for trusted domains
   - Updated `__init__()` to accept `trusted_domains` parameter
   - Updated `get_url_validator()` to accept and pass `trusted_domains`

2. `backend/app.py`:
   - Added parsing of `URL_VALIDATION_TRUSTED_DOMAINS` environment variable
   - Pass `trusted_domains` to `get_url_validator()`
   - Added logging of trusted domains on startup

3. `docs/readmes/URL_VALIDATION.md`:
   - Added trusted domains configuration section
   - Updated validation method documentation
   - Added examples for trusted domain handling

**New Files:**

1. `FIX_PRIVATE_REPO_URLS.md` - Comprehensive fix documentation

#### Configuration

**Default (Recommended):**
```bash
ENABLE_URL_VALIDATION=true
URL_VALIDATION_TIMEOUT=5
# No need to set trusted domains - defaults are built-in
```

**With Additional Trusted Domains:**
```bash
ENABLE_URL_VALIDATION=true
URL_VALIDATION_TIMEOUT=5
URL_VALIDATION_TRUSTED_DOMAINS=internal.example.com,private.company.com
```

#### Validation Flow

```
URL in response
    ↓
Is from trusted domain?
    ├─ YES → ✅ Always valid (skip HTTP check)
    └─ NO → HTTP validation
              ↓
         Status < 400?
              ├─ YES → ✅ Valid
              └─ NO → ❌ Invalid
```

#### Logs

Startup logs now show:
```
[APP] URL validation enabled (timeout: 5s)
[APP] Trusted domains (bypass validation): github.com/wso2-enterprise, github.com/wso2, wso2.com, console.choreo.dev, docs.choreo.dev
```

During validation:
```
[DEBUG] URL is from trusted domain, marking as valid: https://github.com/wso2-enterprise/choreo-console
```

Instead of (before fix):
```
[WARNING] URL validation failed (status 404): https://github.com/wso2-enterprise/choreo-console
[INFO] Filtering out source with invalid URL: https://github.com/wso2-enterprise/choreo-console
```

#### Benefits

✅ **Private repositories visible** - Internal GitHub URLs now show in responses  
✅ **No false positives** - Trusted internal URLs never removed  
✅ **Performance improvement** - Trusted domains skip HTTP requests  
✅ **Configurable** - Can add more trusted domains via env variable  
✅ **Backward compatible** - External URLs still validated normally  
✅ **Security** - Only known trusted domains bypass validation  

#### Migration

**No migration needed!** The change is backward compatible.

Simply restart your application:
```bash
cd backend
uvicorn app:app --reload
```

Trusted domains are built-in, so no configuration changes required.

#### Testing

Test with a query about repositories:
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Where is Choreo Console repository?"}'
```

Response should now include:
```json
{
  "answer": "...https://github.com/wso2-enterprise/choreo-console...",
  "sources": [...]
}
```

#### Security Note

Trusted domains bypass URL validation because they are **known internal/private resources** that may require authentication. This is appropriate for:

- Internal tools (like this AI assistant for WSO2 developers)
- Private GitHub repositories (wso2-enterprise)
- Company documentation sites

For public-facing applications, review the trusted domains list to ensure only appropriate domains are whitelisted.

#### Related

- Issue: Private repository URLs showing "[URL removed - not accessible]"
- Feature: URL Validation (v1.5.0)
- Fix: asyncio import (v1.5.0)

---

## Previous Versions

### [1.5.0] - 2024-12-03
- Added URL Validation System
- Fixed asyncio import for streaming

### [1.4.0] - Previous Release
- Streaming responses
- Conversation memory management

---

## Summary

This update fixes the issue where private GitHub repository URLs (like `wso2-enterprise/choreo-console`) were being incorrectly removed from AI responses. URLs from trusted domains now bypass validation and are always preserved, while external URLs continue to be validated normally.

**Upgrade:** Just restart your application - no configuration changes needed!

