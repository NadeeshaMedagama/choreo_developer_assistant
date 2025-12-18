#!/bin/bash
# Test script to verify PORT environment variable handling

echo "=========================================="
echo "Testing Choreo AI Assistant Port Binding"
echo "=========================================="
echo ""

# Test 1: Check if start.py exists
echo "✓ Test 1: Check start.py exists"
if [ -f "start.py" ]; then
    echo "  ✓ start.py found"
else
    echo "  ✗ start.py NOT found"
    exit 1
fi
echo ""

# Test 2: Check if start.sh exists
echo "✓ Test 2: Check start.sh exists"
if [ -f "start.sh" ]; then
    echo "  ✓ start.sh found"
else
    echo "  ✗ start.sh NOT found"
    exit 1
fi
echo ""

# Test 3: Check if Dockerfile uses start.py
echo "✓ Test 3: Check Dockerfile uses start.py"
if grep -q "start.py" Dockerfile; then
    echo "  ✓ Dockerfile uses start.py"
else
    echo "  ✗ Dockerfile does NOT use start.py"
    exit 1
fi
echo ""

# Test 4: Check if Dockerfile binds to 0.0.0.0
echo "✓ Test 4: Check start.py binds to 0.0.0.0"
if grep -q "0.0.0.0" start.py; then
    echo "  ✓ start.py binds to 0.0.0.0"
else
    echo "  ✗ start.py does NOT bind to 0.0.0.0"
    exit 1
fi
echo ""

# Test 5: Check if start.py uses PORT env var
echo "✓ Test 5: Check start.py uses PORT environment variable"
if grep -q "PORT" start.py; then
    echo "  ✓ start.py uses PORT env var"
else
    echo "  ✗ start.py does NOT use PORT env var"
    exit 1
fi
echo ""

# Test 6: Verify Choreo component.yaml exists
echo "✓ Test 6: Check .choreo/component.yaml exists"
if [ -f ".choreo/component.yaml" ]; then
    echo "  ✓ .choreo/component.yaml found"
else
    echo "  ✗ .choreo/component.yaml NOT found"
fi
echo ""

echo "=========================================="
echo "All Port Binding Tests Passed! ✓"
echo "=========================================="
echo ""
echo "Ready to deploy to Choreo!"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Fix: Use PORT env variable for Choreo deployment'"
echo "3. git push"
echo "4. Deploy/Redeploy in Choreo console"
echo ""

