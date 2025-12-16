# 🔧 QUICK FIX - Install python-pptx and Process PPTX Files

## The Problem

Your PPTX files are failing with:
```
PPTX extraction failed: No module named 'pptx'
```

## ✅ The Solution (ONE COMMAND)

Run this script - it will install python-pptx and optionally process your files:

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"
python3 fix_and_process.py
```

This interactive script will:
1. ✅ Install python-pptx in the correct Python environment
2. ✅ Verify the installation
3. ✅ Give you options to process files immediately

---

## Alternative: Manual Steps

If you prefer to do it manually:

### Step 1: Install python-pptx

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/diagram_processor"
python3 -m pip install python-pptx
```

### Step 2: Verify Installation

```bash
python3 -c "import pptx; print('✓ Installed, version:', pptx.__version__)"
```

### Step 3: Process PPTX Files

Choose one:

```bash
# Option A: Process ONLY PPTX files (fastest - ~5 min)
python3 main.py --file-types pptx

# Option B: Process all files, skip already done (incremental - ~10 min)
python3 main.py --incremental

# Option C: Process everything from scratch (~15 min)
python3 main.py
```

---

## 📊 Expected Results

After running the fix, your PPTX files will process successfully:

```
--- Processing 80/87: 2024-01- WSO2 Presentation Template.pptx ---
  [1/5] Extracting text...
    ✓ Extracted 1500 characters from 10 slides
  [2/5] Generating summary...
    ✓ Summary: 450 chars, 8 concepts, 12 entities
  [3/5] Creating chunks...
    ✓ Created 2 chunks from summary
  [4/5] Generating embeddings...
    ✓ Generated 2 embeddings
  [5/5] Storing in Pinecone...
    ✓ Stored 2 embeddings in Pinecone

Final Summary:
✓ Files Processed: 87/87 (100%!)
✓ Chunks Created: 136+
✓ Embeddings Stored: 136+
```

---

## 🚀 Recommended Command

Just run this and follow the prompts:

```bash
cd diagram_processor
python3 fix_and_process.py
```

**That's it!** The script will handle everything for you. 🎉

