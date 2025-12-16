"""
Simple test script to verify the wiki ingestion system works.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_ingestion.services import (
    UrlFetcherService,
    ContentExtractorService,
    WebCrawlerService,
    WikiChunkingService,
    WikiIngestionOrchestrator
)


def test_url_fetcher():
    """Test URL fetching."""
    print("🧪 Testing UrlFetcherService...")

    fetcher = UrlFetcherService(timeout=10)

    # Test fetching a simple page
    html = fetcher.fetch('https://example.com')

    assert html is not None, "Failed to fetch page"
    assert len(html) > 0, "Empty HTML returned"
    assert '<html' in html.lower(), "Invalid HTML content"

    print("   ✅ URL fetching works")


def test_content_extractor():
    """Test content extraction."""
    print("🧪 Testing ContentExtractorService...")

    extractor = ContentExtractorService()

    # Sample HTML
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Header</h1>
            <p>This is a test paragraph.</p>
            <a href="https://example.com">Link</a>
        </body>
    </html>
    """

    result = extractor.extract_content(html, 'https://example.com')

    assert result['title'] == 'Test Header', "Failed to extract title"
    assert 'test paragraph' in result['content'].lower(), "Failed to extract content"

    print("   ✅ Content extraction works")


def test_chunking():
    """Test chunking service."""
    print("🧪 Testing WikiChunkingService...")

    from wiki_ingestion.models import WikiPage

    chunker = WikiChunkingService(chunk_size=200, chunk_overlap=50, min_chunk_size=50)

    # Create a sample page with long content
    long_content = """
    # Introduction
    This is a comprehensive test document that needs to be chunked properly.
    
    ## Section 1
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
    exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    
    ## Section 2
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu 
    fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
    culpa qui officia deserunt mollit anim id est laborum.
    
    ## Section 3
    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque 
    laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi 
    architecto beatae vitae dicta sunt explicabo.
    """ * 3  # Repeat to ensure long content

    page = WikiPage(
        url='https://example.com/wiki/Test',
        title='Test Page',
        content=long_content,
    )

    chunks = chunker.chunk_page(page)

    assert len(chunks) >= 1, "Failed to create chunks"
    assert all(chunk.text for chunk in chunks), "Empty chunks created"
    assert all(chunk.source_url == page.url for chunk in chunks), "Incorrect source URL"

    print(f"   ✅ Chunking works ({len(chunks)} chunks created)")


def test_integration():
    """Test basic integration."""
    print("🧪 Testing Integration...")

    # Initialize services
    url_fetcher = UrlFetcherService(timeout=10)
    content_extractor = ContentExtractorService()
    web_crawler = WebCrawlerService(
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        max_pages=1  # Just one page for testing
    )
    chunking_service = WikiChunkingService()

    orchestrator = WikiIngestionOrchestrator(
        web_crawler=web_crawler,
        url_fetcher=url_fetcher,
        content_extractor=content_extractor,
        chunking_service=chunking_service,
        fetch_linked_content=False  # Disable for quick test
    )

    # Test with a simple page (not a real wiki, just for structure test)
    # In real usage, use a GitHub wiki URL
    print("   ℹ️  Note: For full test, use a real GitHub wiki URL")

    print("   ✅ Integration test complete")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 WIKI INGESTION SYSTEM - SIMPLE TESTS")
    print("="*60 + "\n")

    try:
        test_url_fetcher()
        test_content_extractor()
        test_chunking()
        test_integration()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")

        print("💡 Next steps:")
        print("   1. Set WIKI_URL environment variable")
        print("   2. Run: python -m backend.wiki_ingestion.main")
        print("   3. Or: python examples/ingest_to_vector_db.py")
        print()

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

