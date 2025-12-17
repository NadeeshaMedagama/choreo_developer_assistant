"""
Summary Generation Service

Responsible for generating comprehensive summaries from extracted text.
Uses OpenAI GPT models to create intelligent summaries with key concepts.
"""

from typing import List, Dict, Any, Optional
import json
import re

from ..models import ExtractedContent, Summary, DiagramFile
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SummaryGenerationService:
    """Service for generating summaries from extracted text using LLM."""

    def __init__(self, openai_api_key: str, model: str = "gpt-4", max_summary_length: int = 500,
                 azure_endpoint: Optional[str] = None, azure_api_version: Optional[str] = None,
                 azure_deployment: Optional[str] = None):
        """
        Initialize summary generation service.

        Args:
            openai_api_key: OpenAI or Azure OpenAI API key
            model: Model to use for generation (or Azure deployment name)
            max_summary_length: Maximum length of summary in words
            azure_endpoint: Azure OpenAI endpoint (if using Azure)
            azure_api_version: Azure OpenAI API version (if using Azure)
            azure_deployment: Azure OpenAI deployment name (if using Azure)
        """
        self.api_key = openai_api_key
        self.model = model
        self.max_summary_length = max_summary_length
        self.is_azure = azure_endpoint is not None

        try:
            if self.is_azure:
                # Use Azure OpenAI
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=openai_api_key,
                    api_version=azure_api_version or "2024-12-01-preview",
                    azure_endpoint=azure_endpoint
                )
                self.model = azure_deployment or model
                logger.info(f"✓ Azure OpenAI client initialized with deployment: {self.model}")
            else:
                # Use standard OpenAI
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_api_key)
                logger.info(f"✓ OpenAI client initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def generate_summary(self, extracted_content: ExtractedContent) -> Summary:
        """
        Generate a comprehensive summary from extracted content.

        Args:
            extracted_content: ExtractedContent object

        Returns:
            Summary object with summary text, key concepts, and relationships
        """
        logger.info(f"Generating summary for: {extracted_content.source_file.file_name}")

        if not extracted_content.raw_text or len(extracted_content.raw_text.strip()) < 50:
            logger.warning("Insufficient content for summary generation")
            return Summary(
                source_file=extracted_content.source_file,
                summary_text="Insufficient content extracted from diagram.",
                key_concepts=[],
                entities=[],
                relationships=[]
            )

        try:
            # Generate summary with structured output
            summary_data = self._generate_structured_summary(extracted_content.raw_text)

            summary = Summary(
                source_file=extracted_content.source_file,
                summary_text=summary_data.get("summary", ""),
                key_concepts=summary_data.get("key_concepts", []),
                entities=summary_data.get("entities", []),
                relationships=summary_data.get("relationships", []),
                metadata={
                    "model": self.model,
                    "content_length": len(extracted_content.raw_text),
                    "extraction_method": extracted_content.extraction_method
                }
            )

            logger.info(f"✓ Generated summary ({len(summary.summary_text)} chars, "
                       f"{len(summary.key_concepts)} concepts, {len(summary.entities)} entities)")

            return summary

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return Summary(
                source_file=extracted_content.source_file,
                summary_text=f"Error generating summary: {str(e)}",
                key_concepts=[],
                entities=[],
                relationships=[],
                metadata={"error": str(e)}
            )

    def _generate_structured_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate structured summary using OpenAI.

        Args:
            text: Text to summarize

        Returns:
            Dictionary with summary, key_concepts, entities, and relationships
        """
        # Truncate text if too long (GPT-4 context limit)
        max_chars = 12000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            logger.info(f"Truncated text to {max_chars} characters")

        prompt = f"""You are an expert at analyzing architecture diagrams and technical documentation.

Given the following text extracted from a Choreo platform architecture diagram, provide:

1. A comprehensive summary (max {self.max_summary_length} words) that captures the main purpose and key information
2. A list of key concepts and technologies mentioned
3. A list of main entities (components, services, systems)
4. Relationships between entities (if evident)

Text to analyze:
{text}

Respond ONLY with valid JSON in this exact format:
{{
    "summary": "comprehensive summary text here",
    "key_concepts": ["concept1", "concept2", ...],
    "entities": ["entity1", "entity2", ...],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "relationship_type"}},
        ...
    ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a technical documentation expert specializing in cloud architecture and distributed systems. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback")
            return {
                "summary": response_text[:self.max_summary_length * 5],  # Rough char estimate
                "key_concepts": self._extract_keywords(text),
                "entities": [],
                "relationships": []
            }

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Fallback method to extract keywords using simple heuristics.

        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        # Simple keyword extraction (uppercase words, technical terms)
        words = re.findall(r'\b[A-Z][A-Za-z]+\b', text)

        # Count frequency
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]

    def generate_batch_summaries(self, extracted_contents: List[ExtractedContent]) -> List[Summary]:
        """
        Generate summaries for multiple extracted contents.

        Args:
            extracted_contents: List of ExtractedContent objects

        Returns:
            List of Summary objects
        """
        summaries = []

        for i, content in enumerate(extracted_contents, 1):
            logger.info(f"Processing {i}/{len(extracted_contents)}: {content.source_file.file_name}")
            summary = self.generate_summary(content)
            summaries.append(summary)

        return summaries

