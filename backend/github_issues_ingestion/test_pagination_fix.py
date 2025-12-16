#!/usr/bin/env python3
"""
Test script to verify the pagination fix for GitHub API.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from github_issues_ingestion.services.github_issue_fetcher import GitHubIssueFetcher


def test_pagination_fix():
    """Test that pagination handles the 1000 item limit gracefully."""
    
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return False
    
    print("Initializing GitHubIssueFetcher...")
    fetcher = GitHubIssueFetcher(github_token)
    
    # Test with the problematic repository
    owner = "wso2-enterprise"
    repo = "choreo"
    
    print(f"\nTesting issue fetching from {owner}/{repo}...")
    print("This repository has >1000 issues, which previously caused a 422 error.")
    print("The fix should now handle this gracefully.\n")
    
    try:
        # Fetch issues (should stop at 1000 without crashing)
        issues = fetcher.fetch_issues(
            owner=owner,
            repo=repo,
            state="all",
            max_issues=None  # No limit - will test pagination handling
        )
        
        print(f"\n✓ Success! Fetched {len(issues)} issues without errors.")
        print(f"  - The fetcher correctly handled GitHub's pagination limits")
        
        if len(issues) >= 1000:
            print(f"  - Reached the maximum fetchable issues (1000)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pagination_fix()
    sys.exit(0 if success else 1)

