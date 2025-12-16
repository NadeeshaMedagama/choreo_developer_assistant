"""
Test script for searching GitHub repositories under an organization with keywords.
This demonstrates the new functionality to find repositories in the WSO2 organization
that match the keyword "choreo".
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.github_service import GitHubService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Search for repositories under WSO2 organization with keyword 'choreo'."""
    
    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        # Look for .env in backend directory
        env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
        load_dotenv(env_path)
    except ImportError:
        logger.warning("python-dotenv not installed, reading from environment directly")
    
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        logger.warning("⚠️  No GITHUB_TOKEN found in environment. Using unauthenticated requests (lower rate limits).")
        print("\n⚠️  WARNING: No GitHub token found. Rate limits will be restricted to 60 requests/hour.")
        print("To avoid this, add GITHUB_TOKEN to your backend/.env file.\n")
    
    # Initialize GitHub service
    github_service = GitHubService(token=github_token)
    
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
        repositories = github_service.search_org_repositories(org=organization, keyword=keyword)
        
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
        
        # Optional: Ask if user wants to see README for any repo
        print("\n" + "=" * 80)
        print("📖 README Preview")
        print("=" * 80)
        
        # Show README for first 3 repositories as a sample
        max_readme_preview = min(3, len(repositories))
        print(f"\nShowing README preview for first {max_readme_preview} repositories...\n")
        
        for i, repo in enumerate(repositories[:max_readme_preview], 1):
            repo_owner = repo['owner']
            repo_name = repo['name']
            
            print(f"\n{'─' * 80}")
            print(f"📖 README for: {repo_name}")
            print(f"{'─' * 80}")
            
            readme = github_service.get_readme_content(repo_owner, repo_name)
            
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
        logger.error(f"Error during repository search: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
