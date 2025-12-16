"""
Models package for GitHub Issues Ingestion system.
"""

from .chunk import TextChunk
from .github_issue import GitHubIssue

__all__ = [
    "TextChunk",
    "GitHubIssue",
]

