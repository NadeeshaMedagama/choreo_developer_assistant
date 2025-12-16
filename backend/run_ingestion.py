"""
Script to ingest Choreo documentation from GitHub into Milvus.

This script:
1. Connects to GitHub using the REST API
2. Fetches all .md files from the specified repository
3. Chunks the documents into manageable pieces
4. Generates embeddings using a language model
5. Stores the embeddings in Milvus vector database

Usage:
    python run_ingestion.py

Environment Variables Required:
    - MILVUS_URI: Your Milvus instance URI
    - MILVUS_TOKEN: Your Milvus authentication token
    - GITHUB_TOKEN: (Optional) GitHub personal access token for higher rate limits
    - OPENAI_API_KEY: (Optional) If using OpenAI embeddings
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try loading from backend/.env first
    backend_env = backend_path / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
        print(f"Loaded environment from: {backend_env}")

    # Also try loading from parent directory
    parent_env = backend_path.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env, override=False)  # Don't override existing values
        print(f"Loaded environment from: {parent_env}")

    if not backend_env.exists() and not parent_env.exists():
        print("Warning: No .env file found. Make sure environment variables are set.")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

from utils.config import config
from utils.logger import get_logger
from db.vector_client import VectorClient
from services.llm_service import LLMService
from services.github_service import GitHubService
from services.ingestion import IngestionService, start_keyboard_monitor

logger = get_logger(__name__)


def main():
    """Main ingestion function."""

    logger.info("=" * 60)
    logger.info("Starting Choreo Documentation Ingestion")
    logger.info("=" * 60)

    # Start keyboard monitor for manual skip feature
    logger.info("\n🎛️  Starting manual skip feature...")
    start_keyboard_monitor()
    logger.info("💡 TIP: Press 'q' + Enter anytime to skip the current file if RAM is too high\n")

    # Validate configuration
    try:
        config.validate()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set the required environment variables")
        return

    # Repository details
    REPO_OWNER = "NadeeshaMedagama"
    REPO_NAME = "python_Sample"

    logger.info(f"Target repository: {REPO_OWNER}/{REPO_NAME}")

    try:
        # Initialize services
        logger.info("\n" + "=" * 60)
        logger.info("Initializing Services")
        logger.info("=" * 60)

        # 1. Initialize Vector Client
        logger.info("1. Initializing Milvus Vector Client...")
        vector_client = VectorClient(
            uri=config.MILVUS_URI,
            token=config.MILVUS_TOKEN,
            collection_name=config.MILVUS_COLLECTION_NAME,
            dimension=config.MILVUS_DIMENSION,
            metric=config.MILVUS_METRIC
        )

        # Test connection
        if vector_client.test_connection():
            logger.info("   ✓ Milvus connection successful")
        else:
            logger.error("   ✗ Milvus connection failed")
            return

        # 2. Initialize LLM Service
        logger.info("2. Initializing LLM Service for embeddings...")
        use_openai = bool(config.OPENAI_API_KEY)

        if use_openai:
            logger.info("   Using OpenAI embeddings (text-embedding-ada-002)")
            llm_service = LLMService(use_openai=True)
        else:
            logger.info(f"   Using SentenceTransformer: {config.EMBEDDING_MODEL}")
            llm_service = LLMService(model_name=config.EMBEDDING_MODEL, use_openai=False)

        logger.info(f"   Embedding dimension: {llm_service.get_dimension()}")

        # 3. Initialize GitHub Service
        logger.info("3. Initializing GitHub Service...")
        github_service = GitHubService(token=config.GITHUB_TOKEN)

        if config.GITHUB_TOKEN:
            logger.info("   ✓ Using authenticated GitHub API (higher rate limits)")
        else:
            logger.info("   ⚠ Using unauthenticated GitHub API (lower rate limits)")

        # 4. Initialize Ingestion Service
        logger.info("4. Initializing Ingestion Service...")
        ingestion_service = IngestionService(
            github_service=github_service,
            llm_service=llm_service,
            vector_client=vector_client,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        logger.info(f"   Chunk size: {config.CHUNK_SIZE}, Overlap: {config.CHUNK_OVERLAP}")

        # Run ingestion
        logger.info("\n" + "=" * 60)
        logger.info("Starting Ingestion Process")
        logger.info("=" * 60)

        result = ingestion_service.ingest_from_github(REPO_OWNER, REPO_NAME)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("Ingestion Complete - Summary")
        logger.info("=" * 60)
        logger.info(f"Status: {result['status']}")
        logger.info(f"Repository: {result.get('repository', 'N/A')}")
        logger.info(f"Files fetched: {result['files_fetched']}")
        logger.info(f"Chunks created: {result['chunks_created']}")
        logger.info(f"Embeddings stored: {result['embeddings_stored']}")
        logger.info("=" * 60)

        if result['embeddings_stored'] > 0:
            logger.info("✓ Ingestion completed successfully!")
        else:
            logger.warning("⚠ No embeddings were stored")

    except Exception as e:
        logger.error(f"\n✗ Ingestion failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
