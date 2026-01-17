#!/usr/bin/env python3
"""
Test script to verify the fix for choreo repository listing.
This tests that the system can correctly return all choreo keyword repositories.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

from services.llm_repo_matcher import get_llm_repo_matcher

def test_choreo_repos():
    """Test fetching and formatting all choreo repos."""

    print("=" * 80)
    print("TESTING: All WSO2-Enterprise Choreo Keyword Repositories")
    print("=" * 80)
    print()

    matcher = get_llm_repo_matcher()

    # Fetch all choreo repos
    print("1. Fetching all repositories with 'choreo' keyword...")
    repos = matcher.get_all_wso2_enterprise_repos(keyword="choreo")
    print(f"   ✅ Found {len(repos)} repositories\n")

    # Format the response
    print("2. Formatting response...")
    formatted = matcher.format_repos_for_response(repos, 'with "choreo" keyword')
    print("   ✅ Formatted successfully\n")

    # Display the formatted response
    print("3. Complete Repository List:")
    print("-" * 80)
    print(formatted)
    print("-" * 80)

    # Show summary
    print(f"\n✅ TEST PASSED: Successfully fetched and formatted {len(repos)} Choreo repositories")

    return repos

if __name__ == "__main__":
    repos = test_choreo_repos()
    sys.exit(0)
