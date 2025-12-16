#!/bin/bash
# Script to start completely fresh - removes all git history
# This creates a brand new repository with no previous commits
set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║           ⚠️  WARNING - DESTRUCTIVE OPERATION  ⚠️                   ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  1. Delete ALL git history"
echo "  2. Create a completely fresh repository"
echo "  3. Make ONE clean commit"
echo "  4. Push as a brand new project"
echo ""
echo -e "${RED}This action CANNOT be undone!${NC}"
echo ""
read -p "Are you ABSOLUTELY sure? Type 'yes' to continue: " confirm
if [[ "$confirm" != "yes" ]]; then
    echo ""
    echo "Operation cancelled. No changes made."
    exit 0
fi
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1: Final Security Scan${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo "Scanning for exposed credentials..."
# Scan for common credential patterns (GitHub tokens, API keys, etc.)
if grep -r -E "(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35})" --include="*.md" --include="*.yml" --include="*.yaml" --include="*.py" --include="*.js" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv . 2>/dev/null | grep -v "your_" | grep -v "example" | grep -v "placeholder"; then
    echo -e "${RED}❌ ERROR: Found exposed credentials!${NC}"
    echo "Please remove all credentials before starting fresh."
    exit 1
else
    echo -e "${GREEN}✅ No exposed credentials found${NC}"
fi
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2: Backup Current .git Directory${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
if [ -d ".git" ]; then
    echo "Creating backup of .git directory..."
    mv .git .git.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Backup created${NC}"
else
    echo "No .git directory found"
fi
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3: Initialize Fresh Repository${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
git init
echo -e "${GREEN}✅ Fresh git repository initialized${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4: Add All Files${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
git add .
echo -e "${GREEN}✅ All files staged${NC}"
echo ""
echo "Files to be committed:"
git status --short | head -20
echo "..."
echo "Total files: $(git status --short | wc -l)"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 5: Create Initial Commit${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
git commit -m "Initial commit: Choreo Developer Assistant
- AI-powered chatbot for Choreo platform documentation
- Milvus vector database for semantic search
- Azure OpenAI integration
- React + Vite frontend
- FastAPI backend
- Comprehensive monitoring and logging
- Security: All credentials in .env (gitignored)
"
echo -e "${GREEN}✅ Initial commit created${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 6: Configure Remote${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
if [ -z "$1" ]; then
    echo -e "${RED}❌ ERROR: GitHub username not provided${NC}"
    echo ""
    echo "Usage: ./START_FRESH_REPO.sh <github_username>"
    exit 1
fi
GITHUB_USERNAME="$1"
REPO_NAME="choreo_developer_assistant"
echo "Adding remote: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git branch -M main
echo -e "${GREEN}✅ Remote configured${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 7: Push to GitHub${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}⚠️  About to force push to:${NC}"
echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
read -p "Continue? (y/n): " push_confirm
if [[ ! $push_confirm =~ ^[Yy]$ ]]; then
    echo "Push cancelled."
    exit 0
fi
echo ""
echo "Pushing to remote..."
if git push -u origin main --force; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ SUCCESS!                                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 Fresh repository pushed successfully!${NC}"
    echo ""
    echo "Repository URL:"
    echo -e "  ${BLUE}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}${NC}"
    echo ""
    echo "History:"
    echo "  • Old commits: REMOVED ✓"
    echo "  • New commits: 1 (clean initial commit)"
    echo "  • Secrets: NONE ✓"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Push failed!${NC}"
    echo ""
    echo "The repository may already have content."
    echo "To completely replace it, you may need to:"
    echo "  1. Delete the repository on GitHub"
    echo "  2. Create it fresh (don't initialize)"
    echo "  3. Run this script again"
    exit 1
fi
