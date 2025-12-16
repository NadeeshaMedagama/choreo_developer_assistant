#!/usr/bin/env python3
"""
Debug script to test GitHub organization access and find repositories.
This will help diagnose why no repositories were found.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.github_service import GitHubService
from backend.utils.config import load_config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("GitHub Organization Access Debug Script")
    logger.info("=" * 80)

    # Load configuration
    try:
        config = load_config()
        logger.info("✓ Configuration loaded")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1

    # Initialize GitHub service
    github_token = config.get("GITHUB_TOKEN")
    if not github_token:
        logger.error("❌ GITHUB_TOKEN not found in .env file")
        return 1

    logger.info(f"✓ GitHub token found: {github_token[:10]}...")
    github_service = GitHubService(token=github_token)

    # Test 1: Try to fetch wso2-enterprise org repositories (all)
    logger.info("\n" + "=" * 80)
    logger.info("Test 1: Fetching ALL repositories from wso2-enterprise")
    logger.info("=" * 80)
    try:
        repos = github_service.search_org_repositories("wso2-enterprise", "")
        logger.info(f"✓ Found {len(repos)} total repositories in wso2-enterprise")

        if repos:
            logger.info("\nFirst 10 repositories:")
            for i, repo in enumerate(repos[:10], 1):
                logger.info(f"  {i}. {repo['name']} - {repo.get('description', 'No description')[:60]}")

        # Check for choreo in names
        choreo_repos = [r for r in repos if 'choreo' in r['name'].lower()]
        logger.info(f"\n✓ Found {len(choreo_repos)} repositories with 'choreo' in name:")
        for repo in choreo_repos:
            logger.info(f"  - {repo['name']}")

    except Exception as e:
        logger.error(f"❌ Failed to fetch wso2-enterprise repositories: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    # Test 2: Try with keyword filter
    logger.info("\n" + "=" * 80)
    logger.info("Test 2: Fetching with keyword 'choreo'")
    logger.info("=" * 80)
    try:
        repos = github_service.search_org_repositories("wso2-enterprise", "choreo")
        logger.info(f"✓ Found {len(repos)} repositories matching 'choreo'")
        for repo in repos:
            logger.info(f"  - {repo['name']} - {repo.get('description', 'N/A')}")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")

    # Test 3: Try fetching a known public repo to verify API access
    logger.info("\n" + "=" * 80)
    logger.info("Test 3: Testing API access with a known public org (wso2)")
    logger.info("=" * 80)
    try:
        repos = github_service.search_org_repositories("wso2", "")
        logger.info(f"✓ Found {len(repos)} repositories in wso2 organization")
        if repos:
            logger.info(f"  Sample repo: {repos[0]['name']}")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")

    # Test 4: Check if we can search for choreo in wso2 org
    logger.info("\n" + "=" * 80)
    logger.info("Test 4: Searching for 'choreo' in wso2 organization")
    logger.info("=" * 80)
    try:
        repos = github_service.search_org_repositories("wso2", "choreo")
        logger.info(f"✓ Found {len(repos)} repositories matching 'choreo' in wso2")
        for repo in repos:
            logger.info(f"  - {repo['full_name']} - {repo.get('description', 'N/A')[:60]}")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")

    logger.info("\n" + "=" * 80)
    logger.info("Debug complete!")
    logger.info("=" * 80)
    logger.info("\nRecommendations:")
    logger.info("1. If wso2-enterprise returned 0 repos, it might be a private org")
    logger.info("2. Check if your GitHub token has access to wso2-enterprise")
    logger.info("3. Consider using 'wso2' organization instead if that has choreo repos")
    logger.info("4. Or provide a specific list of repository URLs to ingest")

    return 0


if __name__ == "__main__":
    sys.exit(main())

