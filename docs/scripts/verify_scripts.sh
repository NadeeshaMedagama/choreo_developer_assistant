#!/bin/bash
# Quick verification that all scripts exist

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          VERIFICATION: All Scripts Created              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

check_file() {
    if [ -x "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1 (missing or not executable)"
        return 1
    fi
}

echo "Checking startup scripts..."
echo ""

check_file "./start_local.sh"
check_file "./test_setup.sh"
check_file "./backend/start_local.sh"
check_file "./frontend/start_local.sh"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    READY TO START                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. ./test_setup.sh     # Verify environment"
echo "  2. ./start_local.sh    # Start application"
echo "  3. Open: http://localhost:5173"
echo ""

