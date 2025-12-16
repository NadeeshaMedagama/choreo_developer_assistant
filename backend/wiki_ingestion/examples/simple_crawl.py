"""
Example: Simple wiki crawl without vector database integration.
Just crawl, extract, chunk, and save to JSON.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from wiki_ingestion.services import (
    UrlFetcherService,
    ContentExtractorService,
    WebCrawlerService,
    WikiChunkingService,
    WikiIngestionOrchestrator
)
from wiki_ingestion.config import WikiIngestionConfig


def main():
    """Run simple wiki ingestion and save to JSON."""
    
    # Simple configuration (can also use .env file)
    config = WikiIngestionConfig(
        wiki_url='https://github.com/wso2/docs-choreo-dev/wiki',
        max_depth=1,
        max_pages=100,
        fetch_linked_content=False,  # Disable for speed
        chunk_size=1000,
        chunk_overlap=200,
    )
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              SIMPLE WIKI CRAWL EXAMPLE                       ║
╚══════════════════════════════════════════════════════════════╝

📍 Wiki: {config.wiki_url}
📊 Max Pages: {config.max_pages}
🔗 Fetch Linked: {config.fetch_linked_content}
""")
    
    # Initialize services
    print("🔧 Initializing services...")
    url_fetcher = UrlFetcherService(
        timeout=config.request_timeout,
        max_retries=config.max_retries
    )
    
    content_extractor = ContentExtractorService()
    
    web_crawler = WebCrawlerService(
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        max_pages=config.max_pages
    )
    
    chunking_service = WikiChunkingService(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        min_chunk_size=config.min_chunk_size
    )
    
    orchestrator = WikiIngestionOrchestrator(
        web_crawler=web_crawler,
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        chunking_service=chunking_service,
        fetch_linked_content=config.fetch_linked_content
    )
    
    print("✅ Ready!\n")
    
    # Run ingestion
    result = orchestrator.ingest_wiki(
        wiki_url=config.wiki_url,
        max_depth=config.max_depth,
        max_pages=config.max_pages
    )
    
    if not result['success']:
        print(f"❌ Failed: {result.get('error')}")
        return 1
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f'wiki_crawl_{timestamp}.json'
    
    chunks = result['chunks']
    pages = result['pages']
    
    output_data = {
        'metadata': {
            'wiki_url': config.wiki_url,
            'timestamp': timestamp,
            'statistics': result['statistics'],
            'config': {
                'max_depth': config.max_depth,
                'max_pages': config.max_pages,
                'chunk_size': config.chunk_size,
            }
        },
        'summary': {
            'total_pages': len(pages),
            'total_chunks': len(chunks),
            'wiki_chunks': sum(1 for c in chunks if c.source_type == 'wiki_page'),
            'linked_chunks': sum(1 for c in chunks if c.source_type == 'linked_content'),
        },
        'chunks': [chunk.to_dict() for chunk in chunks],
        'pages': [page.to_dict() for page in pages[:5]],  # Sample of pages
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"📁 File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Display sample
    print("\n" + "="*80)
    print("📦 SAMPLE CHUNKS (first 3)")
    print("="*80)
    
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n{i}. {chunk.source_title}")
        print(f"   URL: {chunk.source_url}")
        print(f"   Type: {chunk.source_type}")
        print(f"   Size: {chunk.chunk_size} chars")
        print(f"   Preview: {chunk.text[:150]}...")
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print(f"📊 {len(pages)} pages → {len(chunks)} chunks")
    print(f"💾 Output: {output_file}")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

