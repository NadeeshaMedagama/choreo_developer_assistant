"""
Chunking utilities for markdown files with minimum and maximum requirements.
Respects markdown structure (headers, code blocks) when splitting content.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Tuple
import re

# Default chunking parameters (can be overridden by config)
DEFAULT_MIN_CHUNK_CHARS = 1000
DEFAULT_MAX_CHUNK_CHARS = 4000
DEFAULT_OVERLAP_CHARS = 200
DEFAULT_SIZE_THRESHOLD_BYTES = 10_000  # 10KB - when to start chunking files

# Regex patterns for markdown structure
HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```.*$", re.MULTILINE)


def should_chunk_markdown_file(
    path: str | Path,
    size_threshold_bytes: int = DEFAULT_SIZE_THRESHOLD_BYTES
) -> bool:
    """
    Determine if a markdown file should be chunked based on file size.

    Args:
        path: Path to the markdown file
        size_threshold_bytes: Minimum file size (in bytes) to trigger chunking

    Returns:
        True if file size exceeds threshold, False otherwise
    """
    p = Path(path)
    try:
        file_size = p.stat().st_size
        return file_size > size_threshold_bytes
    except FileNotFoundError:
        return False


def _find_code_fence_ranges(text: str) -> List[Tuple[int, int]]:
    """
    Find all code block ranges (``` ... ```) in the text.
    Returns list of (start_index, end_index) tuples.
    """
    ranges: List[Tuple[int, int]] = []
    positions = [m.start() for m in CODE_FENCE_RE.finditer(text)]

    # Pair up opening and closing fences
    for i in range(0, len(positions) - 1, 2):
        start = positions[i]
        # Find end of the closing fence line
        end_pos = text.find("\n", positions[i + 1])
        end = len(text) if end_pos == -1 else end_pos + 1
        ranges.append((start, end))

    return ranges


def _inside_any_range(idx: int, ranges: List[Tuple[int, int]]) -> bool:
    """Check if index falls within any of the given ranges."""
    return any(start <= idx < end for start, end in ranges)


def _safe_split_before(
    text: str,
    limit: int,
    code_ranges: List[Tuple[int, int]]
) -> int:
    """
    Find a safe split position before `limit`, preferring natural boundaries.
    Avoids splitting inside code blocks.

    Priority:
    1. Double newline (paragraph boundary)
    2. Single newline (line boundary)
    3. Hard limit if no safe boundary found
    """
    # Try double newline (paragraph boundary)
    pos = text.rfind("\n\n", 0, limit)
    while pos != -1 and _inside_any_range(pos, code_ranges):
        pos = text.rfind("\n\n", 0, pos)
    if pos != -1 and pos > 0:
        return pos + 2  # Include the blank line

    # Try single newline (line boundary)
    pos = text.rfind("\n", 0, limit)
    while pos != -1 and _inside_any_range(pos, code_ranges):
        pos = text.rfind("\n", 0, pos)

    return limit if pos <= 0 else pos + 1


def _extract_sections(content: str) -> List[Tuple[str, str]]:
    """
    Split markdown content into sections based on headers.
    Returns list of (section_title, section_content) tuples.
    """
    sections: List[Tuple[str, str]] = []
    matches = list(HEADER_RE.finditer(content))

    if not matches:
        # No headers found, treat entire content as one section
        return [("", content)]

    # Handle preamble (content before first header)
    first_match = matches[0]
    if first_match.start() > 0:
        preamble = content[:first_match.start()]
        sections.append(("", preamble))

    # Extract each section
    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end]
        sections.append((title, section_content))

    return sections


def chunk_markdown(
    content: str,
    min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    file_path: str = "README.md",
) -> List[Dict]:
    """
    Chunk markdown content while respecting structure (headers, code blocks).

    Args:
        content: Markdown content to chunk
        min_chunk_chars: Minimum chunk size (small chunks will be merged)
        max_chunk_chars: Maximum chunk size (larger sections will be split)
        overlap_chars: Number of overlapping characters between chunks
        file_path: Original file path (for metadata)

    Returns:
        List of chunk dictionaries with content and metadata
    """
    code_ranges = _find_code_fence_ranges(content)
    sections = _extract_sections(content)

    chunks: List[Dict] = []

    for section_title, section_text in sections:
        section_len = len(section_text)

        # If section fits in one chunk, add it directly
        if section_len <= max_chunk_chars:
            if section_text.strip():
                chunks.append({
                    "content": section_text.strip(),
                    "section_title": section_title,
                    "file_path": file_path,
                })
            continue

        # Split large sections into multiple chunks
        start = 0
        while start < section_len:
            limit = min(start + max_chunk_chars, section_len)
            end = _safe_split_before(section_text, limit, code_ranges)

            # Safety fallback: ensure we make progress
            if end <= start:
                end = limit

            piece = section_text[start:end].strip()
            if piece:
                chunks.append({
                    "content": piece,
                    "section_title": section_title,
                    "file_path": file_path,
                })

            # Check if we've reached the end
            if end >= section_len:
                break

            # Move start position with overlap
            start = max(0, end - overlap_chars)

    # Merge tiny chunks into previous chunks when possible
    merged: List[Dict] = []
    for chunk in chunks:
        if merged and len(chunk["content"]) < min_chunk_chars:
            prev_chunk = merged[-1]
            combined_len = len(prev_chunk["content"]) + len(chunk["content"])

            # Only merge if combined size is reasonable
            if combined_len <= max_chunk_chars + overlap_chars:
                prev_chunk["content"] = (
                    prev_chunk["content"].rstrip() + "\n\n" + chunk["content"]
                ).strip()
                continue

        merged.append(chunk)

    # Add final metadata (chunk indices)
    total_chunks = len(merged)
    for i, chunk in enumerate(merged):
        chunk["chunk_index"] = i
        chunk["total_chunks"] = total_chunks

    return merged


def chunk_markdown_file(
    file_path: str | Path,
    min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    size_threshold_bytes: int = DEFAULT_SIZE_THRESHOLD_BYTES,
) -> List[Dict]:
    """
    Load and chunk a markdown file.

    Args:
        file_path: Path to markdown file
        min_chunk_chars: Minimum chunk size
        max_chunk_chars: Maximum chunk size
        overlap_chars: Overlap between chunks
        size_threshold_bytes: Minimum file size to trigger chunking

    Returns:
        List of chunks with content and metadata
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    # Check if chunking is needed
    if not should_chunk_markdown_file(path, size_threshold_bytes):
        # Return single chunk for small files
        return [{
            "content": content.strip(),
            "chunk_index": 0,
            "total_chunks": 1,
            "section_title": "",
            "file_path": str(path),
        }]

    return chunk_markdown(
        content,
        min_chunk_chars=min_chunk_chars,
        max_chunk_chars=max_chunk_chars,
        overlap_chars=overlap_chars,
        file_path=str(path),
    )

