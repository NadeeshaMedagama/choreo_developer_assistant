"""
Script to fetch all README files from filtered repositories in WSO2 organization.
This searches for repositories with the keyword "choreo" and fetches their README files.
"""
import os
import sys
import json
import requests
import base64
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


class SimpleLogger:
    """Simple logger for console output."""
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
API_CALL_DELAY = 0.1


class GitHubService:
    """Service for interacting with GitHub API."""

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
                return None

        except Exception as e:
            return None


def save_readme_to_file(readme_data: dict, repo_name: str, output_dir: str):
    """Save README content to a file."""
    os.makedirs(output_dir, exist_ok=True)

    readme_filename = f"{repo_name}_README.md"
    readme_path = os.path.join(output_dir, readme_filename)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_data['content'])

    return readme_path


def save_metadata(repositories: list, readmes: dict, output_dir: str):
    """Save metadata about repositories and their READMEs."""
    metadata = {
        "fetch_date": datetime.now().isoformat(),
        "total_repositories": len(repositories),
        "total_readmes_fetched": len(readmes),
        "repositories": []
    }

    for repo in repositories:
        repo_info = {
            "name": repo['name'],
            "full_name": repo['full_name'],
            "description": repo['description'],
            "url": repo['url'],
            "stars": repo['stars'],
            "forks": repo['forks'],
            "language": repo['language'],
            "has_readme": repo['name'] in readmes
        }

        if repo['name'] in readmes:
            repo_info['readme_size'] = readmes[repo['name']]['size']
            repo_info['readme_path'] = readmes[repo['name']]['local_path']

        metadata['repositories'].append(repo_info)

    metadata_path = os.path.join(output_dir, 'repositories_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    return metadata_path


def main():
    """Fetch all README files from WSO2 Choreo repositories."""

    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
    except ImportError:
        pass

    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("\n⚠️  WARNING: No GitHub token found. Using unauthenticated requests.")
        print("Rate limits will be restricted to 60 requests/hour.\n")

    # Initialize GitHub service
    github_service = GitHubService(token=github_token)

    # Search parameters
    organization = "wso2"
    keyword = "choreo"

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"choreo_readmes_{timestamp}"

    print("=" * 80)
    print(f"🔍 Fetching README files from WSO2 Choreo repositories")
    print("=" * 80)
    print(f"Organization: {organization}")
    print(f"Keyword: {keyword}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)
    print()

    try:
        # Step 1: Search for repositories
        print("📦 Step 1: Searching for repositories...")
        repositories = github_service.search_org_repositories(org=organization, keyword=keyword)

        if not repositories:
            print(f"❌ No repositories found matching keyword '{keyword}'")
            return

        print(f"✅ Found {len(repositories)} repositories\n")

        # Step 2: Fetch README files
        print("📖 Step 2: Fetching README files...")
        print("─" * 80)

        readmes = {}
        successful = 0
        failed = 0

        for i, repo in enumerate(repositories, 1):
            repo_name = repo['name']
            repo_owner = repo['owner']

            print(f"\n[{i}/{len(repositories)}] Fetching README for: {repo_name}")

            try:
                readme = github_service.get_readme_content(repo_owner, repo_name)

                if readme:
                    # Save README to file
                    local_path = save_readme_to_file(readme, repo_name, output_dir)

                    readmes[repo_name] = {
                        'content': readme['content'],
                        'size': readme['size'],
                        'url': readme['url'],
                        'local_path': local_path
                    }

                    print(f"   ✅ Saved: {local_path}")
                    print(f"   📏 Size: {readme['size']} bytes")
                    successful += 1
                else:
                    print(f"   ⚠️  No README found")
                    failed += 1

            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
                continue

        print("\n" + "─" * 80)

        # Step 3: Save metadata
        print("\n📊 Step 3: Saving metadata...")
        metadata_path = save_metadata(repositories, readmes, output_dir)
        print(f"✅ Metadata saved to: {metadata_path}")

        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total repositories found: {len(repositories)}")
        print(f"READMEs successfully fetched: {successful}")
        print(f"READMEs not found/failed: {failed}")
        print(f"Success rate: {(successful/len(repositories)*100):.1f}%")
        print(f"\nAll files saved in: {output_dir}/")
        print("=" * 80)

        # List all saved files
        print("\n📁 Files saved:")
        print("─" * 80)

        for filename in sorted(os.listdir(output_dir)):
            filepath = os.path.join(output_dir, filename)
            file_size = os.path.getsize(filepath)
            print(f"   • {filename} ({file_size:,} bytes)")

        print("\n✅ Process completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

