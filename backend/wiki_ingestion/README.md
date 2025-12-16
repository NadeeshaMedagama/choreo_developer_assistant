# GitHub Wiki Ingestion System

A robust, SOLID-architecture-based system for crawling GitHub wikis, extracting content, following links, and preparing data for Milvus vector database embedding.

## 🎯 Features

✅ **Complete Wiki Crawling**
- Crawls entire GitHub wiki starting from main URL
- Configurable depth and page limits
- BFS (Breadth-First Search) crawling strategy
- Intelligent URL normalization and deduplication

✅ **Private Repository Support**
- Git-based cloning for private wikis
- GitHub token authentication
- Access to enterprise/private repositories
- Direct markdown file processing

✅ **Content Extraction**
- Extracts clean content from HTML
- Converts to markdown format
- Preserves document structure
- Extracts metadata (title, description, etc.)

✅ **Linked Content Processing**
- Identifies all URLs within wiki pages
- Fetches and processes linked content
- Distinguishes internal vs external links
- Configurable or unlimited URL processing

✅ **Smart Chunking**
- Respects markdown structure (headers, paragraphs)
- Configurable chunk size (default: 1000 chars, 200 overlap)
- Natural boundary splitting (sentences, paragraphs)
- Maintains context across chunks

✅ **Milvus Vector Database Integration**
- Direct embedding and storage in Milvus
- Azure OpenAI embeddings (1536 dimensions)
- Rich metadata for filtering and tracing
- Traceable back to original source

✅ **SOLID Architecture**
- Interface-based design (Dependency Inversion)
- Single Responsibility Principle
- Easy to test and extend
- Dependency Injection pattern

## 📁 Project Structure

```
backend/wiki_ingestion/
├── __init__.py
├── config.py                        # Configuration module
├── diagnose_wiki.py                 # Diagnostic tool
├── quickstart_milvus.sh             # Quick start script
├── test_system.py                   # System tests
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── CLEANUP_SUMMARY.md               # Recent cleanup details
│
├── interfaces/                      # Abstractions (SOLID - Dependency Inversion)
│   ├── __init__.py
│   ├── web_crawler.py              # IWebCrawler interface
│   ├── content_extractor.py        # IContentExtractor interface
│   └── url_fetcher.py              # IUrlFetcher interface
│
├── models/                          # Data models
│   ├── __init__.py
│   ├── wiki_page.py                # WikiPage model
│   └── wiki_chunk.py               # WikiChunk model
│
├── services/                        # Service implementations
│   ├── __init__.py
│   ├── url_fetcher_service.py      # HTTP fetching with retry
│   ├── content_extractor_service.py # HTML to clean content
│   ├── web_crawler_service.py      # Web crawling logic
│   ├── wiki_chunking_service.py    # Smart chunking
│   └── wiki_ingestion_orchestrator.py # Main orchestrator
│
├── examples/                        # Usage examples (Milvus only)
│   ├── README.md                   # Examples documentation
│   ├── ingest_to_milvus.py         # HTTP-based Milvus ingestion
│   ├── ingest_private_wiki_git.py  # Git-based private wiki ingestion
│   ├── simple_crawl.py             # Basic crawling example
│   └── verify_milvus_data.py       # Data verification tool
│
├── scripts/                         # Helper scripts
│   ├── debug_wiki_url.py
│   ├── search_choreo.py
│   └── test_auth.py
│
├── docs/                            # Documentation
│   ├── guides/
│   └── readmes/
│
├── logs/                            # Application logs
│   └── README.md
│
└── utils/                           # Utility functions
```

## 🏗️ Architecture

### SOLID Principles Applied

**1. Single Responsibility Principle (SRP)**
- Each service has one clear responsibility
- `UrlFetcherService`: Fetch URLs
- `ContentExtractorService`: Extract content
- `WebCrawlerService`: Crawl websites
- `WikiChunkingService`: Chunk content
- `WikiIngestionOrchestrator`: Coordinate workflow

**2. Open/Closed Principle (OCP)**
- Open for extension via interfaces
- Closed for modification
- Easy to add new crawler types or extraction strategies

**3. Liskov Substitution Principle (LSP)**
- Any implementation of `IWebCrawler` can replace another
- Any implementation of `IContentExtractor` can replace another

