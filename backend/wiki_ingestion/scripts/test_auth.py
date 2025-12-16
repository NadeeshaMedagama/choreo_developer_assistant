"""
Test GitHub authentication and check if Choreo wiki exists.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from wiki_ingestion.services import UrlFetcherService


def test_github_auth():
    """Test GitHub authentication with the token from .env"""
    
    print("="*80)
    print("🔐 TESTING GITHUB AUTHENTICATION")
    print("="*80)
    print()
    
    # Load token
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ ERROR: GITHUB_TOKEN not found in environment")
        print("   Make sure .env file exists in backend/ directory")
        return False
    
    print(f"✅ GitHub token loaded: {github_token[:8]}...{github_token[-4:]}")
    print()
    
    # Initialize fetcher with auth
    fetcher = UrlFetcherService(timeout=10, github_token=github_token)
    
    print("="*80)
    print("🧪 TEST 1: Public Repository (should work)")
    print("="*80)
    url = "https://github.com/wso2/docs-apim"
    print(f"Testing: {url}")
    html = fetcher.fetch(url)
    if html:
        print(f"✅ SUCCESS - Fetched {len(html)} characters")
    else:
        print(f"❌ FAILED")
    print()
    
    print("="*80)
    print("🧪 TEST 2: Private Choreo Repository")
    print("="*80)
    url = "https://github.com/wso2-enterprise/choreo"
    print(f"Testing: {url}")
    html = fetcher.fetch(url)
    if html:
        print(f"✅ SUCCESS - Fetched {len(html)} characters")
        print(f"   Repository is accessible with your token!")
    else:
        print(f"❌ FAILED - Repository not accessible")
        print(f"   Possible reasons:")
        print(f"   1. Token doesn't have access to this repository")
        print(f"   2. Repository doesn't exist")
        print(f"   3. Token has expired or is invalid")
    print()
    
    print("="*80)
    print("🧪 TEST 3: Choreo Wiki (if it exists)")
    print("="*80)
    
    test_urls = [
        "https://github.com/wso2-enterprise/choreo/wiki",
        "https://github.com/wso2-enterprise/choreo/wiki/Home",
        "https://api.github.com/repos/wso2-enterprise/choreo",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        html = fetcher.fetch(url)
        if html:
            print(f"✅ SUCCESS - {len(html)} characters")
            if 'wiki' in html.lower():
                print(f"   📚 Contains wiki content!")
            return url
        else:
            print(f"❌ Failed")
    
    print()
    print("="*80)
    print("❓ WIKI NOT FOUND")
    print("="*80)
    print()
    print("The Choreo repository might not have a wiki enabled.")
    print()
    print("To check manually:")
    print("1. Visit: https://github.com/wso2-enterprise/choreo")
    print("2. Look for a 'Wiki' tab")
    print("3. If no Wiki tab exists, the repository has no wiki")
    print()
    print("Alternative: Check if documentation is in the repository itself")
    print("Try: https://github.com/wso2-enterprise/choreo/tree/main/docs")
    print()
    
    return None


if __name__ == "__main__":
    print()
    test_github_auth()
    print()

