#!/usr/bin/env python3
"""
Script to ingest all 154 Choreo repositories from wso2-enterprise organization.

This ensures the LLM has access to all repository information and can provide
accurate URLs based on the ingested content.
"""

import os
import sys
import asyncio
import requests
import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChoreoRepoIngester:
    """Ingest all Choreo repositories from wso2-enterprise organization."""
    
    def __init__(self, github_token: str = None, backend_url: str = "http://localhost:8000"):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.backend_url = backend_url
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        if self.github_token:
            self.headers["Authorization"] = f"Bearer {self.github_token}"
    
    def search_choreo_repos(self) -> List[Dict]:
        """
        Search for all Choreo-related repositories in wso2-enterprise.
        
        Returns:
            List of repository dictionaries
        """
        logger.info("Searching for Choreo repositories in wso2-enterprise...")
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"https://api.github.com/orgs/wso2-enterprise/repos?type=all&per_page={per_page}&page={page}"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                page_repos = response.json()
                
                if not page_repos:
                    break
                
                # Filter for Choreo-related repos
                for repo in page_repos:
                    repo_name = repo.get('name', '').lower()
                    description = (repo.get('description') or '').lower()
                    
                    # Include if "choreo" in name or description
                    if 'choreo' in repo_name or 'choreo' in description:
                        repos.append({
                            'name': repo['name'],
                            'full_name': repo['full_name'],
                            'url': repo['html_url'],
                            'description': repo.get('description', ''),
                            'default_branch': repo.get('default_branch', 'main'),
                            'private': repo.get('private', False)
                        })
                
                logger.info(f"Processed page {page}, found {len(repos)} Choreo repos so far")
                
                if len(page_repos) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching repositories: {e}")
                break
        
        logger.info(f"Found {len(repos)} Choreo-related repositories")
        return repos
    
    def ingest_repository(self, repo_url: str, branch: str = 'main') -> Dict:
        """
        Ingest a single repository via the backend API.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to ingest
            
        Returns:
            Ingestion result dictionary
        """
        ingest_url = f"{self.backend_url}/api/ingest/github"
        
        payload = {
            "repo_url": repo_url,
            "branch": branch
        }
        
        try:
            logger.info(f"Ingesting {repo_url}...")
            response = requests.post(ingest_url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✓ Successfully ingested {repo_url}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to ingest {repo_url}: {e}")
            return {"error": str(e), "repo_url": repo_url}
    
    def ingest_all_choreo_repos(self, repos: List[Dict], max_repos: int = None) -> Dict:
        """
        Ingest all Choreo repositories.
        
        Args:
            repos: List of repository dictionaries
            max_repos: Maximum number of repos to ingest (None = all)
            
        Returns:
            Summary dictionary with results
        """
        if max_repos:
            repos = repos[:max_repos]
        
        logger.info(f"Starting ingestion of {len(repos)} repositories...")
        
        results = {
            'total': len(repos),
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, repo in enumerate(repos, 1):
            logger.info(f"\n[{i}/{len(repos)}] Processing {repo['name']}...")
            
            result = self.ingest_repository(
                repo_url=repo['url'],
                branch=repo['default_branch']
            )
            
            if 'error' in result:
                results['failed'] += 1
                results['errors'].append({
                    'repo': repo['name'],
                    'error': result['error']
                })
            else:
                results['succeeded'] += 1
            
            # Small delay between repos
            time.sleep(1)
        
        return results
    
    def print_summary(self, results: Dict):
        """Print ingestion summary."""
        print("\n" + "="*80)
        print("INGESTION SUMMARY")
        print("="*80)
        print(f"Total repositories: {results['total']}")
        print(f"Successfully ingested: {results['succeeded']}")
        print(f"Failed: {results['failed']}")
        
        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors'][:10]:  # Show first 10
                print(f"  ✗ {error['repo']}: {error['error']}")
            
            if len(results['errors']) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")
        
        print("="*80)
        
        success_rate = (results['succeeded'] / results['total'] * 100) if results['total'] > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")


def main():
    """Main function to run the ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest Choreo repositories from wso2-enterprise')
    parser.add_argument('--backend-url', default='http://localhost:8000',
                        help='Backend API URL (default: http://localhost:8000)')
    parser.add_argument('--max-repos', type=int, default=None,
                        help='Maximum number of repositories to ingest')
    parser.add_argument('--github-token', default=None,
                        help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--list-only', action='store_true',
                        help='Only list repositories, do not ingest')
    
    args = parser.parse_args()
    
    # Create ingester
    ingester = ChoreoRepoIngester(
        github_token=args.github_token,
        backend_url=args.backend_url
    )
    
    # Search for repos
    repos = ingester.search_choreo_repos()
    
    if not repos:
        logger.error("No Choreo repositories found!")
        sys.exit(1)
    
    # Print found repositories
    print("\n" + "="*80)
    print(f"FOUND {len(repos)} CHOREO REPOSITORIES")
    print("="*80)
    for i, repo in enumerate(repos[:20], 1):  # Show first 20
        private_marker = "🔒" if repo['private'] else "🌐"
        print(f"{i:3d}. {private_marker} {repo['name']}")
        if repo['description']:
            print(f"      {repo['description'][:70]}")
    
    if len(repos) > 20:
        print(f"      ... and {len(repos) - 20} more repositories")
    print("="*80)
    
    if args.list_only:
        logger.info("List-only mode. Exiting without ingestion.")
        sys.exit(0)
    
    # Confirm ingestion
    print(f"\nThis will ingest {args.max_repos or len(repos)} repositories into the knowledge base.")
    print("This may take a significant amount of time.")
    
    confirm = input("\nProceed with ingestion? [y/N]: ")
    if confirm.lower() != 'y':
        logger.info("Ingestion cancelled by user.")
        sys.exit(0)
    
    # Ingest repositories
    results = ingester.ingest_all_choreo_repos(repos, max_repos=args.max_repos)
    
    # Print summary
    ingester.print_summary(results)


if __name__ == "__main__":
    main()