**4. Interface Segregation Principle (ISP)**
- Small, focused interfaces
- Clients depend only on what they use

**5. Dependency Inversion Principle (DIP)**
- High-level orchestrator depends on abstractions
- Low-level services implement abstractions
- Dependency injection throughout

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CRAWL WIKI                                               │
│    ┌──────────────┐                                         │
│    │ Start URL    │──┐                                      │
│    └──────────────┘  │                                      │
│                      ▼                                      │
│    ┌─────────────────────────────┐                         │
│    │ WebCrawlerService (BFS)     │                         │
│    │  - Fetch page               │                         │
│    │  - Extract links            │                         │
│    │  - Queue new pages          │                         │
│    └─────────────────────────────┘                         │
│                      │                                      │
│                      ▼                                      │
│    ┌─────────────────────────────┐                         │
│    │ WikiPage objects            │                         │
│    │  - URL, title, content      │                         │
│    │  - Internal/external links  │                         │
│    └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EXTRACT LINKED URLS                                      │
│    ┌─────────────────────────────┐                         │
│    │ Collect all URLs from pages │                         │
│    │  - Deduplicate              │                         │
│    │  - Filter out wiki pages    │                         │
│    │  - Limit to max_linked_urls │                         │
│    └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CHUNK WIKI PAGES                                         │
│    ┌─────────────────────────────┐                         │
│    │ WikiChunkingService         │                         │
│    │  - Smart chunking           │                         │
│    │  - Respect markdown         │                         │
│    │  - Add metadata             │                         │
│    └─────────────────────────────┘                         │
│                      │                                      │
│                      ▼                                      │
│    ┌─────────────────────────────┐                         │
│    │ WikiChunk objects           │                         │
│    │  (from wiki pages)          │                         │
│    └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FETCH & CHUNK LINKED CONTENT                             │
│    ┌─────────────────────────────┐                         │
│    │ For each linked URL:        │                         │
│    │  - Fetch content            │                         │
│    │  - Extract clean text       │                         │
│    │  - Chunk content            │                         │
│    └─────────────────────────────┘                         │
│                      │                                      │
│                      ▼                                      │
│    ┌─────────────────────────────┐                         │
│    │ WikiChunk objects           │                         │
│    │  (from linked content)      │                         │
│    └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PREPARE FOR EMBEDDING                                    │
│    ┌─────────────────────────────┐                         │
│    │ Combine all chunks          │                         │
│    │  - Wiki page chunks         │                         │
│    │  - Linked content chunks    │                         │
│    └─────────────────────────────┘                         │
│                      │                                      │
│                      ▼                                      │
│    ┌─────────────────────────────┐                         │
│    │ Ready for embedding         │                         │
│    │  {id, text, metadata}       │                         │
│    └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
cd backend/wiki_ingestion
pip install -r requirements.txt
```

### Basic Usage

```python
from wiki_ingestion.services import (
    UrlFetcherService,
    ContentExtractorService,
    WebCrawlerService,
    WikiChunkingService,
    WikiIngestionOrchestrator
)

# Initialize services
url_fetcher = UrlFetcherService()
content_extractor = ContentExtractorService()
web_crawler = WebCrawlerService(url_fetcher, content_extractor)
chunking_service = WikiChunkingService()

# Create orchestrator
orchestrator = WikiIngestionOrchestrator(
    web_crawler=web_crawler,
    url_fetcher=url_fetcher,
    content_extractor=content_extractor,
    chunking_service=chunking_service
)

# Run ingestion
result = orchestrator.ingest_wiki(
    wiki_url='https://github.com/owner/repo/wiki',
    max_depth=2,
    max_pages=50
)

# Get chunks
chunks = result['chunks']
```

### Command Line Usage

```bash
# Set environment variables
export WIKI_URL="https://github.com/wso2/docs-choreo-dev/wiki"
export WIKI_MAX_DEPTH=2
export WIKI_MAX_PAGES=50
export WIKI_FETCH_LINKED=true

