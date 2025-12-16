"""
GitHub Issue Fetcher Service.
Implements IIssueFetcher interface.
"""

import requests
import time
from typing import List, Dict, Any, Optional

from ..interfaces.issue_fetcher import IIssueFetcher
from ..models.github_issue import GitHubIssue


class GitHubIssueFetcher(IIssueFetcher):
    """Service for fetching issues from GitHub repositories using REST API."""

    def __init__(self, token: str):
        """
        Initialize GitHub Issue Fetcher.

        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        }
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to GitHub API with rate limiting.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        # Check rate limit
        if self.rate_limit_remaining is not None and self.rate_limit_remaining < 10:
            if self.rate_limit_reset:
                wait_time = max(0, self.rate_limit_reset - time.time())
                if wait_time > 0:
                    print(f"Rate limit low, waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time)

        response = requests.get(url, headers=self.headers, params=params or {})
        
        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
        self.rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
        
        response.raise_for_status()
        return response.json()

    def _make_paginated_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        max_items: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Make paginated requests to GitHub API.

        Args:
            url: API endpoint URL
            params: Query parameters
            max_items: Maximum number of items to fetch

        Returns:
            List of all items from all pages
        """
        all_items = []
        params = params or {}
        params["per_page"] = 100  # Max items per page
        page = 1
        # GitHub API has a hard limit of 1000 results (10 pages of 100 items)
        max_pages = 10

        while True:
            params["page"] = page

            # Check if we've hit GitHub's pagination limit
            if page > max_pages:
                print(f"Warning: Reached GitHub's pagination limit ({max_pages} pages, {len(all_items)} items)")
                break

            try:
                items = self._make_request(url, params)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 422:
                    # Unprocessable Entity - usually means we've exceeded pagination limits
                    print(f"Warning: Pagination limit reached at page {page}. Collected {len(all_items)} items so far.")
                    break
                raise  # Re-raise other HTTP errors

            if not items:
                break
            
            all_items.extend(items)
            
            # Check if we've reached max_items
            if max_items and len(all_items) >= max_items:
                all_items = all_items[:max_items]
                break
            
            # Check if this was the last page
            if len(items) < 100:
                break
            
            page += 1
            time.sleep(0.1)  # Small delay between requests

        return all_items

    def _fetch_issues_via_search(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        labels: Optional[List[str]] = None,
        since: Optional[str] = None,
        max_issues: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch issues using the Search API (for repositories with >1000 issues).

        Args:
            owner: Repository owner/organization
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            labels: Filter by labels
            since: Only issues updated after this timestamp
            max_issues: Maximum number of issues to fetch

        Returns:
            List of issue data dictionaries
        """
        # Build search query
        query_parts = [f"repo:{owner}/{repo}", "is:issue"]

        if state != "all":
            query_parts.append(f"state:{state}")

        if labels:
            for label in labels:
                query_parts.append(f'label:"{label}"')

        if since:
            query_parts.append(f"updated:>={since}")

        query = " ".join(query_parts)

        url = f"{self.base_url}/search/issues"
        params = {"q": query, "sort": "updated", "order": "desc"}

        print(f"Using Search API: {query}")

        # Search API returns different structure
        all_items = []
        params["per_page"] = 100
        page = 1
        max_pages = 10  # Search API also has pagination limits

        while True:
            params["page"] = page

            if page > max_pages:
                print(f"Warning: Reached search pagination limit at page {page}")
                break

            try:
                response = self._make_request(url, params)
                items = response.get("items", [])
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 422:
                    print(f"Warning: Search pagination limit reached at page {page}")
                    break
                raise

            if not items:
                break

            all_items.extend(items)

            # Check if we've reached max_issues
            if max_issues and len(all_items) >= max_issues:
                all_items = all_items[:max_issues]
                break

            # Check if we've fetched all results
            total_count = response.get("total_count", 0)
            if len(all_items) >= total_count or len(items) < 100:
                break

            page += 1
            time.sleep(1)  # Search API has stricter rate limits

        return all_items

    def fetch_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        labels: Optional[List[str]] = None,
        since: Optional[str] = None,
        max_issues: Optional[int] = None
    ) -> List[GitHubIssue]:
        """
        Fetch issues from a GitHub repository.

        Args:
            owner: Repository owner/organization
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            labels: Filter by labels
            since: Only issues updated after this timestamp (ISO 8601 format)
            max_issues: Maximum number of issues to fetch

        Returns:
            List of GitHubIssue objects with all information
        """
        # Try standard API first
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state}
        
        if labels:
            params["labels"] = ",".join(labels)
        
        if since:
            params["since"] = since

        print(f"Fetching issues from {owner}/{repo}...")
        issues_data = self._make_paginated_request(url, params, max_issues)
        
        # If we hit the pagination limit and no max_issues specified, try search API
        if len(issues_data) >= 1000 and not max_issues:
            print("Standard API pagination limit reached, switching to Search API...")
            additional_issues = self._fetch_issues_via_search(owner, repo, state, labels, since, max_issues)

            # Merge results, avoiding duplicates
            existing_ids = {issue["id"] for issue in issues_data}
            for issue in additional_issues:
                if issue["id"] not in existing_ids:
                    issues_data.append(issue)
                    existing_ids.add(issue["id"])

        # No filtering - include all issues (including pull requests)
        print(f"Fetched {len(issues_data)} issues (including pull requests)")

        # Convert to GitHubIssue objects
        issues = []
        for issue_data in issues_data:
            issue = GitHubIssue.from_api_response(issue_data, owner, repo)
            
            # Fetch comments for this issue
            comments = self.fetch_issue_comments(owner, repo, issue.number)
            issue.add_comments(comments)
            
            issues.append(issue)
        
        return issues

    def fetch_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific issue.

        Args:
            owner: Repository owner/organization
            repo: Repository name
            issue_number: Issue number

        Returns:
            List of comment dictionaries
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        
        try:
            comments_data = self._make_paginated_request(url)
            
            # Extract relevant information from comments
            comments = []
            for comment in comments_data:
                comments.append({
                    "id": comment["id"],
                    "user": comment.get("user", {}).get("login"),
                    "body": comment.get("body", ""),
                    "created_at": comment["created_at"],
                    "updated_at": comment["updated_at"],
                })
            
            return comments
        except Exception as e:
            print(f"Warning: Failed to fetch comments for issue #{issue_number}: {e}")
            return []

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Dictionary with rate limit information
        """
        url = f"{self.base_url}/rate_limit"
        response = self._make_request(url)
        return response.get("resources", {}).get("core", {})

