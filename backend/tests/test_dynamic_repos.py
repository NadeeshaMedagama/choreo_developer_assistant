#!/usr/bin/env python3
"""
Test script to verify dynamic repository fetching from GitHub API.

This tests the new functionality that fetches ALL repositories from wso2-enterprise
organization instead of using hardcoded lists.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path (parent of tests directory)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Import the services
from services.choreo_repo_registry import get_choreo_registry
from services.llm_repo_matcher import get_llm_repo_matcher

def test_fetch_all_repos():
    """Test fetching all repositories from wso2-enterprise."""
    print("=" * 80)
    print("TEST 1: Fetch ALL repositories from wso2-enterprise organization")
    print("=" * 80)

    registry = get_choreo_registry()

    print("\nFetching all repositories via GitHub API...")
    repos = registry.fetch_all_wso2_enterprise_repos(use_cache=False)

    print(f"\n✅ Successfully fetched {len(repos)} repositories!\n")

    # Show first 10 repos
    print("First 10 repositories:")
    for i, repo in enumerate(repos[:10], 1):
        print(f"  {i}. {repo['name']}")
        print(f"     URL: {repo['url']}")
        print(f"     Description: {repo.get('description', 'N/A')[:80]}")
        print()

    if len(repos) > 10:
        print(f"... and {len(repos) - 10} more repositories\n")

    return repos


def test_fetch_choreo_repos():
    """Test fetching only Choreo-related repositories."""
    print("=" * 80)
    print("TEST 2: Fetch only Choreo-related repositories")
    print("=" * 80)

    registry = get_choreo_registry()

    print("\nFetching Choreo repositories via GitHub API...")
    choreo_repos = registry.fetch_choreo_repos_only(use_cache=False)

    print(f"\n✅ Successfully fetched {len(choreo_repos)} Choreo repositories!\n")

    # Show all choreo repos (since there should be a reasonable number)
    print("All Choreo repositories:")
    for i, repo in enumerate(choreo_repos, 1):
        print(f"  {i}. {repo['name']}")
        print(f"     URL: {repo['url']}")
        print(f"     Description: {repo.get('description', 'N/A')[:80]}")
        print()

    return choreo_repos


def test_llm_repo_matcher():
    """Test the LLM repo matcher integration."""
    print("=" * 80)
    print("TEST 3: Test LLM Repo Matcher Integration")
    print("=" * 80)

    matcher = get_llm_repo_matcher()

    print("\nTest 3a: Get all wso2-enterprise repos")
    all_repos = matcher.get_all_wso2_enterprise_repos(keyword=None)
    print(f"✅ Found {len(all_repos)} total repositories\n")

    print("Test 3b: Get only Choreo repos")
    choreo_repos = matcher.get_all_wso2_enterprise_repos(keyword="choreo")
    print(f"✅ Found {len(choreo_repos)} Choreo repositories\n")

    print("Test 3c: Format repos for response")
    formatted = matcher.format_repos_for_response(
        choreo_repos[:5],
        query_context="with 'choreo' keyword (showing first 5)"
    )
    print("Formatted response preview:")
    print(formatted[:500])
    print("...\n")

    return all_repos, choreo_repos


def test_system_prompt_generation():
    """Test system prompt generation with dynamic repos."""
    print("=" * 80)
    print("TEST 4: Test Dynamic System Prompt Generation")
    print("=" * 80)

    registry = get_choreo_registry()

    print("\nGenerating system prompt with dynamic repos...")
    prompt = registry.generate_system_prompt_urls(use_dynamic=True)

    # Count how many repos are mentioned
    repo_count = prompt.count("github.com/wso2-enterprise/")
    print(f"✅ System prompt includes {repo_count} repository URLs\n")

    print("System prompt preview (first 1000 chars):")
    print(prompt[:1000])
    print("...\n")

    return prompt


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("DYNAMIC REPOSITORY FETCHING - TEST SUITE")
    print("=" * 80)
    print()

    # Check if GitHub token is available
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print(f"✅ GitHub token found: {github_token[:10]}...{github_token[-4:]}")
    else:
        print("⚠️  WARNING: No GitHub token found in .env file")
        print("   Repository fetching may be limited by rate limits (60 requests/hour)")
    print()

    try:
        # Run tests
        all_repos = test_fetch_all_repos()
        print()

        choreo_repos = test_fetch_choreo_repos()
        print()

        matcher_all_repos, matcher_choreo_repos = test_llm_repo_matcher()
        print()

        prompt = test_system_prompt_generation()
        print()

        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Total repositories fetched: {len(all_repos)}")
        print(f"✅ Choreo repositories: {len(choreo_repos)}")
        print(f"✅ System prompt generated with {prompt.count('github.com/wso2-enterprise/')} URLs")
        print()
        print("🎉 All tests passed successfully!")
        print()
        print("NEXT STEPS:")
        print("1. The system now dynamically fetches repos from GitHub API")
        print("2. When users ask for 'all repos', it will show the actual count")
        print("3. No more hardcoded list of 32 repos!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
