#!/bin/bash
# Quick validation script for requirements.txt migration

cd "/home/nadeeshame/Projects/Choreo AI Assistant/choreo-ai-assistant"

echo "======================================"
echo "Requirements.txt Migration Validation"
echo "======================================"
echo ""

# 1. Check file existence
echo "1. File Existence Check"
echo "----------------------"
files=(
    "requirements.txt"
    "backend/requirements.txt"
    "backend/choreo-ai-assistant/requirements.txt"
    "backend/diagram_processor/requirements.txt"
    "backend/start.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file MISSING"
    fi
done
echo ""

# 2. Check file sizes
echo "2. File Sizes"
echo "-------------"
ls -lh backend/requirements.txt backend/choreo-ai-assistant/requirements.txt 2>/dev/null
echo ""

# 3. Compare files
echo "3. File Content Comparison"
echo "--------------------------"
if diff -q backend/requirements.txt backend/choreo-ai-assistant/requirements.txt >/dev/null 2>&1; then
    echo "✅ backend/requirements.txt and backend/choreo-ai-assistant/requirements.txt are identical"
else
    echo "❌ Files differ!"
fi
echo ""

# 4. Check Dockerfile references
echo "4. Dockerfile References"
echo "------------------------"
echo "Root Dockerfile:"
grep "requirements.txt" Dockerfile | head -3
echo ""
echo "Backend Dockerfile:"
grep "requirements.txt" backend/Dockerfile | head -3
echo ""
echo "Docker Compose Dockerfile:"
grep "requirements.txt" docker/Dockerfile | head -3
echo ""

# 5. Python syntax check
echo "5. Python Syntax Validation"
echo "---------------------------"
if python3 -m py_compile backend/start.py 2>/dev/null; then
    echo "✅ backend/start.py syntax is valid"
else
    echo "❌ backend/start.py has syntax errors"
fi
echo ""

# 6. Test root requirements references
echo "6. Root Requirements.txt References"
echo "-----------------------------------"
python3 << 'EOF'
import os
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        if line.startswith('-r'):
            path = line.replace('-r', '').strip()
            if os.path.exists(path):
                print(f"✅ {path}")
            else:
                print(f"❌ {path} NOT FOUND")
EOF
echo ""

echo "======================================"
echo "Validation Complete!"
echo "======================================"