# Run ingestion
python -m backend.wiki_ingestion.main
```

### Public Wikis (HTTP-based Milvus Integration)

```bash
# Set environment variables
export WIKI_URL="https://github.com/wso2/docs-choreo-dev/wiki"
export MILVUS_URI="https://your-instance.vectordb.zillizcloud.com:19530"
export MILVUS_TOKEN="your-milvus-token"
export MILVUS_COLLECTION_NAME="choreo_developer_assistant"
export MILVUS_DIMENSION=1536
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="choreo-ai-embedding"

# Run HTTP-based ingestion
python -m backend.wiki_ingestion.examples.ingest_to_milvus
```

### Private Wikis (Git-based Milvus Integration)

```bash
# Set environment variables
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
export GITHUB_TOKEN="your-github-token"
export MILVUS_URI="https://your-instance.vectordb.zillizcloud.com:19530"
export MILVUS_TOKEN="your-milvus-token"
export MILVUS_COLLECTION_NAME="choreo_developer_assistant"

# Run git-based ingestion for private repos
python -m backend.wiki_ingestion.examples.ingest_private_wiki_git
```

### Quick Start Script

```bash
cd backend/wiki_ingestion
./quickstart_milvus.sh
```


## 📊 Configuration

### Environment Variables

```bash
# Wiki Configuration
WIKI_URL=https://github.com/owner/repo/wiki    # Starting wiki URL
WIKI_MAX_DEPTH=2                                # Max crawl depth (0 = only start page)
WIKI_MAX_PAGES=50                               # Max pages to crawl
WIKI_FETCH_LINKED=true                          # Fetch content from linked URLs
WIKI_MAX_LINKED_URLS=0                          # 0 = unlimited, N = limit to N URLs

# Chunking Configuration
CHUNK_SIZE=1000                                 # Target chunk size (characters)
CHUNK_OVERLAP=200                               # Overlap between chunks
MIN_CHUNK_SIZE=100                              # Minimum chunk size

# Fetching Configuration
REQUEST_TIMEOUT=30                              # HTTP request timeout (seconds)
MAX_RETRIES=3                                   # Max retry attempts
BACKOFF_FACTOR=0.5                             # Retry backoff factor

# GitHub Authentication (for private repos)
GITHUB_TOKEN=your-github-token                  # GitHub personal access token

# Milvus Vector Database
MILVUS_URI=https://your-instance.vectordb.zillizcloud.com:19530
MILVUS_TOKEN=your-milvus-token
MILVUS_COLLECTION_NAME=choreo_developer_assistant
MILVUS_DIMENSION=1536                           # Embedding dimension

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=choreo-ai-embedding
AZURE_OPENAI_EMBEDDINGS_VERSION=2024-02-01
```

### Programmatic Configuration

```python
# Custom crawler configuration
web_crawler = WebCrawlerService(
    url_fetcher=url_fetcher,
    content_extractor=content_extractor,
    max_pages=100,              # Override max pages
    respect_robots=True         # Respect robots.txt
)

# Custom chunking configuration
chunking_service = WikiChunkingService(
    chunk_size=1500,            # Larger chunks
    chunk_overlap=300,          # More overlap
    min_chunk_size=200          # Higher minimum
)

# Custom orchestrator configuration
orchestrator = WikiIngestionOrchestrator(
    web_crawler=web_crawler,
    url_fetcher=url_fetcher,
    content_extractor=content_extractor,
    chunking_service=chunking_service,
    fetch_linked_content=True,  # Enable linked content
    max_linked_urls=100         # More linked URLs
)
```

## 🔍 Data Models

### WikiPage

Represents a single wiki page.

```python
@dataclass
class WikiPage:
    url: str                        # Page URL
    title: str                      # Page title
    content: str                    # Clean text content
    raw_html: str                   # Original HTML
    markdown: str                   # Markdown format
    internal_urls: Set[str]         # URLs within same wiki
    external_urls: Set[str]         # External URLs
    repository: str                 # e.g., "wso2/choreo"
    owner: str                      # e.g., "wso2"
    wiki_name: str                  # Wiki name
    page_path: str                  # Path within wiki
    fetched_at: datetime            # When fetched
    metadata: Dict[str, Any]        # Additional metadata
    depth: int                      # Crawl depth
    parent_url: str                 # Parent page URL
