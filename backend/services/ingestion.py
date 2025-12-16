from typing import List, Dict, Any
import re
import gc
import psutil
import os
import threading
import sys
import select

from ..utils.logger import get_logger
from ..utils.resource_monitor import (
    wait_for_memory,
    force_garbage_collection,
    get_memory_usage_mb,
    get_memory_usage_percent
)
from .github_service import GitHubService
from .llm_service import LLMService
from .image_service import ImageProcessingService
from ..db.vector_client import VectorClient

logger = get_logger(__name__)

# Global flag for manual skip
_manual_skip_flag = False
_skip_lock = threading.Lock()


def set_manual_skip():
    """Set the manual skip flag to skip the current file."""
    global _manual_skip_flag
    with _skip_lock:
        _manual_skip_flag = True


def clear_manual_skip():
    """Clear the manual skip flag."""
    global _manual_skip_flag
    with _skip_lock:
        _manual_skip_flag = False


def check_manual_skip() -> bool:
    """Check if manual skip was requested."""
    global _manual_skip_flag
    with _skip_lock:
        return _manual_skip_flag


def keyboard_monitor_thread():
    """Background thread that listens for 'q' key press to skip current file."""
    logger.info("⌨️  Keyboard monitor started - Press 'q' + Enter to skip current file")
    logger.info("📋 This allows you to manually skip files when RAM usage is too high")

    while True:
        try:
            # Check if input is available (non-blocking on Unix systems)
            if sys.stdin in select.select([sys.stdin], [], [], 0.5)[0]:  # Check every 0.5 seconds
                line = sys.stdin.readline().strip().lower()
                if line == 'q':
                    set_manual_skip()
                    logger.warning("🔴 MANUAL SKIP REQUESTED by user - Will skip current file after current operation...")
                    logger.warning("⏭️  The program will continue with the next file")
        except Exception as e:
            # Silently ignore errors in keyboard monitoring to prevent crashes
            pass


def start_keyboard_monitor():
    """Start the keyboard monitoring thread."""
    monitor_thread = threading.Thread(target=keyboard_monitor_thread, daemon=True)
    monitor_thread.start()
    logger.info("✓ Manual skip feature enabled - Press 'q' + Enter anytime to skip problematic files")


def get_memory_usage() -> str:
    """Get current memory usage of the process."""
    try:
        mem_mb = get_memory_usage_mb()
        mem_percent = get_memory_usage_percent()
        return f"{mem_mb:.1f}MB ({mem_percent:.1f}%)"
    except:
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            return f"{mem_mb:.1f}MB"
        except:
            return "N/A"


def remove_images_from_markdown(text: str) -> str:
    """
    Remove all image references from markdown text.

    This function removes:
    - Inline images: ![alt text](image.png)
    - Reference-style images: ![alt text][ref]
    - Image reference definitions: [ref]: image.png
    - HTML img tags: <img src="image.png">
    - Images with attributes and titles

    Args:
        text: Markdown text content

    Returns:
        Text with all image references removed
    """
    if not text:
        return text

    # Remove inline markdown images: ![alt text](url "title")
    # Matches: ![anything](url) or ![anything](url "title")
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)

    # Remove reference-style markdown images: ![alt text][ref]
    text = re.sub(r'!\[([^\]]*)\]\[([^\]]*)\]', '', text)

    # Remove image reference definitions: [ref]: url "title"
    # This handles lines like: [logo]: https://example.com/logo.png "Logo"
    text = re.sub(r'^\s*\[([^\]]+)\]:\s+\S+.*$', '', text, flags=re.MULTILINE)

    # Remove HTML img tags with any attributes
    # Matches: <img src="..." alt="..." /> or <img src="...">
    text = re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)

    # Remove multiple consecutive blank lines (cleanup)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    logger.debug(f"Removed images from markdown text")
    return text


