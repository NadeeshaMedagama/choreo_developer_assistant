# 🚀 GitHub Actions CI/CD Documentation

## Overview

This repository includes a comprehensive CI/CD pipeline using GitHub Actions to ensure code quality, security, and automated deployments.

## 📋 Workflows

### 1. **CI/CD Pipeline** (`ci-cd.yml`)

Main continuous integration and deployment workflow.

**Triggers:**
- Push to `main`, `develop`, or `feature/*` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**
- ✅ **Backend Tests** - Python linting, testing, and coverage
- ✅ **Frontend Build** - NPM build and linting
- ✅ **Docker Build** - Container image building and pushing
- ✅ **Security Scan** - Trivy vulnerability scanning
- ✅ **Deploy to Choreo** - Deployment notification
- ✅ **Notifications** - Workflow summary

### 2. **Pull Request Checks** (`pr-checks.yml`)

Validates pull requests before merging.

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**
- ✅ **PR Validation** - Title format, merge conflicts
- ✅ **Code Quality** - Black, isort, Pylint, Bandit
- ✅ **File Size Check** - Large file detection
- ✅ **Dependency Review** - Dependency vulnerability check
- ✅ **PR Summary** - Automated comment with results

### 3. **Security Analysis** (`security.yml`)

Comprehensive security scanning.

**Triggers:**
- Push to `main` or `develop`
- Pull requests
- Daily at 6 AM UTC
- Manual workflow dispatch

**Jobs:**
- 🔐 **CodeQL Analysis** - Code security analysis
- 🔐 **Secret Scanning** - Gitleaks & TruffleHog
- 🔐 **OWASP Dependency Check** - Safety & pip-audit
- 🔐 **Container Scanning** - Trivy Docker scan
- 📊 **Security Summary** - Consolidated report

### 4. **Dependency Updates** (`dependency-check.yml`)

Automated dependency tracking.

**Triggers:**
- Weekly on Mondays at 9 AM UTC
- Manual workflow dispatch

**Jobs:**
- 📦 **Python Dependencies** - pip-audit, pip-review
- 📦 **NPM Dependencies** - npm outdated, npm audit
- 📝 **Create Update Issue** - Weekly tracking issue

### 5. **Release** (`release.yml`)

Automated release process.

**Triggers:**
- Push tags matching `v*.*.*`
- Manual workflow dispatch with version input

**Jobs:**
- 🎉 **Create Release** - GitHub release with changelog
- 🐳 **Docker Release** - Multi-platform Docker images
- 📢 **Notifications** - Release summary

### 6. **Auto-assign and Label** (`auto-assign.yml`)

Automated issue and PR management.

**Triggers:**
- Issues opened
- Pull requests opened

**Jobs:**
- 🏷️ **Auto-assign** - Assign to creator
- 🏷️ **Auto-label** - Label based on keywords
- 👋 **Welcome** - First-time contributor message

---

## 🔧 Setup Instructions

### 1. Required Secrets

Configure these secrets in your GitHub repository settings:

**Settings → Secrets and variables → Actions → New repository secret**

#### Docker Hub (Optional - for Docker image publishing)
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token-or-password
```

#### Code Coverage (Optional)
```
CODECOV_TOKEN=your-codecov-token
```

#### Gitleaks (Optional)
```
GITLEAKS_LICENSE=your-gitleaks-license
```

### 2. Repository Settings

Enable these features in repository settings:

#### Security
- **Settings → Security → Code security and analysis**
  - ✅ Enable Dependency graph
  - ✅ Enable Dependabot alerts
  - ✅ Enable Dependabot security updates
  - ✅ Enable Code scanning (CodeQL)
  - ✅ Enable Secret scanning

#### Actions
- **Settings → Actions → General**
  - ✅ Allow all actions and reusable workflows
  - ✅ Read and write permissions for GITHUB_TOKEN
  - ✅ Allow GitHub Actions to create and approve pull requests

### 3. Branch Protection Rules

**Settings → Branches → Add branch protection rule**

For `main` branch:
```
✅ Require pull request reviews before merging
✅ Require status checks to pass before merging
   - Backend Tests
   - Frontend Build & Test
   - CodeQL Analysis