```

### WikiChunk

Represents a chunk of content ready for embedding.

```python
@dataclass
class WikiChunk:
    chunk_id: str                   # Unique chunk ID
    text: str                       # Chunk text
    chunk_index: int                # Index within source
    source_url: str                 # Source page URL
    source_title: str               # Source page title
    source_type: str                # 'wiki_page' or 'linked_content'
    repository: str                 # Repository
    owner: str                      # Owner
    chunk_size: int                 # Size in characters
    total_chunks: int               # Total chunks from source
    metadata: Dict[str, Any]        # Additional metadata
    created_at: datetime            # Creation time
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest backend/wiki_ingestion/tests/

# Run specific test file
pytest backend/wiki_ingestion/tests/test_web_crawler.py

# Run with coverage
pytest --cov=backend.wiki_ingestion backend/wiki_ingestion/tests/
```

### Manual Testing

```python
# Test URL fetching
from wiki_ingestion.services import UrlFetcherService

fetcher = UrlFetcherService()
html = fetcher.fetch('https://github.com/wso2/docs-choreo-dev/wiki')
print(f"Fetched {len(html)} characters")

# Test content extraction
from wiki_ingestion.services import ContentExtractorService

extractor = ContentExtractorService()
content = extractor.extract_content(html, url)
print(f"Title: {content['title']}")
print(f"Content: {content['content'][:200]}...")

# Test chunking
from wiki_ingestion.services import WikiChunkingService

chunker = WikiChunkingService()
chunks = chunker.chunk_page(page)
print(f"Created {len(chunks)} chunks")
```

## 📈 Performance

### Crawling Speed

- **Average**: 2-3 pages/second
- **With linked content**: 1-2 pages/second
- **Respects rate limits**: Automatic backoff

### Memory Usage

- **Per page**: ~50-200 KB
- **Per chunk**: ~1-5 KB
- **Efficient**: Processes in batches

### Recommendations

```python
# For large wikis (100+ pages)
max_pages=100
max_depth=2
fetch_linked_content=False  # Or limit max_linked_urls

# For complete ingestion
max_pages=None  # No limit
max_depth=3
fetch_linked_content=True
max_linked_urls=200
```

## 🛠️ Extending the System

### Custom Crawler Implementation

```python
from wiki_ingestion.interfaces import IWebCrawler

class CustomCrawler(IWebCrawler):
    def crawl(self, start_url: str, max_depth: int = 3):
        # Your custom crawling logic
        pass
    
    def extract_page(self, url: str):
        # Your custom extraction logic
        pass

# Use it
custom_crawler = CustomCrawler()
orchestrator = WikiIngestionOrchestrator(
    web_crawler=custom_crawler,  # Inject custom implementation
    # ... other services
)
```

### Custom Content Extractor

```python
from wiki_ingestion.interfaces import IContentExtractor

class CustomExtractor(IContentExtractor):
    def extract_content(self, html: str, url: str):
        # Your custom extraction logic
        pass

# Use it
custom_extractor = CustomExtractor()
web_crawler = WebCrawlerService(
    url_fetcher=url_fetcher,
    content_extractor=custom_extractor  # Inject custom implementation
)
```

## 🐛 Troubleshooting

### Issue: Crawler not finding pages

**Solution**: Check URL pattern matching
```python
# Debug URL validation
crawler = WebCrawlerService(...)
url = "https://github.com/owner/repo/wiki/Page"
is_valid = crawler.is_valid_url(url, base_domain)
print(f"URL valid: {is_valid}")
```

### Issue: Content extraction failing

**Solution**: Check HTML structure
```python
# Debug content extraction
extractor = ContentExtractorService()
content = extractor.extract_content(html, url)
print(f"Extracted: {content}")
```

### Issue: Too many chunks

**Solution**: Increase chunk size
```python
chunker = WikiChunkingService(
    chunk_size=2000,  # Larger chunks
    min_chunk_size=500  # Higher minimum
)
```

## 📝 License

Same as parent project.

## 🤝 Contributing

1. Follow SOLID principles
2. Add tests for new features
3. Update documentation
4. Use type hints
5. Follow existing code style

## 📞 Support

For issues or questions, please open an issue in the main repository.

---

**Built with ❤️ using SOLID principles**

