# Reprocessing Failed Files Guide

## Problem

Your previous run processed 47/87 files successfully. The 40 failed files were mostly PowerPoint (.pptx) files that failed due to missing `python-pptx` module.

**Good news:** The module is now installed! ✅

## Solution - Incremental Processing

I've added an `--incremental` flag to the diagram processor that will:
- ✅ **Skip files that were already processed successfully** (have summaries)
- ✅ **Reprocess files that failed** (no summaries)
- ✅ **Process any new files** added since last run

### Quick Command

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"
source ../.venv/bin/activate
python main.py --incremental
```

This will:
1. Skip the 47 files that were already processed ⏭️
2. Process the 40 failed files (now that python-pptx is installed) ✅
3. Much faster than reprocessing everything! 🚀

## Expected Output

You should see output like:

```
[STEP 2-6/7] Processing 87 files...

--- Processing 1/87: already_processed.png ---
  ⏭️  Skipping (already processed)

--- Processing 42/87: failed_pptx_file.pptx ---
  [1/5] Extracting text...
    ✓ Extracted 2500 characters from 15 slides
  [2/5] Generating summary...
    ✓ Summary: 680 chars, 12 concepts, 18 entities
  [3/5] Creating chunks...
    ✓ Created 3 chunks from summary
  [4/5] Generating embeddings...
    ✓ Generated 3 embeddings
  [5/5] Storing in Pinecone...
    ✓ Stored 3 embeddings in Pinecone

================================================================================
📊 PROCESSING SUMMARY
================================================================================
✓ Files Processed: 40/87
⏭️  Files Skipped: 47
✓ Summaries Generated: 40
✓ Chunks Created: 62  (new chunks from failed files)
✓ Embeddings Stored: 62  (new embeddings)
✓ Knowledge Graph: 1200+ nodes, 2100+ edges
⏱️  Total Time: ~10 minutes
================================================================================
```

## Alternative: Full Reprocess

If you want to reprocess ALL files from scratch:

```bash
# Backup existing output
mv output output_backup_$(date +%Y%m%d)

# Run full processing
python main.py
```

This will:
- Process all 87 files again
- Take longer (~10-15 minutes)
- Overwrite existing embeddings in Pinecone

## Verify PPTX Support

Before running, verify python-pptx is working:

```bash
python -c "import pptx; print('✓ python-pptx is installed, version:', pptx.__version__)"
```

Should output:
```
✓ python-pptx is installed, version: 0.6.23
```

## Command Options

```bash
# Incremental processing (recommended)
python main.py --incremental

# Process only PPTX files (if you want to focus on just those)
python main.py --file-types pptx

# Dry run to see what would be processed
python main.py --dry-run

# Full reprocess (no skip)
python main.py
```

## Expected Results

After incremental processing completes:
- **Total processed:** 87/87 files (100%)
- **New embeddings:** ~60-80 (from the 40 previously failed files)
- **Total embeddings in Pinecone:** ~130-150 total
- **Knowledge graph:** Will be regenerated with all data

---

**Ready to run?** 

```bash
cd diagram_processor
python main.py --incremental
```

This will efficiently process only the failed files while skipping already-processed ones! 🎉

