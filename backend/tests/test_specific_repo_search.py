"""Test specific repository search functionality."""

import os
from dotenv import load_dotenv
load_dotenv()

from services.llm_repo_matcher import get_llm_repo_matcher

def test_specific_repo_search():
    """Test searching for specific repositories."""
    
    matcher = get_llm_repo_matcher()
    
    test_queries = [
        "project manager",
        "product management",
        "security token service",
        "sts",
        "choreo console",
        "telemetry",
        "observability api",
        "performance analyzer",
    ]
    
    print("=" * 80)
    print("SPECIFIC REPOSITORY SEARCH TEST")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 80)
        
        repo = matcher.find_repository_by_name(query)
        
        if repo:
            print(f"✅ FOUND: {repo.get('name')}")
            print(f"   URL: {repo.get('url')}")
            print(f"   Description: {repo.get('description', 'N/A')[:80]}")
            print(f"   Relevance Score: {repo.get('relevance_score', 0):.2f}")
        else:
            print("❌ NOT FOUND")
    
    print("\n" + "=" * 80)
    print("Testing formatted response...")
    print("=" * 80)
    
    # Test formatted response for project manager
    repo = matcher.find_repository_by_name("project manager")
    if repo:
        formatted = matcher.format_single_repo_response(repo, "project manager")
        print(formatted)

if __name__ == "__main__":
    test_specific_repo_search()
