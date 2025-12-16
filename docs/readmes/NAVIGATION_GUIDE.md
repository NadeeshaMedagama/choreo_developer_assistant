# 📚 Documentation Navigation Guide

Quick guide to finding what you need in the restructured documentation.

## 🎯 Start Here

**New to the project?**
→ Start with [`README.md`](./README.md) for overview
→ Then go to [`01-getting-started/`](./01-getting-started/)

**Looking for something specific?**
→ Check [`INDEX.md`](./INDEX.md) for complete listing

## 🗺️ Folder Guide

### 01-getting-started/ 🎯
**When**: Setting up the project, first time use
**Contains**: Setup guides, quick starts, environment config
**Start with**: `MAIN_README.md` or `SETUP_GUIDE.md`

### 02-features/ ✨
**When**: Learning about features
**Contains**: Conversation memory, streaming, sources, monitoring
**Start with**: `README.md` for feature overview

### 03-deployment/ 🚀
**When**: Deploying to Choreo or Docker
**Contains**: Deployment guides, production setup
**Start with**: `CHOREO_DEPLOYMENT.md`

### 04-troubleshooting/ 🔧
**When**: Encountering errors or issues
**Contains**: Error fixes, problem solutions
**Start with**: Error-specific guide (e.g., `TROUBLESHOOTING_429_ERRORS.md`)

### 05-implementation-notes/ 💻
**When**: Understanding technical details
**Contains**: Implementation guides, component docs
**Start with**: `IMPLEMENTATION_SUMMARY.md`

### 06-migration-history/ 📜
**When**: Understanding project evolution
**Contains**: Historical changes, security audits, migrations
**Start with**: `README.md`

### 07-url-validation/ 🔗
**When**: Working with URL validation feature
**Contains**: Feature docs, architecture, fixes
**Start with**: `URL_VALIDATION.md` or `QUICK_START_URL_VALIDATION.md`

### 08-ai-models/ 🤖
**When**: Configuring AI models
**Contains**: Model documentation, configuration guides
**Start with**: `MODELS_DOCUMENTATION.md`

### 09-bug-fixes/ 🐛
**When**: Learning about resolved bugs
**Contains**: Bug reports, fixes, solutions
**Start with**: `README.md`

### 10-changelog/ 📋
**When**: Checking version changes
**Contains**: Feature changelogs, version history
**Start with**: Latest changelog

## 🔍 Common Tasks

### "I want to set up the project"
1. Go to `01-getting-started/`
2. Read `SETUP_GUIDE.md`
3. Follow `RUN_PROJECT.md`

### "I want to enable conversation memory"
1. Go to `02-features/`
2. Read `CONVERSATION_MEMORY_IMPLEMENTATION.md`
3. Check `QUICK_START_CONVERSATION_MEMORY.md` in `01-getting-started/`

### "I want to deploy to Choreo"
1. Go to `03-deployment/`
2. Read `CHOREO_DEPLOYMENT.md`
3. Follow `READY_TO_PUSH.md`

### "I'm getting 429 errors"
1. Go to `04-troubleshooting/`
2. Read `TROUBLESHOOTING_429_ERRORS.md`
3. Try `QUICK_FIX_429.md`

### "I want to validate URLs"
1. Go to `07-url-validation/`
2. Read `URL_VALIDATION.md`
3. Check `QUICK_START_URL_VALIDATION.md`

### "I want to change AI models"
1. Go to `08-ai-models/`
2. Read `MODELS_DOCUMENTATION.md`
3. Update your `.env` file

### "I want to see recent changes"
1. Go to `10-changelog/`
2. Check latest changelog files

## 📋 Documentation Types

### Setup Guides
Location: `01-getting-started/`
- Installation
- Configuration
- Environment setup

### Feature Documentation
Location: `02-features/`, `07-url-validation/`
- How features work
- Configuration options
- Usage examples

### Deployment Guides
Location: `03-deployment/`
- Platform deployment
- Docker setup
- Production configuration

### Troubleshooting
Location: `04-troubleshooting/`, `09-bug-fixes/`
- Error solutions
- Bug fixes
- Common problems

### Technical Docs
Location: `05-implementation-notes/`, `08-ai-models/`
- Implementation details
- Architecture
- Technical specifications

### Historical
Location: `06-migration-history/`, `10-changelog/`
- Project evolution
- Version history
- Past changes

## 🎯 Quick Links

| What | Where |
|------|-------|
| Master Overview | [`README.md`](./README.md) |
| Complete Index | [`INDEX.md`](./INDEX.md) |
| Setup Project | [`01-getting-started/SETUP_GUIDE.md`](./01-getting-started/SETUP_GUIDE.md) |
| Run Project | [`01-getting-started/RUN_PROJECT.md`](./01-getting-started/RUN_PROJECT.md) |
| Conversation Memory | [`02-features/CONVERSATION_MEMORY_IMPLEMENTATION.md`](./02-features/CONVERSATION_MEMORY_IMPLEMENTATION.md) |
| Streaming | [`02-features/STREAMING_IMPLEMENTATION.md`](./02-features/STREAMING_IMPLEMENTATION.md) |
| Deploy to Choreo | [`03-deployment/CHOREO_DEPLOYMENT.md`](./03-deployment/CHOREO_DEPLOYMENT.md) |
| Fix 429 Errors | [`04-troubleshooting/TROUBLESHOOTING_429_ERRORS.md`](./04-troubleshooting/TROUBLESHOOTING_429_ERRORS.md) |
| URL Validation | [`07-url-validation/URL_VALIDATION.md`](./07-url-validation/URL_VALIDATION.md) |
| AI Models | [`08-ai-models/MODELS_DOCUMENTATION.md`](./08-ai-models/MODELS_DOCUMENTATION.md) |

## 💡 Tips

1. **Start with folder READMEs** - Each folder has a README explaining its contents
2. **Use the INDEX** - See all docs at a glance
3. **Follow cross-references** - Docs link to related content
4. **Check quick starts** - Many topics have quick start guides
5. **Browse by topic** - Use folder structure to find related docs

## 🔄 Finding Related Documentation

When reading a document, look for:
- **See Also** sections
- **Related** links
- Cross-references to other folders
- Links in folder READMEs

Example: Reading about URL validation?
- Main docs in `07-url-validation/`
- Quick start in `01-getting-started/`
- Changelog in `10-changelog/`
- Bug fixes in `09-bug-fixes/`

## 📝 Document Naming Conventions

- **README.md** - Folder overview
- **MAIN_*.md** - Primary documentation
- **QUICK_START_*.md** - Quick start guides
- **SETUP_*.md** - Setup instructions
- **FIX_*.md** - Bug fixes
- **TROUBLESHOOTING_*.md** - Problem solving
- **IMPLEMENTATION_*.md** - Technical details
- **CHANGELOG_*.md** - Version history

## 🆘 Still Can't Find It?

1. Check [`INDEX.md`](./INDEX.md) - Complete document listing
2. Search within folders using file names
3. Use grep to search content:
   ```bash
   grep -r "your search term" docs/readmes/
   ```
4. Check folder READMEs for related docs

---

**Happy documenting! 📚**

Last updated: December 3, 2024

