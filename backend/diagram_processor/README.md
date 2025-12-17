# Diagram Processor

A comprehensive, SOLID-architecture solution for processing Choreo platform architecture diagrams. This system extracts text from various diagram formats, generates intelligent summaries, creates embeddings, stores them in Milvus, and builds a knowledge graph visualization.

## 🎯 Features

- **Multi-Format Support**: PNG, JPG, SVG, PDF, Draw.io, DOCX, XLSX, PPTX
- **Intelligent OCR**: Uses Google Cloud Vision API (fallback to Tesseract)
- **AI-Powered Summaries**: Generates comprehensive summaries with GPT-4
- **Vector Embeddings**: Creates and stores embeddings in Milvus
- **Knowledge Graph**: Builds interactive visualizations showing relationships
- **SOLID Architecture**: Clean, maintainable, extensible code structure

## 📁 Project Structure

```
diagram_processor/
├── __init__.py           # Package initialization
├── main.py              # Main entry point
├── requirements.txt     # Dependencies
│
├── models/              # Domain models (Single Responsibility)
│   └── __init__.py      # DiagramFile, Summary, TextChunk, etc.
│
├── services/            # Business logic services
│   ├── __init__.py      # DiagramProcessorOrchestrator
│   ├── file_discovery.py      # File discovery
│   ├── text_extraction.py     # OCR and text extraction
│   ├── summary_generation.py  # AI summary generation
│   ├── chunking.py            # Text chunking
│   ├── embedding.py           # Embedding generation
│   └── knowledge_graph.py     # Graph building and visualization
│
├── repositories/        # Data access layer
│   └── __init__.py      # VectorStoreRepository (Milvus)
│
├── utils/              # Utilities
│   ├── __init__.py     # Config
│   └── logger.py       # Logging
│
└── output/             # Generated outputs
    ├── summaries/      # Text summaries
    ├── graphs/         # Knowledge graph visualizations
    └── processing.log  # Processing logs
```

## 🏗️ SOLID Principles Applied

### Single Responsibility Principle
- Each service has ONE clear purpose
- `FileDiscoveryService`: Only discovers files
- `TextExtractionService`: Only extracts text
- `SummaryGenerationService`: Only generates summaries

### Open/Closed Principle
- Extractor pattern allows adding new file types without modifying existing code
- New extractors extend `TextExtractor` abstract class

### Liskov Substitution Principle
- All extractors can be used interchangeably through `TextExtractor` interface
- Services depend on abstractions, not concrete implementations

### Interface Segregation Principle
- Focused interfaces for each service
- No client depends on methods it doesn't use

### Dependency Inversion Principle
- High-level orchestrator depends on service abstractions
- Services are injected, not created internally

## 🚀 Setup

### 1. Install Dependencies

```bash
cd diagram_processor
pip install -r requirements.txt
```

### 2. Install System Dependencies

**For OCR (Tesseract)**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

**For Graphviz**:
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
# Download from: https://graphviz.org/download/
```

### 3. Configure Environment Variables

The processor uses the same `.env` file as your main project. Ensure these are set:

```bash
# OpenAI (for embeddings and summaries)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Milvus (for vector storage)
MILVUS_URI=https://your-milvus-instance.serverless.aws-eu-central-1.cloud.zilliz.com
MILVUS_TOKEN=your_milvus_token_here
MILVUS_COLLECTION_NAME=readme_embeddings
MILVUS_DIMENSION=1536
MILVUS_METRIC=COSINE

# Google Cloud Vision (optional, for better OCR)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### 4. Verify Setup

```bash
python main.py --dry-run
```

This will discover all files without processing them.

## 📋 Usage

### Process All Diagrams

```bash
python main.py
```

### Process Specific File Types

```bash
# Process only images
python main.py --file-types png jpg jpeg

# Process only documents
python main.py --file-types docx pdf

# Process only Draw.io files
python main.py --file-types drawio
```

