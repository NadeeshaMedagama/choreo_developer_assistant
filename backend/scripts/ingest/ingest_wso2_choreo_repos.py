#!/usr/bin/env python3
"""
Standalone script to ingest files from organization repositories into the Milvus database.

This script supports two modes:
1. DEFAULT MODE: Ingests markdown (.md) and API definition files (.yaml, .yml, .json, .graphql, .proto)
2. ALL FILES MODE (--all-files): Ingests ALL text-based files including:
   - Source code (.py, .js, .ts, .java, .go, .rs, .bal, etc.)
   - Configuration files (.yaml, .yml, .json, .toml, .ini, etc.)
   - Documentation (.md, .rst, .txt, etc.)
   - Build files (Dockerfile, Makefile, pom.xml, etc.)
   - Shell scripts (.sh, .bash, etc.)
   - And many more text-based files
   Binary files (images, archives, executables) are excluded.

Usage:
    # Default mode (markdown + API files only)
    python backend/scripts/ingest/ingest_wso2_choreo_repos.py

    # Ingest ALL files from repositories
    python backend/scripts/ingest/ingest_wso2_choreo_repos.py --all-files

    # With options:
    python backend/scripts/ingest/ingest_wso2_choreo_repos.py --org wso2-enterprise --keyword choreo --all-files
    python backend/scripts/ingest/ingest_wso2_choreo_repos.py --max-repos 5 --all-files
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from services.github_service import GitHubService
from services.llm_service import LLMService
from services.ingestion import IngestionService, start_keyboard_monitor
from db.vector_client import VectorClient
from utils.config import load_config
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main function to run the ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest files from organization repositories filtered by keyword"
    )
    parser.add_argument(
        "--org",
        type=str,
        default="wso2",
        help="GitHub organization name (default: wso2)"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="choreo",
        help="Keyword to filter repositories (default: choreo)"
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=None,
        help="Maximum number of repositories to process (default: all)"
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        default=False,
        help="Retrieve ALL files (code, config, docs, etc.) instead of just markdown and API files"
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("WSO2 Choreo Repositories Ingestion Script")
    logger.info("=" * 80)
    logger.info(f"Organization: {args.org}")
    logger.info(f"Keyword filter: {args.keyword}")
    logger.info(f"Max repositories: {args.max_repos or 'All'}")
    if args.all_files:
        logger.info("📋 Mode: ALL FILES (code, config, docs, etc.)")
    else:
        logger.info("📋 Mode: MARKDOWN + API FILES only")
    logger.info("=" * 80)

    # Start keyboard monitor for manual skip feature
    logger.info("\n🎛️  Starting manual skip feature...")
    start_keyboard_monitor()
    logger.info("💡 TIP: Press 'q' + Enter anytime to skip the current file if RAM is too high\n")

    # Load configuration from .env file
    logger.info("Loading configuration from .env file...")
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Make sure you have a .env file with all required credentials")
        sys.exit(1)

    # Verify required configuration
    required_keys = [
        "MILVUS_URI",
        "MILVUS_TOKEN",
        "MILVUS_COLLECTION_NAME",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
        "GITHUB_TOKEN"
    ]

    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logger.error(f"Missing required configuration keys: {', '.join(missing_keys)}")
        logger.error("Please add these to your .env file")
        sys.exit(1)

    logger.info(f"✓ Configuration loaded successfully")
    logger.info(f"  - Milvus Collection: {config['MILVUS_COLLECTION_NAME']}")
    logger.info(f"  - Azure OpenAI Endpoint: {config['AZURE_OPENAI_ENDPOINT']}")
    logger.info(f"  - Azure Deployment: {config['AZURE_OPENAI_DEPLOYMENT']}")
    logger.info(f"  - GitHub Token: {'✓ Configured' if config.get('GITHUB_TOKEN') else '✗ Not configured'}")

    # Initialize services
    logger.info("\nInitializing services...")

    try:
        # Initialize Vector Client (Milvus)
        vector_client = VectorClient(
            uri=config["MILVUS_URI"],
            token=config["MILVUS_TOKEN"],
            collection_name=config["MILVUS_COLLECTION_NAME"],
            dimension=config.get("MILVUS_DIMENSION", 1536),
            metric=config.get("MILVUS_METRIC", "COSINE")
        )
        logger.info("✓ Milvus client initialized")

        # Initialize LLM Service (Azure OpenAI)
        llm_service = LLMService(
            endpoint=config["AZURE_OPENAI_ENDPOINT"],
            api_key=config["AZURE_OPENAI_KEY"],
            deployment=config["AZURE_OPENAI_DEPLOYMENT"],
            api_version=config.get("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview",
        )

        # Set embeddings deployment if provided
        if config.get("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"):
            llm_service.set_embeddings_deployment(config["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"])

        logger.info("✓ Azure OpenAI service initialized")

        # Initialize GitHub Service
        github_service = GitHubService(token=config.get("GITHUB_TOKEN"))
        logger.info("✓ GitHub service initialized")

        # Initialize Ingestion Service
        ingestion_service = IngestionService(
            github_service=github_service,
            llm_service=llm_service,
            vector_client=vector_client,
            image_service=None  # We're only ingesting markdown files
        )
        logger.info("✓ Ingestion service initialized")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        sys.exit(1)

    # Test Milvus connection
    logger.info("\nTesting Milvus connection...")
    if vector_client.test_connection():
        logger.info("✓ Milvus connection successful")
    else:
        logger.error("✗ Milvus connection failed")
        sys.exit(1)

    # Start ingestion
    logger.info("\n" + "=" * 80)
    logger.info("Starting bulk ingestion process...")
    logger.info("=" * 80)

    try:
        # Choose the ingestion method based on --all-files flag
        if args.all_files:
            logger.info("🚀 Using ALL FILES mode - will retrieve all text-based files")
            result = ingestion_service.ingest_org_repositories_all_files(
                org=args.org,
                keyword=args.keyword,
                max_repos=args.max_repos
            )
        else:
            logger.info("📄 Using default mode - will retrieve markdown and API files only")
            result = ingestion_service.ingest_org_repositories(
                org=args.org,
                keyword=args.keyword,
                max_repos=args.max_repos
            )

        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("INGESTION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Status: {result.get('status', 'unknown')}")
        logger.info(f"Organization: {result.get('organization', args.org)}")
        logger.info(f"Keyword filter: {result.get('keyword', args.keyword)}")
        logger.info(f"Repositories found: {result.get('repositories_found', 0)}")
        logger.info(f"Repositories processed: {result.get('repositories_processed', 0)}")
        logger.info(f"Repositories failed: {result.get('repositories_failed', 0)}")
        logger.info(f"Total files processed: {result.get('total_files_processed', 0)}")
        logger.info(f"Total files skipped: {result.get('total_files_skipped', 0)}")
        if result.get('total_files_dropped_memory', 0) > 0:
            logger.info(f"Total files dropped (memory): {result.get('total_files_dropped_memory', 0)}")
        logger.info(f"Total embeddings stored: {result.get('total_embeddings_stored', 0)}")

        # Display file type breakdown for --all-files mode
        if args.all_files and result.get('processed_by_type'):
            logger.info("\nFiles processed by type:")
            for ft, count in sorted(result.get('processed_by_type', {}).items()):
                logger.info(f"  📁 {ft}: {count}")

        logger.info("=" * 80)

        # Display details for each repository
        if result.get('details'):
            logger.info("\nPer-Repository Details:")
            logger.info("-" * 80)
            for detail in result['details']:
                repo_name = detail.get('repository', 'Unknown')
                status = detail.get('status', 'unknown')
                files = detail.get('files_processed', 0)
                skipped = detail.get('files_skipped', 0)
                dropped = detail.get('files_dropped_memory', 0)
                embeddings = detail.get('embeddings_stored', 0)

                if status == "completed":
                    status_line = f"✓ {repo_name}: {files} files, {embeddings} embeddings"
                    if skipped > 0:
                        status_line += f" (skipped: {skipped}"
                        if dropped > 0:
                            status_line += f", dropped: {dropped} due to memory"
                        status_line += ")"
                    logger.info(status_line)
                else:
                    error = detail.get('error', 'Unknown error')
                    logger.info(f"✗ {repo_name}: FAILED - {error}")
            logger.info("-" * 80)

        if result.get('status') == 'completed':
            logger.info("\n✓ Ingestion completed successfully!")
            return 0
        else:
            logger.warning(f"\n⚠️  Ingestion completed with status: {result.get('status')}")
            return 1

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Ingestion interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n\n✗ Ingestion failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
