#!/bin/bash
# Quick guide to run the ingestion pipeline after the pagination fix

echo "==================================================================="
echo "GitHub Issues Ingestion - Pagination Fix Applied"
echo "==================================================================="
echo ""
echo "The pagination fix has been applied to handle repositories with >1000 issues."
echo ""
echo "Key Changes:"
echo "  - Added pagination limit checks (max 10 pages = 1000 items)"
echo "  - Graceful handling of 422 errors"
echo "  - Search API fallback method (optional)"
echo ""
echo "==================================================================="
echo ""

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  WARNING: GITHUB_TOKEN environment variable is not set"
    echo ""
    echo "Please set it using:"
    echo "  export GITHUB_TOKEN=your_github_token"
    echo ""
    exit 1
fi

echo "✓ GITHUB_TOKEN is set"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/.."

echo "Options:"
echo "  1. Run full ingestion (will fetch up to 1000 issues per repo)"
echo "  2. Run with max_issues limit (e.g., 500 issues)"
echo "  3. Run test to verify the fix"
echo ""
read -p "Select option (1-3): " option

case $option in
    1)
        echo ""
        echo "Running full ingestion..."
        python run_ingestion.py
        ;;
    2)
        read -p "Enter max issues per repo (e.g., 500): " max_issues
        echo ""
        echo "Running ingestion with max_issues=$max_issues..."
        # Note: You may need to modify run_ingestion.py to accept this parameter
        python run_ingestion.py --max-issues "$max_issues"
        ;;
    3)
        echo ""
        echo "Running pagination fix test..."
        python github_issues_ingestion/test_pagination_fix.py
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "==================================================================="
echo "Process completed"
echo "==================================================================="

