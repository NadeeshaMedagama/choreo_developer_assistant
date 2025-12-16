#!/usr/bin/env python3
"""
Debug script to check GitHub API access and repository visibility.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.github_service import GitHubService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def test_direct_api_access(token, org):
    """Test direct API access to organization."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }

    print(f"\n{'=' * 80}")
    print(f"Direct API Test for: {org}")
    print(f"{'=' * 80}")

    # Test 1: Organization info
    print("\n1. Testing organization access...")
    url = f"https://api.github.com/orgs/{org}"
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            org_data = response.json()
            print(f"   ✓ Organization: {org_data.get('login')}")
            print(f"   ✓ Name: {org_data.get('name', 'N/A')}")
            print(f"   ✓ Public repos: {org_data.get('public_repos', 0)}")
        elif response.status_code == 404:
            print(f"   ✗ Organization not found or no access")
        else:
            print(f"   ✗ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    # Test 2: List repositories with type=all
    print("\n2. Testing repository listing (type=all, per_page=100)...")
    url = f"https://api.github.com/orgs/{org}/repos?type=all&per_page=100&page=1"
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            repos = response.json()
            print(f"   ✓ Found {len(repos)} repositories on first page")

            # Check for private repos
            private_count = sum(1 for r in repos if r.get('private', False))
            public_count = len(repos) - private_count
            print(f"   ✓ Private: {private_count}, Public: {public_count}")

            # Show first 5 repos
            if repos:
                print("\n   First 5 repositories:")
                for i, repo in enumerate(repos[:5], 1):
                    visibility = "🔒 Private" if repo.get('private') else "🔓 Public"
                    print(f"   {i}. {repo['name']} - {visibility}")

        elif response.status_code == 404:
            print(f"   ✗ Not found - token may not have org access")
        elif response.status_code == 401:
            print(f"   ✗ Unauthorized - token invalid or not authorized for SSO")
        else:
            print(f"   ✗ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    # Test 3: Search with query parameter
    print("\n3. Testing repository search with 'choreo' keyword...")
    url = f"https://api.github.com/orgs/{org}/repos?type=all&per_page=100&page=1"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repos = response.json()
            # Filter by choreo keyword
            choreo_repos = [r for r in repos if 'choreo' in r['name'].lower() or
                          'choreo' in (r.get('description') or '').lower()]
            print(f"   ✓ Found {len(choreo_repos)} repositories matching 'choreo' on first page")

            if choreo_repos:
                print("\n   Choreo repositories (first 10):")
                for i, repo in enumerate(choreo_repos[:10], 1):
                    visibility = "🔒 Private" if repo.get('private') else "🔓 Public"
                    print(f"   {i}. {repo['name']} - {visibility}")
        else:
            print(f"   ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")


def main():
    """Test GitHub API access and repository visibility."""
    # Load environment variables
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from: {env_path}")
    else:
        print(f"✗ .env file not found at: {env_path}")
        return

    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("✗ GITHUB_TOKEN not found in .env file")
        return

    print(f"✓ GitHub token found: {github_token[:10]}...")
    print(f"✓ Token scopes in .env: admin:org, copilot, repo, user, workflow")

    # Test direct API access first
    test_direct_api_access(github_token, "wso2-enterprise")

    # Initialize GitHub service
    print(f"\n{'=' * 80}")
    print("Testing with GitHubService class...")
    print(f"{'=' * 80}")

    github_service = GitHubService(github_token)

    # Test organizations
    orgs_to_test = [
        ("wso2-enterprise", "choreo"),
        ("wso2-enterprise", ""),  # All repos
    ]

    for org, keyword in orgs_to_test:
        print(f"\n{'=' * 80}")
        print(f"Organization: {org}")
        print(f"Keyword: '{keyword}' (empty = all repos)")
        print(f"{'=' * 80}")

        try:
            repos = github_service.search_org_repositories(org, keyword)
            print(f"Found {len(repos)} repositories matching criteria")

            if repos:
                print("\nRepositories:")
                for i, repo in enumerate(repos[:10], 1):  # Show first 10
                    private = "🔒 Private" if repo.get("is_private", False) else "🔓 Public"
                    print(f"{i}. {repo['name']} - {private}")
                    if repo.get("description"):
                        print(f"   Description: {repo['description'][:100]}")

                if len(repos) > 10:
                    print(f"\n... and {len(repos) - 10} more repositories")
            else:
                print("No repositories found")

        except Exception as e:
            print(f"✗ Error accessing {org}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("TROUBLESHOOTING STEPS")
    print(f"{'=' * 80}")
    print("If you see 'Unauthorized' or 404 errors:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Find your token: 'wso2-enterprise-repo-ai-assistant'")
    print("3. Look for 'Configure SSO' button next to wso2-enterprise")
    print("4. Click 'Authorize' to grant SSO access")
    print("5. Re-run this script")
    print("\nIf no 'Configure SSO' button appears:")
    print("1. Delete the current token")
    print("2. Create a new token with same scopes")
    print("3. After creation, check for SSO authorization option")
    print("4. Update GITHUB_TOKEN in backend/.env file")


if __name__ == "__main__":
    main()
