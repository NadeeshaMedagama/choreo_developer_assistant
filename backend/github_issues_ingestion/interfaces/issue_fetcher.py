"""
Interface for fetching GitHub issues.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IIssueFetcher(ABC):
    """Interface for fetching issues from GitHub repositories."""

    @abstractmethod
    def fetch_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        labels: Optional[List[str]] = None,
        since: Optional[str] = None,
        max_issues: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
            List of issue dictionaries with all information
        """
        pass

    @abstractmethod
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
        pass

