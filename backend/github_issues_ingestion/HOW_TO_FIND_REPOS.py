"""
How to Find and Ingest Issues from a Particular Repository

This guide explains how to discover repositories and ingest their issues
into the vector database for semantic search.
"""

# ============================================================================
# METHOD 1: Direct Repository Ingestion (You know the repo)
# ============================================================================

from github_issues_ingestion import create_ingestion_pipeline

# Create the pipeline
orchestrator = create_ingestion_pipeline()

# Ingest issues from a specific repository
# Format: owner/repo
stats = orchestrator.ingest_repository(
    owner="wso2",           # Repository owner/organization
    repo="choreo",          # Repository name
    state="all",            # 'open', 'closed', or 'all'
    max_issues=100          # Limit number of issues (optional)
)

print(f"Ingested {stats['total_issues']} issues")
print(f"Created {stats['total_chunks']} chunks")
print(f"Generated {stats['total_embeddings']} embeddings")


# ============================================================================
# METHOD 2: Find Repositories Using GitHub API
# ============================================================================

import requests

def find_github_repos(query: str, token: str, max_results: int = 10):
    """
    Search for GitHub repositories matching a query.
    
    Args:
        query: Search query (e.g., "wso2 api language:python")
        token: GitHub token
        max_results: Maximum number of results
    
    Returns:
        List of repository dictionaries
    """
    url = "https://api.github.com/search/repositories"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    repos = []
    for item in response.json()["items"]:
        repos.append({
            "owner": item["owner"]["login"],
            "repo": item["name"],
            "full_name": item["full_name"],
            "description": item["description"],
            "stars": item["stargazers_count"],
            "issues_count": item["open_issues_count"],
            "url": item["html_url"]
        })
    
    return repos


# Example: Find WSO2 repositories
import os
github_token = os.getenv("GITHUB_TOKEN")

# Search for WSO2 repositories
repos = find_github_repos("org:wso2", github_token, max_results=10)

print("\nFound repositories:")
for i, repo in enumerate(repos, 1):
    print(f"{i}. {repo['full_name']}")
    print(f"   Description: {repo['description']}")
    print(f"   Stars: {repo['stars']}, Open Issues: {repo['issues_count']}")
    print()


# ============================================================================
# METHOD 3: List Repositories from an Organization
# ============================================================================

def list_org_repos(org: str, token: str, max_results: int = 30):
    """
    List all repositories from a GitHub organization.
    
    Args:
        org: Organization name (e.g., "wso2")
        token: GitHub token
        max_results: Maximum number of repos to return
    
    Returns:
        List of repository dictionaries
    """
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "sort": "updated",
        "per_page": max_results
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    repos = []
    for item in response.json():
        repos.append({
            "owner": item["owner"]["login"],
            "repo": item["name"],
            "full_name": item["full_name"],
            "description": item["description"],
            "stars": item["stargazers_count"],
            "issues_count": item["open_issues_count"],
            "updated_at": item["updated_at"],
            "url": item["html_url"]
        })
    
    return repos


# Example: List all WSO2 repositories
wso2_repos = list_org_repos("wso2", github_token, max_results=30)

print(f"\nFound {len(wso2_repos)} WSO2 repositories:")
for repo in wso2_repos[:5]:  # Show first 5
    print(f"- {repo['full_name']} ({repo['issues_count']} open issues)")


# ============================================================================
# METHOD 4: Check if Repository Has Issues Before Ingesting
# ============================================================================

