#!/usr/bin/env python3
"""
Test script to validate which Choreo repository URLs actually exist on GitHub.
"""

import asyncio
import aiohttp
from services.url_validator import get_url_validator
from services.choreo_repo_registry import get_choreo_registry

async def test_github_urls():
    """Test which GitHub URLs actually exist."""
    print("=" * 80)
    print("TESTING GITHUB REPOSITORY EXISTENCE")
    print("=" * 80)

    # Get the registry and validator
    registry = get_choreo_registry()
    validator = get_url_validator(enable_validation=True, timeout=10)

    # Get all components
    components = registry.get_all_components()

    # Test URLs that the user mentioned as problematic
    test_urls = [
        "https://github.com/wso2-enterprise/choreo-ai-capacity-planner",
        "https://github.com/wso2-enterprise/choreo-ai-data-mapper",
        "https://github.com/wso2-enterprise/choreo-ai-data-mapper-vscode-plugin",
        "https://github.com/wso2-enterprise/choreo-ai-deployment-optimizer",
        "https://github.com/wso2-enterprise/choreo-ai-performance-analyzer",
        "https://github.com/wso2-enterprise/choreo-ai-program-analyzer",
        "https://github.com/wso2-enterprise/choreo-linker",
        "https://github.com/wso2-enterprise/choreo-deployment",
        "https://github.com/wso2-enterprise/choreo-observability",
    ]

    print("\n1. Testing user-reported problematic URLs:")
    print("-" * 80)

    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            is_valid = await validator.validate_github_repo(url, session)
            status = "✓ EXISTS" if is_valid else "✗ NOT FOUND"
            print(f"{status}: {url}")

    print("\n2. Testing ALL 32 Choreo component URLs:")
    print("-" * 80)

    all_urls = [comp['url'] for comp in components]

    async with aiohttp.ClientSession() as session:
        validation_results = {}
        for url in all_urls:
            is_valid = await validator.validate_github_repo(url, session)
            validation_results[url] = is_valid

    # Separate into valid and invalid
    valid_repos = [url for url, valid in validation_results.items() if valid]
    invalid_repos = [url for url, valid in validation_results.items() if not valid]

    print(f"\n✓ VALID REPOSITORIES ({len(valid_repos)}):")
    for url in sorted(valid_repos):
        print(f"  {url}")

    print(f"\n✗ INVALID/NOT FOUND REPOSITORIES ({len(invalid_repos)}):")
    for url in sorted(invalid_repos):
        print(f"  {url}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total components in registry: {len(components)}")
    print(f"Valid repositories: {len(valid_repos)}")
    print(f"Invalid/Not found: {len(invalid_repos)}")
    print(f"Success rate: {len(valid_repos)/len(components)*100:.1f}%")

    if invalid_repos:
        print("\n⚠️  WARNING: Some repository URLs in the registry don't exist!")
        print("   These should be removed from choreo_repo_registry.py")

if __name__ == "__main__":
    asyncio.run(test_github_urls())
