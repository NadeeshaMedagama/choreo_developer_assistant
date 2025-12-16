# Quick Start: URL Validation

## Installation

1. **Install the required dependency:**
   ```bash
   pip install aiohttp>=3.9.0
   ```

2. **Add configuration to your `.env` file:**
   ```bash
   # Add to backend/.env
   ENABLE_URL_VALIDATION=true
   URL_VALIDATION_TIMEOUT=5
   ```

3. **Restart your application:**
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

That's it! URL validation is now active.

## Test It

### Option 1: Use the Test Script

```bash
cd /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant
python test_url_validation.py
```

This runs 7 comprehensive tests showing how URL validation works.

### Option 2: Test with a Real Query

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy to Choreo?"
  }' | jq
```

Look for the `url_validation` field in the response:
```json
{
  "answer": "...",
  "sources": [...],
  "url_validation": {
    "total_urls": 3,
    "valid_urls": 2,
    "invalid_urls": 1,
    "validation_enabled": true
  }
}
```

## Monitor It

Watch the logs to see URL validation in action:

```bash
tail -f logs/ai.log | grep "URL validation"
```

You'll see entries like:
```
[AI] URL validation completed - validation_duration=0.45s, valid_urls=2, invalid_urls=1
[AI] Filtering out source with invalid URL: https://broken.example.com
```

## Configure It

### For Production (Recommended)
```bash
ENABLE_URL_VALIDATION=true
URL_VALIDATION_TIMEOUT=5
```

### For Development (Faster)
```bash
ENABLE_URL_VALIDATION=true
URL_VALIDATION_TIMEOUT=3
```

### To Disable
```bash
ENABLE_URL_VALIDATION=false
```

## How to Know It's Working

1. **Check response metadata**: Look for `url_validation` field
2. **Check logs**: Search for "URL validation" entries
3. **Test with known broken URL**: Add a fake URL to your data and verify it's filtered
4. **Performance**: Should add ~200-500ms for typical responses with a few URLs

## Troubleshooting

**URLs incorrectly marked as invalid?**
- Increase timeout: `URL_VALIDATION_TIMEOUT=10`
- Check network connectivity
- Review logs for specific errors

**Too slow?**
- Reduce timeout: `URL_VALIDATION_TIMEOUT=3`
- Check number of URLs being validated
- Consider disabling temporarily

**Not seeing validation in responses?**
- Verify `ENABLE_URL_VALIDATION=true` in `.env`
- Restart the application
- Check that answer contains URLs

## What Gets Validated

✅ URLs in AI-generated answers
✅ URLs in source documents
✅ Plain URLs: `https://example.com`
✅ Markdown links: `[text](https://example.com)`

## What Happens to Invalid URLs

**In answers:**
- `https://broken.com` → `[URL removed - not accessible]`
- `[link](https://broken.com)` → `link [link removed - not accessible]`

**In sources:**
- Sources with invalid URLs are completely removed

## Next Steps

- Read the [full documentation](URL_VALIDATION.md)
- Review the [implementation summary](URL_VALIDATION_IMPLEMENTATION.md)
- Customize configuration for your needs
- Monitor validation metrics in production

## Questions?

See the comprehensive documentation:
- `docs/readmes/URL_VALIDATION.md` - Complete feature guide
- `URL_VALIDATION_IMPLEMENTATION.md` - Implementation details
- `test_url_validation.py` - Working examples

