#!/usr/bin/env python3
"""
Demo script to test markdown chunking functionality.
Shows how to use the chunking utilities with maximum/minimum requirements.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils import chunk_markdown_file, should_chunk_markdown_file
from backend.utils.config import Config
from backend.services.markdown_processor import MarkdownProcessor, process_readme


def print_separator(title: str = ""):
    """Print a visual separator."""
    width = 80
    if title:
        print(f"\n{'=' * width}")
        print(f"  {title}")
        print(f"{'=' * width}\n")
    else:
        print(f"{'=' * width}\n")


def demo_chunk_requirements():
    """Demonstrate the chunking requirements."""
    print_separator("CHUNKING REQUIREMENTS")

    print(f"Minimum chunk size:        {Config.MIN_CHUNK_CHARS} characters")
    print(f"Maximum chunk size:        {Config.MAX_CHUNK_CHARS} characters")
    print(f"Overlap between chunks:    {Config.CHUNK_OVERLAP_CHARS} characters")
    print(f"File size threshold:       {Config.CHUNK_SIZE_THRESHOLD_BYTES} bytes ({Config.CHUNK_SIZE_THRESHOLD_BYTES // 1024}KB)")
    print(f"\nFiles smaller than {Config.CHUNK_SIZE_THRESHOLD_BYTES} bytes will NOT be chunked.")


def demo_basic_chunking():
    """Demonstrate basic chunking with a sample README."""
    print_separator("BASIC CHUNKING DEMO")

    # Create sample markdown content
    sample_md = """# Main Title

This is a preamble section before any subsections.

## Introduction

This is the introduction section with some content.
It has multiple paragraphs.

Here's the second paragraph of the introduction.

## Features

- Feature one with details
- Feature two with more information
- Feature three

## Code Example

Here's how to use it:

```python
def hello_world():
    print("Hello, World!")
    return True
```

The code above demonstrates basic usage.

## Installation

Run the following command:

```bash
pip install example-package
```

## Conclusion

Thank you for reading this README file.
"""

    # Save to temporary file
    temp_file = Path("/tmp/demo_readme.md")
    temp_file.write_text(sample_md)

    print(f"Created sample README: {temp_file}")
    print(f"File size: {temp_file.stat().st_size} bytes")
    print(f"Content length: {len(sample_md)} characters\n")

    # Check if it should be chunked
    should_chunk = should_chunk_markdown_file(temp_file)
    print(f"Should chunk: {should_chunk}\n")

    # Chunk it (with smaller limits for demo)
    chunks = chunk_markdown_file(
        temp_file,
        min_chunk_chars=100,
        max_chunk_chars=300,
        overlap_chars=50,
        size_threshold_bytes=100,  # Low threshold for demo
    )

    print(f"Created {len(chunks)} chunk(s):\n")

    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}:")
        print(f"  Section: '{chunk['section_title']}'")
        print(f"  Size: {len(chunk['content'])} characters")
        print(f"  Preview: {chunk['content'][:100]}...")
        print()


def demo_processor_service():
    """Demonstrate using the MarkdownProcessor service."""
    print_separator("MARKDOWN PROCESSOR SERVICE DEMO")

    # Create a larger sample file
    large_content = """# Large Documentation

""" + "\n\n".join([f"## Section {i}\n\nThis is section {i} with content. " * 50 for i in range(10)])

    temp_file = Path("/tmp/large_readme.md")
    temp_file.write_text(large_content)

    print(f"Created large README: {temp_file}")
    print(f"File size: {temp_file.stat().st_size} bytes\n")

    # Use the processor service
    processor = MarkdownProcessor(
        min_chunk_chars=500,
        max_chunk_chars=2000,
        overlap_chars=100,
        size_threshold_bytes=1000,
    )

    chunks = processor.process_file(temp_file)

    print(f"\nProcessor created {len(chunks)} chunk(s)")

    # Show statistics
    if chunks:
        sizes = [len(c['content']) for c in chunks]
        print(f"\nChunk size statistics:")
        print(f"  Smallest: {min(sizes)} chars")
        print(f"  Largest:  {max(sizes)} chars")
        print(f"  Average:  {sum(sizes) // len(sizes)} chars")


def demo_real_readme():
    """Try to process the actual project README if it exists."""
    print_separator("REAL PROJECT README DEMO")

    # Look for README in project root
    project_root = Path(__file__).parent
    readme_path = project_root / "README.md"

    if not readme_path.exists():
        print(f"README.md not found at: {readme_path}")
        print("Skipping real README demo.")
        return

    print(f"Found README: {readme_path}")
    print(f"File size: {readme_path.stat().st_size} bytes\n")

    try:
        chunks = process_readme(readme_path)

        print(f"Processed into {len(chunks)} chunk(s)\n")

        # Show first chunk details
        if chunks:
            first = chunks[0]
            print(f"First chunk:")
            print(f"  Section: '{first.get('section_title', 'N/A')}'")
            print(f"  Size: {len(first['content'])} characters")
            print(f"  Preview:\n{first['content'][:200]}...\n")

    except Exception as e:
        print(f"Error processing README: {e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  MARKDOWN CHUNKING DEMONSTRATION")
    print("  Maximum/Minimum Requirements for Chunking .md Files")
    print("=" * 80)

    demo_chunk_requirements()
    demo_basic_chunking()
    demo_processor_service()
    demo_real_readme()

    print_separator("DEMO COMPLETE")
    print("✓ All demos completed successfully!\n")
    print("You can now use these utilities in your ingestion pipeline:")
    print("  - from backend.utils import chunk_markdown_file")
    print("  - from backend.services.markdown_processor import MarkdownProcessor")
    print()


if __name__ == "__main__":
    main()

