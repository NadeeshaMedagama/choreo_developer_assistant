"""
Wiki Chunking Service.
Chunks wiki content for embedding.
"""

from typing import List, Dict, Any
import re

from ..models.wiki_page import WikiPage
from ..models.wiki_chunk import WikiChunk


class WikiChunkingService:
    """Service for chunking wiki content."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize chunking service.

        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            min_chunk_size: Minimum chunk size (don't create tiny chunks)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_page(self, page: WikiPage) -> List[WikiChunk]:
        """
        Chunk a wiki page into smaller pieces.

        Args:
            page: WikiPage to chunk

        Returns:
            List of WikiChunk objects
        """
        # Use markdown content if available, otherwise use plain content
        text = page.markdown or page.content
        
        if not text or len(text) < self.min_chunk_size:
            # Page too small, return as single chunk
            return [self._create_chunk(page, text, 0, 1)]
        
        # Chunk the text
        chunks = self._smart_chunk(text)
        
        # Create WikiChunk objects
        wiki_chunks = []
        total_chunks = len(chunks)
        
        for idx, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.min_chunk_size:
                wiki_chunk = self._create_chunk(page, chunk_text, idx, total_chunks)
                wiki_chunks.append(wiki_chunk)
        
        return wiki_chunks
    
    def chunk_linked_content(
        self,
        content: str,
        source_url: str,
        source_title: str,
        metadata: Dict[str, Any]
    ) -> List[WikiChunk]:
        """
        Chunk content from a linked URL.

        Args:
            content: Text content to chunk
            source_url: URL of the source
            source_title: Title of the source
            metadata: Additional metadata

        Returns:
            List of WikiChunk objects
        """
        if not content or len(content) < self.min_chunk_size:
            return [WikiChunk(
                chunk_id=WikiChunk.generate_id(),
                text=content,
                chunk_index=0,
                source_url=source_url,
                source_title=source_title,
                source_type="linked_content",
                total_chunks=1,
                metadata=metadata,
            )]
        
        chunks = self._smart_chunk(content)
        wiki_chunks = []
        total_chunks = len(chunks)
        
        for idx, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.min_chunk_size:
                wiki_chunk = WikiChunk(
                    chunk_id=WikiChunk.generate_id(),
                    text=chunk_text.strip(),
                    chunk_index=idx,
                    source_url=source_url,
                    source_title=source_title,
                    source_type="linked_content",
                    total_chunks=total_chunks,
                    metadata=metadata,
                )
                wiki_chunks.append(wiki_chunk)
        
        return wiki_chunks
    
    def _create_chunk(
        self,
        page: WikiPage,
        text: str,
        index: int,
        total: int
    ) -> WikiChunk:
        """Create a WikiChunk from page data."""
        return WikiChunk(
            chunk_id=WikiChunk.generate_id(),
            text=text.strip(),
            chunk_index=index,
            source_url=page.url,
            source_title=page.title,
            source_type="wiki_page",
            repository=page.repository,
            owner=page.owner,
            total_chunks=total,
            metadata={
                'wiki_name': page.wiki_name,
                'page_path': page.page_path,
                'depth': page.depth,
                'parent_url': page.parent_url,
                **page.metadata,
            },
        )
    
    def _smart_chunk(self, text: str) -> List[str]:
        """
        Smart chunking that respects markdown structure.
        
        Tries to chunk on:
        1. Headers
        2. Paragraphs
        3. Sentences
        4. Character boundaries (fallback)
        """
        chunks = []
        
        # Split on major headers first
        sections = re.split(r'\n(#{1,2}\s+.+?\n)', text)
        
        current_chunk = ""
        
        for section in sections:
            # If adding this section exceeds chunk size and we have content
            if len(current_chunk) + len(section) > self.chunk_size and current_chunk:
                # Try to split the current chunk further if it's too large
                if len(current_chunk) > self.chunk_size:
                    sub_chunks = self._split_large_section(current_chunk)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(current_chunk)
                
                # Start new chunk with overlap
                if chunks:
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = overlap_text + section
                else:
                    current_chunk = section
            else:
                current_chunk += section
        
        # Add remaining chunk
        if current_chunk.strip():
            if len(current_chunk) > self.chunk_size:
                sub_chunks = self._split_large_section(current_chunk)
                chunks.extend(sub_chunks)
            else:
                chunks.append(current_chunk)
        
        return [c.strip() for c in chunks if c.strip()]
    
    def _split_large_section(self, text: str) -> List[str]:
        """Split a large section into smaller chunks."""
        chunks = []
        
        # Try splitting on paragraphs
        paragraphs = re.split(r'\n\n+', text)
        
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            
            # If single paragraph is too large, split on sentences
            if len(current_chunk) > self.chunk_size * 1.5:
                sentence_chunks = self._split_on_sentences(current_chunk)
                chunks.extend(sentence_chunks[:-1])
                current_chunk = sentence_chunks[-1] if sentence_chunks else ""
        
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_on_sentences(self, text: str) -> List[str]:
        """Split text on sentence boundaries."""
        # Simple sentence splitting
        sentences = re.split(r'([.!?]+\s+)', text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]
            
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap + sentence
            else:
                current_chunk += sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        """Get overlap text from the end of a chunk."""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to get overlap at a natural boundary
        overlap_text = text[-self.chunk_overlap:]
        
        # Try to start at a sentence boundary
        sentence_start = overlap_text.find('. ')
        if sentence_start > 0:
            overlap_text = overlap_text[sentence_start + 2:]
        
        return overlap_text

