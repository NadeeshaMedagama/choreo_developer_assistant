#!/usr/bin/env python3
"""Simple test of GitHub API repository fetching."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path (parent of tests directory)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from backend/.env
load_dotenv(backend_dir / '.env')

def test_github_api():
    """Test GitHub API directly."""
    from services.github_service import GitHubService

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"GitHub Token: {'Found' if github_token else 'Not Found'}")

    if not github_token:
        print("ERROR: No GitHub token in .env file")
        return

    print(f"Token preview: {github_token[:10]}...{github_token[-4:]}")
    print()

    github_service = GitHubService(token=github_token)

    print("Fetching repositories from wso2-enterprise...")
    repos = github_service.search_org_repositories(
        org="wso2-enterprise",
        keyword="",
        per_page=100
    )

    print(f"\n✅ Found {len(repos)} repositories\n")

    # Show first 10
    for i, repo in enumerate(repos[:10], 1):
        print(f"{i}. {repo['name']}")
        print(f"   URL: {repo['url']}")
        print()

    if len(repos) > 10:
        print(f"... and {len(repos) - 10} more")

    print(f"\nTotal: {len(repos)} repositories")

if __name__ == "__main__":
    test_github_api()
