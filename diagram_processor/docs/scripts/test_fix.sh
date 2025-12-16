#!/bin/bash
# Quick Test Script for Chunking & Embedding Console Output

echo "=========================================="
echo "Testing Chunking & Embedding Console Output"
echo "=========================================="

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"

# Activate virtual environment
source ../.venv/bin/activate

echo ""
echo "1️⃣  Testing Pinecone format fix..."
python test_console_output.py

echo ""
echo "2️⃣  Ready to run full processing!"
echo ""
echo "To process all diagrams, run:"
echo "  python main.py"
echo ""
echo "Expected output will include:"
echo "  ✓ Created X chunks from summary"
echo "  ✓ Generated X embeddings"
echo "  ✓ Stored X embeddings in Pinecone"
echo ""
echo "=========================================="

