#!/bin/bash

# Quick Start Script for Wiki Ingestion to Milvus
# This script helps you run the wiki ingestion with proper configuration

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Wiki Ingestion to Milvus - Quick Start                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/.." || exit 1

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in backend/"
    echo ""
    echo "Please create a .env file with the following variables:"
    echo "  - AZURE_OPENAI_API_KEY"
    echo "  - AZURE_OPENAI_ENDPOINT"
    echo "  - AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"
    echo "  - MILVUS_URI"
    echo "  - MILVUS_TOKEN"
    echo "  - MILVUS_COLLECTION_NAME"
    echo "  - WIKI_URL"
    echo ""
    exit 1
fi

# Source the .env file to check variables
source .env 2>/dev/null || true

# Check required environment variables
missing_vars=0

if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "❌ Missing: AZURE_OPENAI_API_KEY"
    missing_vars=1
fi

if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "❌ Missing: AZURE_OPENAI_ENDPOINT"
    missing_vars=1
fi

if [ -z "$MILVUS_URI" ]; then
    echo "❌ Missing: MILVUS_URI"
    missing_vars=1
fi

if [ -z "$MILVUS_TOKEN" ]; then
    echo "❌ Missing: MILVUS_TOKEN"
    missing_vars=1
fi

if [ $missing_vars -eq 1 ]; then
    echo ""
    echo "Please add the missing variables to your .env file"
    exit 1
fi

# Display configuration
echo "📋 Configuration:"
echo "  Wiki URL: ${WIKI_URL:-https://github.com/wso2/docs-choreo-dev/wiki}"
echo "  Max Depth: ${WIKI_MAX_DEPTH:-2}"
echo "  Max Pages: ${WIKI_MAX_PAGES:-50}"
echo "  Milvus Collection: ${MILVUS_COLLECTION_NAME:-choreo_developer_assistant}"
echo ""

# Ask for confirmation
read -p "Continue with ingestion? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting wiki ingestion..."
echo ""

# Run the ingestion script
python -m wiki_ingestion.examples.ingest_to_milvus

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Ingestion completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Verify data in Milvus"
    echo "  2. Test search functionality"
    echo "  3. Integrate with your RAG pipeline"
    echo ""
else
    echo ""
    echo "❌ Ingestion failed. Check the output above for errors."
    echo ""
    exit 1
fi

