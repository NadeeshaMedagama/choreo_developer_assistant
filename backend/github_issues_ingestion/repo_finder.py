#!/usr/bin/env python3
"""
Repository Finder and Issue Ingestion Tool

This script helps you:
1. Discover GitHub repositories
2. Check their issue count
3. Ingest issues into the vector database

Usage:
    # Search for repositories
    python repo_finder.py search "wso2"
    
    # List organization repositories
    python repo_finder.py list-org wso2
    
    # Check specific repository
    python repo_finder.py check wso2/choreo
    
    # Ingest specific repository
    python repo_finder.py ingest wso2/choreo --max-issues 50
    
    # Find and ingest multiple repos
    python repo_finder.py auto-ingest "org:wso2" --max-repos 3
"""

import sys
import argparse
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import requests
from github_issues_ingestion import create_ingestion_pipeline
from github_issues_ingestion.config import Settings


class RepositoryFinder:
    """Helper class to find and analyze GitHub repositories."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}"
        }
    
    def search_repositories(self, query: str, max_results: int = 10):
        """Search for repositories matching a query."""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        repos = []
        for item in response.json()["items"]:
            repos.append({
                "owner": item["owner"]["login"],
                "repo": item["name"],
                "full_name": item["full_name"],
                "description": item["description"] or "No description",
                "stars": item["stargazers_count"],
                "issues_count": item["open_issues_count"],
                "url": item["html_url"],
                "has_issues": item["has_issues"]
            })
        
        return repos
    
    def list_org_repos(self, org: str, max_results: int = 30):
        """List repositories from an organization."""
        url = f"{self.base_url}/orgs/{org}/repos"
        params = {
            "sort": "updated",
            "per_page": max_results
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        repos = []
        for item in response.json():
            repos.append({
                "owner": item["owner"]["login"],
                "repo": item["name"],
                "full_name": item["full_name"],
                "description": item["description"] or "No description",
                "stars": item["stargazers_count"],
                "issues_count": item["open_issues_count"],
                "url": item["html_url"],
                "has_issues": item["has_issues"],
                "updated_at": item["updated_at"]
            })
        
        return repos
    
    def get_repo_info(self, owner: str, repo: str):
        """Get detailed information about a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Get issue counts by state
        issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        # Count open issues
        open_params = {"state": "open", "per_page": 1}
        open_resp = requests.get(issues_url, headers=self.headers, params=open_params)
        
        # Count closed issues
        closed_params = {"state": "closed", "per_page": 1}
        closed_resp = requests.get(issues_url, headers=self.headers, params=closed_params)
        
        return {
            "owner": owner,
            "repo": repo,
            "full_name": data["full_name"],
            "description": data["description"] or "No description",
            "open_issues": data["open_issues_count"],
            "has_issues": data["has_issues"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "url": data["html_url"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "language": data["language"]
        }


def cmd_search(args):
    """Search for repositories."""
    settings = Settings.from_env()
    finder = RepositoryFinder(settings.github_token)
    
    print(f"\n🔍 Searching for repositories: '{args.query}'")
    print("="*80)
    
    repos = finder.search_repositories(args.query, max_results=args.max_results)
    
    if not repos:
        print("No repositories found.")
        return
    
    print(f"\nFound {len(repos)} repositories:\n")
    
    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['full_name']}")
        print(f"   ⭐ Stars: {repo['stars']:,} | 🐛 Issues: {repo['issues_count']:,}")
        print(f"   📝 {repo['description'][:100]}...")
        print(f"   🔗 {repo['url']}")
        print()


def cmd_list_org(args):
    """List organization repositories."""
    settings = Settings.from_env()
    finder = RepositoryFinder(settings.github_token)
    
    print(f"\n📂 Listing repositories for organization: {args.org}")
    print("="*80)
    
    repos = finder.list_org_repos(args.org, max_results=args.max_results)
    
    if not repos:
        print("No repositories found.")
        return
    
    print(f"\nFound {len(repos)} repositories:\n")
    
    # Sort by issues count
    repos_sorted = sorted(repos, key=lambda x: x['issues_count'], reverse=True)
    
    for i, repo in enumerate(repos_sorted, 1):
        if not repo['has_issues']:
            continue
            
        print(f"{i}. {repo['full_name']}")
        print(f"   ⭐ Stars: {repo['stars']:,} | 🐛 Issues: {repo['issues_count']:,}")
        print(f"   📝 {repo['description'][:100]}...")
        print(f"   🕐 Updated: {repo['updated_at'][:10]}")
        print()


def cmd_check(args):
    """Check a specific repository."""
    settings = Settings.from_env()
    finder = RepositoryFinder(settings.github_token)
    
    # Parse owner/repo
    parts = args.repository.split("/")
    if len(parts) != 2:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    owner, repo = parts
    
    print(f"\n🔍 Checking repository: {args.repository}")
    print("="*80)
    
    try:
        info = finder.get_repo_info(owner, repo)
        
        print(f"\nRepository: {info['full_name']}")
        print(f"Description: {info['description']}")
        print(f"\n📊 Statistics:")
        print(f"  ⭐ Stars: {info['stars']:,}")
        print(f"  🔱 Forks: {info['forks']:,}")
        print(f"  🐛 Open Issues: {info['open_issues']:,}")
        print(f"  🔧 Has Issues: {info['has_issues']}")
        print(f"  💻 Language: {info['language'] or 'N/A'}")
        print(f"\n📅 Dates:")
        print(f"  Created: {info['created_at'][:10]}")
        print(f"  Updated: {info['updated_at'][:10]}")
        print(f"\n🔗 URL: {info['url']}")
        
        if info['has_issues'] and info['open_issues'] > 0:
            print(f"\n✅ This repository has {info['open_issues']} open issues ready to ingest!")
        else:
            print(f"\n⚠️  This repository has no issues to ingest.")
        
    except requests.HTTPError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_ingest(args):
    """Ingest issues from a specific repository."""
    # Parse owner/repo
    parts = args.repository.split("/")
    if len(parts) != 2:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    owner, repo = parts
    
    print(f"\n📥 Ingesting issues from: {args.repository}")
    print("="*80)
    
    # Create pipeline
    orchestrator = create_ingestion_pipeline()
    
    # Parse labels
    labels = None
    if args.labels:
        labels = [label.strip() for label in args.labels.split(",")]
    
    # Ingest
    try:
        stats = orchestrator.ingest_repository(
            owner=owner,
            repo=repo,
            state=args.state,
            labels=labels,
            since=args.since,
            max_issues=args.max_issues
        )
        
        print(f"\n✅ Ingestion complete!")
        print(f"   Issues processed: {stats['total_issues']}")
        print(f"   Chunks created: {stats['total_chunks']}")
        print(f"   Embeddings generated: {stats['total_embeddings']}")
        
        if stats['errors']:
            print(f"\n⚠️  Encountered {len(stats['errors'])} error(s)")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        sys.exit(1)


def cmd_auto_ingest(args):
    """Find and automatically ingest multiple repositories."""
    settings = Settings.from_env()
    finder = RepositoryFinder(settings.github_token)
    
    print(f"\n🤖 Auto-ingesting repositories matching: '{args.query}'")
    print("="*80)
    
    # Find repositories
    repos = finder.search_repositories(args.query, max_results=args.max_repos * 2)
    
    # Filter repositories with enough issues
    eligible = [
        r for r in repos
        if r['has_issues'] and r['issues_count'] >= args.min_issues
    ][:args.max_repos]
    
    if not eligible:
        print("No eligible repositories found.")
        return
    
    print(f"\n📋 Found {len(eligible)} repositories to ingest:\n")
    for i, repo in enumerate(eligible, 1):
        print(f"{i}. {repo['full_name']} ({repo['issues_count']} issues)")
    
    # Confirm
    if not args.yes:
        response = input("\nProceed with ingestion? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return
    
    # Create pipeline
    orchestrator = create_ingestion_pipeline()
    
    # Ingest each repository
    results = []
    for i, repo in enumerate(eligible, 1):
        print(f"\n[{i}/{len(eligible)}] Processing: {repo['full_name']}")
        print("-"*80)
        
        try:
            stats = orchestrator.ingest_repository(
                owner=repo['owner'],
                repo=repo['repo'],
                max_issues=args.issues_per_repo
            )
            
            results.append({
                "repository": repo['full_name'],
                "success": True,
                "stats": stats
            })
            
            print(f"✅ Success! Ingested {stats['total_issues']} issues")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "repository": repo['full_name'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("📊 INGESTION SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\nTotal repositories: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    print("\nDetails:")
    for result in results:
        if result['success']:
            stats = result['stats']
            print(f"\n✅ {result['repository']}")
            print(f"   Issues: {stats['total_issues']}, Chunks: {stats['total_chunks']}")
        else:
            print(f"\n❌ {result['repository']}")
            print(f"   Error: {result['error']}")


def main():
    parser = argparse.ArgumentParser(
        description="Find and ingest GitHub repository issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for repositories')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', type=int, default=10, help='Maximum results')
    search_parser.set_defaults(func=cmd_search)
    
    # List org command
    list_parser = subparsers.add_parser('list-org', help='List organization repositories')
    list_parser.add_argument('org', help='Organization name')
    list_parser.add_argument('--max-results', type=int, default=30, help='Maximum results')
    list_parser.set_defaults(func=cmd_list_org)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check repository details')
    check_parser.add_argument('repository', help='Repository (owner/repo)')
    check_parser.set_defaults(func=cmd_check)
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest repository issues')
    ingest_parser.add_argument('repository', help='Repository (owner/repo)')
    ingest_parser.add_argument('--state', default='all', choices=['open', 'closed', 'all'])
    ingest_parser.add_argument('--labels', help='Comma-separated labels')
    ingest_parser.add_argument('--since', help='ISO timestamp')
    ingest_parser.add_argument('--max-issues', type=int, help='Maximum issues to ingest')
    ingest_parser.set_defaults(func=cmd_ingest)
    
    # Auto-ingest command
    auto_parser = subparsers.add_parser('auto-ingest', help='Auto-find and ingest repos')
    auto_parser.add_argument('query', help='Search query')
    auto_parser.add_argument('--max-repos', type=int, default=3, help='Max repos to ingest')
    auto_parser.add_argument('--min-issues', type=int, default=5, help='Min issues required')
    auto_parser.add_argument('--issues-per-repo', type=int, default=50, help='Issues per repo')
    auto_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    auto_parser.set_defaults(func=cmd_auto_ingest)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()

