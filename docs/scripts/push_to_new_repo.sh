#!/bin/bash

# Script to push project to new repository: choreo_developer_assistant
# Usage: ./push_to_new_repo.sh <your_github_username>

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Push to New Repository: choreo_developer_assistant              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if username provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: GitHub username not provided${NC}"
    echo ""
    echo "Usage: ./push_to_new_repo.sh <your_github_username>"
    echo ""
    echo "Example:"
    echo "  ./push_to_new_repo.sh nadeeshame"
    exit 1
fi

GITHUB_USERNAME="$1"
REPO_NAME="choreo_developer_assistant"

echo -e "${YELLOW}⚠️  IMPORTANT: Make sure you have created the repository on GitHub first!${NC}"
echo ""
echo "Repository URL will be:"
echo -e "  ${GREEN}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git${NC}"
echo ""
read -p "Have you created this repository on GitHub? (y/n): " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Please create the repository first:${NC}"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: ${REPO_NAME}"
    echo "3. DO NOT initialize with README, .gitignore, or license"
    echo "4. Click 'Create repository'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1: Security Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

# Check for .env in tracked files
if git ls-files | grep -q "\.env$"; then
    echo -e "${RED}❌ ERROR: .env file is tracked by git!${NC}"
    echo "This is a security risk. Please remove it from git first."
    exit 1
else
    echo -e "${GREEN}✅ .env files are not tracked${NC}"
fi

# Check for credentials
if git ls-files | grep -q "^credentials/"; then
    echo -e "${RED}❌ ERROR: credentials/ directory is tracked by git!${NC}"
    echo "This is a security risk. Please remove it from git first."
    exit 1
else
    echo -e "${GREEN}✅ credentials/ is not tracked${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2: Check Git Status${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

git status

echo ""
read -p "Do you want to add all changes? (y/n): " add_all

if [[ $add_all =~ ^[Yy]$ ]]; then
    echo "Adding all changes..."
    git add .
    echo -e "${GREEN}✅ Changes added${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3: Commit Changes${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
else
    read -p "Enter commit message (or press Enter for default): " commit_msg

    if [ -z "$commit_msg" ]; then
        commit_msg="Initial commit: Choreo Developer Assistant with Milvus migration"
    fi

    echo "Committing with message: $commit_msg"
    git commit -m "$commit_msg"
    echo -e "${GREEN}✅ Changes committed${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4: Configure Remote${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

# Remove old remote if exists
if git remote | grep -q "^origin$"; then
    echo "Removing old remote..."
    git remote remove origin
    echo -e "${GREEN}✅ Old remote removed${NC}"
fi

# Add new remote
echo "Adding new remote..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
echo -e "${GREEN}✅ New remote added${NC}"

# Verify remote
echo ""
echo "Remote configuration:"
git remote -v

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 5: Rename Branch to main${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

git branch -M main
echo -e "${GREEN}✅ Branch renamed to main${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 6: Push to New Repository${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${YELLOW}⚠️  About to push to:${NC}"
echo -e "  ${GREEN}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git${NC}"
echo ""
read -p "Continue with push? (y/n): " push_confirm

if [[ ! $push_confirm =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Push cancelled. You can manually push later with:${NC}"
    echo "  git push -u origin main"
    exit 0
fi

echo ""
echo "Pushing to remote repository..."
echo ""

if git push -u origin main; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ SUCCESS!                                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 Your project has been pushed to the new repository!${NC}"
    echo ""
    echo "Repository URL:"
    echo -e "  ${BLUE}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository to verify files"
    echo "  2. Add repository description and topics"
    echo "  3. Set up branch protection rules (optional)"
    echo "  4. Configure GitHub Actions (optional)"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Push failed!${NC}"
    echo ""
    echo "Common issues:"
    echo "  1. Authentication: Use GitHub Personal Access Token as password"
    echo "     Generate at: https://github.com/settings/tokens"
    echo ""
    echo "  2. Repository doesn't exist: Create it on GitHub first"
    echo ""
    echo "  3. Branch protection: Disable branch protection temporarily"
    echo ""
    echo "You can try again manually with:"
    echo "  git push -u origin main"
    exit 1
fi

