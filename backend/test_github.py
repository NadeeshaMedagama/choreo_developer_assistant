"""
Test script to verify GitHub API connection and list .md files.

This script tests the GitHub service without performing the full ingestion.
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

    # Also try loading from parent directory
    parent_env = backend_path.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env, override=False)
except ImportError:
    pass

from services.github_service import GitHubService
from utils.logger import get_logger

logger = get_logger(__name__)


def test_github_connection():
    """Test GitHub API connection."""

    REPO_OWNER = "NadeeshaMedagama"
    REPO_NAME = "docs-choreo-dev"

    logger.info("=" * 60)
    logger.info("Testing GitHub API Connection")
    logger.info("=" * 60)

    # Get token from environment (optional)
    github_token = os.getenv("GITHUB_TOKEN")

    if github_token:
        logger.info("✓ Using GitHub token (authenticated)")
    else:
        logger.info("⚠ No GitHub token found (rate limited to 60 requests/hour)")

    # Initialize GitHub service
    github_service = GitHubService(token=github_token)

    try:
        # Test: List all markdown files
        logger.info(f"\nSearching for .md files in {REPO_OWNER}/{REPO_NAME}...")
        md_files = github_service.find_all_markdown_files(REPO_OWNER, REPO_NAME)

        logger.info(f"\n✓ Found {len(md_files)} markdown files:")
        logger.info("-" * 60)

        for i, file_info in enumerate(md_files, 1):
            logger.info(f"{i}. {file_info['path']}")

        # Test: Fetch content from first file
        if md_files:
            logger.info("\n" + "=" * 60)
            logger.info("Testing Content Fetch")
            logger.info("=" * 60)

            first_file = md_files[0]
            logger.info(f"Fetching content from: {first_file['path']}")

            content = github_service.get_file_content(
                REPO_OWNER,
                REPO_NAME,
                first_file['path']
            )

            logger.info(f"✓ Successfully fetched content")
            logger.info(f"Content length: {len(content)} characters")
            logger.info(f"First 200 characters:\n{content[:200]}...")

        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests passed!")
        logger.info("=" * 60)
        logger.info("\nYou can now run the full ingestion with:")
        logger.info("  python run_ingestion.py")

    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    test_github_connection()
