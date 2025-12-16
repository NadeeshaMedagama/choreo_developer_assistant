"""
Debug script to check wiki accessibility and find the correct URL.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiki_ingestion.services import UrlFetcherService


def test_wiki_urls():
    """Test different wiki URL formats to find the correct one."""

    print("="*80)
    print("🔍 WIKI URL DEBUGGER")
    print("="*80)
    print()

    fetcher = UrlFetcherService(timeout=10)

    # Different URL formats to try
    base_repo = "wso2-enterprise/choreo"

    test_urls = [
        f"https://github.com/{base_repo}/wiki",
        f"https://github.com/{base_repo}/wiki/Home",
        f"https://github.com/{base_repo}",
        f"https://github.com/{base_repo}.wiki.git",
    ]

    print(f"Testing URLs for repository: {base_repo}")
    print("-" * 80)
    print()

    for url in test_urls:
        print(f"🔍 Testing: {url}")
        html = fetcher.fetch(url, timeout=10)

        if html:
            print(f"   ✅ SUCCESS - Fetched {len(html)} characters")

            # Check if it looks like a wiki
            if 'wiki' in html.lower():
                print(f"   📚 Contains wiki content!")
                print(f"   ✨ TRY THIS URL: {url}")
                print()
                return url
            else:
                print(f"   ⚠️  Fetched but doesn't look like wiki content")
        else:
            print(f"   ❌ FAILED - Could not fetch")

        print()

    print("="*80)
    print("❓ WIKI NOT FOUND")
    print("="*80)
    print()
    print("Possible reasons:")
    print("1. ✗ The repository doesn't have a wiki enabled")
    print("2. ✗ The wiki is private (requires authentication)")
    print("3. ✗ The repository name/owner is incorrect")
    print()
    print("How to check:")
    print("1. Visit https://github.com/wso2-enterprise/choreo")
    print("2. Look for a 'Wiki' tab at the top")
    print("3. Click it to see if the wiki exists")
    print()
    print("If the wiki exists but is private, you'll need to:")
    print("- Add GitHub authentication to the UrlFetcherService")
    print("- Use a personal access token")
    print()

    return None


def check_repo_exists():
    """Check if the repository itself exists."""
    print("="*80)
    print("🔍 CHECKING REPOSITORY")
    print("="*80)
    print()

    fetcher = UrlFetcherService(timeout=10)
    repo_url = "https://github.com/wso2-enterprise/choreo"

    print(f"Testing: {repo_url}")
    html = fetcher.fetch(repo_url, timeout=10)

    if html:
        print(f"✅ Repository exists!")
        print(f"   Fetched {len(html)} characters")

        # Check for wiki tab
        if 'wiki' in html.lower():
            print(f"   📚 Wiki tab appears to be present")
        else:
            print(f"   ⚠️  No wiki tab found - wiki may be disabled")

        print()
        return True
    else:
        print(f"❌ Repository not found or not accessible")
        print()
        return False


if __name__ == "__main__":
    print()

    # First check if repo exists
    if check_repo_exists():
        # Then try to find wiki
        working_url = test_wiki_urls()

        if working_url:
            print()
            print("="*80)
            print("✅ WORKING URL FOUND!")
            print("="*80)
            print()
            print(f"Use this command:")
            print(f'export WIKI_URL="{working_url}"')
            print(f'python -m wiki_ingestion.main')
            print()
    else:
        print()
        print("="*80)
        print("❌ REPOSITORY NOT ACCESSIBLE")
        print("="*80)
        print()
        print("Suggestions:")
        print("1. Check the repository name is correct")
        print("2. Verify the repository is public")
        print("3. If private, add GitHub authentication")
        print()

    print()
    print("💡 Alternative: Try a public wiki for testing")
    print("-" * 80)
    print()
    print("Public wikis you can test with:")
    print("• https://github.com/microsoft/vscode/wiki")
    print("• https://github.com/facebook/react/wiki")
    print("• https://github.com/wso2/product-apim/wiki")
    print()
    print("Example:")
    print('export WIKI_URL="https://github.com/wso2/product-apim/wiki"')
    print('python -m wiki_ingestion.main')
    print()

