# 📚 Quick Reference Card - Documentation Navigation

## 🎯 Start Here
**Main Hub**: `docs/readmes/INDEX.md`

## 📂 Directory Quick Reference

| Directory | Purpose | File Count | Key Documents |
|-----------|---------|------------|---------------|
| **01-getting-started/** | Setup & Quick Starts | 11 | MAIN_README, SETUP_GUIDE, RUN_PROJECT |
| **02-features/** | Feature Documentation | 15 | CONVERSATION_MEMORY, STREAMING, MONITORING |
| **03-deployment/** | Deployment Guides | 8 | CHOREO_DEPLOYMENT, DOCKER_README |
| **04-troubleshooting/** | Problem Solving | 11 | TROUBLESHOOTING_429, FIX_OPENCHOREO |
| **05-implementation-notes/** | Technical Details | 22 | IMPLEMENTATION_SUMMARY, INGESTION |
| **06-migration-history/** | Historical Docs | 5 | SECURITY_AUDIT, MIGRATIONS |

## 🚀 Common Tasks

### Get Started
```bash
cd docs/readmes
cat 01-getting-started/README.md
```

### Learn Features
```bash
cd docs/readmes/02-features
ls -1
```

### Fix Issues
```bash
cd docs/readmes/04-troubleshooting
cat README.md  # See issue index
```

### Deploy
```bash
cd docs/readmes/03-deployment
cat CHOREO_DEPLOYMENT.md
```

## 📍 Navigation Shortcuts

### By Intent
- **"I'm new"** → `01-getting-started/MAIN_README.md`
- **"I need help"** → `04-troubleshooting/README.md`
- **"Deploy it"** → `03-deployment/README.md`
- **"Learn features"** → `02-features/README.md`

### By Role
- **User** → Start with `01-getting-started/`
- **Developer** → Check `05-implementation-notes/`
- **DevOps** → See `03-deployment/` and `02-features/MONITORING.md`
- **Contributor** → Read `05-implementation-notes/IMPLEMENTATION_SUMMARY.md`

## 🔗 Key Links

| What | Where |
|------|-------|
| Main Navigation | `INDEX.md` |
| Setup Guide | `01-getting-started/SETUP_GUIDE.md` |
| Run Project | `01-getting-started/RUN_PROJECT.md` |
| Conversation Memory | `02-features/CONVERSATION_MEMORY_IMPLEMENTATION.md` |
| Streaming | `02-features/STREAMING_IMPLEMENTATION.md` |
| Deploy to Choreo | `03-deployment/CHOREO_DEPLOYMENT.md` |
| Fix 429 Errors | `04-troubleshooting/TROUBLESHOOTING_429_ERRORS.md` |
| Implementation Status | `05-implementation-notes/IMPLEMENTATION_SUMMARY.md` |

## 💡 Tips

1. **Each directory has a README** - Start there for overview
2. **INDEX.md is your map** - Complete navigation system
3. **Use "I want to..." navigation** - Intent-based quick access
4. **Follow recommended paths** - Guided learning for your role
5. **Check directory READMEs** - See all related docs together

## 🎨 Visual Structure

```
docs/readmes/
├── INDEX.md ⭐ START HERE
├── 01-getting-started/ 📘
│   └── README.md (Setup & Quick Starts)
├── 02-features/ 🎨
│   └── README.md (Feature Docs)
├── 03-deployment/ 🚀
│   └── README.md (Deployment)
├── 04-troubleshooting/ 🔧
│   └── README.md (Fixes)
├── 05-implementation-notes/ 💻
│   └── README.md (Technical)
└── 06-migration-history/ 📜
    └── README.md (History)
```

## ✅ Quick Check

**To verify organization:**
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/docs/readmes"
ls -d */
cat INDEX.md
```

**To find a specific doc:**
```bash
find . -name "*CONVERSATION*"
find . -name "*DEPLOY*"
find . -name "*FIX*"
```

---

**Total Files**: 75 organized documentation files  
**Organization Date**: December 2, 2025  
**Status**: ✅ Complete and ready to use

**📖 Full Details**: See `DOCUMENTATION_REORGANIZATION.md`