### Dry Run (Discovery Only)

```bash
python main.py --dry-run
```

## 🔄 Processing Pipeline

The system processes each diagram through 7 stages:

1. **File Discovery** - Scans directory for supported files
2. **Text Extraction** - Extracts text using OCR or parsing
3. **Summary Generation** - Creates AI-powered summaries with key concepts
4. **Chunking** - Breaks content into optimal chunks
5. **Embedding Generation** - Creates vector embeddings
6. **Vector Storage** - Stores in Milvus database
7. **Knowledge Graph** - Builds and visualizes relationships

## 📊 Output

After processing, you'll find:

### 1. Summaries (`output/summaries/`)
- Individual text files for each diagram
- Contains summary, key concepts, entities, and relationships

### 2. Knowledge Graph (`output/graphs/`)
- **NetworkX Visualization** (PNG): High-quality network diagram
- **Graphviz Visualization** (PNG): Hierarchical graph view
- **Mermaid Diagram** (MD): Text-based diagram for documentation
- **Graph JSON**: Complete graph data for custom visualization

### 3. Processing Log (`output/processing.log`)
- Detailed processing information
- Error tracking and debugging info

### 4. Processing Report
- Comprehensive report with statistics
- Individual file results
- Timestamps and performance metrics

## 🎨 Knowledge Graph Visualization

The knowledge graph shows:
- **Blue nodes**: Document files
- **Green nodes**: Components/entities (services, systems)
- **Pink nodes**: Concepts/technologies
- **Edges**: Relationships between nodes

### Example relationships:
- `Document` --[contains]--> `Component`
- `Document` --[discusses]--> `Concept`
- `Component` --[uses]--> `Component`
- `Component` --[connects_to]--> `Component`

## 🔍 Querying the Data

After processing, all diagram content is searchable in your Milvus Cloud database. The embeddings include:

- Full text content from diagrams
- AI-generated summaries
- Key concepts and entities
- Source file information

You can query using your existing RAG system!

## 🛠️ Extending the System

### Add New File Type Support

1. Create a new extractor class:

```python
class NewFormatExtractor(TextExtractor):
    def can_extract(self, file: DiagramFile) -> bool:
        return file.file_type == FileType.NEW_FORMAT
    
    def extract(self, file: DiagramFile) -> ExtractedContent:
        # Your extraction logic
        pass
```

2. Register it in `TextExtractionService`:

```python
self.extractors.append(NewFormatExtractor())
```

### Customize Chunking Strategy

Modify `ChunkingService` to implement your own chunking logic.

### Add New Graph Visualizations

Extend `KnowledgeGraphService` with new visualization methods.

## 📈 Performance

- Processes ~50 diagrams in ~10-15 minutes (depends on file sizes)
- Uses batching to avoid API rate limits
- Memory-efficient processing (one file at a time)
- Parallel-ready architecture for future optimization

## 🐛 Troubleshooting

### "No module named 'pptx'" when processing PowerPoint files
**Solution:** Install python-pptx module:
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
source .venv/bin/activate
pip install python-pptx
```

Then re-run the processing to process the previously failed PPTX files.

### "No module named 'google.cloud.vision'"
```bash
pip install google-cloud-vision
```

### "Tesseract not found"
Install Tesseract OCR (see Setup section)

### "Rate limit exceeded"
The system includes automatic delays. For heavy use, increase delays in embedding service.

### Memory issues
Reduce `CHUNK_SIZE` or `BATCH_SIZE` in `.env` file

### Some files were skipped during processing
Check the processing log at `output/processing.log` for detailed error messages. Common reasons:
- Missing Python modules (install via pip)
- Insufficient text extracted (file might be an image without text)
- File corruption or unsupported format variant

## 📝 License

Part of the Choreo AI Assistant project.

## 🤝 Contributing

This is a modular, SOLID-architecture system designed for easy extension. Add new features by creating new services or extending existing ones!

