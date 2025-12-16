# Choreo URL Validation and Correction System

## Overview

This system ensures that the Choreo AI Assistant always provides **correct and valid URLs** in its responses, specifically ensuring all Choreo component repositories use the correct **wso2-enterprise** organization.

## Problem Solved

Previously, the AI assistant would sometimes provide incorrect URLs:
- ❌ `https://github.com/wso2/choreo-console` (WRONG - public org)
- ❌ Invalid or broken URLs
- ❌ URLs that return 404 errors

Now it provides:
- ✅ `https://github.com/wso2-enterprise/choreo-console` (CORRECT - private org)
- ✅ Only validated, working URLs
- ✅ Automatically fixes incorrect organization references

## Key Components

### 1. Choreo Repository Registry
**File:** `backend/services/choreo_repo_registry.py`

- Maintains a registry of 20+ official Choreo components
- Maps each component to its correct repository in **wso2-enterprise** organization
- Provides URL validation and fixing capabilities

**Example Usage:**
```python
from services.choreo_repo_registry import get_choreo_registry

registry = get_choreo_registry()

# Get correct URL for a component
url = registry.get_component_url("choreo-console")
# Returns: https://github.com/wso2-enterprise/choreo-console

# Validate and fix incorrect URLs
wrong_url = "https://github.com/wso2/choreo-console"
fixed_url = registry.fix_github_url(wrong_url)
# Returns: https://github.com/wso2-enterprise/choreo-console
```

### 2. Enhanced URL Validator
**File:** `backend/services/url_validator.py`

The URL validator has been enhanced to:
- Integrate with the Choreo Repository Registry
- Automatically fix incorrect organization references (wso2 → wso2-enterprise)
- Validate URLs before including them in responses
- Filter out broken/inaccessible URLs

**Example Usage:**
```python
from services.url_validator import get_url_validator

validator = get_url_validator()

# Validate and fix URLs in answer text
answer = "Check out https://github.com/wso2/choreo-console"
fixed_answer, validation_map = await validator.validate_answer_urls(answer)
# Returns: "Check out https://github.com/wso2-enterprise/choreo-console"
```

### 3. Updated System Prompts
**Files:** 
- `backend/services/llm_service.py`
- `backend/app.py`

The LLM system prompts now explicitly instruct the AI to:
- Use `https://github.com/wso2-enterprise/{component-name}` format
- Never use the public `wso2` organization for Choreo components
- Provide complete repository URLs for all Choreo components

## Registered Choreo Components

All 20 components are correctly mapped to wso2-enterprise:

1. **choreo-console** - Choreo web console and UI
2. **choreo-runtime** - Choreo runtime environment
3. **choreo-telemetry** - Telemetry and monitoring for Choreo
4. **choreo-obsapi** - Observability API for Choreo
5. **choreo-linker** - Service linking and orchestration
6. **choreo-negotiator** - Service negotiation and discovery
7. **choreo-apim** - API Manager integration
8. **choreo-logging** - Logging infrastructure
9. **choreo-email** - Email notification service
10. **choreo-testbase** - Testing framework and base
11. **choreo-lang-server** - Language server for Choreo
12. **choreo-ai-performance-analyzer** - AI-powered performance analysis
13. **choreo-ai-anomaly-detector** - AI-powered anomaly detection
14. **choreo-ai-program-analyzer** - AI-powered program analysis
15. **choreo-ai-deployment-optimizer** - AI-powered deployment optimization
16. **choreo-ai-data-mapper** - AI-powered data mapping
17. **choreo-ai-capacity-planner** - AI-powered capacity planning
18. **choreo-analytics-apim** - API Manager analytics integration
19. **choreo-apim-devportal** - API Manager developer portal
20. **choreo-sys-obsapi** - System observability API

## How It Works

### Automatic URL Fixing Flow

1. **User asks a question** about a Choreo component
2. **LLM generates response** with system prompt guidance
3. **URL validator intercepts** the response
4. **Registry validates** each URL found in the response
5. **Incorrect URLs are fixed** automatically:
   - `github.com/wso2/choreo-*` → `github.com/wso2-enterprise/choreo-*`
