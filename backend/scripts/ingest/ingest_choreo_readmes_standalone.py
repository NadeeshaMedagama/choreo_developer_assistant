"""
Standalone script to ingest README files from Choreo repositories into Pinecone.
This script:
1. Reads all downloaded README files
2. Chunks them into manageable pieces
3. Generates embeddings using Azure OpenAI
4. Stores them in the existing Pinecone index (choreo-ai-assistant-v2)
"""
import os
import sys
import json
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

# Load environment variables from backend/.env
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    env_path = project_root / 'backend' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


# ============================================================================
# CHUNKING UTILITIES (from backend/utils/chunking.py)
# ============================================================================

DEFAULT_MIN_CHUNK_CHARS = 1000
DEFAULT_MAX_CHUNK_CHARS = 4000
DEFAULT_OVERLAP_CHARS = 200

HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```.*$", re.MULTILINE)


def _find_code_fence_ranges(text: str) -> List[Tuple[int, int]]:
    """Find all code block ranges in the text."""
    ranges: List[Tuple[int, int]] = []
    positions = [m.start() for m in CODE_FENCE_RE.finditer(text)]

    for i in range(0, len(positions) - 1, 2):
        start = positions[i]
        end_pos = text.find("\n", positions[i + 1])
        end = len(text) if end_pos == -1 else end_pos + 1
        ranges.append((start, end))

    return ranges


def _inside_any_range(idx: int, ranges: List[Tuple[int, int]]) -> bool:
    """Check if index falls within any of the given ranges."""
    return any(start <= idx < end for start, end in ranges)


def _safe_split_before(text: str, limit: int, code_ranges: List[Tuple[int, int]]) -> int:
    """Find a safe split position before limit, avoiding code blocks."""
    pos = text.rfind("\n\n", 0, limit)
    while pos != -1 and _inside_any_range(pos, code_ranges):
        pos = text.rfind("\n\n", 0, pos)
    if pos != -1 and pos > 0:
        return pos + 2

    pos = text.rfind("\n", 0, limit)
    while pos != -1 and _inside_any_range(pos, code_ranges):
        pos = text.rfind("\n", 0, pos)

    return limit if pos <= 0 else pos + 1


def _extract_sections(content: str) -> List[Tuple[str, str]]:
    """Split markdown content into sections based on headers."""
    sections: List[Tuple[str, str]] = []
    matches = list(HEADER_RE.finditer(content))

    if not matches:
        return [("", content)]

    first_match = matches[0]
    if first_match.start() > 0:
        preamble = content[:first_match.start()]
        sections.append(("", preamble))

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end]
        sections.append((title, section_content))

    return sections


def chunk_markdown(content: str, min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS,
                   max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
                   overlap_chars: int = DEFAULT_OVERLAP_CHARS,
                   file_path: str = "README.md") -> List[Dict]:
    """Chunk markdown content while respecting structure."""
    code_ranges = _find_code_fence_ranges(content)
    sections = _extract_sections(content)

    chunks: List[Dict] = []

    for section_title, section_text in sections:
        section_len = len(section_text)

        if section_len <= max_chunk_chars:
            if section_text.strip():
                chunks.append({
                    "content": section_text.strip(),
                    "section_title": section_title,
                    "file_path": file_path,
                })
            continue

        start = 0
        while start < section_len:
            limit = min(start + max_chunk_chars, section_len)
            end = _safe_split_before(section_text, limit, code_ranges)

            if end <= start:
                end = limit

            piece = section_text[start:end].strip()
            if piece:
                chunks.append({
                    "content": piece,
                    "section_title": section_title,
                    "file_path": file_path,
                })

            if end >= section_len:
                break

            start = max(0, end - overlap_chars)

    merged: List[Dict] = []
    for chunk in chunks:
        if merged and len(chunk["content"]) < min_chunk_chars:
            prev_chunk = merged[-1]
            combined_len = len(prev_chunk["content"]) + len(chunk["content"])

            if combined_len <= max_chunk_chars + overlap_chars:
                prev_chunk["content"] = (
                    prev_chunk["content"].rstrip() + "\n\n" + chunk["content"]
                ).strip()
                continue

        merged.append(chunk)

    return merged


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def find_latest_readme_directory() -> str:
    """Find the most recent choreo_readmes_* directory."""
    current_dir = os.path.dirname(__file__)
    readme_dirs = []

    for item in os.listdir(current_dir):
        if item.startswith("choreo_readmes_") and os.path.isdir(os.path.join(current_dir, item)):
            readme_dirs.append(item)

    if not readme_dirs:
        raise FileNotFoundError("No choreo_readmes_* directory found. Please run backend/scripts/fetch/fetch_choreo_readmes_standalone.py first.")

    readme_dirs.sort(reverse=True)
    latest_dir = os.path.join(current_dir, readme_dirs[0])

    print(f"ℹ️  Found README directory: {latest_dir}")
    return latest_dir


def load_readme_files(readme_dir: str) -> List[Dict[str, Any]]:
    """Load all README files and their metadata."""
    readme_files = []

    metadata_path = os.path.join(readme_dir, "repositories_metadata.json")
    metadata = {}

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata_json = json.load(f)
            for repo in metadata_json.get('repositories', []):
                metadata[repo['name']] = repo

    for filename in os.listdir(readme_dir):
        if filename.endswith('_README.md'):
            repo_name = filename.replace('_README.md', '')
            filepath = os.path.join(readme_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            repo_metadata = metadata.get(repo_name, {})

            readme_files.append({
                'repo_name': repo_name,
                'filename': filename,
                'filepath': filepath,
                'content': content,
                'metadata': repo_metadata
            })

            print(f"ℹ️  Loaded README for {repo_name} ({len(content)} chars)")

    return readme_files


def chunk_readme_files(readme_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk all README files into smaller pieces."""
    all_chunks = []

    print(f"ℹ️  Chunking {len(readme_files)} README files...")

    for readme in readme_files:
        repo_name = readme['repo_name']
        content = readme['content']
        repo_metadata = readme['metadata']

        if not content.strip():
            print(f"⚠️  Skipping empty README for {repo_name}")
            continue

        chunks = chunk_markdown(
            content=content,
            min_chunk_chars=DEFAULT_MIN_CHUNK_CHARS,
            max_chunk_chars=DEFAULT_MAX_CHUNK_CHARS,
            overlap_chars=DEFAULT_OVERLAP_CHARS,
            file_path=f"{repo_name}/README.md"
        )

        for i, chunk in enumerate(chunks):
            chunk['metadata'] = {
                'repository': repo_name,
                'full_name': repo_metadata.get('full_name', repo_name),
                'description': repo_metadata.get('description', '') or '',
                'url': repo_metadata.get('url', '') or '',
                'language': repo_metadata.get('language', '') or '',  # Convert None to empty string
                'stars': int(repo_metadata.get('stars', 0)),
                'forks': int(repo_metadata.get('forks', 0)),
                'source': 'choreo_org_repositories',
                'file_type': 'readme',
                'chunk_index': i,
                'total_chunks': len(chunks),
                'section_title': chunk.get('section_title', '') or '',
                'ingestion_date': datetime.now().isoformat()
            }
            all_chunks.append(chunk)

        print(f"ℹ️  Created {len(chunks)} chunks from {repo_name}")

    print(f"ℹ️  Total chunks created: {len(all_chunks)}")
    return all_chunks


def generate_embeddings_with_azure(chunks: List[Dict[str, Any]], batch_size: int = 50) -> List[Dict[str, Any]]:
    """Generate embeddings using Azure OpenAI."""
    try:
        from openai import AzureOpenAI
    except ImportError:
        raise RuntimeError("OpenAI SDK not installed. Install with: pip install openai")

    # Get Azure OpenAI configuration
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    embeddings_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")

    if not all([api_key, endpoint, embeddings_deployment]):
        raise ValueError("Missing Azure OpenAI configuration in .env file")

    print(f"ℹ️  Initializing Azure OpenAI...")
    print(f"   Endpoint: {endpoint}")
    print(f"   Deployment: {embeddings_deployment}")

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

    print(f"ℹ️  Generating embeddings for {len(chunks)} chunks...")

    items_with_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_texts = [chunk['content'] for chunk in batch]

        batch_num = i // batch_size + 1
        total_batches = (len(chunks) - 1) // batch_size + 1
        print(f"ℹ️  Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")

        try:
            response = client.embeddings.create(
                input=batch_texts,
                model=embeddings_deployment
            )

            embeddings = [item.embedding for item in response.data]

            for chunk, embedding in zip(batch, embeddings):
                items_with_embeddings.append({
                    'content': chunk['content'],
                    'vector': embedding,
                    'metadata': chunk['metadata']
                })

        except Exception as e:
            print(f"❌ Error generating embeddings for batch {batch_num}: {e}")
            raise

    print(f"✅ Generated {len(items_with_embeddings)} embeddings")
    return items_with_embeddings


def store_in_milvus(items: List[Dict[str, Any]], batch_size: int = 100):
    """Store embeddings in Milvus database."""
    try:
        from pymilvus import MilvusClient
        import uuid
    except ImportError:
        raise RuntimeError("Milvus SDK not installed. Install with: pip install pymilvus")

    # Get Milvus configuration
    uri = os.getenv("MILVUS_URI")
    token = os.getenv("MILVUS_TOKEN")
    collection_name = os.getenv("MILVUS_COLLECTION_NAME", "readme_embeddings")
    dimension = int(os.getenv("MILVUS_DIMENSION", "1536"))

    if not uri or not token:
        raise ValueError("MILVUS_URI and MILVUS_TOKEN not found in .env file")

    print(f"ℹ️  Connecting to Milvus...")
    print(f"   Collection: {collection_name}")
    print(f"   Dimension: {dimension}")

    client = MilvusClient(uri=uri, token=token)

    # Check if collection exists, create if not
    if not client.has_collection(collection_name=collection_name):
        print(f"ℹ️  Creating new Milvus collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            dimension=dimension,
            metric_type="COSINE",
            auto_id=False,
            enable_dynamic_field=True
        )

    print(f"ℹ️  Storing {len(items)} embeddings in Milvus...")

    total_stored = 0

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        batch_num = i // batch_size + 1
        total_batches = (len(items) - 1) // batch_size + 1
        print(f"ℹ️  Storing batch {batch_num}/{total_batches} ({len(batch)} items)")

        data_list = []
        for item in batch:
            doc_id = str(uuid.uuid4())
            meta = item.get("metadata", {})

            data = {
                "id": doc_id,
                "vector": item["vector"],
                "content": item["content"],
                **meta  # Include all metadata fields
            }
            data_list.append(data)

        try:
            client.insert(collection_name=collection_name, data=data_list)
            total_stored += len(batch)

        except Exception as e:
            print(f"❌ Error storing batch {batch_num}: {e}")
            raise

    print(f"✅ Stored {total_stored} embeddings in Milvus")
    return total_stored


def main():
    """Main ingestion pipeline."""

    print("=" * 80)
    print("📚 Choreo README Ingestion Pipeline")
    print("=" * 80)
    print()

    try:
        # Step 1: Find and load README files
        print("📂 Step 1: Loading README files...")
        readme_dir = find_latest_readme_directory()
        readme_files = load_readme_files(readme_dir)

        if not readme_files:
            print("❌ No README files found!")
            return

        print(f"✅ Loaded {len(readme_files)} README files")
        print()

        # Step 2: Chunk README files
        print("✂️  Step 2: Chunking README files...")
        chunks = chunk_readme_files(readme_files)

        if not chunks:
            print("❌ No chunks created!")
            return

        print(f"✅ Created {len(chunks)} chunks")
        print()

        # Step 3: Generate embeddings
        print("🧮 Step 3: Generating embeddings with Azure OpenAI...")
        items_with_embeddings = generate_embeddings_with_azure(chunks, batch_size=50)
        print()

        # Step 4: Store in Milvus
        print("💾 Step 4: Storing in Milvus...")
        total_stored = store_in_milvus(items_with_embeddings, batch_size=100)
        print()

        # Summary
        print("=" * 80)
        print("📊 INGESTION SUMMARY")
        print("=" * 80)
        print(f"README files processed: {len(readme_files)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Embeddings generated: {len(items_with_embeddings)}")
        print(f"Embeddings stored in Milvus: {total_stored}")
        print(f"Milvus collection: {os.getenv('MILVUS_COLLECTION_NAME', 'readme_embeddings')}")
        print("=" * 80)
        print()
        print("✅ Ingestion completed successfully!")
        print()
        print("🎯 Next steps:")
        print("   - Your Choreo README embeddings are now searchable in Milvus")
        print("   - You can query them using the RAG system")
        print("   - The embeddings include metadata about each repository")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
