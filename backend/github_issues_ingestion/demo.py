#!/usr/bin/env python3
"""
Quick Demo: Find and Ingest Issues from a Repository

This script demonstrates the complete workflow:
1. Search for repositories
2. Check repository details
3. Ingest issues
4. Query the database

Run this to see the system in action!
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import os
import requests
from github_issues_ingestion import create_ingestion_pipeline
from github_issues_ingestion.config import Settings


def demo_find_repositories():
    """Demo: Find repositories in WSO2 organization."""
    print("\n" + "="*80)
    print("DEMO 1: Finding Repositories")
    print("="*80)
    
    settings = Settings.from_env()
    
    url = "https://api.github.com/orgs/wso2/repos"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"sort": "updated", "per_page": 5}
    
    print("\n🔍 Searching for WSO2 repositories...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    repos = response.json()
    
    print(f"\n📋 Found {len(repos)} repositories (showing top 5):\n")
    
    repo_list = []
    for i, repo in enumerate(repos, 1):
        if not repo["has_issues"]:
            continue
            
        repo_info = {
            "owner": repo["owner"]["login"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "issues": repo["open_issues_count"],
            "stars": repo["stargazers_count"]
        }
        repo_list.append(repo_info)
        
        print(f"{i}. {repo_info['full_name']}")
        print(f"   ⭐ Stars: {repo_info['stars']:,} | 🐛 Issues: {repo_info['issues']:,}")
        print(f"   🔗 https://github.com/{repo_info['full_name']}")
        print()
    
    return repo_list


def demo_check_repository(owner, repo):
    """Demo: Check repository details."""
    print("\n" + "="*80)
    print(f"DEMO 2: Checking Repository Details - {owner}/{repo}")
    print("="*80)
    
    settings = Settings.from_env()
    
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"\n🔍 Fetching details for {owner}/{repo}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    print(f"\n📊 Repository Information:")
    print(f"  Name: {data['full_name']}")
    print(f"  Description: {data['description'] or 'No description'}")
    print(f"  ⭐ Stars: {data['stargazers_count']:,}")
    print(f"  🔱 Forks: {data['forks_count']:,}")
    print(f"  🐛 Open Issues: {data['open_issues_count']:,}")
    print(f"  💻 Language: {data['language'] or 'N/A'}")
    print(f"  📅 Updated: {data['updated_at'][:10]}")
    
    if data['has_issues'] and data['open_issues_count'] > 0:
        print(f"\n✅ This repository has {data['open_issues_count']} open issues ready to ingest!")
        return True
    else:
        print(f"\n⚠️  This repository has no issues to ingest.")
        return False


def demo_ingest_issues(owner, repo, max_issues=5):
    """Demo: Ingest issues from repository."""
    print("\n" + "="*80)
    print(f"DEMO 3: Ingesting Issues from {owner}/{repo}")
    print("="*80)
    
    print(f"\n📥 Starting ingestion (max {max_issues} issues)...")
    print("This demonstrates the complete workflow:")
    print("  1. Fetch issues from GitHub")
    print("  2. Process and clean text")
    print("  3. Chunk text into smaller pieces")
    print("  4. Create embeddings with Azure OpenAI")
    print("  5. Store in Pinecone vector database")
    
    # Create pipeline
    orchestrator = create_ingestion_pipeline()
    
    # Ingest
    try:
        stats = orchestrator.ingest_repository(
            owner=owner,
            repo=repo,
            max_issues=max_issues
        )
        
        print(f"\n✅ Ingestion Complete!")
        print(f"  📊 Statistics:")
        print(f"     Issues processed: {stats['total_issues']}")
        print(f"     Chunks created: {stats['total_chunks']}")
        print(f"     Embeddings generated: {stats['total_embeddings']}")
        
        if stats['errors']:
            print(f"     ⚠️  Errors: {len(stats['errors'])}")
        
        return orchestrator, stats
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def demo_query_issues(orchestrator, query="authentication error"):
    """Demo: Query ingested issues."""
    if not orchestrator:
        print("\n⚠️  Skipping query demo - no data ingested")
        return
    
    print("\n" + "="*80)
    print(f"DEMO 4: Querying Issues - '{query}'")
    print("="*80)
    
    print(f"\n🔍 Searching for issues related to: '{query}'")
    print("This uses semantic search to find similar content...")
    
    try:
        results = orchestrator.query_issues(query, top_k=3)
        
        if not results:
            print("\nNo results found.")
            return
        
        print(f"\n📋 Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            print(f"{i}. Issue #{metadata.get('issue_number', 'N/A')}: {metadata.get('issue_title', 'N/A')}")
            print(f"   Repository: {metadata.get('repository', 'N/A')}")
            print(f"   State: {metadata.get('state', 'N/A')}")
            print(f"   Labels: {', '.join(metadata.get('labels', []))}")
            print(f"   Relevance Score: {result['score']:.4f}")
            print(f"   Chunk: {metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}")
            print(f"   URL: {metadata.get('url', 'N/A')}")
            print(f"   Preview: {result['content'][:150]}...")
            print()
        
    except Exception as e:
        print(f"\n❌ Error during query: {e}")


def main():
    """Run the complete demo."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "GitHub Issues Ingestion - LIVE DEMO" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\nThis demo will:")
    print("  1. Find WSO2 repositories")
    print("  2. Check a repository's details")
    print("  3. Ingest a small number of issues")
    print("  4. Query the ingested data")
    print("\n⚠️  Note: This will use your Azure OpenAI and Pinecone quotas")
    
    response = input("\nContinue with demo? (yes/no): ")
    if response.lower() != "yes":
        print("Demo cancelled.")
        return
    
    try:
        # Demo 1: Find repositories
        repos = demo_find_repositories()
        
        if not repos:
            print("No repositories found. Exiting.")
            return
        
        # Use first repo with issues
        selected_repo = repos[0]
        owner = selected_repo['owner']
        repo_name = selected_repo['name']
        
        # Demo 2: Check repository
        has_issues = demo_check_repository(owner, repo_name)
        
        if not has_issues:
            print(f"\nRepository {owner}/{repo_name} has no issues. Exiting.")
            return
        
        # Demo 3: Ingest issues (just a few for demo)
        orchestrator, stats = demo_ingest_issues(owner, repo_name, max_issues=3)
        
        if not orchestrator or not stats:
            print("\nIngestion failed. Exiting.")
            return
        
        # Demo 4: Query issues
        demo_query_issues(orchestrator, query="error")
        
        # Summary
        print("\n" + "="*80)
        print("DEMO COMPLETE!")
        print("="*80)
        print(f"\n✅ Successfully demonstrated:")
        print(f"   - Finding repositories in GitHub")
        print(f"   - Checking repository details")
        print(f"   - Ingesting {stats['total_issues']} issues")
        print(f"   - Creating {stats['total_chunks']} text chunks")
        print(f"   - Generating {stats['total_embeddings']} embeddings")
        print(f"   - Querying with semantic search")
        
        print(f"\n💡 Next steps:")
        print(f"   - Ingest more issues: python main.py {owner}/{repo_name} --max-issues 50")
        print(f"   - Query issues: python main.py {owner}/{repo_name} --query 'your search'")
        print(f"   - Find more repos: python repo_finder.py list-org {owner}")
        
        print("\n🎉 You're ready to use the system!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

