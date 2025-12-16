# Changelog Documentation

This folder contains changelogs documenting version changes and feature additions.

## 📚 Contents

- **[CHANGELOG_URL_VALIDATION.md](./CHANGELOG_URL_VALIDATION.md)** - Changelog for URL validation feature (v1.5.0)
- **[CHANGELOG_TRUSTED_DOMAINS.md](./CHANGELOG_TRUSTED_DOMAINS.md)** - Changelog for trusted domains whitelist (v1.5.1)

## 📋 Changelogs

### Version 1.5.1 (2024-12-03)
**Feature**: Trusted Domains Whitelist
- Added whitelist for private repositories and internal sites
- URLs from trusted domains bypass validation
- Fixes issue with private GitHub repos being filtered
- **Details**: [CHANGELOG_TRUSTED_DOMAINS.md](./CHANGELOG_TRUSTED_DOMAINS.md)

### Version 1.5.0 (2024-12-03)
**Feature**: URL Validation System
- Automatic URL validation in responses
- Filters out broken/404 URLs
- Concurrent validation with caching
- Configurable timeout settings
- **Details**: [CHANGELOG_URL_VALIDATION.md](./CHANGELOG_URL_VALIDATION.md)

## 📖 What's Inside

Each changelog includes:

- ✅ Version number and date
- ✅ New features and changes
- ✅ Files modified
- ✅ Configuration changes
- ✅ Migration notes
- ✅ Benefits and impact
- ✅ Testing instructions

## 🔢 Version History

| Version | Date | Feature | Status |
|---------|------|---------|--------|
| 1.5.1 | 2024-12-03 | Trusted Domains | ✅ Released |
| 1.5.0 | 2024-12-03 | URL Validation | ✅ Released |
| 1.4.0 | Previous | Streaming & Memory | ✅ Released |
| 1.3.0 | Previous | Monitoring | ✅ Released |

## 📝 Changelog Format

Each changelog follows this structure:

```markdown
## [Version] - Date

### Added/Fixed/Changed
- Feature description
- Changes made
- Benefits

### Configuration
- New environment variables
- Updated settings

### Files Modified
- List of changed files

### Migration
- Upgrade instructions
- Breaking changes (if any)
```

## 🚀 Related

For implementation details, see:
- **[05-implementation-notes/](../05-implementation-notes/)** - Implementation guides
- **[07-url-validation/](../07-url-validation/)** - URL validation docs
- **[08-ai-models/](../08-ai-models/)** - AI models documentation

