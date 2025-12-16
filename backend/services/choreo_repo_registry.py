"""
Choreo Repository Registry

This module maintains a registry of official Choreo components and their GitHub repository locations.
It provides URL validation and resolution for Choreo-related repositories.
"""

from typing import Dict, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class ChoreoRepoRegistry:
    """Registry of official Choreo repositories and components."""

    # Official Choreo components and their repository locations
    # Each component has its own repository in wso2-enterprise organization (primary)
    # Format: component_name -> (organization, repo_name, description)
    OFFICIAL_REPOS = {
        # Main Choreo Components - Each in wso2-enterprise (has all main Choreo information)
        "choreo-console": ("wso2-enterprise", "choreo-console", "Choreo web console and UI"),
        "choreo-telemetry": ("wso2-enterprise", "choreo-telemetry", "Telemetry and monitoring for Choreo"),
        "choreo-obsapi": ("wso2-enterprise", "choreo-obsapi", "Observability API for Choreo"),
        "choreo-runtime": ("wso2-enterprise", "choreo-runtime", "Choreo runtime environment"),
        "choreo-linker": ("wso2-enterprise", "choreo-linker", "Service linking and orchestration"),
        "choreo-negotiator": ("wso2-enterprise", "choreo-negotiator", "Service negotiation and discovery"),
        "choreo-ai-performance-analyzer": ("wso2-enterprise", "choreo-ai-performance-analyzer", "AI-powered performance analysis"),
        "choreo-analytics-apim": ("wso2-enterprise", "choreo-analytics-apim", "API Manager analytics integration"),
        "choreo-email": ("wso2-enterprise", "choreo-email", "Email notification service"),
        "choreo-apim": ("wso2-enterprise", "choreo-apim", "API Manager integration"),
        "choreo-testbase": ("wso2-enterprise", "choreo-testbase", "Testing framework and base"),
        "choreo-logging": ("wso2-enterprise", "choreo-logging", "Logging infrastructure"),
        "choreo-lang-server": ("wso2-enterprise", "choreo-lang-server", "Language server for Choreo"),
        "choreo-ai-anomaly-detector": ("wso2-enterprise", "choreo-ai-anomaly-detector", "AI-powered anomaly detection"),
        "choreo-sys-obsapi": ("wso2-enterprise", "choreo-sys-obsapi", "System observability API"),
        "choreo-ai-program-analyzer": ("wso2-enterprise", "choreo-ai-program-analyzer", "AI-powered program analysis"),
        "choreo-apim-devportal": ("wso2-enterprise", "choreo-apim-devportal", "API Manager developer portal"),
        "choreo-ai-deployment-optimizer": ("wso2-enterprise", "choreo-ai-deployment-optimizer", "AI-powered deployment optimization"),
        "choreo-ai-data-mapper": ("wso2-enterprise", "choreo-ai-data-mapper", "AI-powered data mapping"),
        "choreo-ai-capacity-planner": ("wso2-enterprise", "choreo-ai-capacity-planner", "AI-powered capacity planning"),
        # Other important Choreo repositories
        "choreo": ("wso2-enterprise", "choreo", "Main Choreo repository"),
        "choreo-control-plane": ("wso2-enterprise", "choreo-control-plane", "Choreo control plane"),
        "choreo-observability": ("wso2-enterprise", "choreo-observability", "Observability infrastructure"),
        "choreo-ci-tools": ("wso2-enterprise", "choreo-ci-tools", "CI/CD tools"),
        "choreo-www": ("wso2-enterprise", "choreo-www", "Choreo website"),
        "choreo-common-pipeline-templates": ("wso2-enterprise", "choreo-common-pipeline-templates", "Common pipeline templates"),
        "choreo-performance": ("wso2-enterprise", "choreo-performance", "Performance testing"),
        "choreo-idp": ("wso2-enterprise", "choreo-idp", "Identity provider"),
        "choreo-deployment": ("wso2-enterprise", "choreo-deployment", "Deployment configurations"),
        "choreo-default-backend": ("wso2-enterprise", "choreo-default-backend", "Default backend service"),
        "choreo-ai-data-mapper-vscode-plugin": ("wso2-enterprise", "choreo-ai-data-mapper-vscode-plugin", "VS Code plugin for data mapper"),
        "ballerina-registry-control-plane": ("wso2-enterprise", "ballerina-registry-control-plane", "Ballerina registry control plane"),
    }

    # Known aliases for components
    ALIASES = {
        "console": "choreo-console",
        "telemetry": "choreo-telemetry",
        "obs-api": "choreo-obsapi",
        "obsapi": "choreo-obsapi",
        "runtime": "choreo-runtime",
        "linker": "choreo-linker",
        "negotiator": "choreo-negotiator",
    }

    # Base GitHub URL
    GITHUB_BASE = "https://github.com"

    # Official Choreo documentation URLs
    OFFICIAL_DOCS = {
        "main": "https://wso2.com/choreo/",
        "docs": "https://wso2.com/choreo/docs/",
        "console": "https://console.choreo.dev",
    }

    def __init__(self):
        """Initialize the repository registry."""
        self._url_cache: Dict[str, str] = {}
        self._component_pattern = re.compile(r'choreo-[\w-]+', re.IGNORECASE)

    def get_component_url(self, component_name: str) -> Optional[str]:
        """
        Get the GitHub URL for a Choreo component repository.

        Args:
            component_name: Name of the component (e.g., 'choreo-console' or 'console')

        Returns:
            Full GitHub URL or None if component not found
        """
        # Normalize component name
        component_name = component_name.lower().strip()

        # Check cache first
        if component_name in self._url_cache:
            return self._url_cache[component_name]

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        # Look up in official repos
        if component_name in self.OFFICIAL_REPOS:
            org, repo, _ = self.OFFICIAL_REPOS[component_name]
            # Simple repository URL format: https://github.com/wso2/choreo-console
            url = f"{self.GITHUB_BASE}/{org}/{repo}"
            self._url_cache[component_name] = url
            return url

        return None

    def get_component_info(self, component_name: str) -> Optional[Dict[str, str]]:
        """
        Get detailed information about a Choreo component.

        Args:
            component_name: Name of the component

        Returns:
            Dictionary with component details or None if not found
        """
        component_name = component_name.lower().strip()

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        if component_name in self.OFFICIAL_REPOS:
            org, repo, description = self.OFFICIAL_REPOS[component_name]
            base_url = f"{self.GITHUB_BASE}/{org}/{repo}"
            return {
                "name": component_name,
                "organization": org,
                "repository": repo,
                "description": description,
                "url": base_url,
                "issues_url": f"{base_url}/issues",
                "docs_url": f"{base_url}#readme"
            }

        return None

    def is_valid_choreo_component(self, component_name: str) -> bool:
        """
        Check if a component name is a valid Choreo component.

        Args:
            component_name: Name to check

        Returns:
            True if valid Choreo component, False otherwise
        """
        component_name = component_name.lower().strip()

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        return component_name in self.OFFICIAL_REPOS

    def extract_components_from_text(self, text: str) -> List[str]:
        """
        Extract Choreo component names from text.

        Args:
            text: Text to search for component names

        Returns:
            List of found component names
        """
        matches = self._component_pattern.findall(text)
        # Deduplicate and normalize
        components = list(set(m.lower() for m in matches))
        # Filter to only valid components
        return [c for c in components if self.is_valid_choreo_component(c)]

    def get_all_components(self) -> List[Dict[str, str]]:
        """
        Get information about all registered Choreo components.

        Returns:
            List of component information dictionaries
        """
        components = []
        for component_name in sorted(self.OFFICIAL_REPOS.keys()):
            info = self.get_component_info(component_name)
            if info:
                components.append(info)
        return components

    def validate_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Validate if a GitHub URL corresponds to an official Choreo repository.
        Checks both wso2 and wso2-enterprise organizations, prefers wso2-enterprise.

        Args:
            url: GitHub URL to validate

        Returns:
            Component info if valid, None otherwise
        """
        # Extract org and repo from URL
        # Pattern: https://github.com/{org}/{repo}
        pattern = r'github\.com/([^/]+)/([^/]+?)(?:/|$|\?|#)'
        match = re.search(pattern, url)

        if not match:
            return None

        org, repo = match.groups()
        org = org.lower().strip()
        repo = repo.lower().strip()

        # Check if this matches any official repo
        for component_name, (official_org, official_repo, description) in self.OFFICIAL_REPOS.items():
            if repo == official_repo.lower():
                # Found matching repository name
                # Check if organization matches (wso2 or wso2-enterprise both acceptable)
                if org in ["wso2", "wso2-enterprise"]:
                    # Prefer wso2-enterprise over wso2 (has main Choreo information)
                    correct_org = "wso2-enterprise"
                    correct_url = f"{self.GITHUB_BASE}/{correct_org}/{official_repo}"

                    return {
                        "component": component_name,
                        "organization": correct_org,
                        "repository": official_repo,
                        "description": description,
                        "is_valid": True,
                        "correct_url": correct_url,
                        "needs_org_fix": org != correct_org
                    }

        return None

    def fix_github_url(self, url: str) -> Optional[str]:
        """
        Fix a potentially incorrect GitHub URL to point to the correct repository.
        Converts wso2-enterprise to wso2 organization if needed.

        Args:
            url: Potentially incorrect GitHub URL

        Returns:
            Corrected URL or None if cannot be fixed or already correct
        """
        validation = self.validate_github_url(url)
        if validation:
            correct_url = validation.get("correct_url")
            needs_fix = validation.get("needs_org_fix", False)

            # If it needs organization fix or the URL is different, return corrected
            if needs_fix or (correct_url and correct_url != url):
                return correct_url

        return None

    def enrich_text_with_urls(self, text: str) -> str:
        """
        Enrich text by adding GitHub URLs next to component mentions.

        Args:
            text: Text containing component names

        Returns:
            Enriched text with URLs
        """
        components = self.extract_components_from_text(text)

        enriched_text = text
        for component in components:
            url = self.get_component_url(component)
            if url:
                # Add URL reference if component is mentioned without a link
                # Only add if the URL isn't already in the text
                if url not in enriched_text:
                    # Find the component mention and add URL
                    pattern = r'\b' + re.escape(component) + r'\b'
                    replacement = f"{component} ({url})"
                    enriched_text = re.sub(pattern, replacement, enriched_text, count=1, flags=re.IGNORECASE)

        return enriched_text

    def get_component_markdown_links(self) -> str:
        """
        Generate a markdown list of all components with links.

        Returns:
            Markdown formatted string
        """
        components = self.get_all_components()
        lines = ["# Choreo Components\n"]

        for comp in components:
            lines.append(f"- **{comp['name']}**: {comp['description']}")
            lines.append(f"  - Repository: [{comp['organization']}/{comp['repository']}]({comp['url']})")
            lines.append("")

        return "\n".join(lines)

    def search_components(self, query: str) -> List[Dict[str, str]]:
        """
        Search for components matching a query.

        Args:
            query: Search query

        Returns:
            List of matching component info
        """
        query_lower = query.lower().strip()
        results = []

        for component_name, (org, repo, description) in self.OFFICIAL_REPOS.items():
            if (query_lower in component_name.lower() or
                query_lower in description.lower() or
                query_lower in repo.lower()):
                results.append({
                    "name": component_name,
                    "organization": org,
                    "repository": repo,
                    "description": description,
                    "url": f"{self.GITHUB_BASE}/{org}/{repo}",
                    "relevance_score": self._calculate_relevance(query_lower, component_name, description)
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results

    def _calculate_relevance(self, query: str, name: str, description: str) -> float:
        """Calculate relevance score for search results."""
        score = 0.0

        # Exact match in name
        if query == name.lower():
            score += 10.0
        # Query is in name
        elif query in name.lower():
            score += 5.0

        # Query in description
        if query in description.lower():
            score += 2.0

        # Word match
        query_words = set(query.split())
        name_words = set(name.lower().split('-'))
        desc_words = set(description.lower().split())

        common_with_name = len(query_words & name_words)
        common_with_desc = len(query_words & desc_words)

        score += common_with_name * 3.0
        score += common_with_desc * 1.0

        return score


# Singleton instance
_registry_instance: Optional[ChoreoRepoRegistry] = None


def get_choreo_registry() -> ChoreoRepoRegistry:
    """
    Get the singleton instance of the Choreo repository registry.

    Returns:
        ChoreoRepoRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        _registry_instance = ChoreoRepoRegistry()
        logger.info(f"Choreo repository registry initialized with {len(_registry_instance.OFFICIAL_REPOS)} components")

    return _registry_instance

