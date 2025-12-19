#!/bin/bash
# Quick commit and push script for workflow fixes

echo "🔧 GitHub Actions Workflow Fixes - Quick Deploy"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -d ".github/workflows" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this script from the repository root"
    exit 1
fi

echo "📋 Changes to be committed:"
echo ""
echo "Workflow files (6 files):"
echo "  ✅ .github/workflows/ci-cd.yml"
echo "  ✅ .github/workflows/pr-checks.yml"
echo "  ✅ .github/workflows/security.yml"
echo "  ✅ .github/workflows/dependency-check.yml"
echo "  ✅ .github/workflows/release.yml"
echo "  ✅ .github/workflows/auto-assign.yml"
echo ""
echo "Documentation files (3 files):"
echo "  ✅ .github/NETWORK_TIMEOUT_FIX.md"
echo "  ✅ .github/WORKFLOW_FIXES_APPLIED.md"
echo "  ✅ .github/ISSUE_TEMPLATE/DOCKER_FIX_SUMMARY.md"
echo ""

read -p "📤 Do you want to commit and push these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Committing changes..."

    # Add all workflow files
    git add .github/workflows/*.yml

    # Add documentation files
    git add .github/NETWORK_TIMEOUT_FIX.md
    git add .github/WORKFLOW_FIXES_APPLIED.md
    git add .github/ISSUE_TEMPLATE/DOCKER_FIX_SUMMARY.md

    # Commit with detailed message
    git commit -m "fix(workflows): Add network timeout resilience to all GitHub Actions workflows

- Add job-level timeouts (5-60 min depending on job type)
- Add step-level timeouts for checkout (10 min)
- Configure shallow clones (fetch-depth: 1) for faster checkout
- Disable credential persistence for better security
- Add non-interactive mode (GIT_TERMINAL_PROMPT: 0)

Fixes network timeout errors:
- Error: Failed to connect to github.com port 443
- The process '/usr/bin/git' failed with exit code 128

Updated workflows:
- ci-cd.yml (5 jobs)
- pr-checks.yml (2+ jobs)
- security.yml (3 jobs)
- dependency-check.yml (3 jobs)
- release.yml (1 job)
- auto-assign.yml (2 jobs)

Documentation:
- Added NETWORK_TIMEOUT_FIX.md with detailed troubleshooting
- Added WORKFLOW_FIXES_APPLIED.md with complete summary
- Updated DOCKER_FIX_SUMMARY.md with network fix reference"

    echo ""
    echo "📤 Pushing to GitHub..."
    git push origin main

    echo ""
    echo "✅ Success!"
    echo ""
    echo "📊 Next steps:"
    echo "  1. Go to: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
    echo "  2. Watch the workflow run"
    echo "  3. Verify checkout completes in <1 minute"
    echo ""
    echo "📚 Documentation:"
    echo "  - .github/NETWORK_TIMEOUT_FIX.md - Detailed fix guide"
    echo "  - .github/WORKFLOW_FIXES_APPLIED.md - Complete summary"
    echo ""
else
    echo ""
    echo "⏸️  Aborted. No changes committed."
    echo ""
    echo "To commit manually later:"
    echo "  git add .github/"
    echo "  git commit -m 'fix: Add network timeout resilience to workflows'"
    echo "  git push origin main"
    echo ""
fi

