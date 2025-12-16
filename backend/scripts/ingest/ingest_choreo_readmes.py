"""
Script to ingest README files from Choreo repositories into Pinecone.
This script:
1. Reads all downloaded README files
2. Chunks them into manageable pieces
3. Generates embeddings using Azure OpenAI
4. Stores them in the existing Pinecone index (choreo-ai-assistant-v2)
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.chunking import chunk_markdown, DEFAULT_MIN_CHUNK_CHARS, DEFAULT_MAX_CHUNK_CHARS, DEFAULT_OVERLAP_CHARS
from backend.services.llm_service import LLMService
from backend.db.vector_client import VectorClient
from backend.utils.logger import get_logger
from backend.utils.config import Config

logger = get_logger(__name__)


def find_latest_readme_directory() -> str:
    """Find the most recent choreo_readmes_* directory."""
    current_dir = os.path.dirname(__file__)
    readme_dirs = []

    for item in os.listdir(current_dir):
        if item.startswith("choreo_readmes_") and os.path.isdir(os.path.join(current_dir, item)):
            readme_dirs.append(item)

    if not readme_dirs:
        raise FileNotFoundError("No choreo_readmes_* directory found. Please run backend/scripts/fetch/fetch_choreo_readmes_standalone.py first.")

    # Sort by timestamp (directory name includes timestamp)
    readme_dirs.sort(reverse=True)
    latest_dir = os.path.join(current_dir, readme_dirs[0])

    logger.info(f"Found README directory: {latest_dir}")
    return latest_dir


def load_readme_files(readme_dir: str) -> List[Dict[str, Any]]:
    """Load all README files and their metadata."""
    readme_files = []

    # Load metadata if exists
    metadata_path = os.path.join(readme_dir, "repositories_metadata.json")
    metadata = {}

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata_json = json.load(f)
            # Create a dict mapping repo names to metadata
            for repo in metadata_json.get('repositories', []):
                metadata[repo['name']] = repo

    # Load all README files
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

            logger.info(f"Loaded README for {repo_name} ({len(content)} chars)")

    return readme_files


def chunk_readme_files(readme_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk all README files into smaller pieces."""
    all_chunks = []

    logger.info(f"Chunking {len(readme_files)} README files...")

    for readme in readme_files:
        repo_name = readme['repo_name']
        content = readme['content']
        repo_metadata = readme['metadata']

        # Skip empty files
        if not content.strip():
            logger.warning(f"Skipping empty README for {repo_name}")
            continue

        # Chunk the markdown content
        chunks = chunk_markdown(
            content=content,
            min_chunk_chars=DEFAULT_MIN_CHUNK_CHARS,
            max_chunk_chars=DEFAULT_MAX_CHUNK_CHARS,
            overlap_chars=DEFAULT_OVERLAP_CHARS,
            file_path=f"{repo_name}/README.md"
        )

        # Add repository metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk['metadata'] = {
                'repository': repo_name,
                'full_name': repo_metadata.get('full_name', repo_name),
                'description': repo_metadata.get('description', ''),
                'url': repo_metadata.get('url', ''),
                'language': repo_metadata.get('language', ''),
                'stars': repo_metadata.get('stars', 0),
                'forks': repo_metadata.get('forks', 0),
                'source': 'choreo_org_repositories',
                'file_type': 'readme',
                'chunk_index': i,
                'total_chunks': len(chunks),
                'section_title': chunk.get('section_title', ''),
                'ingestion_date': datetime.now().isoformat()
            }
            all_chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {repo_name}")

    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def generate_embeddings_batch(chunks: List[Dict[str, Any]], llm_service: LLMService, batch_size: int = 50) -> List[Dict[str, Any]]:
    """Generate embeddings for chunks in batches."""
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")

    items_with_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_texts = [chunk['content'] for chunk in batch]

        logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch)} chunks)")

        try:
            # Generate embeddings for the batch
            embeddings = llm_service.get_embeddings(batch_texts)

            # Combine chunks with their embeddings
            for chunk, embedding in zip(batch, embeddings):
                items_with_embeddings.append({
                    'content': chunk['content'],
                    'vector': embedding,
                    'metadata': chunk['metadata']
                })

            logger.info(f"Generated {len(embeddings)} embeddings")

        except Exception as e:
            logger.error(f"Error generating embeddings for batch: {e}")
            raise

    logger.info(f"Total embeddings generated: {len(items_with_embeddings)}")
    return items_with_embeddings


def store_in_pinecone(items: List[Dict[str, Any]], vector_client: VectorClient, batch_size: int = 100):
    """Store embeddings in Pinecone database."""
    logger.info(f"Storing {len(items)} embeddings in Pinecone...")

    total_stored = 0

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        logger.info(f"Storing batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1} ({len(batch)} items)")

        try:
            vector_client.insert_embeddings_batch(batch)
            total_stored += len(batch)
            logger.info(f"Stored {total_stored}/{len(items)} embeddings")

        except Exception as e:
            logger.error(f"Error storing batch in Pinecone: {e}")
            raise

    logger.info(f"Successfully stored all {total_stored} embeddings in Pinecone")
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

        # Step 3: Initialize services
        print("🔧 Step 3: Initializing services...")
        config = Config()

        # Initialize LLM service for embeddings
        llm_service = LLMService(
            use_openai=True,
            endpoint=config.azure_openai_endpoint,
            api_key=config.azure_openai_api_key,
            api_version=config.azure_openai_api_version,
            deployment=config.azure_openai_chat_deployment
        )
        llm_service.set_embeddings_deployment(config.azure_openai_embeddings_deployment)

        # Initialize Pinecone vector client
        vector_client = VectorClient(
            api_key=config.pinecone_api_key,
            index_name=config.pinecone_index_name,
            dimension=config.pinecone_dimension,
            cloud=config.pinecone_cloud,
            region=config.pinecone_region
        )

        print(f"✅ Services initialized")
        print(f"   - Pinecone Index: {config.pinecone_index_name}")
        print(f"   - Embedding Model: {config.azure_openai_embeddings_deployment}")
        print(f"   - Dimension: {config.pinecone_dimension}")
        print()

        # Step 4: Generate embeddings
        print("🧮 Step 4: Generating embeddings...")
        items_with_embeddings = generate_embeddings_batch(chunks, llm_service, batch_size=50)
        print(f"✅ Generated {len(items_with_embeddings)} embeddings")
        print()

        # Step 5: Store in Pinecone
        print("💾 Step 5: Storing in Pinecone...")
        total_stored = store_in_pinecone(items_with_embeddings, vector_client, batch_size=100)
        print(f"✅ Stored {total_stored} embeddings")
        print()

        # Summary
        print("=" * 80)
        print("📊 INGESTION SUMMARY")
        print("=" * 80)
        print(f"README files processed: {len(readme_files)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Embeddings generated: {len(items_with_embeddings)}")
        print(f"Embeddings stored in Pinecone: {total_stored}")
        print(f"Pinecone index: {config.pinecone_index_name}")
        print("=" * 80)
        print()
        print("✅ Ingestion completed successfully!")
        print()
        print("🎯 Next steps:")
        print("   - Your Choreo README embeddings are now searchable in Pinecone")
        print("   - You can query them using the RAG system")
        print("   - The embeddings include metadata about each repository")

    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