✅ Require branches to be up to date before merging
✅ Require conversation resolution before merging
✅ Do not allow bypassing the above settings
```

---

## 📊 Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI/CD%20Pipeline/badge.svg)
![Security Scan](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CodeQL%20Security%20Analysis/badge.svg)
![Release](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Release/badge.svg)
```

---

## 🔄 Workflow Examples

### Running CI/CD Manually

```bash
# Go to Actions tab → CI/CD Pipeline → Run workflow
# Select branch and click "Run workflow"
```

### Creating a Release

```bash
# Method 1: Create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Method 2: Use GitHub UI
# Go to Actions → Release → Run workflow → Enter version
```

### Checking Security Issues

```bash
# Security tab shows:
# - CodeQL alerts
# - Dependabot alerts
# - Secret scanning alerts
```

---

## 🧪 Testing Workflows Locally

### Using Act (GitHub Actions locally)

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run a specific job
act -j backend-test

# Run PR checks
act pull_request

# Run with secrets
act -s DOCKER_USERNAME=myuser -s DOCKER_PASSWORD=mypass
```

### Manual Testing

```bash
# Backend tests
cd choreo-ai-assistant
pip install -r requirements.txt
pytest backend/tests/ -v

# Frontend tests
cd frontend
npm ci
npm run build

# Code quality
pip install black isort flake8
black backend/
isort backend/
flake8 backend/

# Security
pip install safety bandit
safety check -r requirements.txt
bandit -r backend/
```

---

## 📝 Best Practices

### Commit Messages
Follow conventional commits:
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
perf: improve performance
test: add tests
build: update build system
ci: update CI/CD
chore: maintenance tasks
```

### PR Titles
Use the same format as commit messages:
```
feat(backend): add new endpoint for data ingestion
fix(frontend): resolve table overflow issue
docs: update GitHub Actions documentation
```

### Branch Naming
```
feature/add-new-endpoint
fix/resolve-overflow-bug
hotfix/security-vulnerability
chore/update-dependencies
docs/improve-readme
```

---

## 🐛 Troubleshooting

### Workflow Fails

**Check the logs:**
1. Go to Actions tab
2. Click on the failed workflow run
3. Click on the failed job
4. Expand the failed step

**Common issues:**
- Missing secrets → Add in repository settings
- Permissions error → Enable write permissions for GITHUB_TOKEN
- Dependency conflicts → Update requirements.txt
- Test failures → Fix failing tests locally first

### Docker Build Fails

```bash
# Test Docker build locally
docker build -t test-build -f Dockerfile .

# Check for missing files
ls -la

# Verify Dockerfile syntax
docker build --no-cache -t test-build -f Dockerfile .
```

### CodeQL Analysis Fails

- Ensure all dependencies are installable
- Check for syntax errors in code
- Verify Python/JavaScript versions match workflow

---

## 📈 Monitoring

### Workflow Runs
- **Actions tab** → View all workflow runs
- **Pull Requests** → See required checks
- **Security tab** → View security alerts

### Notifications
Configure in **Settings → Notifications**:
- ✅ Email notifications for failed workflows
- ✅ GitHub mobile app notifications

---

## 🔐 Security Considerations

### Secrets Management
- ✅ Never commit secrets to repository
- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate secrets regularly
- ✅ Use environment-specific secrets

### Dependency Security
- ✅ Review Dependabot alerts weekly
- ✅ Update vulnerable dependencies promptly
- ✅ Test updates in non-production first

### Code Scanning
- ✅ Review CodeQL alerts
- ✅ Fix high/critical issues immediately
- ✅ Monitor security tab regularly

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

---

## ✅ Checklist

Before pushing to production:

- [ ] All secrets configured
- [ ] Branch protection rules enabled
- [ ] All workflows passing
- [ ] No security alerts
- [ ] Dependencies up to date
- [ ] Docker images building successfully
- [ ] Tests passing locally and in CI
- [ ] Documentation updated

---

**Need help?** Open an issue with the `ci/cd` label.

