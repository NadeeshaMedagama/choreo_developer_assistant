# URL Validation Feature

## Overview

The URL validation feature automatically validates all URLs in AI-generated answers and source documents to ensure they are accessible before presenting them to users. This prevents broken links (404 errors) and inaccessible URLs from being included in responses.

## Features

- ✅ **Automatic URL Detection**: Extracts URLs from both plain text and markdown format
- ✅ **Asynchronous Validation**: Validates multiple URLs concurrently for performance
- ✅ **Smart Caching**: Caches validation results to avoid redundant checks
- ✅ **Answer Filtering**: Removes or marks invalid URLs in AI responses
- ✅ **Source Filtering**: Filters out source documents with broken URLs
- ✅ **Configurable**: Enable/disable validation and adjust timeout settings
- ✅ **Monitoring**: Logs validation metrics and results

## How It Works

### Validation Process

1. **Answer Generation**: AI generates response with potential URLs
2. **URL Extraction**: System extracts all URLs from the answer text
3. **Concurrent Validation**: Validates all URLs in parallel (max 10 concurrent requests)
4. **Filtering**: Removes or marks invalid URLs
5. **Source Validation**: Validates URLs in source documents
6. **Response**: Returns filtered answer with only valid URLs

### Validation Flow

```
User Question
     ↓
AI generates answer with URLs
     ↓
Extract URLs from answer
     ↓
Validate URLs concurrently ──→ Check cache first
     ↓                           ↓
Filter invalid URLs          Cache results
     ↓
Validate source URLs
     ↓
Filter invalid sources
     ↓
Return clean response
```

## Configuration

### Environment Variables

Add these to your `backend/.env` file:

```bash
# Enable/disable URL validation (default: true)
ENABLE_URL_VALIDATION=true

# Validation timeout in seconds (default: 5)
URL_VALIDATION_TIMEOUT=5

# Additional trusted domains to bypass validation (comma-separated, optional)
# Default trusted domains are built-in: github.com/wso2-enterprise, github.com/wso2, wso2.com, console.choreo.dev, docs.choreo.dev
URL_VALIDATION_TRUSTED_DOMAINS=internal.example.com,private-docs.company.com
```

### Trusted Domains

**Important**: URLs from trusted domains **bypass validation** because they may require authentication (e.g., private GitHub repos).

**Default Trusted Domains** (built-in):
- `github.com/wso2-enterprise` - WSO2 Enterprise private repositories
- `github.com/wso2` - WSO2 public repositories
- `wso2.com` - Official WSO2 website
- `console.choreo.dev` - Choreo console
- `docs.choreo.dev` - Choreo documentation

These domains are automatically trusted and their URLs will always be included in responses, even if they return 404 (e.g., private repos requiring authentication).

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_URL_VALIDATION` | `true` | Enable/disable URL validation globally |
| `URL_VALIDATION_TIMEOUT` | `5` | Request timeout in seconds |

## Usage

### Standard Endpoint

URL validation is **automatically enabled** for all `/api/ask` requests:

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy to Choreo?"
  }'
```

Response includes validation info:

```json
{
  "answer": "To deploy to Choreo, visit https://console.choreo.dev...",
  "sources": [
    {
      "url": "https://wso2.com/choreo/docs/deploy",
      "score": 0.85
    }
  ],
  "url_validation": {
    "total_urls": 3,
    "valid_urls": 2,
    "invalid_urls": 1,
    "validation_enabled": true
  }
}
```

### Streaming Endpoint

URL validation also works with streaming responses:

```bash
curl -N -X POST "http://localhost:8000/api/ask/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Choreo?"
  }'
```

## Validation Logic

### URL Detection

The system detects URLs in two formats:

1. **Plain URLs**: `https://example.com/path`
2. **Markdown Links**: `[Link Text](https://example.com/path)`

### Validation Method

1. **Trusted Domain Check** ⚡ (Fast - No Network Request)
   - If URL contains a trusted domain → Automatically marked as valid
   - Trusted domains: `github.com/wso2-enterprise`, `github.com/wso2`, `wso2.com`, `console.choreo.dev`, `docs.choreo.dev`
   - Bypasses HTTP validation (important for private repos requiring authentication)
   
2. **Cache Check** ⚡ (Fast - No Network Request)
   - If URL previously validated → Return cached result

3. **HTTP Validation** 🌐 (Slower - Network Request)
   - Only for non-trusted URLs not in cache
   - **HEAD Request**: First tries HTTP HEAD (faster, no body download)
   - **GET Request**: Falls back to GET if HEAD is not supported
   - **Status Check**: URLs with status < 400 are considered valid
   - **Timeout**: Requests timeout after configured seconds (default: 5s)
   - **Error Handling**: Network errors, timeouts, and exceptions mark URL as invalid

### Invalid URL Handling

**In Answers:**
- Plain URLs: Replaced with `[URL removed - not accessible]`
- Markdown Links: Converted to `Link Text [link removed - not accessible]`

**In Sources:**
- Sources with invalid URLs are completely removed from the list
- Only sources with valid URLs (or no URLs) are returned

