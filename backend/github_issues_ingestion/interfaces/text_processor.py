"""
Interface for text processing operations.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ITextProcessor(ABC):
    """Interface for processing and cleaning text from GitHub issues."""

    @abstractmethod
    def process_issue(self, issue_data: Dict[str, Any]) -> str:
        """
        Process a GitHub issue into clean text.

        Args:
            issue_data: Raw issue data from GitHub API

        Returns:
            Processed and cleaned text combining all relevant fields
        """
        pass

    @abstractmethod
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        pass