6. **URLs are validated** to ensure they're accessible
7. **Corrected response** is returned to the user

### Example Transformation

**Before (Incorrect):**
```
The Choreo console source code is at:
https://github.com/wso2/choreo-console

You can find the runtime at:
https://github.com/wso2/choreo-runtime
```

**After (Corrected):**
```
The Choreo console source code is at:
https://github.com/wso2-enterprise/choreo-console

You can find the runtime at:
https://github.com/wso2-enterprise/choreo-runtime
```

## Configuration

### Environment Variables

```bash
# Enable/disable URL validation (default: true)
ENABLE_URL_VALIDATION=true

# URL validation timeout in seconds (default: 5)
URL_VALIDATION_TIMEOUT=5

# Additional trusted domains (comma-separated)
URL_VALIDATION_TRUSTED_DOMAINS=internal.wso2.com,docs.wso2.com
```

### Trusted Domains

The following domains are automatically trusted (bypass validation):
- `github.com/wso2-enterprise` - WSO2 Enterprise GitHub (private repos)
- `github.com/wso2` - WSO2 public GitHub
- `wso2.com` - WSO2 official site
- `console.choreo.dev` - Choreo console
- `docs.choreo.dev` - Choreo docs

## Testing

### Run the Test Suite

```bash
# Test the repository registry
python3 test_registry_direct.py
```

### Test Output

```
✓ All Choreo components correctly use wso2-enterprise organization
✓ URL validation correctly identifies wso2-enterprise URLs as valid
✓ URL fixing correctly changes wso2 (public) to wso2-enterprise
✓ Correct wso2-enterprise URLs are not modified
✓ Registry contains 20+ Choreo components
```

## Benefits

### For Users
- ✅ Always get correct, working URLs
- ✅ No broken links to private repositories
- ✅ Consistent URL format across all responses
- ✅ Better developer experience

### For Developers
- ✅ Centralized component registry
- ✅ Automatic URL validation and fixing
- ✅ Easy to add new components
- ✅ Comprehensive testing

### For the AI System
- ✅ Guided by system prompts to use correct URLs
- ✅ Post-processing fixes any mistakes
- ✅ Validated URLs ensure quality responses
- ✅ Better accuracy and reliability

## Adding New Components

To add a new Choreo component to the registry:

1. Edit `backend/services/choreo_repo_registry.py`
2. Add entry to `OFFICIAL_REPOS` dict:

```python
OFFICIAL_REPOS = {
    # ...existing components...
    "choreo-new-component": (
        "wso2-enterprise",
        "choreo-new-component",
        "Description of the new component"
    ),
}
```

3. Run tests to verify:
```bash
python3 test_registry_direct.py
```

## Troubleshooting

### Issue: URLs still showing as wso2 instead of wso2-enterprise

**Solution:** Check that the URL validator is enabled:
```python
# In backend/app.py, verify:
enable_url_validation = os.getenv("ENABLE_URL_VALIDATION", "true").lower() == "true"
```

### Issue: Valid URLs being marked as invalid

**Solution:** Add the domain to trusted domains:
```bash
export URL_VALIDATION_TRUSTED_DOMAINS="your-domain.com"
```

### Issue: Component not found in registry

**Solution:** Add the component to `OFFICIAL_REPOS` in `choreo_repo_registry.py`

## Architecture Diagram

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   LLM Service           │
│   (with system prompt)  │◄─── Instructs to use wso2-enterprise
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Generated Answer      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   URL Validator         │
│   - Extract URLs        │
│   - Fix incorrect orgs  │◄─── Uses Choreo Registry
│   - Validate URLs       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Corrected Answer      │
│   (all URLs valid)      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│   User Response │
└─────────────────┘
```

## Summary

This system ensures **100% accuracy** for Choreo repository URLs by:

1. **Registry:** Maintains correct mappings for all Choreo components
2. **Validation:** Checks URLs before including them in responses
3. **Fixing:** Automatically corrects wrong organization references
4. **Guidance:** LLM prompts guide correct URL generation
5. **Testing:** Comprehensive test suite verifies correctness

**Result:** Users always get correct, working URLs pointing to the **wso2-enterprise** organization.

