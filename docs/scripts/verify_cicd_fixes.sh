#!/bin/bash
# Verification script for CI/CD fixes

echo "======================================"
echo "CI/CD Fixes Verification"
echo "======================================"
echo ""

echo "1. Checking MonitoringButton.jsx exists..."
if [ -f "frontend/src/components/MonitoringButton.jsx" ]; then
    echo "   ✅ MonitoringButton.jsx exists"
    echo "   Lines: $(wc -l < frontend/src/components/MonitoringButton.jsx)"
    echo "   First line: $(head -1 frontend/src/components/MonitoringButton.jsx)"
else
    echo "   ❌ MonitoringButton.jsx NOT FOUND"
fi
echo ""

echo "2. Checking App.jsx imports..."
if grep -q "MonitoringButton" frontend/src/App.jsx; then
    echo "   ✅ App.jsx imports MonitoringButton"
    grep "MonitoringButton" frontend/src/App.jsx | head -1
else
    echo "   ❌ App.jsx does NOT import MonitoringButton"
fi
echo ""

echo "3. Checking .gitignore for monitoring entries..."
if grep -q "prometheus_data" .gitignore; then
    echo "   ✅ .gitignore includes monitoring exclusions"
    grep -A 3 "Monitoring runtime data" .gitignore
else
    echo "   ❌ .gitignore missing monitoring exclusions"
fi
echo ""

echo "4. Checking CI/CD workflow for disk cleanup..."
if grep -q "Free up disk space" .github/workflows/ci-cd.yml; then
    echo "   ✅ CI/CD workflow has disk cleanup step"
else
    echo "   ❌ CI/CD workflow missing disk cleanup"
fi
echo ""

echo "5. Checking git status..."
git status --short
echo ""

echo "6. Recent commits..."
git log --oneline -3
echo ""

echo "======================================"
echo "Verification Complete!"
echo "======================================"