**Trusted Domain URLs:**
- Always kept in responses, even if they return 404 (e.g., private repositories)
- Example: `https://github.com/wso2-enterprise/choreo-console` is always included

## Performance

### Optimization Features

- **Concurrent Validation**: Up to 10 URLs validated simultaneously
- **In-Memory Caching**: Results cached to avoid repeated checks
- **Semaphore Control**: Prevents overwhelming servers with requests
- **Configurable Timeout**: Balance between accuracy and speed

### Performance Impact

| Scenario | Added Latency |
|----------|---------------|
| No URLs in answer | ~0ms |
| 1-3 URLs | ~200-500ms |
| 4-10 URLs | ~500-1000ms |
| 10+ URLs | ~1-2s (concurrent) |

### Disable for Performance

If URL validation impacts performance:

```bash
# Disable globally
export ENABLE_URL_VALIDATION=false

# Or reduce timeout
export URL_VALIDATION_TIMEOUT=2
```

## Monitoring

### Log Output

URL validation logs include:

```
[AI] URL validation completed - validation_duration=0.45s, valid_urls=2, invalid_urls=1
[AI] Filtering out source with invalid URL: https://broken.example.com
```

### Response Metadata

Each response includes validation statistics:

```json
{
  "url_validation": {
    "total_urls": 3,
    "valid_urls": 2,
    "invalid_urls": 1,
    "validation_enabled": true
  }
}
```

## Examples

### Example 1: Valid URLs

**Answer:**
```
Visit https://console.choreo.dev to deploy your application.
Documentation: https://wso2.com/choreo/docs
```

**Validation Result:**
- Both URLs are valid
- Answer remains unchanged
- `url_validation: {total: 2, valid: 2, invalid: 0}`

### Example 2: Invalid URLs

**Answer:**
```
Visit https://console.choreo.dev (valid)
Old docs: https://old.choreo.dev/404 (invalid)
```

**Filtered Answer:**
```
Visit https://console.choreo.dev
Old docs: [URL removed - not accessible]
```

**Validation Result:**
- `url_validation: {total: 2, valid: 1, invalid: 1}`

### Example 3: Markdown Links

**Answer:**
```
See the [deployment guide](https://wso2.com/choreo/deploy) for more info.
Check [old docs](https://broken.example.com) as well.
```

**Filtered Answer:**
```
See the [deployment guide](https://wso2.com/choreo/deploy) for more info.
Check old docs [link removed - not accessible] as well.
```

## Troubleshooting

### Issue: URLs being incorrectly marked as invalid

**Possible Causes:**
- Timeout too short for slow servers
- Network connectivity issues
- Server blocking HEAD requests

**Solutions:**
```bash
# Increase timeout
export URL_VALIDATION_TIMEOUT=10

# Check logs for specific errors
tail -f logs/ai.log | grep "URL validation"
```

### Issue: Performance degradation

**Solutions:**
```bash
# Reduce timeout
export URL_VALIDATION_TIMEOUT=3

# Temporarily disable validation
export ENABLE_URL_VALIDATION=false
```

### Issue: Cache contains stale results

**Solution:**
The cache is in-memory and clears on restart. To clear manually:

```python
from backend.services.url_validator import get_url_validator

validator = get_url_validator()
validator.clear_cache()
```

## Technical Details

### Architecture

```
┌─────────────────────────────────────┐
│ URLValidator Service (Singleton)    │
│                                     │
│ ┌────────────────────────────────┐ │
│ │ In-Memory Cache                │ │
│ │ {url: is_valid}               │ │
│ └────────────────────────────────┘ │
│                                     │
│ ┌────────────────────────────────┐ │
│ │ Semaphore (max 10 concurrent) │ │
│ └────────────────────────────────┘ │
│                                     │
│ Methods:                            │
│ - extract_urls_from_text()         │
│ - validate_url()                   │
│ - validate_urls()                  │
│ - validate_answer_urls()           │
│ - validate_and_filter_sources()    │
└─────────────────────────────────────┘
```

### Implementation

- **Service**: `backend/services/url_validator.py`
- **Integration**: `backend/app.py` (ask and streaming endpoints)
- **Dependencies**: `aiohttp` for async HTTP requests

## Best Practices

1. **Keep Validation Enabled in Production**: Ensures user experience with working links
2. **Monitor Logs**: Watch for patterns of broken URLs to fix at source
3. **Adjust Timeout**: Balance between accuracy and performance for your use case
4. **Use Caching**: The built-in cache prevents redundant validations
5. **Review Invalid URLs**: Check logs to identify systemic issues with URL sources

## Future Enhancements

Potential improvements:

- [ ] Persistent cache (Redis) for multi-instance deployments
- [ ] Configurable retry logic for transient failures
- [ ] URL normalization (handle redirects, trailing slashes)
- [ ] Domain whitelist/blacklist
- [ ] Custom replacement text for invalid URLs
- [ ] Webhook notifications for broken URLs
- [ ] Analytics dashboard for URL health

## See Also

- [Conversation Memory](./CONVERSATION_MEMORY_IMPLEMENTATION.md)
- [Streaming Implementation](./STREAMING_IMPLEMENTATION.md)
- [Monitoring Guide](../backend/monitoring/README.md)

