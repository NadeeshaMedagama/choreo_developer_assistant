#!/bin/bash
#
# Quick Dockerfile Verification Script
# Checks the Dockerfile for common issues without building
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "======================================"
echo "🔍 Quick Dockerfile Check"
echo "======================================"
echo ""

# Track issues
ISSUES=0

# Check 1: Dockerfile exists
echo "1️⃣  Checking Dockerfile existence..."
if [ -f "Dockerfile" ]; then
    echo "   ✅ Dockerfile found"
else
    echo "   ❌ Dockerfile NOT found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Check 2: start.py exists
echo "2️⃣  Checking start.py existence..."
if [ -f "start.py" ]; then
    echo "   ✅ start.py found"
else
    echo "   ❌ start.py NOT found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Check 3: No start.sh reference
echo "3️⃣  Checking for incorrect start.sh reference..."
if grep -q "start.sh" Dockerfile 2>/dev/null; then
    echo "   ❌ PROBLEM: Dockerfile references start.sh (which doesn't exist)"
    echo "   Found at:"
    grep -n "start.sh" Dockerfile | head -5
    ISSUES=$((ISSUES + 1))
else
    echo "   ✅ No start.sh reference (correct!)"
fi
echo ""

# Check 4: Correct chmod command
echo "4️⃣  Checking chmod command..."
if grep -q "chmod.*start.py" Dockerfile 2>/dev/null; then
    echo "   ✅ chmod for start.py found"
    echo "   Line:"
    grep -n "chmod.*start.py" Dockerfile | head -1
else
    echo "   ⚠️  No chmod for start.py (might be OK)"
fi
echo ""

# Check 5: Verify CMD references start.py
echo "5️⃣  Checking CMD/ENTRYPOINT..."
if grep -E "^CMD|^ENTRYPOINT" Dockerfile | grep -q "start.py" 2>/dev/null; then
    echo "   ✅ CMD/ENTRYPOINT references start.py"
    grep -E "^CMD|^ENTRYPOINT" Dockerfile | grep "start.py"
else
    echo "   ⚠️  CMD/ENTRYPOINT doesn't reference start.py"
    grep -E "^CMD|^ENTRYPOINT" Dockerfile || echo "   (No CMD/ENTRYPOINT found)"
fi
echo ""

# Summary
echo "======================================"
if [ $ISSUES -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo "======================================"
    echo ""
    echo "The Dockerfile looks good. You can:"
    echo "  • Commit and push to trigger GitHub Actions"
    echo "  • Run a local build: docker build -t test ."
    echo "  • Run full validation: .github/scripts/validate-docker-build.sh"
    echo ""
    exit 0
else
    echo "❌ FOUND $ISSUES ISSUE(S)"
    echo "======================================"
    echo ""
    echo "Please fix the issues above before proceeding."
    echo ""
    exit 1
fi

