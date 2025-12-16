# URL Validation Documentation

This folder contains all documentation related to the URL validation feature.

## 📚 Contents

### Core Documentation
- **[URL_VALIDATION.md](./URL_VALIDATION.md)** - Complete feature guide with configuration and usage examples
- **[URL_VALIDATION_ARCHITECTURE.md](./URL_VALIDATION_ARCHITECTURE.md)** - Architecture diagrams and technical flow
- **[URL_VALIDATION_IMPLEMENTATION.md](./URL_VALIDATION_IMPLEMENTATION.md)** - Implementation summary and details

### Quick Guides
- **[QUICK_START_URL_VALIDATION.md](./QUICK_START_URL_VALIDATION.md)** - Quick start guide for URL validation

### Fixes & Enhancements
- **[FIX_PRIVATE_REPO_URLS.md](./FIX_PRIVATE_REPO_URLS.md)** - Fix for private repository URLs being filtered

## 🎯 Overview

The URL validation feature automatically validates all URLs in AI responses and source documents to ensure they are accessible before presenting them to users. This prevents broken links (404 errors) and inaccessible URLs from being included in responses.

## ✨ Key Features

- ✅ Automatic URL detection and validation
- ✅ Trusted domains whitelist (private repos, internal sites)
- ✅ Concurrent validation for performance
- ✅ Smart caching to avoid redundant checks
- ✅ Configurable via environment variables

## 🚀 Quick Start

1. Enable URL validation (enabled by default):
   ```bash
   ENABLE_URL_VALIDATION=true
   URL_VALIDATION_TIMEOUT=5
   ```

2. Restart your application:
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

3. URLs are now automatically validated!

## 📖 Read More

Start with **[URL_VALIDATION.md](./URL_VALIDATION.md)** for complete documentation, or **[QUICK_START_URL_VALIDATION.md](./QUICK_START_URL_VALIDATION.md)** for a quick guide.

