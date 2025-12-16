"""
README and Markdown processing service.
Handles chunking of markdown files with configurable requirements.
"""
from pathlib import Path
from typing import List, Dict
from backend.utils import chunk_markdown_file, should_chunk_markdown_file
from backend.utils.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MarkdownProcessor:
    """Process markdown files with intelligent chunking."""

    def __init__(
        self,
        min_chunk_chars: int = None,
        max_chunk_chars: int = None,
        overlap_chars: int = None,
        size_threshold_bytes: int = None,
    ):
        """
        Initialize processor with chunking configuration.

        Args:
            min_chunk_chars: Minimum chunk size (defaults to Config value)
            max_chunk_chars: Maximum chunk size (defaults to Config value)
            overlap_chars: Overlap between chunks (defaults to Config value)
            size_threshold_bytes: File size threshold for chunking (defaults to Config value)
        """
        self.min_chunk_chars = min_chunk_chars or Config.MIN_CHUNK_CHARS
        self.max_chunk_chars = max_chunk_chars or Config.MAX_CHUNK_CHARS
        self.overlap_chars = overlap_chars or Config.CHUNK_OVERLAP_CHARS
        self.size_threshold_bytes = size_threshold_bytes or Config.CHUNK_SIZE_THRESHOLD_BYTES

        logger.info(
            f"MarkdownProcessor initialized with: "
            f"min={self.min_chunk_chars}, max={self.max_chunk_chars}, "
            f"overlap={self.overlap_chars}, threshold={self.size_threshold_bytes}B"
        )

    def process_file(self, file_path: str | Path) -> List[Dict]:
        """
        Process a markdown file and return chunks.

        Args:
            file_path: Path to markdown file

        Returns:
            List of chunk dictionaries with content and metadata
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"Markdown file not found: {path}")

        if not path.suffix.lower() in ['.md', '.markdown']:
            logger.warning(f"File is not a markdown file: {path}")

        logger.info(f"Processing markdown file: {path}")

        # Check if chunking is needed
        needs_chunking = should_chunk_markdown_file(path, self.size_threshold_bytes)
        file_size = path.stat().st_size

        if needs_chunking:
            logger.info(
                f"File size ({file_size}B) exceeds threshold ({self.size_threshold_bytes}B), "
                f"chunking enabled"
            )
        else:
            logger.info(
                f"File size ({file_size}B) below threshold ({self.size_threshold_bytes}B), "
                f"returning single chunk"
            )

        # Process and chunk the file
        chunks = chunk_markdown_file(
            file_path=path,
            min_chunk_chars=self.min_chunk_chars,
            max_chunk_chars=self.max_chunk_chars,
            overlap_chars=self.overlap_chars,
            size_threshold_bytes=self.size_threshold_bytes,
        )

        logger.info(f"Created {len(chunks)} chunk(s) from {path.name}")

        # Log chunk statistics
        if chunks:
            sizes = [len(chunk["content"]) for chunk in chunks]
            logger.debug(
                f"Chunk size stats - min: {min(sizes)}, max: {max(sizes)}, "
                f"avg: {sum(sizes) // len(sizes)}"
            )

        return chunks

    def process_directory(self, dir_path: str | Path, pattern: str = "*.md") -> Dict[str, List[Dict]]:
        """
        Process all markdown files in a directory.

        Args:
            dir_path: Path to directory
            pattern: Glob pattern for files (default: "*.md")

        Returns:
            Dictionary mapping file paths to their chunks
        """
        directory = Path(dir_path)

        if not directory.is_dir():
            logger.error(f"Not a directory: {directory}")
            raise NotADirectoryError(f"Not a directory: {directory}")

        logger.info(f"Processing markdown files in: {directory}")

        results = {}
        md_files = list(directory.glob(pattern))

        logger.info(f"Found {len(md_files)} markdown file(s) matching '{pattern}'")

        for md_file in md_files:
            try:
                chunks = self.process_file(md_file)
                results[str(md_file)] = chunks
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
                results[str(md_file)] = []

        total_chunks = sum(len(chunks) for chunks in results.values())
        logger.info(f"Processed {len(md_files)} files, created {total_chunks} total chunks")

        return results


def process_readme(readme_path: str | Path) -> List[Dict]:
    """
    Convenience function to process a README file with default settings.

    Args:
        readme_path: Path to README.md file

    Returns:
        List of chunks with metadata
    """
    processor = MarkdownProcessor()
    return processor.process_file(readme_path)

