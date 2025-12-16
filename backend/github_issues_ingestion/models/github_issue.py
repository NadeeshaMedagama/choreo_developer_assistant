"""
GitHubIssue model representing a GitHub issue with all its information.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class GitHubIssue:
    """Represents a GitHub issue with all its information."""

    number: int
    title: str
    body: Optional[str]
    state: str
    owner: str
    repo: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    labels: List[str] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    user: Optional[str] = None
    assignees: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any], owner: str, repo: str) -> "GitHubIssue":
        """
        Create GitHubIssue from GitHub API response.

        Args:
            data: Raw API response data
            owner: Repository owner
            repo: Repository name

        Returns:
            GitHubIssue instance
        """
        # Parse dates
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        closed_at = None
        if data.get("closed_at"):
            closed_at = datetime.fromisoformat(data["closed_at"].replace("Z", "+00:00"))

        # Extract labels
        labels = [label["name"] for label in data.get("labels", [])]

        # Extract assignees
        assignees = [assignee["login"] for assignee in data.get("assignees", [])]

        # Extract user
        user = data.get("user", {}).get("login") if data.get("user") else None

        # Extract milestone
        milestone = data.get("milestone", {}).get("title") if data.get("milestone") else None

        return cls(
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data["state"],
            owner=owner,
            repo=repo,
            created_at=created_at,
            updated_at=updated_at,
            closed_at=closed_at,
            labels=labels,
            comments=[],  # Comments fetched separately
            user=user,
            assignees=assignees,
            milestone=milestone,
            url=data.get("html_url"),
            raw_data=data,
        )

    def add_comments(self, comments: List[Dict[str, Any]]):
        """Add comments to the issue."""
        self.comments = comments

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "owner": self.owner,
            "repo": self.repo,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "labels": self.labels,
            "comments": self.comments,
            "user": self.user,
            "assignees": self.assignees,
            "milestone": self.milestone,
            "url": self.url,
        }

    def __repr__(self) -> str:
        """String representation of issue."""
        return f"GitHubIssue(#{self.number}: {self.title[:50]}..., state={self.state})"

