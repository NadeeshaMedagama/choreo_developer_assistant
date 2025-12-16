"""
Example: Integrate wiki ingestion with Milvus vector database.
Shows how to embed and store wiki chunks in Milvus.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from wiki_ingestion.services import (
    UrlFetcherService,
    ContentExtractorService,
    WebCrawlerService,
    WikiChunkingService,
    WikiIngestionOrchestrator
)

# Import VectorClient
try:
    from db.vector_client import VectorClient
except ImportError:
    # If relative import fails, try absolute import
    import sys
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from db.vector_client import VectorClient


def main():
    """Run wiki ingestion and store in Milvus vector database."""
    # Load environment variables from backend/.env
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(env_path)

    # Configuration
    WIKI_URL = os.getenv('WIKI_URL', 'https://github.com/wso2-enterprise/choreo/wiki')
    MAX_DEPTH = int(os.getenv('WIKI_MAX_DEPTH', '2'))
    MAX_PAGES = int(os.getenv('WIKI_MAX_PAGES', '50'))
    FETCH_LINKED = os.getenv('WIKI_FETCH_LINKED', 'true').lower() == 'true'
    MAX_LINKED_URLS = int(os.getenv('WIKI_MAX_LINKED_URLS', '0'))  # 0 = no limit

    # Milvus Configuration
    MILVUS_URI = os.getenv('MILVUS_URI')
    MILVUS_TOKEN = os.getenv('MILVUS_TOKEN')
    MILVUS_COLLECTION = os.getenv('MILVUS_COLLECTION_NAME', 'choreo_developer_assistant')
    MILVUS_DIMENSION = int(os.getenv('MILVUS_DIMENSION', '1536'))
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_EMBEDDING_DEPLOYMENT = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT', 'choreo-ai-embedding')
    AZURE_API_VERSION = os.getenv('AZURE_OPENAI_EMBEDDINGS_VERSION', '2024-02-01')
    
    # GitHub Token
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    # Validate required environment variables
    if not all([MILVUS_URI, MILVUS_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
        print("❌ Missing required environment variables:")
        if not MILVUS_URI:
            print("   - MILVUS_URI")
        if not MILVUS_TOKEN:
            print("   - MILVUS_TOKEN")
        if not AZURE_OPENAI_ENDPOINT:
            print("   - AZURE_OPENAI_ENDPOINT")
        if not AZURE_OPENAI_API_KEY:
            print("   - AZURE_OPENAI_API_KEY")
        print("\nPlease check your backend/.env file")
        return 1

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       WIKI INGESTION + MILVUS VECTOR DATABASE                ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  📚 Wiki URL: {WIKI_URL}
  🔍 Max Depth: {MAX_DEPTH}
  📄 Max Pages: {MAX_PAGES}
  🔗 Fetch Linked Content: {FETCH_LINKED}
  📎 Max Linked URLs: {'No limit' if MAX_LINKED_URLS == 0 else MAX_LINKED_URLS}
  
  🗄️  Milvus Collection: {MILVUS_COLLECTION}
  📏 Embedding Dimension: {MILVUS_DIMENSION}
  🤖 Embedding Model: {AZURE_EMBEDDING_DEPLOYMENT}
  
""")

    # Initialize wiki ingestion services
    print("🔧 Initializing wiki ingestion services...")

    url_fetcher = UrlFetcherService(
        timeout=30,
        max_retries=3,
        github_token=GITHUB_TOKEN
    )
    
    content_extractor = ContentExtractorService()
    
    web_crawler = WebCrawlerService(
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        max_pages=MAX_PAGES
    )
    
    chunking_service = WikiChunkingService(
        chunk_size=1000,
        chunk_overlap=200,
        min_chunk_size=100
    )
    
    orchestrator = WikiIngestionOrchestrator(
        web_crawler=web_crawler,
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        chunking_service=chunking_service,
        fetch_linked_content=FETCH_LINKED,
        max_linked_urls=MAX_LINKED_URLS if MAX_LINKED_URLS > 0 else None  # None = no limit
    )

    print("✅ Wiki ingestion services initialized\n")

    # Run wiki ingestion
    print("🕷️  Starting wiki crawl and ingestion...\n")
    result = orchestrator.ingest_wiki(
        wiki_url=WIKI_URL,
        max_depth=MAX_DEPTH,
        max_pages=MAX_PAGES
    )

    if not result['success']:
        print(f"\n❌ Ingestion failed: {result.get('error')}")
        return 1

    chunks = result['chunks']
    pages = result['pages']
    stats = result['statistics']
    
    print(f"\n✅ Successfully crawled {stats['total_pages']} pages")
    print(f"✅ Created {len(chunks)} chunks from wiki pages")
    if stats.get('total_linked_urls', 0) > 0:
        print(f"✅ Processed {stats['total_linked_urls']} linked URLs")
    print()

    # Initialize Milvus vector database
    print("🔧 Initializing Milvus vector database...")
    try:
        vector_client = VectorClient(
            uri=MILVUS_URI,
            token=MILVUS_TOKEN,
            collection_name=MILVUS_COLLECTION,
            dimension=MILVUS_DIMENSION,
            metric="COSINE"
        )
        print("✅ Connected to Milvus vector database\n")
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        return 1

    # Initialize Azure OpenAI for embeddings
    print("🔧 Initializing Azure OpenAI embedding service...")
    try:
        from openai import AzureOpenAI

        openai_client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print("✅ Azure OpenAI embedding service initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI: {e}")
        return 1

    # Embed and store chunks
    print(f"📦 Embedding and storing {len(chunks)} chunks in Milvus...")
    print("="*80)

    batch_size = 10
    stored_count = 0
    failed_count = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        try:
            # Create embeddings
            texts = [chunk.text for chunk in batch]

            print(f"   🔄 Creating embeddings...")
            response = openai_client.embeddings.create(
                model=AZURE_EMBEDDING_DEPLOYMENT,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]

            # Prepare data for Milvus using insert_embeddings_batch format
            items_to_insert = []
            for chunk, embedding in zip(batch, embeddings):
                # Get metadata
                metadata = chunk.to_vector_metadata()
                
                # Prepare item for batch insertion
                item = {
                    'content': chunk.text,
                    'vector': embedding,
                    'metadata': metadata
                }
                items_to_insert.append(item)

            # Insert to Milvus
            print(f"   💾 Storing in Milvus...")
            vector_client.insert_embeddings_batch(items_to_insert)

            stored_count += len(batch)
            print(f"   ✅ Batch complete ({stored_count}/{len(chunks)} total)")

        except Exception as e:
            failed_count += len(batch)
            print(f"   ❌ Error processing batch: {e}")
            continue

    # Summary
    print("\n" + "="*80)
    print("✅ WIKI INGESTION TO MILVUS COMPLETE")
    print("="*80)
    print(f"\n📊 Statistics:")
    print(f"   • Wiki pages crawled: {stats['total_pages']}")
    print(f"   • Linked URLs processed: {stats.get('total_linked_urls', 0)}")
    print(f"   • Total chunks created: {len(chunks)}")
    print(f"   • Chunks stored in Milvus: {stored_count}")
    print(f"   • Failed chunks: {failed_count}")

    # Calculate success rate, handle zero chunks case
    if len(chunks) > 0:
        success_rate = stored_count/len(chunks)*100
        print(f"   • Success rate: {success_rate:.1f}%")
    else:
        print(f"   • Success rate: N/A (no chunks to process)")

    print(f"\n🗄️  Milvus Collection: {MILVUS_COLLECTION}")
    print(f"📏 Embedding Dimension: {MILVUS_DIMENSION}")
    print("="*80 + "\n")

    # Warning if no data was ingested
    if len(chunks) == 0:
        print("⚠️  WARNING: No data was ingested!")
        print("   Possible reasons:")
        print("   - Wiki has no pages (404 error)")
        print("   - Wiki URL is incorrect")
        print("   - Repository is private and authentication failed")
        print("   - Wiki is disabled in repository settings")
        print("\n   💡 Run diagnostic: python wiki_ingestion/diagnose_wiki.py")
        print("="*80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

