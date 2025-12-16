# 🚀 GitHub Actions - Quick Reference Card

## 📁 Files Created (11 total)

### Workflows (6)
```
.github/workflows/
├── ci-cd.yml             ⚡ Main CI/CD pipeline
├── pr-checks.yml         🔍 PR validation
├── security.yml          🔐 Security scanning
├── dependency-check.yml  📦 Weekly dependency checks
├── release.yml           🎁 Release automation
└── auto-assign.yml       🏷️  Issue/PR automation
```

### Templates (3)
```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.md         🐛 Bug reports
│   └── feature_request.md    ✨ Feature requests
└── pull_request_template.md  📝 PR template
```

### Documentation (2)
```
.github/
├── ACTIONS_GUIDE.md           📚 Complete guide
└── CI_CD_SETUP_COMPLETE.md    📖 Setup docs
```

---

## ⚡ Quick Commands

### Test Locally
```bash
# Run backend tests
pytest backend/tests/ -v --cov=backend

# Run frontend build
cd frontend && npm run build

# Lint Python code
black backend/ && isort backend/ && flake8 backend/

# Test Docker build
docker build -t test .
```

### GitHub Actions
```bash
# Commit workflows
git add .github/
git commit -m "ci: add GitHub Actions CI/CD"
git push origin main

# Create test PR
git checkout -b test/actions
echo "test" > TEST.md
git add TEST.md
git commit -m "test: CI/CD verification"
git push origin test/actions
# Then create PR on GitHub

# Create release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 🎯 Workflow Triggers

| Workflow | Auto Trigger | Manual |
|----------|-------------|--------|
| CI/CD | Push, PR | ✅ |
| PR Checks | PR only | ✅ |
| Security | Push, PR, Daily | ✅ |
| Dependencies | Weekly Mon | ✅ |
| Release | Tags v*.*.* | ✅ |
| Auto-assign | Issues, PRs | ❌ |

---

## ✅ Setup Checklist

### Immediate (Required)
- [ ] Push .github/ folder to GitHub
- [ ] Verify workflows appear in Actions tab
- [ ] Test with a sample PR

### Important (Recommended)
- [ ] Enable branch protection on main
- [ ] Enable security features
- [ ] Add status badges to README

### Optional (Enhanced Features)
- [ ] Add DOCKER_USERNAME secret
- [ ] Add DOCKER_PASSWORD secret
- [ ] Add CODECOV_TOKEN secret
- [ ] Configure Slack notifications

---

## 🔐 Required Secrets (Optional)

Add in: **Settings → Secrets and variables → Actions**

```
DOCKER_USERNAME      # Docker Hub username
DOCKER_PASSWORD      # Docker Hub token
CODECOV_TOKEN        # Codecov integration
GITLEAKS_LICENSE     # Secret scanning
```

---

## 📊 What Each Workflow Does

### CI/CD (`ci-cd.yml`)
```
Push/PR → Test Backend → Build Frontend → Docker Build → Deploy
          (pytest)      (npm build)     (if main)     (if main)
```

### PR Checks (`pr-checks.yml`)
```
PR Opened → Validate → Code Quality → File Check → Comment
           (title)    (lint/format)  (size)      (summary)
```

### Security (`security.yml`)
```
Trigger → CodeQL → Secrets → Dependencies → Container → Report
         (code)   (scan)    (audit)        (Trivy)    (summary)
```

### Dependencies (`dependency-check.yml`)
```
Weekly → Python Check → NPM Check → Create Issue
        (pip-audit)    (npm audit)  (tracking)
```

### Release (`release.yml`)
```
Tag v*.*.* → Changelog → Build → Release → Docker Images
            (auto)      (all)    (GitHub)  (multi-arch)
```

### Auto-assign (`auto-assign.yml`)
```
Issue/PR → Assign Creator → Add Labels → Welcome Message
          (automatic)      (keywords)   (first-time)
```

---

## 🧪 Testing Guide

### 1. Test CI/CD
```bash
git checkout -b test/pipeline
echo "test" > test.md
git add test.md
git commit -m "test: verify pipeline"
git push origin test/pipeline
# Check Actions tab
```

### 2. Test PR Workflow
```bash
# Create PR from test branch
# Go to GitHub → Pull requests → New pull request
# Select test/pipeline → Create PR
# Watch checks run
```

### 3. Manual Workflow Run
```bash
# GitHub → Actions → Select workflow → Run workflow
```

---

## 🐛 Common Issues & Solutions

### Issue: Workflow not running
**Solution:** Check .github/workflows/ exists and .yml files are valid

### Issue: Tests failing
**Solution:** Run locally first: `pytest backend/tests/`

### Issue: Docker build fails
**Solution:** Test locally: `docker build -t test .`

### Issue: Permission denied
**Solution:** Settings → Actions → Workflow permissions → Read/Write

### Issue: Secrets not working
**Solution:** Check secret names match exactly in workflow files

---

## 📈 Monitoring

### Check Status
```
Repository → Actions tab          # All workflows
Repository → Pull requests        # PR checks
Repository → Security tab         # Alerts
Repository → Insights             # Analytics
```

### Notifications
```
Settings → Notifications
✅ Email for failed workflows
✅ GitHub app notifications
```

---

## 📝 Commit Message Format

```
type(scope): description

Types:
feat     - New feature
fix      - Bug fix
docs     - Documentation
style    - Formatting
refactor - Code restructure
perf     - Performance
test     - Tests
build    - Build system
ci       - CI/CD changes
chore    - Maintenance

Examples:
feat(backend): add new API endpoint
fix(frontend): resolve table overflow
docs: update actions guide
ci: add security workflow
```

---

## 🎯 Next Steps

1. **Push to GitHub**
   ```bash
   git add .github/
   git commit -m "ci: add complete CI/CD pipeline"
   git push origin main
   ```

2. **Verify Setup**
   - Check Actions tab
   - Create test PR
   - Watch workflows run

3. **Configure Security**
   - Enable branch protection
   - Enable security features
   - Add required secrets

4. **Monitor & Maintain**
   - Review workflow runs
   - Check security alerts
   - Update dependencies

---

## 🏆 Success Indicators

✅ Actions tab shows 6 workflows  
✅ PR checks run automatically  
✅ Security scans complete  
✅ Docker builds succeed  
✅ Tests pass consistently  
✅ Documentation is clear  

---

## 📞 Getting Help

**Documentation:**
- `.github/ACTIONS_GUIDE.md` - Complete guide
- `.github/CI_CD_SETUP_COMPLETE.md` - Setup docs

**GitHub Resources:**
- [Actions Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/actions/reference/workflow-syntax-for-github-actions)

**Support:**
- Open issue with `ci/cd` label
- Check Actions tab for error logs
- Review workflow run details

---

**Quick Ref Version:** 1.0  
**Last Updated:** 2025-01-11  
**Status:** ✅ Production Ready