class DocumentChunker:
    """Utility class for chunking documents."""

    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        """
        Initialize chunker.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def pre_split_large_text(self, text: str, max_section_size: int = 15000) -> List[str]:
        """
        Pre-split very large text into smaller sections to prevent timeout issues.
        This is done BEFORE the detailed chunking algorithm runs.

        Splits at natural boundaries (paragraph breaks, then newlines) to maintain context.

        Args:
            text: Text to split
            max_section_size: Maximum characters per section (default 15KB)

        Returns:
            List of text sections
        """
        if len(text) <= max_section_size:
            return [text]

        sections = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + max_section_size

            if end >= text_length:
                # Last section
                sections.append(text[start:].strip())
                break

            # Try to split at a paragraph break (two newlines)
            split_pos = text.rfind('\n\n', start, end)

            # If no paragraph break, try single newline
            if split_pos == -1 or split_pos <= start:
                split_pos = text.rfind('\n', start, end)

            # If still no good split point, try space
            if split_pos == -1 or split_pos <= start:
                split_pos = text.rfind(' ', start, end)

            # If still nothing, force split at max_section_size
            if split_pos == -1 or split_pos <= start:
                split_pos = end

            sections.append(text[start:split_pos].strip())
            start = split_pos + 1  # Skip the split character

        logger.debug(f"Pre-split {text_length} chars into {len(sections)} sections")
        return sections

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        For large texts (>15KB), pre-splits into sections first to prevent timeouts.

        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []

        # **NEW: Pre-split large files to prevent timeout**
        # If text is larger than 15KB, split into sections first
        if len(text) > 15000:
            logger.info(f"Large file detected ({len(text)} chars), pre-splitting into sections...")
            sections = self.pre_split_large_text(text, max_section_size=15000)
            logger.info(f"Pre-split into {len(sections)} sections")

            all_chunks = []
            global_char_offset = 0

            for section_idx, section in enumerate(sections):
                if not section.strip():
                    continue

                # Chunk each section independently
                section_chunks = self._chunk_section(section, metadata, global_char_offset)
                all_chunks.extend(section_chunks)
                global_char_offset += len(section) + 1  # +1 for the split character

            # Update chunk indices to be sequential
            for idx, chunk in enumerate(all_chunks):
                chunk["metadata"]["chunk_index"] = idx

            logger.info(f"Created {len(all_chunks)} chunks from {len(sections)} sections (total {len(text)} chars)")
            return all_chunks

        # For small files, use the regular chunking
        return self._chunk_section(text, metadata, 0)

    def _chunk_section(self, text: str, metadata: Dict[str, Any] = None, char_offset: int = 0) -> List[Dict[str, Any]]:
        """
        Internal method to chunk a single section of text.
        Optimized to avoid expensive rfind() operations that cause timeouts.

        Args:
            text: Text section to chunk
            metadata: Metadata to attach
            char_offset: Character offset for absolute positioning

        Returns:
            List of chunks
        """
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # If this is the last chunk, just take the rest
            if end >= text_length:
                end = text_length
            else:
                # Try to find a good break point NEAR the end (not from start!)
                # Only search in the last 300 chars to avoid expensive scans
                search_start = max(start, end - 300)
                found_break = False

                # Look for paragraph break first (in limited range)
                paragraph_pos = text.rfind('\n\n', search_start, end)
                if paragraph_pos != -1 and paragraph_pos > start:
                    end = paragraph_pos + 2  # Include the newlines
                    found_break = True

                # If no paragraph break, look for single newline
                if not found_break:
                    newline_pos = text.rfind('\n', search_start, end)
                    if newline_pos != -1 and newline_pos > start:
                        end = newline_pos + 1
                        found_break = True

                # If still no break, look for sentence ending (in limited range)
                if not found_break:
                    for marker in ['. ', '.\n', '! ', '? ', ': ', ':\n']:
                        marker_pos = text.rfind(marker, search_start, end)
                        if marker_pos != -1 and marker_pos > start:
                            end = marker_pos + len(marker)
                            found_break = True
                            break

                # Last resort: look for space (in limited range)
                if not found_break:
                    space_pos = text.rfind(' ', search_start, end)
                    if space_pos != -1 and space_pos > start:
                        end = space_pos + 1
                        found_break = True

                # If absolutely no break point found, just hard split
                # This prevents infinite loops

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_data = {
                    "content": chunk_text,
                    "metadata": {
                        **(metadata or {}),
                        "chunk_index": len(chunks),
                        "start_char": start + char_offset,
                        "end_char": end + char_offset
                    }
                }
                chunks.append(chunk_data)

            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else text_length

            # Safety check: ensure we're making progress
            if start >= text_length:
                break

        return chunks


class IngestionService:
    """Service for ingesting documents from GitHub and storing in Pinecone."""

    def __init__(
        self,
        github_service: GitHubService,
        llm_service: LLMService,
        vector_client: VectorClient,
        image_service: ImageProcessingService = None,
        chunk_size: int = 3000,
        chunk_overlap: int = 200
    ):
        """
        Initialize ingestion service.

        Args:
            github_service: GitHub service instance
            llm_service: LLM service for embeddings
            vector_client: Vector database client
            image_service: Image processing service (optional)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.github_service = github_service
        self.llm_service = llm_service
        self.vector_client = vector_client
        self.image_service = image_service
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)

    def ingest_from_github(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Ingest all markdown files AND API definition files from a GitHub repository in a memory-efficient way.
        Processes files and embeddings in small batches to avoid RAM spikes.
        Skips files that have already been processed (same SHA hash).

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Summary statistics of the ingestion process
        """
        logger.info(f"Starting ingestion from GitHub: {owner}/{repo}")
        logger.info(f"Initial memory usage: {get_memory_usage()}")
        logger.info("=" * 60)
        logger.info("📋 INGESTION MODE: MARKDOWN + API DEFINITION FILES")
        logger.info("✅ Will process: .md files AND API files (.yaml, .yml, .json)")
        logger.info("=" * 60)
        repository_id = f"{owner}/{repo}"

        # Step 1: Find ALL markdown AND API files using ultra-fast method
        logger.info("Step 1: Finding all markdown + API files in GitHub repository...")
        logger.info("🚀 Attempting ULTRA-FAST tree API search for BOTH file types...")

        try:
            # Try ultra-fast combined method (single API call for everything)
            result = self.github_service.find_all_markdown_and_api_files_fast(owner, repo)
            markdown_files = result.get("markdown_files", [])
            api_files = result.get("api_files", [])

            # Combine both lists with proper file_type marking
            for md_file in markdown_files:
                if "file_type" not in md_file:
                    md_file["file_type"] = "markdown"
            for api_file in api_files:
                if "file_type" not in api_file:
                    api_file["file_type"] = "api_definition"

            all_files = markdown_files + api_files

        except Exception as e:
            logger.warning(f"Ultra-fast combined search failed, using standard method: {e}")
            # Fallback to regular parallel methods
            markdown_files = self.github_service.find_all_markdown_files(owner, repo)
            api_files = self.github_service.find_all_api_files(owner, repo)

            # Mark file types
            for md_file in markdown_files:
                md_file["file_type"] = "markdown"
            for api_file in api_files:
                if "file_type" not in api_file:
                    api_file["file_type"] = "api_definition"

            all_files = markdown_files + api_files

        if not all_files:
            logger.warning(f"No markdown or API files found in the repository {owner}/{repo}")
            return {
                "status": "completed",
                "files_fetched": 0,
                "files_skipped": 0,
                "chunks_created": 0,
                "embeddings_stored": 0,
                "repository": repository_id
            }

        # Count file types
        md_count = sum(1 for f in all_files if f.get("file_type") == "markdown")
        api_count = sum(1 for f in all_files if f.get("file_type") == "api_definition")

        logger.info(f"Found {len(all_files)} total files to process:")
        logger.info(f"  📄 {md_count} markdown files (.md)")
        logger.info(f"  🔧 {api_count} API definition files (.yaml, .yml, .json)")

        # Step 2: Process each file one at a time
        logger.info("Step 2: Processing files one at a time...")
        total_chunks_created = 0
        total_embeddings_stored = 0
        files_processed = 0
        files_skipped = 0
        files_dropped_due_to_memory = 0

        # Track by file type
        md_processed = 0
        api_processed = 0

        for file_idx, file_info in enumerate(all_files, 1):
            # **MANUAL SKIP CHECK** - Check if user pressed 'q' to skip
            if check_manual_skip():
                logger.warning(f"⏭️  MANUAL SKIP: User requested to skip {file_info['name']}")
                clear_manual_skip()
                files_skipped += 1
                force_garbage_collection()
                continue

            try:
                # **MEMORY SAFETY CHECK** - Check if memory is too high before processing
                current_memory = get_memory_usage_percent()
                if current_memory > 98.0:
                    logger.warning(f"⚠️  High memory ({current_memory:.1f}%) - Skipping file to prevent freeze")
                    files_dropped_due_to_memory += 1
                    files_skipped += 1
                    force_garbage_collection()
                    continue

                file_path = file_info['path']
                file_sha = file_info.get('sha', '')
                file_size = file_info.get('size', 0)
                file_type = file_info.get('file_type', 'unknown')
                max_file_size = 1000000  # 1000KB limit per file (increased for API files which can be larger)

                logger.info(f"Processing file {file_idx}/{len(all_files)}: {file_path} ({file_type}) [Memory: {get_memory_usage()}]")

                # Check file size before processing
                if file_size > max_file_size:
                    logger.warning(f"⚠️  File too large ({file_size} bytes, max: {max_file_size}) - Skipping: {file_path}")
                    files_skipped += 1
                    continue

                # **EARLY SHA CHECK** - Check if already processed BEFORE fetching content (saves time)
                if file_sha and self.vector_client.file_already_processed(repository_id, file_path, file_sha):
                    logger.info(f"⏭️  Skipping {file_info['name']} - already processed (SHA: {file_sha[:8]})")
                    files_skipped += 1
                    continue

                # If file SHA changed, delete old chunks before adding new ones
                if file_sha:
                    logger.debug(f"Checking for outdated chunks of {file_path}...")
                    self.vector_client.delete_file_chunks(repository_id, file_path)

                # Fetch content for this file
                content = self.github_service.get_file_content(owner, repo, file_path)

                if not content or not content.strip():
                    logger.warning(f"Skipping empty file: {file_path}")
                    files_skipped += 1
                    continue

                # Add character limit check for very large files (AFTER fetching content)
                max_file_chars = 1000000  # Maximum 1000K characters to prevent chunking timeouts
                if len(content) > max_file_chars:
                    logger.warning(f"⚠️  File content too large ({len(content)} chars, max: {max_file_chars}) - Skipping: {file_path}")
                    files_skipped += 1
                    del content
                    force_garbage_collection()
                    continue

                # For markdown files, remove image references
                original_length = len(content)
                if file_type == 'markdown':
                    content = remove_images_from_markdown(content)
                    cleaned_length = len(content)
                    if original_length != cleaned_length:
                        logger.info(f"Removed images from {file_path}: {original_length} -> {cleaned_length} chars")

                if not content or not content.strip():
                    logger.warning(f"Skipping file with no content after processing: {file_path}")
                    files_skipped += 1
                    continue

                # **MEMORY SAFETY CHECK** - Check memory before chunking
                pre_chunk_memory = get_memory_usage_percent()
                if pre_chunk_memory > 97.0:
                    logger.warning(f"⚠️  High memory ({pre_chunk_memory:.1f}%) before chunking - Skipping file: {file_info['name']}")
                    files_dropped_due_to_memory += 1
                    files_skipped += 1
                    del content
                    force_garbage_collection()
                    continue

                # Chunk this file
                file_metadata = {
                    "source": "github",
                    "repository": repository_id,
                    "file_path": file_path,
                    "file_name": file_info["name"],
                    "file_type": file_type,
                    "file_sha": file_sha,
                    "url": file_info.get("url", "")
                }

                # Create chunks
                try:
                    # **MANUAL SKIP CHECK** - Check again before chunking
                    if check_manual_skip():
                        logger.warning(f"⏭️  MANUAL SKIP: User requested to skip {file_info['name']}")
                        clear_manual_skip()
                        files_skipped += 1
                        del content
                        force_garbage_collection()
                        continue

                    logger.info(f"📝 Chunking {file_info['name']} ({len(content)} chars, type: {file_type})...")

                    # **TIMEOUT PROTECTION** using threading (works in any thread/process)
                    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

                    def chunk_with_timeout():
                        return self.chunker.chunk_text(content, file_metadata)

                    try:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(chunk_with_timeout)
                            chunks = future.result(timeout=5)  # 5 seconds timeout
                    except (FutureTimeoutError, TimeoutError):
                        logger.error(f"⏱️  TIMEOUT: Chunking took too long for {file_info['name']} - SKIPPING")
                        files_dropped_due_to_memory += 1
                        files_skipped += 1
                        del content
                        force_garbage_collection()
                        continue

                    logger.info(f"✓ Created {len(chunks)} chunks from {file_info['name']}")

                    # **IMMEDIATE MEMORY CLEANUP** after chunking
                    del content
                    force_garbage_collection()

                except Exception as e:
                    logger.error(f"❌ Error chunking {file_path}: {e}")
                    files_skipped += 1
                    force_garbage_collection()
                    continue

                if not chunks:
                    logger.warning(f"No chunks created from {file_path}")
                    files_skipped += 1
                    continue

                total_chunks_created += len(chunks)

                # Process embeddings in batches
                batch_size = 5
                embedding_batch_failed = False

                logger.info(f"🔄 Processing {len(chunks)} chunks in batches of {batch_size}...")

                for j in range(0, len(chunks), batch_size):
                    # **MANUAL SKIP CHECK**
                    if check_manual_skip():
                        logger.warning(f"⏭️  MANUAL SKIP: User requested to skip rest of {file_info['name']}")
                        clear_manual_skip()
                        embedding_batch_failed = True
                        files_dropped_due_to_memory += 1
                        force_garbage_collection()
                        break

                    batch_chunks = chunks[j:j + batch_size]
                    texts = [chunk["content"] for chunk in batch_chunks]

                    batch_num = j//batch_size + 1
                    total_batches = (len(chunks) + batch_size - 1) // batch_size
                    logger.info(f"  Batch {batch_num}/{total_batches}: Generating embeddings... [Memory: {get_memory_usage()}]")

                    # **MEMORY SAFETY CHECK**
                    current_batch_memory = get_memory_usage_percent()
                    if current_batch_memory > 98.0:
                        logger.warning(f"⚠️  High memory ({current_batch_memory:.1f}%) during embedding - Skipping rest of file")
                        embedding_batch_failed = True
                        files_dropped_due_to_memory += 1
                        break

                    # Generate embeddings
                    try:
                        embeddings = self.llm_service.get_embeddings(texts)
                        logger.info(f"  ✓ Generated {len(embeddings)} embeddings")

                        # Pair embeddings with metadata
                        batch_items = [
                            {
                                "content": chunk["content"],
                                "vector": embedding,
                                "metadata": chunk["metadata"]
                            }
                            for chunk, embedding in zip(batch_chunks, embeddings)
                        ]

                        # Insert immediately to free memory
                        logger.info(f"  💾 Storing embeddings in Milvus...")
                        self.vector_client.insert_embeddings_batch(batch_items)
                        total_embeddings_stored += len(batch_items)
                        logger.info(f"  ✓ Stored batch {batch_num}/{total_batches} ({len(batch_items)} embeddings)")

                        # Free memory
                        del batch_chunks, texts, embeddings, batch_items
                        force_garbage_collection()

                    except Exception as embed_error:
                        logger.error(f"Failed to generate embeddings for batch {batch_num}: {embed_error}")
                        del batch_chunks, texts
                        gc.collect()
                        continue

                # Only count as processed if we completed all embedding batches
                if not embedding_batch_failed:
                    files_processed += 1
                    if file_type == "markdown":
                        md_processed += 1
                    elif file_type == "api_definition":
                        api_processed += 1
                    logger.info(f"✓ Completed {file_info['name']} ({file_idx}/{len(all_files)})")
                else:
                    logger.warning(f"⚠️  Partially processed or skipped {file_info['name']} due to memory constraints")
                    files_skipped += 1

                # Release memory
                del chunks
                gc.collect()

            except Exception as e:
                logger.error(f"Failed to process {file_info.get('path', 'unknown')}: {e}")
                files_skipped += 1
                force_garbage_collection()
                continue

        logger.info("=" * 60)
        logger.info(f"Ingestion completed!")
        logger.info(f"  Total processed: {files_processed}/{len(all_files)} files")
        logger.info(f"    📄 Markdown: {md_processed}")
        logger.info(f"    🔧 API files: {api_processed}")
        logger.info(f"  Skipped: {files_skipped} files")
        if files_dropped_due_to_memory > 0:
            logger.info(f"  Dropped due to memory: {files_dropped_due_to_memory}")
        logger.info(f"  Final memory: {get_memory_usage()}")
        logger.info("=" * 60)

        return {
            "status": "completed",
            "files_fetched": files_processed,
            "files_skipped": files_skipped,
            "files_dropped_memory": files_dropped_due_to_memory,
            "chunks_created": total_chunks_created,
            "embeddings_stored": total_embeddings_stored,
            "markdown_processed": md_processed,
            "api_files_processed": api_processed,
            "repository": repository_id
        }

    def ingest_single_file(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """
        Ingest a single document.

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            Number of chunks stored
        """
        logger.info("Ingesting single document")

        # Chunk the document
        chunks = self.chunker.chunk_text(content, metadata)

        if not chunks:
            return 0

        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.llm_service.get_embeddings(texts)

        # Store in Pinecone
        batch_items = []
        for chunk, embedding in zip(chunks, embeddings):
            batch_items.append({
                "content": chunk["content"],
                "vector": embedding,
                "metadata": chunk["metadata"]
            })

        self.vector_client.insert_embeddings_batch(batch_items)

        logger.info(f"Stored {len(batch_items)} chunks")
        return len(batch_items)

    def ingest_github_repo(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Ingest all markdown files from a GitHub repository URL.

        Args:
            repo_url: Full GitHub repository URL (e.g., https://github.com/owner/repo or https://github.com/owner/repo.git)
            branch: Branch name (currently not used, always fetches from default branch)

        Returns:
            Summary statistics of the ingestion process
        """
        # Parse owner and repo from URL
        # Support formats: https://github.com/owner/repo, https://github.com/owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', repo_url)

        if not match:
            logger.error(f"Invalid GitHub URL format: {repo_url}")
            return {
                "status": "error",
                "message": f"Invalid GitHub URL format: {repo_url}",
                "files_fetched": 0,
                "chunks_created": 0,
                "embeddings_stored": 0
            }

        owner = match.group(1)
        repo = match.group(2)

        logger.info(f"Parsed GitHub URL: owner={owner}, repo={repo}, branch={branch}")

        # Call the existing ingest_from_github method
        return self.ingest_from_github(owner, repo)

    def ingest_images_from_github(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Ingest all image files from a GitHub repository using Google Vision API.
        Processes images one at a time to avoid memory issues.
        Skips images that have already been processed (same SHA hash).

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Summary statistics of the ingestion process
        """
        if not self.image_service:
            logger.warning("Image service not configured - skipping image ingestion")
            return {
                "status": "skipped",
                "message": "Image service not configured",
                "images_fetched": 0,
                "images_skipped": 0,
                "embeddings_stored": 0
            }

        logger.info(f"Starting image ingestion from GitHub: {owner}/{repo}")
        logger.info(f"Initial memory usage: {get_memory_usage()}")
        repository_id = f"{owner}/{repo}"

        # Step 1: Find all image files
        logger.info("Step 1: Finding image files in GitHub repository...")
        image_file_paths = self.github_service.find_all_image_files(owner, repo)

        if not image_file_paths:
            logger.info("No image files found in the repository")
            return {
                "status": "completed",
                "images_fetched": 0,
                "images_skipped": 0,
                "embeddings_stored": 0
            }

        logger.info(f"Found {len(image_file_paths)} image files")

        # Step 2: Process images one at a time
        logger.info("Step 2: Processing images one at a time...")
        total_embeddings_stored = 0
        images_processed = 0
        images_skipped = 0

        for i, file_info in enumerate(image_file_paths, 1):
            try:
                file_path = file_info['path']
                file_sha = file_info.get('sha', '')

                logger.info(f"Processing image {i}/{len(image_file_paths)}: {file_path} [Memory: {get_memory_usage()}]")

                # Check if this exact image (with same SHA) was already processed
                if file_sha and self.vector_client.file_already_processed(repository_id, file_path, file_sha):
                    logger.info(f"⏭️  Skipping {file_info['name']} - already processed (SHA: {file_sha[:8]})")
                    images_skipped += 1
                    continue

                # If image SHA changed, delete old chunks before adding new ones
                if file_sha:
                    logger.debug(f"Checking for outdated chunks of {file_path}...")
                    self.vector_client.delete_file_chunks(repository_id, file_path)

                # Fetch raw image bytes
                image_bytes = self.github_service.get_file_bytes(owner, repo, file_path)

                if not image_bytes:
                    logger.warning(f"Skipping empty image: {file_path}")
                    continue

                # Process image with Google Vision API
                vision_result = self.image_service.extract_text_from_image(image_bytes, file_path)

                if vision_result.get("error"):
                    logger.error(f"Failed to process image {file_path}: {vision_result['error']}")
                    continue

                # Format the extracted information as text
                formatted_content = self.image_service.format_image_content(
                    vision_result, file_path, file_info["name"]
                )

                if not formatted_content.strip():
                    logger.warning(f"No content extracted from image: {file_path}")
                    continue

                # Create metadata for the image
                file_metadata = {
                    "source": "github",
                    "repository": repository_id,
                    "file_path": file_path,
                    "file_name": file_info["name"],
                    "file_sha": file_sha,
                    "file_type": "image",
                    "url": file_info.get("url", "")
                }

                # Chunk the formatted content
                chunks = self.chunker.chunk_text(formatted_content, file_metadata)

                if not chunks:
                    logger.warning(f"No chunks created from image {file_path}")
                    continue

                logger.info(f"Created {len(chunks)} chunks from image {file_info['name']}")

                # Process embeddings in small batches (reduced from 25 to 10)
                batch_size = 10
                for j in range(0, len(chunks), batch_size):
                    batch_chunks = chunks[j:j + batch_size]
                    texts = [chunk["content"] for chunk in batch_chunks]

                    # **MEMORY SAFETY CHECK** - Wait if memory usage is too high before processing next batch
                    try:
                        wait_for_memory(
                            threshold_percent=98.0,  # Stop if RAM > 98%
                            check_interval=2.0,      # Check every 2 seconds
                            timeout=120.0,           # Wait up to 2 minutes
                            raise_on_timeout=True    # Abort if memory stays high
                        )
                    except RuntimeError as mem_error:
                        logger.error(f"❌ Aborting image ingestion due to high memory: {mem_error}")
                        logger.error(f"Processed {images_processed}/{len(image_file_paths)} images before stopping")
                        return {
                            "status": "aborted_high_memory",
                            "images_fetched": images_processed,
                            "images_skipped": images_skipped,
                            "embeddings_stored": total_embeddings_stored,
                            "error": str(mem_error)
                        }

                    # Generate embeddings
                    embeddings = self.llm_service.get_embeddings(texts)

                    # Pair embeddings with metadata
                    batch_items = [
                        {
                            "content": chunk["content"],
                            "vector": embedding,
                            "metadata": chunk["metadata"]
                        }
                        for chunk, embedding in zip(batch_chunks, embeddings)
                    ]

                    # Insert to vector database
                    self.vector_client.insert_embeddings_batch(batch_items)
                    total_embeddings_stored += len(batch_items)
                    logger.debug(f"Stored batch of {len(batch_items)} embeddings from {file_info['name']}")

                    # Free memory
                    del batch_chunks, texts, embeddings, batch_items
                    gc.collect()

                images_processed += 1
                logger.info(f"✓ Completed image {file_info['name']} ({i}/{len(image_file_paths)})")

                # Release memory
                del image_bytes, vision_result, formatted_content, chunks
                gc.collect()

            except Exception as e:
                logger.error(f"Failed to process image {file_info['path']}: {e}")
                continue

        logger.info(
            f"Image ingestion completed! Processed {images_processed}/{len(image_file_paths)} images, "
            f"Skipped {images_skipped} already-processed images [Final memory: {get_memory_usage()}]"
        )

        return {
            "status": "completed",
            "images_fetched": images_processed,
            "images_skipped": images_skipped,
            "embeddings_stored": total_embeddings_stored,
            "repository": repository_id
        }

    def ingest_github_repo_with_images(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Ingest both markdown files and images from a GitHub repository.

        Args:
            repo_url: Full GitHub repository URL
            branch: Branch name

        Returns:
            Combined summary statistics
        """
        # Parse owner and repo from URL
        match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', repo_url)

        if not match:
            logger.error(f"Invalid GitHub URL format: {repo_url}")
            return {
                "status": "error",
                "message": f"Invalid GitHub URL format: {repo_url}"
            }

        owner = match.group(1)
        repo = match.group(2)

        logger.info(f"Parsed GitHub URL: owner={owner}, repo={repo}, branch={branch}")
        logger.info("=" * 60)
        logger.info("Starting full repository ingestion (Markdown + Images)")
        logger.info("=" * 60)

        # First, ingest markdown files
        md_result = self.ingest_from_github(owner, repo)

        # Then, ingest images
        img_result = self.ingest_images_from_github(owner, repo)

        # Combine results
        return {
            "status": "completed",
            "repository": f"{owner}/{repo}",
            "markdown": {
                "files_processed": md_result.get("files_fetched", 0),
                "files_skipped": md_result.get("files_skipped", 0),
                "chunks_created": md_result.get("chunks_created", 0),
                "embeddings_stored": md_result.get("embeddings_stored", 0)
            },
            "images": {
                "images_processed": img_result.get("images_fetched", 0),
                "images_skipped": img_result.get("images_skipped", 0),
                "embeddings_stored": img_result.get("embeddings_stored", 0)
            },
            "total_embeddings": md_result.get("embeddings_stored", 0) + img_result.get("embeddings_stored", 0)
        }

    def ingest_org_repositories(self, org: str, keyword: str = "", max_repos: int = None) -> Dict[str, Any]:
        """
        Ingest all markdown files from multiple repositories in an organization,
        optionally filtered by a keyword.

        Args:
            org: Organization name (e.g., 'wso2-enterprise')
            keyword: Optional keyword to filter repositories (e.g., 'choreo')
            max_repos: Optional maximum number of repositories to process

        Returns:
            Summary statistics of the bulk ingestion process
        """
        logger.info("=" * 80)
        logger.info(f"Starting bulk organization ingestion: {org} (keyword: '{keyword}')")
        logger.info("=" * 80)
        logger.info(f"Initial memory usage: {get_memory_usage()}")

        # Step 1: Find all repositories in the organization
        logger.info(f"Step 1: Finding repositories in organization '{org}'...")
        try:
            repositories = self.github_service.search_org_repositories(org, keyword)
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch repositories: {str(e)}",
                "repositories_processed": 0,
                "total_files": 0,
                "total_embeddings": 0
            }

        if not repositories:
            logger.warning(f"No repositories found in organization '{org}' with keyword '{keyword}'")
            return {
                "status": "completed",
                "message": "No repositories found",
                "repositories_processed": 0,
                "total_files": 0,
                "total_embeddings": 0
            }

        logger.info(f"Found {len(repositories)} repositories matching criteria")

        # Limit the number of repositories if specified
        if max_repos and max_repos > 0:
            repositories = repositories[:max_repos]
            logger.info(f"Limited to first {max_repos} repositories")

        # Step 2: Process each repository
        logger.info(f"Step 2: Processing {len(repositories)} repositories...")

        results = []
        total_files_processed = 0
        total_files_skipped = 0
        total_files_dropped_memory = 0
        total_files_manually_skipped = 0
        total_embeddings_stored = 0
        repos_processed = 0
        repos_failed = 0

        for i, repo_info in enumerate(repositories, 1):
            repo_name = repo_info.get("name", "")
            owner = repo_info.get("owner", org)
            full_name = repo_info.get("full_name", f"{owner}/{repo_name}")

            # **MANUAL SKIP CHECK** - Clear skip flag at the start of each repo
            # This allows skipping individual files within a repo, but continues to next repo
            if check_manual_skip():
                logger.info(f"Manual skip flag was set, clearing for next repository: {full_name}")
                clear_manual_skip()

            logger.info("=" * 80)
            logger.info(f"Repository {i}/{len(repositories)}: {full_name}")
            logger.info(f"Description: {repo_info.get('description', 'N/A')}")
            logger.info(f"Memory before processing: {get_memory_usage()}")
            logger.info("=" * 80)

            try:
                # Wait for memory to be available before processing next repo
                wait_for_memory(
                    threshold_percent=96.0,  # Adjusted for systems with high baseline memory usage
                    check_interval=2.0,
                    timeout=120.0,
                    raise_on_timeout=True
                )

                # Ingest this repository
                result = self.ingest_from_github(owner, repo_name)

                repos_processed += 1
                total_files_processed += result.get("files_fetched", 0)
                total_files_skipped += result.get("files_skipped", 0)
                total_files_dropped_memory += result.get("files_dropped_memory", 0)
                total_embeddings_stored += result.get("embeddings_stored", 0)

                results.append({
                    "repository": full_name,
                    "status": result.get("status", "completed"),
                    "files_processed": result.get("files_fetched", 0),
                    "files_skipped": result.get("files_skipped", 0),
                    "files_dropped_memory": result.get("files_dropped_memory", 0),
                    "embeddings_stored": result.get("embeddings_stored", 0)
                })

                logger.info(f"✓ Completed {full_name}: {result.get('files_fetched', 0)} files, {result.get('embeddings_stored', 0)} embeddings" +
                           (f" (dropped {result.get('files_dropped_memory', 0)} due to memory)" if result.get('files_dropped_memory', 0) > 0 else ""))
                logger.info(f"Memory after processing: {get_memory_usage()}")

                # Force garbage collection between repositories
                force_garbage_collection()

            except Exception as e:
                repos_failed += 1
                logger.error(f"❌ Failed to process {full_name}: {e}")
                results.append({
                    "repository": full_name,
                    "status": "failed",
                    "error": str(e),
                    "files_processed": 0,
                    "files_skipped": 0,
                    "files_dropped_memory": 0,
                    "embeddings_stored": 0
                })
                continue

        logger.info("=" * 80)
        logger.info("BULK INGESTION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Organization: {org}")
        logger.info(f"Keyword filter: '{keyword}'")
        logger.info(f"Repositories processed: {repos_processed}/{len(repositories)}")
        logger.info(f"Repositories failed: {repos_failed}")
        logger.info(f"Total files processed: {total_files_processed}")
        logger.info(f"Total files skipped: {total_files_skipped}")
        if total_files_dropped_memory > 0:
            logger.info(f"Total files dropped due to memory: {total_files_dropped_memory}")
        logger.info(f"Total files dropped due to memory: {total_files_dropped_memory}")
        logger.info(f"Total embeddings stored: {total_embeddings_stored}")
        logger.info(f"Final memory usage: {get_memory_usage()}")
        logger.info("=" * 80)

        return {
            "status": "completed",
            "organization": org,
            "keyword": keyword,
            "repositories_found": len(repositories),
            "repositories_processed": repos_processed,
            "repositories_failed": repos_failed,
            "total_files_processed": total_files_processed,
            "total_files_skipped": total_files_skipped,
            "total_files_dropped_memory": total_files_dropped_memory,
            "total_embeddings_stored": total_embeddings_stored,
            "details": results
        }
