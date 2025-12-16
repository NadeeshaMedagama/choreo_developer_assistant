"""
Test script for searching GitHub repositories under an organization with keywords.
This demonstrates the new functionality to find repositories in the WSO2 organization
that match the keyword "choreo".
"""
import os
import sys
import requests
import base64
import time
from typing import List, Dict, Any, Optional

# Simple logger for this script
class SimpleLogger:
    @staticmethod
    def info(msg):
        print(f"ℹ️  {msg}")

    @staticmethod
    def warning(msg):
        print(f"⚠️  {msg}")

    @staticmethod
    def error(msg):
        print(f"❌ {msg}")

logger = SimpleLogger()

# GitHub API constants
API_CALL_DELAY = 0.1


class GitHubOrgSearcher:
    """Simple GitHub organization searcher."""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """Make a GET request to GitHub API."""
        try:
            time.sleep(API_CALL_DELAY)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise

    def search_org_repositories(self, org: str, keyword: str = "", per_page: int = 100) -> List[Dict[str, Any]]:
        """Search for public repositories under an organization."""
        logger.info(f"Searching repositories in organization '{org}' with keyword '{keyword}'")

        repositories = []
        page = 1

        while True:
            url = f"{self.base_url}/orgs/{org}/repos?type=public&per_page={per_page}&page={page}"

            try:
                logger.info(f"Fetching page {page} of repositories...")
                repos_data = self._make_request(url)

                if not repos_data or len(repos_data) == 0:
                    break

                for repo in repos_data:
                    repo_name = repo.get("name", "").lower()
                    repo_desc = repo.get("description", "") or ""
                    repo_desc_lower = repo_desc.lower()

                    if keyword:
                        keyword_lower = keyword.lower()
                        if keyword_lower not in repo_name and keyword_lower not in repo_desc_lower:
                            continue

                    repositories.append({
                        "name": repo.get("name", ""),
                        "full_name": repo.get("full_name", ""),
                        "description": repo_desc,
                        "url": repo.get("html_url", ""),
                        "api_url": repo.get("url", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "default_branch": repo.get("default_branch", "main"),
                        "is_private": repo.get("private", False),
                        "owner": repo.get("owner", {}).get("login", "")
                    })

                if len(repos_data) < per_page:
                    break

                page += 1

            except Exception as e:
                logger.error(f"Error fetching repositories: {e}")
                break

        logger.info(f"Found {len(repositories)} repositories matching criteria")
        return repositories

    def get_readme_content(self, owner: str, repo: str) -> Optional[Dict[str, str]]:
        """Get the README file content from a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"

        try:
            logger.info(f"Fetching README for {owner}/{repo}")
            data = self._make_request(url)

            if data and "content" in data:
                content = base64.b64decode(data["content"]).decode("utf-8")

                return {
                    "name": data.get("name", "README.md"),
                    "path": data.get("path", ""),
                    "content": content,
                    "size": data.get("size", 0),
                    "sha": data.get("sha", ""),
                    "url": data.get("html_url", "")
                }
            else:
                logger.warning(f"No README found for {owner}/{repo}")
                return None

        except Exception as e:
            logger.warning(f"Could not fetch README for {owner}/{repo}: {e}")
            return None


def main():
    """Search for repositories under WSO2 organization with keyword 'choreo'."""

    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
    except ImportError:
        pass

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("\n⚠️  WARNING: No GitHub token found. Rate limits will be restricted to 60 requests/hour.")
        print("To avoid this, add GITHUB_TOKEN to your backend/.env file.\n")
    else:
        logger.info("Using GitHub token for authentication")

    # Initialize GitHub searcher
    searcher = GitHubOrgSearcher(token=github_token)

    # Search parameters
    organization = "wso2"
    keyword = "choreo"

    print("=" * 80)
    print(f"🔍 Searching for repositories in organization: {organization}")
    print(f"🔑 Keyword filter: {keyword}")
    print("=" * 80)
    print()

    try:
        # Search for repositories
        repositories = searcher.search_org_repositories(org=organization, keyword=keyword)

        # Display results
        if not repositories:
            print(f"❌ No repositories found matching keyword '{keyword}' in organization '{organization}'")
            return

        print(f"✅ Found {len(repositories)} repositories matching '{keyword}':\n")

        # Display each repository
        for i, repo in enumerate(repositories, 1):
            print(f"\n{'─' * 80}")
            print(f"📦 Repository #{i}: {repo['name']}")
            print(f"{'─' * 80}")
            print(f"   Full Name:    {repo['full_name']}")
            print(f"   URL:          {repo['url']}")
            print(f"   Description:  {repo['description'] or 'No description'}")
            print(f"   Language:     {repo['language'] or 'N/A'}")
            print(f"   ⭐ Stars:      {repo['stars']}")
            print(f"   🍴 Forks:      {repo['forks']}")
            print(f"   📅 Created:    {repo['created_at']}")
            print(f"   📅 Updated:    {repo['updated_at']}")
            print(f"   🌿 Branch:     {repo['default_branch']}")

        print(f"\n{'=' * 80}")
        print(f"📊 Summary: Found {len(repositories)} repositories")
        print("=" * 80)

        # Show README for first 3 repositories as a sample
        print("\n" + "=" * 80)
        print("📖 README Preview")
        print("=" * 80)

        max_readme_preview = min(3, len(repositories))
        print(f"\nShowing README preview for first {max_readme_preview} repositories...\n")

        for i, repo in enumerate(repositories[:max_readme_preview], 1):
            repo_owner = repo['owner']
            repo_name = repo['name']

            print(f"\n{'─' * 80}")
            print(f"📖 README for: {repo_name}")
            print(f"{'─' * 80}")

            readme = searcher.get_readme_content(repo_owner, repo_name)

            if readme:
                content_preview = readme['content'][:500]  # First 500 characters
                print(f"\n{content_preview}...")
                print(f"\n[README size: {readme['size']} bytes]")
                print(f"[Full README URL: {readme['url']}]")
            else:
                print("❌ No README found for this repository")

        print(f"\n{'=' * 80}")
        print("✅ Search completed successfully!")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error during repository search: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

