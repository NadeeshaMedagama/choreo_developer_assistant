"""
Chunking Service

Responsible for breaking down text into chunks suitable for embedding.
Uses intelligent chunking strategies to preserve semantic meaning.
"""

from typing import List, Dict, Any
import re

from ..models import Summary, TextChunk, DiagramFile
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChunkingService:
    """Service for chunking text content for embeddings."""

    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        """
        Initialize chunking service.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_summary(self, summary: Summary) -> List[TextChunk]:
        """
        Create chunks from a summary.

        Args:
            summary: Summary object to chunk

        Returns:
            List of TextChunk objects
        """
        logger.info(f"Chunking summary for: {summary.source_file.file_name}")

        # Prepare comprehensive text including all extracted information
        full_text = self._prepare_text_from_summary(summary)

        # Create chunks
        chunks = self._create_chunks(full_text, summary.source_file)

        # Add summary-specific metadata to each chunk
        for chunk in chunks:
            chunk.metadata.update({
                "key_concepts": summary.key_concepts,
                "entities": summary.entities,
                "has_relationships": len(summary.relationships) > 0,
                "summary_length": len(summary.summary_text)
            })

        logger.info(f"✓ Created {len(chunks)} chunks from summary")
        return chunks

    def _prepare_text_from_summary(self, summary: Summary) -> str:
        """
        Prepare comprehensive text from summary including all metadata.

        Args:
            summary: Summary object

        Returns:
            Formatted text string
        """
        sections = []

        # Add file information
        sections.append(f"=== File: {summary.source_file.file_name} ===")
        sections.append(f"Type: {summary.source_file.file_type.value}")
        sections.append(f"Path: {summary.source_file.relative_path}")
        sections.append("")

        # Add summary
        sections.append("=== Summary ===")
        sections.append(summary.summary_text)
        sections.append("")

        # Add key concepts
        if summary.key_concepts:
            sections.append("=== Key Concepts ===")
            sections.append(", ".join(summary.key_concepts))
            sections.append("")

        # Add entities
        if summary.entities:
            sections.append("=== Components/Entities ===")
            sections.append(", ".join(summary.entities))
            sections.append("")

        # Add relationships
        if summary.relationships:
            sections.append("=== Relationships ===")
            for rel in summary.relationships:
                sections.append(f"- {rel.get('source', 'Unknown')} --[{rel.get('type', 'relates to')}]--> {rel.get('target', 'Unknown')}")
            sections.append("")

        return "\n".join(sections)

    def _create_chunks(self, text: str, source_file: DiagramFile) -> List[TextChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            source_file: Source DiagramFile

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0

        while start < text_length:
            end = start + self.chunk_size

            # If not the last chunk, try to break at natural boundaries
            if end < text_length:
                # Look for paragraph break first
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start:
                    end = paragraph_break
                else:
                    # Look for sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('.\n', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if sentence_break != -1 and sentence_break > start:
                        end = sentence_break + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk = TextChunk(
                    content=chunk_text,
                    chunk_index=chunk_index,
                    source_file=source_file,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                        "chunk_size": len(chunk_text)
                    }
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else text_length

        return chunks

    def chunk_batch(self, summaries: List[Summary]) -> List[TextChunk]:
        """
        Create chunks from multiple summaries.

        Args:
            summaries: List of Summary objects

        Returns:
            List of all TextChunk objects
        """
        all_chunks = []

        for summary in summaries:
            chunks = self.chunk_summary(summary)
            all_chunks.extend(chunks)

        logger.info(f"✓ Created {len(all_chunks)} total chunks from {len(summaries)} summaries")
        return all_chunks

