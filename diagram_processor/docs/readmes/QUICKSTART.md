# Quick Start Guide - Diagram Processor

## ✅ Installation Complete!

All dependencies have been installed successfully.

## 📋 Before Running

You need to add your API keys to the `.env` file in the main project directory:

```bash
# Edit the .env file
nano ../.env

# Add these keys if not already present:
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name

# Optional (for better OCR quality):
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-cloud-credentials.json
```

## 🎯 Quick Commands

### 1. Test the Setup
```bash
python3 test_setup.py
```

### 2. See What Files Will Be Processed (Dry Run)
```bash
python3 main.py --dry-run
```
This will show you all 87 discovered files without processing them.

### 3. Process All Diagrams
```bash
python3 main.py
```
⏱️ This will take approximately 15-30 minutes depending on your API rate limits.

### 4. Process Specific File Types Only
```bash
# Process only images
python3 main.py --file-types png jpg

# Process only documents
python3 main.py --file-types docx pdf

# Process only Draw.io files
python3 main.py --file-types drawio
```

## 📊 What Gets Processed

**87 files discovered** (70.9 MB total):
- 📸 **24 PNG images** (21.6 MB) - OCR extraction
- 📄 **31 DOCX documents** (19.2 MB) - Text parsing
- 🎨 **17 Draw.io files** (2.2 MB) - XML parsing
- 📊 **11 PowerPoint files** (27.1 MB) - Content extraction
- 📈 **3 Excel files** (0.1 MB) - Data extraction
- 🖼️ **1 SVG file** (0.7 MB) - Text parsing

## 📤 What You'll Get

After processing, check the `output/` directory:

### 1. **Summaries** (`output/summaries/`)
Individual text files for each diagram containing:
- Comprehensive AI-generated summary
- Key concepts and technologies
- Identified entities (components, services)
- Relationships between entities

### 2. **Knowledge Graph** (`output/graphs/`)
Multiple visualization formats:
- `*_networkx.png` - Network diagram (high quality)
- `*_graphviz.png` - Hierarchical view
- `*_mermaid.md` - Text-based diagram for docs
- `*.json` - Complete graph data

### 3. **Logs** (`output/processing.log`)
Detailed processing information and any errors

### 4. **Report** (`output/processing_report_*.txt`)
Comprehensive statistics and per-file results

## 🔍 After Processing

All diagram content will be **searchable in your Pinecone database**! The embeddings include:
- Full extracted text
- AI-generated summaries
- Key concepts
- Source file metadata

Use your existing RAG system to query the diagram content!

## 🛠️ Troubleshooting

### If you see "OpenAI API Key not set"
```bash
# Make sure your .env file in the parent directory has:
OPENAI_API_KEY=sk-...
```

### If you see "Pinecone API Key not set"
```bash
# Add to .env:
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...
```

### If OCR quality is poor
Install Google Cloud Vision API credentials for better results:
```bash
# Add to .env:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### If processing is slow
This is normal! Processing 87 files with:
- OCR for images
- AI summarization
- Embedding generation
- Graph building

...takes time. The system includes delays to respect API rate limits.

## 📞 Need Help?

Run with `--help` to see all options:
```bash
python3 main.py --help
```

## 🎉 Ready to Go!

Once your API keys are set in the `.env` file, simply run:
```bash
python3 main.py
```

And watch the magic happen! 🚀

