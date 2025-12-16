"""
Search for Choreo documentation repositories.
"""

import os
import sys
from dotenv import load_dotenv
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def search_choreo_repos():
    """Search for Choreo-related repositories."""
    
    github_token = os.getenv('GITHUB_TOKEN')
    
    print("="*80)
    print("🔍 SEARCHING FOR CHOREO DOCUMENTATION")
    print("="*80)
    print()
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Search different organizations and patterns
    search_patterns = [
        "org:wso2 choreo",
        "org:wso2-enterprise choreo",
        "wso2 choreo docs",
        "wso2 choreo wiki",
    ]
    
    all_repos = []
    
    for pattern in search_patterns:
        print(f"🔍 Searching: {pattern}")
        
        try:
            response = requests.get(
                f"https://api.github.com/search/repositories?q={pattern}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = data.get('items', [])
                print(f"   Found {len(repos)} repositories")
                
                for repo in repos[:5]:  # Top 5
                    repo_info = {
                        'name': repo['full_name'],
                        'url': repo['html_url'],
                        'description': repo.get('description', 'No description'),
                        'has_wiki': repo.get('has_wiki', False),
                        'private': repo.get('private', False),
                    }
                    
                    if repo_info not in all_repos:
                        all_repos.append(repo_info)
                        print(f"   📦 {repo_info['name']}")
                        if repo_info['has_wiki']:
                            print(f"      ✅ Has Wiki!")
                        if repo_info['description']:
                            print(f"      📝 {repo_info['description'][:60]}...")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("="*80)
    print("📚 REPOSITORIES WITH WIKIS")
    print("="*80)
    print()
    
    wiki_repos = [r for r in all_repos if r['has_wiki']]
    
    if wiki_repos:
        for repo in wiki_repos:
            wiki_url = f"{repo['url']}/wiki"
            print(f"Repository: {repo['name']}")
            print(f"Wiki URL: {wiki_url}")
            print(f"Description: {repo['description']}")
            print(f"Private: {repo['private']}")
            print()
            print(f"Try this command:")
            print(f'export WIKI_URL="{wiki_url}"')
            print(f'python -m wiki_ingestion.main')
            print()
            print("-"*80)
            print()
    else:
        print("No repositories with wikis found.")
        print()
    
    print("="*80)
    print("💡 ALL CHOREO-RELATED REPOSITORIES")
    print("="*80)
    print()
    
    for repo in all_repos:
        print(f"• {repo['name']}")
        print(f"  URL: {repo['url']}")
        print(f"  Wiki: {'✅ Yes' if repo['has_wiki'] else '❌ No'}")
        print(f"  Private: {'🔒 Yes' if repo['private'] else '🌐 Public'}")
        if repo['description']:
            print(f"  {repo['description'][:80]}")
        print()


if __name__ == "__main__":
    print()
    search_choreo_repos()

