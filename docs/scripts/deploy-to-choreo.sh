#!/bin/bash
# deploy-to-choreo.sh
# Complete deployment script for Choreo

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         Choreo AI Assistant - Deployment Script               ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Optional cleanup
read -p "Run cleanup to remove unnecessary files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Running cleanup..."
    ./cleanup-before-build.sh
    echo "✅ Cleanup complete!"
    echo ""
fi

# Step 2: Show what will be committed
echo "📊 Changes to be committed:"
git status --short
echo ""

# Step 3: Confirm commit
read -p "Commit these changes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Committing changes..."
    git commit -F COMMIT_MESSAGE.txt
    echo "✅ Committed!"
    echo ""
else
    echo "❌ Commit cancelled."
    exit 0
fi

# Step 4: Push to GitHub
read -p "Push to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    git push origin main
    echo "✅ Pushed!"
    echo ""
else
    echo "⏸️  Push skipped. You can push manually later with:"
    echo "   git push origin main"
    exit 0
fi

# Step 5: Final instructions
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                  ✅ Git operations complete! ✅               ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Go to Choreo Console:"
echo "   https://console.choreo.dev/"
echo ""
echo "2. Navigate to your component"
echo ""
echo "3. Click 'Deploy' button"
echo ""
echo "4. Monitor the build logs"
echo "   → Should complete without disk space errors ✅"
echo ""
echo "5. Once deployed, verify:"
echo "   → Health check at / returns 200"
echo "   → API endpoint /chat works"
echo "   → Memory usage under 2Gi"
echo ""
echo "📖 Documentation:"
echo "   - QUICK_FIX.md (quick reference)"
echo "   - DEPLOYMENT_FIX_SUMMARY.md (detailed guide)"
echo ""
echo "🎉 The build should succeed now! Good luck! 🚀"

