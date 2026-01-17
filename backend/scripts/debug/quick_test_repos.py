import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path (2 levels up: scripts/debug -> backend)
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

load_dotenv()

from services.github_service import GitHubService

github_token = os.getenv('GITHUB_TOKEN')
print(f"Token found: {bool(github_token)}")

if github_token:
    service = GitHubService(token=github_token)
    print("Fetching repos from wso2-enterprise...")
    repos = service.search_org_repositories(org="wso2-enterprise", keyword="", per_page=100)
    print(f"Total repos found: {len(repos)}")
    
    # Show first 5
    print("\nFirst 5 repos:")
    for i, repo in enumerate(repos[:5], 1):
        print(f"  {i}. {repo['name']}: {repo['url']}")
    
    # Count choreo repos
    choreo_count = sum(1 for r in repos if 'choreo' in r['name'].lower())
    print(f"\nChoreo repos: {choreo_count}")
    print(f"Other repos: {len(repos) - choreo_count}")
    print(f"Total: {len(repos)}")
