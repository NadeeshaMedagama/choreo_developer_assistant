#!/usr/bin/env python3
"""Simple test to verify chunking works."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Test basic imports
try:
    from backend.utils.chunking import (
        chunk_markdown,
        should_chunk_markdown_file,
        DEFAULT_MIN_CHUNK_CHARS,
        DEFAULT_MAX_CHUNK_CHARS,
        DEFAULT_OVERLAP_CHARS,
        DEFAULT_SIZE_THRESHOLD_BYTES
    )
    print("✓ Successfully imported chunking utilities")
    print(f"\nDefault Configuration:")
    print(f"  MIN_CHUNK_CHARS:          {DEFAULT_MIN_CHUNK_CHARS}")
    print(f"  MAX_CHUNK_CHARS:          {DEFAULT_MAX_CHUNK_CHARS}")
    print(f"  OVERLAP_CHARS:            {DEFAULT_OVERLAP_CHARS}")
    print(f"  SIZE_THRESHOLD_BYTES:     {DEFAULT_SIZE_THRESHOLD_BYTES} ({DEFAULT_SIZE_THRESHOLD_BYTES // 1024}KB)")

    # Test with sample content
    sample = """# Test README

## Section 1
Content for section 1.

## Section 2
Content for section 2 with more text."""

    chunks = chunk_markdown(sample, min_chunk_chars=50, max_chunk_chars=200, file_path="test.md")
    print(f"\n✓ Chunking works! Created {len(chunks)} chunk(s)")

    for i, chunk in enumerate(chunks, 1):
        print(f"\n  Chunk {i}:")
        print(f"    Section: {chunk.get('section_title', 'N/A')}")
        print(f"    Size: {len(chunk['content'])} chars")

    print("\n✓ All tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

