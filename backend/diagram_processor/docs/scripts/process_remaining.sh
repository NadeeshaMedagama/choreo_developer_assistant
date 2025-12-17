#!/bin/bash
# Quick script to process remaining failed files

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    PROCESS REMAINING FAILED FILES                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"

echo "📍 Current directory: $(pwd)"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

echo ""
echo "✅ Verifying dependencies..."

# Check python-pptx
if python -c "import pptx" 2>/dev/null; then
    echo "  ✓ python-pptx installed"
else
    echo "  ✗ python-pptx NOT installed"
    echo "  Installing now..."
    pip install python-pptx
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                      STARTING INCREMENTAL PROCESSING                       ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will:"
echo "  ⏭️  Skip 47 files that were already processed"
echo "  ✅ Process 40 files that failed previously"
echo "  📦 Create chunks for each file"
echo "  🧮 Generate embeddings"
echo "  💾 Store in Pinecone"
echo ""
echo "Estimated time: ~10 minutes"
echo ""
echo "Press Ctrl+C to cancel, or press Enter to continue..."
read -r

# Run incremental processing
python main.py --incremental

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                              COMPLETE! ✅                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Check the summary above for results."
echo ""
echo "To view detailed logs:"
echo "  cat output/processing.log"
echo ""
echo "To view the processing report:"
echo "  ls -lt output/processing_report_*.txt | head -1 | awk '{print \$NF}' | xargs cat"
echo ""