def check_repo_issues(owner: str, repo: str, token: str):
    """
    Check if a repository has issues and get basic stats.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token
    
    Returns:
        Dictionary with issue statistics
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    # Count issues by state
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    # Get open issues count
    params = {"state": "open", "per_page": 1}
    open_resp = requests.get(issues_url, headers=headers, params=params)
    
    # Get closed issues count
    params = {"state": "closed", "per_page": 1}
    closed_resp = requests.get(issues_url, headers=headers, params=params)
    
    return {
        "owner": owner,
        "repo": repo,
        "full_name": data["full_name"],
        "description": data["description"],
        "open_issues": data["open_issues_count"],
        "has_issues": data["has_issues"],
        "stars": data["stargazers_count"],
        "url": data["html_url"]
    }


# Example: Check Choreo repository
repo_info = check_repo_issues("wso2", "choreo", github_token)

print(f"\nRepository: {repo_info['full_name']}")
print(f"Has issues enabled: {repo_info['has_issues']}")
print(f"Open issues: {repo_info['open_issues']}")
print(f"Stars: {repo_info['stars']}")
print(f"Description: {repo_info['description']}")


# ============================================================================
# METHOD 5: Complete Workflow - Find, Filter, and Ingest
# ============================================================================

def find_and_ingest_repos(
    search_query: str,
    token: str,
    min_issues: int = 5,
    max_repos: int = 5,
    issues_per_repo: int = 50
):
    """
    Find repositories matching criteria and ingest their issues.
    
    Args:
        search_query: GitHub search query
        token: GitHub token
        min_issues: Minimum number of issues required
        max_repos: Maximum repositories to ingest
        issues_per_repo: Maximum issues to ingest per repo
    
    Returns:
        List of ingestion statistics per repository
    """
    from github_issues_ingestion import create_ingestion_pipeline
    
    # Find repositories
    repos = find_github_repos(search_query, token, max_results=20)
    
    # Filter repositories with enough issues
    eligible_repos = [
        r for r in repos 
        if r['issues_count'] >= min_issues
    ][:max_repos]
    
    print(f"\nFound {len(eligible_repos)} eligible repositories to ingest")
    print("="*70)
    
    # Create pipeline
    orchestrator = create_ingestion_pipeline()
    
    # Ingest each repository
    results = []
    for i, repo in enumerate(eligible_repos, 1):
        print(f"\n[{i}/{len(eligible_repos)}] Processing: {repo['full_name']}")
        print(f"  Issues: {repo['issues_count']}, Stars: {repo['stars']}")
        
        try:
            stats = orchestrator.ingest_repository(
                owner=repo['owner'],
                repo=repo['repo'],
                max_issues=issues_per_repo
            )
            
            results.append({
                "repository": repo['full_name'],
                "stats": stats
            })
            
            print(f"  ✓ Ingested {stats['total_issues']} issues")
            print(f"    Created {stats['total_chunks']} chunks")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "repository": repo['full_name'],
                "error": str(e)
            })
    
    return results


# Example: Find and ingest WSO2 repositories with issues
results = find_and_ingest_repos(
    search_query="org:wso2",
    token=github_token,
    min_issues=10,
    max_repos=3,
    issues_per_repo=20
)

print("\n" + "="*70)
print("INGESTION SUMMARY")
print("="*70)
for result in results:
    print(f"\n{result['repository']}:")
    if 'stats' in result:
        stats = result['stats']
        print(f"  ✓ Issues: {stats['total_issues']}")
        print(f"  ✓ Chunks: {stats['total_chunks']}")
        print(f"  ✓ Embeddings: {stats['total_embeddings']}")
    else:
        print(f"  ✗ Error: {result['error']}")


# ============================================================================
# METHOD 6: Filter Issues by Labels or State
# ============================================================================

# Ingest only specific types of issues
stats = orchestrator.ingest_repository(
    owner="wso2",
    repo="choreo",
    state="open",                    # Only open issues
    labels=["bug", "enhancement"],   # Only these labels
    max_issues=50
)

# Ingest recent issues (updated in last 30 days)
from datetime import datetime, timedelta

since_date = datetime.utcnow() - timedelta(days=30)
since_timestamp = since_date.isoformat() + "Z"

stats = orchestrator.ingest_repository(
    owner="wso2",
    repo="choreo",
    since=since_timestamp,
    max_issues=100
)


# ============================================================================
# METHOD 7: Query After Ingestion
# ============================================================================

# After ingesting, you can query the issues
results = orchestrator.query_issues(
    query="authentication error with OAuth",
    top_k=5
)

print("\n" + "="*70)
print("SEARCH RESULTS")
print("="*70)

for i, result in enumerate(results, 1):
    metadata = result['metadata']
    print(f"\n{i}. Issue #{metadata['issue_number']}: {metadata['issue_title']}")
    print(f"   Repository: {metadata['repository']}")
    print(f"   State: {metadata['state']}")
    print(f"   Score: {result['score']:.4f}")
    print(f"   Labels: {', '.join(metadata['labels'])}")
    print(f"   URL: {metadata['url']}")
    print(f"   Preview: {result['content'][:200]}...")


# ============================================================================
# SUMMARY: Step-by-Step Process
# ============================================================================

"""
COMPLETE WORKFLOW:

1. Find Repository:
   - Search: find_github_repos("query", token)
   - List org: list_org_repos("wso2", token)
   - Check info: check_repo_issues("owner", "repo", token)

2. Ingest Issues:
   orchestrator = create_ingestion_pipeline()
   stats = orchestrator.ingest_repository("owner", "repo")

3. Query Issues:
   results = orchestrator.query_issues("your search query")

4. The system automatically:
   - Fetches all issue data (title, body, comments, labels, etc.)
   - Cleans and processes the text
   - Chunks the text (default: 1000 chars with 200 overlap)
   - Creates embeddings using Azure OpenAI
   - Stores in Pinecone with metadata
   - Enables semantic search

5. Stored Metadata per Chunk:
   - issue_number
   - issue_title
   - repository (owner/repo)
   - state (open/closed)
   - labels
   - created_at
   - updated_at
   - url
   - chunk_index
   - total_chunks
"""

