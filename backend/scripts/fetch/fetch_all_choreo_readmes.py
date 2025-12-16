"""
Script to fetch all README files from filtered repositories in WSO2 organization.
This searches for repositories with the keyword "choreo" and fetches their README files.
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.github_service import GitHubService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def save_readme_to_file(readme_data: dict, repo_name: str, output_dir: str):
    """Save README content to a file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save README content
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

    # Save metadata as JSON
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
            logger.info(f"Loaded environment from {env_path}")
    except ImportError:
        pass

    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("\n⚠️  WARNING: No GitHub token found. Using unauthenticated requests.")
        print("Rate limits will be restricted to 60 requests/hour.\n")
    else:
        logger.info("Using GitHub token for authentication")

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
        logger.error(f"Error during process: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

