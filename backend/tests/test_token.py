#!/usr/bin/env python
"""Test GitHub token authentication"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

token = os.getenv('GITHUB_TOKEN')

if not token:
    print("❌ No GITHUB_TOKEN found in backend/.env")
    exit(1)

print(f"✓ Token found (length: {len(token)})")
print(f"  Token starts with: {token[:7]}...")

# Test with curl equivalent
import requests

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}

print("\n🔍 Testing authentication with token...")

try:
    response = requests.get("https://api.github.com/user", headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Authenticated as: {data.get('login', 'Unknown')}")

        # Check rate limit
        rate_response = requests.get("https://api.github.com/rate_limit", headers=headers)
        if rate_response.status_code == 200:
            rate_data = rate_response.json()
            core = rate_data.get('resources', {}).get('core', {})
            print(f"\n📊 Rate Limit Status:")
            print(f"   Limit: {core.get('limit', 'Unknown')}")
            print(f"   Remaining: {core.get('remaining', 'Unknown')}")
            print(f"   Reset: {core.get('reset', 'Unknown')}")

            if core.get('remaining', 0) == 0:
                from datetime import datetime
                reset_time = datetime.fromtimestamp(core.get('reset', 0))
                print(f"   ⚠️  Rate limit exhausted! Resets at: {reset_time}")
            else:
                print(f"   ✓ You have {core.get('remaining')} requests remaining")

    elif response.status_code == 401:
        print("❌ Authentication failed - Invalid token")
        print("   Your token may be expired or incorrect")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(f"   {response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("Now testing repository access...")
print("="*60)

try:
    repo_response = requests.get(
        "https://api.github.com/repos/NadeeshaMedagama/docs-choreo-dev",
        headers=headers
    )

    print(f"Repository Status: {repo_response.status_code}")

    if repo_response.status_code == 200:
        print("✓ Repository accessible!")
    elif repo_response.status_code == 404:
        print("❌ Repository not found - Check the URL")
    elif repo_response.status_code == 403:
        print("❌ Forbidden - Rate limit or permissions issue")

except Exception as e:
    print(f"❌ Error accessing repository: {e}")

