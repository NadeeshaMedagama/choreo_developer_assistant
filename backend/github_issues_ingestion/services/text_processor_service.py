"""
Text Processor Service.
Implements ITextProcessor interface.
"""

import re
from typing import Dict, Any
from ..interfaces.text_processor import ITextProcessor
from ..models.github_issue import GitHubIssue


class TextProcessorService(ITextProcessor):
    """Service for processing and cleaning text from GitHub issues."""

    def __init__(self, include_code_blocks: bool = True):
        """
        Initialize Text Processor.

        Args:
            include_code_blocks: Whether to include code blocks in processed text
        """
        self.include_code_blocks = include_code_blocks

    def process_issue(self, issue: GitHubIssue) -> str:
        """
        Process a GitHub issue into clean text.

        Args:
            issue: GitHubIssue object

        Returns:
            Processed and cleaned text combining all relevant fields
        """
        parts = []

        # Add title
        parts.append(f"# Issue #{issue.number}: {issue.title}")
        parts.append("")

        # Add metadata
        parts.append(f"**Repository:** {issue.owner}/{issue.repo}")
        parts.append(f"**State:** {issue.state}")
        parts.append(f"**Created:** {issue.created_at.strftime('%Y-%m-%d')}")
        parts.append(f"**Updated:** {issue.updated_at.strftime('%Y-%m-%d')}")
        
        if issue.user:
            parts.append(f"**Author:** {issue.user}")
        
        if issue.labels:
            parts.append(f"**Labels:** {', '.join(issue.labels)}")
        
        if issue.assignees:
            parts.append(f"**Assignees:** {', '.join(issue.assignees)}")
        
        if issue.milestone:
            parts.append(f"**Milestone:** {issue.milestone}")
        
        parts.append("")

        # Add body
        if issue.body:
            parts.append("## Description")
            parts.append(self.clean_text(issue.body))
            parts.append("")

        # Add comments
        if issue.comments:
            parts.append(f"## Comments ({len(issue.comments)})")
            parts.append("")
            
            for i, comment in enumerate(issue.comments, 1):
                user = comment.get("user", "Unknown")
                body = comment.get("body", "")
                created_at = comment.get("created_at", "")
                
                parts.append(f"### Comment {i} by {user}")
                if created_at:
                    parts.append(f"*Posted on {created_at}*")
                parts.append("")
                parts.append(self.clean_text(body))
                parts.append("")

        # Join all parts
        full_text = "\n".join(parts)
        
        return full_text

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Handle code blocks
        if not self.include_code_blocks:
            # Remove code blocks
            text = re.sub(r'```[\s\S]*?```', '[code block removed]', text)
            text = re.sub(r'`[^`]+`', '[code]', text)
        
        # Normalize whitespace
        text = re.sub(r'\r\n', '\n', text)  # Windows line endings
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove URLs if they're very long (keep short ones as they might be relevant)
        text = re.sub(r'https?://[^\s]{100,}', '[long URL]', text)
        
        # Remove excessive special characters
        text = re.sub(r'[-=_]{10,}', '---', text)
        
        return text.strip()

    def extract_keywords(self, text: str, max_keywords: int = 10) -> list:
        """
        Extract keywords from text (simple implementation).

        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        # Remove code blocks and special characters
        cleaned = re.sub(r'```[\s\S]*?```', '', text)
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        
        # Split into words
        words = cleaned.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        }
        
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]

