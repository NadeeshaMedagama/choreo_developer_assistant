#!/bin/bash
# Quick deployment script for Pinecone to Milvus migration

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║    PINECONE → MILVUS MIGRATION DEPLOYMENT                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/.choreo/openapi.yaml" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this script from the repository root"
    exit 1
fi

echo "📋 Changes ready to deploy:"
echo ""
echo "✅ backend/.choreo/openapi.yaml"
echo "   • Removed Pinecone references"
echo "   • Added Milvus examples"
echo "   • Updated health endpoints"
echo ""
echo "✅ backend/app.py"
echo "   • Updated /health endpoint"
echo "   • Tests Milvus connection"
echo "   • Returns proper status format"
echo ""
echo "📚 Documentation:"
echo "   • docs/PINECONE_TO_MILVUS_MIGRATION_COMPLETE.md"
echo "   • .github/PINECONE_REMOVED_QUICK_REF.txt"
echo ""

read -p "🚀 Deploy these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📦 Staging changes..."

    # Stage the files
    git add backend/.choreo/openapi.yaml
    git add backend/app.py
    git add docs/PINECONE_TO_MILVUS_MIGRATION_COMPLETE.md
    git add .github/PINECONE_REMOVED_QUICK_REF.txt

    echo ""
    echo "💾 Committing..."

    # Commit with detailed message
    git commit -m "fix: Remove Pinecone references, show Milvus in health checks

- Updated OpenAPI schema to show Milvus examples instead of Pinecone
- Modified /health endpoint to return {status, milvus} format
- Added actual Milvus connection testing in health check
- Updated /api/health to show detailed component status
- Fixed HealthResponse schema with proper nested structure

Health endpoints now correctly show:
- /health: {\"status\": \"healthy\", \"milvus\": \"connected\"}
- /api/health: Detailed component status with Milvus

No more Pinecone references in Choreo deployment! ✅

Files updated:
- backend/.choreo/openapi.yaml (OpenAPI specification)
- backend/app.py (Health check implementation)

Documentation added:
- docs/PINECONE_TO_MILVUS_MIGRATION_COMPLETE.md
- .github/PINECONE_REMOVED_QUICK_REF.txt"

    echo ""
    echo "📤 Pushing to GitHub..."
    git push origin main

    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                    ✅ SUCCESS!                            ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Changes deployed!"
    echo ""
    echo "📊 Next steps:"
    echo ""
    echo "  1. Choreo will auto-deploy your changes"
    echo "  2. Monitor deployment in Choreo Console"
    echo "  3. Verify health endpoint shows:"
    echo "     {\"status\": \"healthy\", \"milvus\": \"connected\"}"
    echo ""
    echo "🔍 Verify deployment:"
    echo "  • Choreo Console → Your Component → Endpoints"
    echo "  • Health check should show Milvus status"
    echo "  • No Pinecone references anywhere!"
    echo ""
    echo "📚 Full documentation:"
    echo "  docs/PINECONE_TO_MILVUS_MIGRATION_COMPLETE.md"
    echo ""
    echo "✅ All Pinecone references removed!"
    echo ""

else
    echo ""
    echo "⏸️  Deployment cancelled."
    echo ""
    echo "To deploy manually later:"
    echo "  git add backend/.choreo/openapi.yaml backend/app.py"
    echo "  git commit -m 'fix: Remove Pinecone, show Milvus status'"
    echo "  git push origin main"
    echo ""
fi

