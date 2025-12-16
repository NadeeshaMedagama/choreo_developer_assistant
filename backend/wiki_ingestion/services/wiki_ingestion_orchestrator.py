"""
Wiki Ingestion Orchestrator.
Main orchestrator that coordinates the entire wiki ingestion process.
Follows SOLID principles - depends on abstractions.
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
import time

from ..interfaces.web_crawler import IWebCrawler
from ..interfaces.url_fetcher import IUrlFetcher
from ..interfaces.content_extractor import IContentExtractor
from ..models.wiki_page import WikiPage
from ..models.wiki_chunk import WikiChunk
from ..services.wiki_chunking_service import WikiChunkingService


class WikiIngestionOrchestrator:
    """
    Orchestrator for the entire wiki ingestion workflow.

    Workflow:
    1. Crawl wiki starting from main URL
    2. Extract all pages and their URLs
    3. Read content from each page
    4. Fetch and process linked content
    5. Chunk all content
    6. Prepare for embedding
    """

    def __init__(
        self,
        web_crawler: IWebCrawler,
        url_fetcher: IUrlFetcher,
        content_extractor: IContentExtractor,
        chunking_service: WikiChunkingService,
        fetch_linked_content: bool = True,
        max_linked_urls: int = 50
    ):
        """
        Initialize Wiki Ingestion Orchestrator.

        Args:
            web_crawler: Service for crawling web pages
            url_fetcher: Service for fetching URLs
            content_extractor: Service for extracting content
            chunking_service: Service for chunking content
            fetch_linked_content: Whether to fetch content from linked URLs
            max_linked_urls: Maximum number of linked URLs to fetch per wiki
        """
        self.web_crawler = web_crawler
        self.url_fetcher = url_fetcher
        self.content_extractor = content_extractor
        self.chunking_service = chunking_service
        self.fetch_linked_content = fetch_linked_content
        self.max_linked_urls = max_linked_urls

        # Statistics
        self.stats = {
            "total_pages": 0,
            "total_chunks": 0,
            "total_linked_urls": 0,
            "linked_content_fetched": 0,
            "linked_content_failed": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
        }

    def ingest_wiki(
        self,
        wiki_url: str,
        max_depth: int = 3,
        max_pages: int = 100
    ) -> Dict[str, Any]:
        """
        Ingest an entire wiki.

        Args:
            wiki_url: Starting URL of the wiki (e.g., https://github.com/owner/repo/wiki)
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl

        Returns:
            Dictionary containing all chunks and statistics
        """
        print(f"\n{'='*80}")
        print(f"🚀 WIKI INGESTION STARTED")
        print(f"{'='*80}")
        print(f"📍 Wiki URL: {wiki_url}")
        print(f"📊 Max Depth: {max_depth}, Max Pages: {max_pages}")
        print(f"🔗 Fetch Linked Content: {self.fetch_linked_content}")
        print(f"{'='*80}\n")

        self.stats["start_time"] = datetime.utcnow()

        try:
            # Step 1: Crawl wiki pages
            print("\n" + "="*80)
            print("STEP 1: CRAWLING WIKI PAGES")
            print("="*80)
            pages = self.web_crawler.crawl(wiki_url, max_depth)
            self.stats["total_pages"] = len(pages)
            print(f"✅ Crawled {len(pages)} wiki pages\n")

            # Step 2: Extract all linked URLs
            print("="*80)
            print("STEP 2: EXTRACTING LINKED URLs")
            print("="*80)
            linked_urls = self._extract_all_linked_urls(pages)
            self.stats["total_linked_urls"] = len(linked_urls)
            print(f"✅ Found {len(linked_urls)} unique linked URLs\n")

            # Step 3: Chunk wiki pages
            print("="*80)
            print("STEP 3: CHUNKING WIKI PAGES")
            print("="*80)
            wiki_chunks = self._chunk_pages(pages)
            print(f"✅ Created {len(wiki_chunks)} chunks from wiki pages\n")

            # Step 4: Fetch and chunk linked content (if enabled)
            linked_chunks = []
            if self.fetch_linked_content and linked_urls:
                print("="*80)
                print("STEP 4: FETCHING AND CHUNKING LINKED CONTENT")
                print("="*80)
                linked_chunks = self._process_linked_content(linked_urls, pages)
                print(f"✅ Created {len(linked_chunks)} chunks from linked content\n")

            # Step 5: Combine all chunks
            all_chunks = wiki_chunks + linked_chunks
            self.stats["total_chunks"] = len(all_chunks)

            # Complete
            self.stats["end_time"] = datetime.utcnow()
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

            print("="*80)
            print("✅ WIKI INGESTION COMPLETE")
            print("="*80)
            print(f"📄 Total Pages: {self.stats['total_pages']}")
            print(f"📦 Total Chunks: {self.stats['total_chunks']}")
            print(f"   - Wiki chunks: {len(wiki_chunks)}")
            print(f"   - Linked content chunks: {len(linked_chunks)}")
            print(f"🔗 Linked URLs: {self.stats['total_linked_urls']}")
            print(f"   - Fetched: {self.stats['linked_content_fetched']}")
            print(f"   - Failed: {self.stats['linked_content_failed']}")
            print(f"⏱️  Duration: {duration:.2f}s")
            print("="*80 + "\n")

            return {
                "chunks": all_chunks,
                "pages": pages,
                "statistics": self.stats,
                "success": True,
            }

        except Exception as e:
            self.stats["end_time"] = datetime.now(timezone.utc)
            self.stats["errors"].append(str(e))
            print(f"\n❌ INGESTION FAILED: {e}\n")

            return {
                "chunks": [],
                "pages": [],
                "statistics": self.stats,
                "success": False,
                "error": str(e),
            }

    def _extract_all_linked_urls(self, pages: List[WikiPage]) -> Set[str]:
        """Extract all unique linked URLs from wiki pages."""
        all_urls = set()
        
        for page in pages:
            # Add both internal and external URLs
            all_urls.update(page.get_all_urls())
        
        # Filter out wiki pages themselves
        wiki_page_urls = {page.url for page in pages}
        linked_urls = all_urls - wiki_page_urls
        
        # Apply limit only if max_linked_urls is set and > 0
        if self.max_linked_urls is not None and self.max_linked_urls > 0 and len(linked_urls) > self.max_linked_urls:
            print(f"⚠️  Limiting linked URLs from {len(linked_urls)} to {self.max_linked_urls}")
            linked_urls = set(list(linked_urls)[:self.max_linked_urls])
        else:
            print(f"📊 Processing all {len(linked_urls)} linked URLs (no limit)")

        return linked_urls

    def _chunk_pages(self, pages: List[WikiPage]) -> List[WikiChunk]:
        """Chunk all wiki pages."""
        all_chunks = []

        for i, page in enumerate(pages, 1):
            print(f"  [{i}/{len(pages)}] Chunking: {page.title}")
            chunks = self.chunking_service.chunk_page(page)
            all_chunks.extend(chunks)
            print(f"     → {len(chunks)} chunks")

        return all_chunks

    def _process_linked_content(
        self,
        urls: Set[str],
        source_pages: List[WikiPage]
    ) -> List[WikiChunk]:
        """Fetch and chunk content from linked URLs."""
        all_chunks = []
        urls_list = list(urls)

        # Create a mapping of URL to source page for better metadata
        url_to_source = {}
        for page in source_pages:
            for url in page.get_all_urls():
                if url not in url_to_source:
                    url_to_source[url] = page

        for i, url in enumerate(urls_list, 1):
            print(f"  [{i}/{len(urls_list)}] Fetching: {url[:80]}...")

            try:
                # Fetch content
                html = self.url_fetcher.fetch(url, timeout=15)

                if html:
                    # Extract content
                    extracted = self.content_extractor.extract_content(html, url)
                    content = extracted['markdown'] or extracted['content']

                    # Get source page metadata
                    source_page = url_to_source.get(url)
                    metadata = {
                        'referenced_from': source_page.url if source_page else None,
                        'referenced_from_title': source_page.title if source_page else None,
                        **extracted['metadata'],
                    }

                    # Chunk content
                    chunks = self.chunking_service.chunk_linked_content(
                        content=content,
                        source_url=url,
                        source_title=extracted['title'],
                        metadata=metadata
                    )

                    all_chunks.extend(chunks)
                    self.stats['linked_content_fetched'] += 1
                    print(f"     ✓ {len(chunks)} chunks created")
                else:
                    self.stats['linked_content_failed'] += 1
                    print(f"     ✗ Failed to fetch")

                # Small delay to be respectful
                time.sleep(0.5)

            except Exception as e:
                self.stats['linked_content_failed'] += 1
                self.stats['errors'].append(f"Error processing {url}: {e}")
                print(f"     ✗ Error: {e}")

        return all_chunks

    def prepare_for_embedding(
        self,
        chunks: List[WikiChunk]
    ) -> List[Dict[str, Any]]:
        """
        Prepare chunks for embedding into vector database.

        Args:
            chunks: List of WikiChunk objects

        Returns:
            List of dictionaries ready for embedding
        """
        prepared = []

        for chunk in chunks:
            prepared.append({
                "id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.to_vector_metadata(),
            })

        return prepared

    def get_statistics(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return self.stats.copy()

