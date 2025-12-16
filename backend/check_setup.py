"""
Quick start script with step-by-step guidance.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from utils.logger import get_logger

logger = get_logger(__name__)


def check_environment():
    """Check if all required environment variables are set."""

    logger.info("=" * 60)
    logger.info("Environment Configuration Check")
    logger.info("=" * 60)

    required = {
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY")
    }

    optional = {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "PINECONE_INDEX_NAME": os.getenv("PINECONE_INDEX_NAME", "choreo-docs"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    }

    # Check required
    all_good = True
    logger.info("\nRequired Variables:")
    for key, value in required.items():
        if value:
            logger.info(f"  ✓ {key}: {'*' * 10} (set)")
        else:
            logger.error(f"  ✗ {key}: NOT SET")
            all_good = False

    # Check optional
    logger.info("\nOptional Variables:")
    for key, value in optional.items():
        if value and key in ["GITHUB_TOKEN", "OPENAI_API_KEY"]:
            logger.info(f"  ✓ {key}: {'*' * 10} (set)")
        elif value:
            logger.info(f"  ✓ {key}: {value}")
        else:
            logger.info(f"  ⚠ {key}: Not set (using default)")

    logger.info("\n" + "=" * 60)

    if not all_good:
        logger.error("\n❌ Missing required environment variables!")
        logger.info("\nPlease follow these steps:")
        logger.info("1. Copy the example environment file:")
        logger.info("   cp .env.example .env")
        logger.info("\n2. Edit .env and add your Pinecone API key:")
        logger.info("   PINECONE_API_KEY=your_key_here")
        logger.info("\n3. (Optional) Add GitHub token for higher rate limits:")
        logger.info("   GITHUB_TOKEN=your_token_here")
        logger.info("\n4. Load environment variables:")
        logger.info("   source .env  # or use python-dotenv")
        return False

    logger.info("✅ All required variables are set!")
    logger.info("\nNext steps:")
    logger.info("1. Test GitHub connection:")
    logger.info("   python backend/tests/test_github.py")
    logger.info("\n2. Run full ingestion:")
    logger.info("   python run_ingestion.py")

    return True


if __name__ == "__main__":
    # Try to load .env file
    try:
        from dotenv import load_dotenv

        # Try loading from backend/.env first
        backend_env = Path(__file__).parent / ".env"
        if backend_env.exists():
            load_dotenv(backend_env)
            logger.info(f"Loaded environment from: {backend_env}")

        # Also try loading from parent directory
        parent_env = Path(__file__).parent.parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env, override=False)
            logger.info(f"Loaded environment from: {parent_env}")

        if not backend_env.exists() and not parent_env.exists():
            logger.warning("No .env file found in backend/ or parent directory")
    except ImportError:
        logger.warning("python-dotenv not installed. Set environment variables manually.")

    check_environment()
