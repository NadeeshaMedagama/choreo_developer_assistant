"""
Test script to verify that specific repository searches work correctly
after the fix for dynamic repository searching.

This test demonstrates that the system can now:
1. Fetch ALL repositories from wso2-enterprise (413+ repos)
2. Find specific repositories using fuzzy matching and synonyms
3. Handle acronyms (e.g., STS = Security Token Service)
4. Return accurate results for user queries
"""

import sys
import os
from pathlib import Path

# Add backend directory to path (parent of tests directory)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# IMPORTANT: Load .env BEFORE importing anything else
from dotenv import load_dotenv
load_dotenv()

# Verify token is loaded
github_token = os.getenv('GITHUB_TOKEN')
if not github_token:
    print("WARNING: GITHUB_TOKEN not found in .env file")
    print("Test will be limited by GitHub API rate limits (60 requests/hour)")
    print()
else:
    print(f"✓ GitHub token loaded successfully")
    print()

from services.choreo_repo_registry import ChoreoRepoRegistry

def test_specific_repo_search():
    """Test specific repository searches."""

    print("=" * 80)
    print("TESTING SPECIFIC REPOSITORY SEARCH FIX")
    print("=" * 80)
    print()

    registry = ChoreoRepoRegistry()

    # Test cases from user's requirements
    test_cases = [
        {
            "query": "Choreo project manager",
            "expected_repo": "choreo-product-management",
            "description": "Should find Choreo product management repo"
        },
        {
            "query": "security token service",
            "expected_repo": "choreo-sts",
            "description": "Should find Choreo STS (acronym matching)"
        },
        {
            "query": "Choreo built-in Security Token Service",
            "expected_repo": "choreo-sts",
            "description": "Should find Choreo STS with full description"
        },
        {
            "query": "project manager",
            "expected_in_top_3": ["choreo-product-management", "apim-product-management"],
            "description": "Should find product management repos"
        }
    ]

    all_passed = True

    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        print(f"Test {i}: {test['description']}")
        print(f'  Query: "{query}"')

        # Search
        results = registry.search_components(query, use_dynamic=True)

        if not results:
            print(f'  ❌ FAILED: No results found')
            all_passed = False
            print()
            continue

        # Check expected repo (if specified)
        if "expected_repo" in test:
            expected = test["expected_repo"]
            found = results[0]["name"]

            if found == expected:
                print(f'  ✅ PASSED: Found "{found}" (score: {results[0].get("relevance_score", 0):.1f})')
                print(f'     URL: {results[0]["url"]}')
            else:
                print(f'  ❌ FAILED: Expected "{expected}", got "{found}"')
                print(f'     Top 3 results:')
                for j, r in enumerate(results[:3], 1):
                    print(f'       {j}. {r["name"]} (score: {r.get("relevance_score", 0):.1f})')
                all_passed = False

        # Check expected in top 3 (if specified)
        elif "expected_in_top_3" in test:
            expected_repos = test["expected_in_top_3"]
            top_3_names = [r["name"] for r in results[:3]]

            found_any = any(exp in top_3_names for exp in expected_repos)

            if found_any:
                print(f'  ✅ PASSED: Found expected repo in top 3')
                print(f'     Top 3:')
                for j, r in enumerate(results[:3], 1):
                    marker = "✓" if r["name"] in expected_repos else " "
                    print(f'     {marker} {j}. {r["name"]} (score: {r.get("relevance_score", 0):.1f})')
            else:
                print(f'  ❌ FAILED: Expected repos not in top 3')
                print(f'     Expected one of: {expected_repos}')
                print(f'     Got: {top_3_names}')
                all_passed = False

        print()

    # Test total repo count
    print("Test: Total repository count")
    all_repos = registry.fetch_all_wso2_enterprise_repos(use_cache=True)
    repo_count = len(all_repos)

    if repo_count > 150:  # Should be 400+ but at least > 150 (not hardcoded 32)
        print(f'  ✅ PASSED: Fetched {repo_count} repositories (dynamic, not hardcoded)')
    else:
        print(f'  ❌ FAILED: Only fetched {repo_count} repositories (expected 400+)')
        all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("✅ ALL TESTS PASSED - Specific repo search is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Review results above")

    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = test_specific_repo_search()
    sys.exit(0 if success else 1)
