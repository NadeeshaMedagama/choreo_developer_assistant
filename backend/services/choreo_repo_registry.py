"""
Choreo Repository Registry

This module maintains a registry of official Choreo components and their GitHub repository locations.
It provides URL validation and resolution for Choreo-related repositories.

Now supports dynamic fetching of ALL repositories from wso2-enterprise organization via GitHub API.
"""

from typing import Dict, Optional, List
import re
import logging
import os

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
        self._dynamic_repos: Optional[List[Dict[str, str]]] = None
        self._github_service = None

    def _get_github_service(self):
        """Lazy load GitHub service with token from environment."""
        if self._github_service is None:
            from services.github_service import GitHubService
            github_token = os.getenv('GITHUB_TOKEN')
            self._github_service = GitHubService(token=github_token)
            logger.info(f"GitHub service initialized {'with' if github_token else 'without'} token")
        return self._github_service

    def fetch_all_wso2_enterprise_repos(self, use_cache: bool = True) -> List[Dict[str, str]]:
        """
        Dynamically fetch ALL repositories from wso2-enterprise organization via GitHub API.

        This replaces the hardcoded OFFICIAL_REPOS list with live data from GitHub.

        Args:
            use_cache: If True, use cached results. If False, fetch fresh from GitHub.

        Returns:
            List of repository info dicts with name, url, description, etc.
        """
        # Return cached if available and requested
        if use_cache and self._dynamic_repos is not None:
            logger.info(f"Using cached repository list ({len(self._dynamic_repos)} repos)")
            return self._dynamic_repos

        logger.info("Fetching ALL repositories from wso2-enterprise organization via GitHub API...")

        try:
            github_service = self._get_github_service()

            # Fetch all repos from wso2-enterprise org (no keyword filter to get ALL repos)
            all_repos = github_service.search_org_repositories(
                org="wso2-enterprise",
                keyword="",  # Empty keyword = get ALL repos
                per_page=100
            )

            logger.info(f"✅ Successfully fetched {len(all_repos)} repositories from wso2-enterprise")

            # Convert to our format
            formatted_repos = []
            for repo in all_repos:
                formatted_repos.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "organization": "wso2-enterprise",
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "") or "No description available",
                    "url": repo.get("url", ""),
                    "is_private": repo.get("is_private", True),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", "")
                })

            # Cache the results
            self._dynamic_repos = formatted_repos

            return formatted_repos

        except Exception as e:
            logger.error(f"❌ Failed to fetch repositories from GitHub: {e}")
            logger.warning("Falling back to hardcoded OFFICIAL_REPOS list")
            # Fallback to hardcoded list
            return self._get_hardcoded_repos_as_list()

    def fetch_choreo_repos_only(self, use_cache: bool = True) -> List[Dict[str, str]]:
        """
        Fetch only repositories with 'choreo' keyword from wso2-enterprise organization.

        Args:
            use_cache: If True, use cached results. If False, fetch fresh from GitHub.

        Returns:
            List of Choreo-related repository info dicts
        """
        logger.info("Fetching Choreo-related repositories from wso2-enterprise organization...")

        try:
            github_service = self._get_github_service()

            # Fetch repos with 'choreo' keyword
            choreo_repos = github_service.search_org_repositories(
                org="wso2-enterprise",
                keyword="choreo",
                per_page=100
            )

            logger.info(f"✅ Successfully fetched {len(choreo_repos)} Choreo repositories")

            # Convert to our format
            formatted_repos = []
            for repo in choreo_repos:
                formatted_repos.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "organization": "wso2-enterprise",
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "") or "No description available",
                    "url": repo.get("url", ""),
                    "is_private": repo.get("is_private", True),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", "")
                })

            return formatted_repos

        except Exception as e:
            logger.error(f"❌ Failed to fetch Choreo repositories from GitHub: {e}")
            logger.warning("Falling back to hardcoded OFFICIAL_REPOS list")
            return self._get_hardcoded_repos_as_list()

    def _get_hardcoded_repos_as_list(self) -> List[Dict[str, str]]:
        """Convert hardcoded OFFICIAL_REPOS dict to list format for fallback."""
        repos = []
        for comp_name, (org, repo, desc) in self.OFFICIAL_REPOS.items():
            repos.append({
                "name": repo,
                "full_name": f"{org}/{repo}",
                "organization": org,
                "repository": repo,
                "description": desc,
                "url": f"{self.GITHUB_BASE}/{org}/{repo}",
                "is_private": True,
                "language": "",
                "updated_at": ""
            })
        return repos

    def get_component_url(self, component_name: str, use_dynamic: bool = True) -> Optional[str]:
        """
        Get the GitHub URL for a Choreo component repository.
        Now searches in dynamically fetched repos, not just hardcoded ones.

        Args:
            component_name: Name of the component (e.g., 'choreo-console' or 'project manager')
            use_dynamic: If True, search in all fetched repos. If False, use hardcoded only.

        Returns:
            Full GitHub URL or None if component not found
        """
        # Normalize component name
        component_name = component_name.lower().strip()

        # Check cache first
        cache_key = f"{component_name}_{use_dynamic}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        # Check aliases (hardcoded shortcuts)
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        # First try exact match in hardcoded repos for performance
        if component_name in self.OFFICIAL_REPOS:
            org, repo, _ = self.OFFICIAL_REPOS[component_name]
            url = f"{self.GITHUB_BASE}/{org}/{repo}"
            self._url_cache[cache_key] = url
            return url

        # If not found and dynamic search enabled, search all repos
        if use_dynamic:
            search_results = self.search_components(component_name, use_dynamic=True)
            if search_results:
                # Return the best match
                best_match = search_results[0]
                url = best_match.get("url")
                if url:
                    self._url_cache[cache_key] = url
                    return url

        return None

    def get_component_info(self, component_name: str, use_dynamic: bool = True) -> Optional[Dict[str, str]]:
        """
        Get detailed information about a Choreo component.
        Now searches in dynamically fetched repos, not just hardcoded ones.

        Args:
            component_name: Name of the component
            use_dynamic: If True, search in all fetched repos. If False, use hardcoded only.

        Returns:
            Dictionary with component details or None if not found
        """
        component_name = component_name.lower().strip()

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        # First try hardcoded for exact matches
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

        # If not found and dynamic search enabled, search all repos
        if use_dynamic:
            search_results = self.search_components(component_name, use_dynamic=True)
            if search_results:
                # Return the best match
                best_match = search_results[0]
                base_url = best_match.get("url", "")
                return {
                    "name": best_match.get("name", ""),
                    "organization": best_match.get("organization", "wso2-enterprise"),
                    "repository": best_match.get("repository", ""),
                    "description": best_match.get("description", "No description available"),
                    "url": base_url,
                    "issues_url": f"{base_url}/issues" if base_url else "",
                    "docs_url": f"{base_url}#readme" if base_url else "",
                    "language": best_match.get("language", ""),
                    "is_private": best_match.get("is_private", True)
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

    def search_components(self, query: str, use_dynamic: bool = True) -> List[Dict[str, str]]:
        """
        Search for components matching a query.
        Now uses dynamic repository fetching to search ALL repos, not just hardcoded ones.

        Args:
            query: Search query
            use_dynamic: If True, search in dynamically fetched repos. If False, use hardcoded list.

        Returns:
            List of matching component info sorted by relevance
        """
        query_lower = query.lower().strip()
        results = []

        # Get repos to search (dynamic or hardcoded)
        if use_dynamic:
            try:
                # Fetch all repos dynamically
                repos = self.fetch_all_wso2_enterprise_repos(use_cache=True)
            except Exception as e:
                logger.error(f"Failed to fetch dynamic repos for search, using hardcoded: {e}")
                repos = self._get_hardcoded_repos_as_list()
        else:
            repos = self._get_hardcoded_repos_as_list()

        # Search through all repos
        for repo in repos:
            repo_name = repo.get("name", "").lower()
            repo_desc = repo.get("description", "").lower()

            # Check if query matches name or description
            if (query_lower in repo_name or
                query_lower in repo_desc or
                self._fuzzy_match(query_lower, repo_name) or
                self._fuzzy_match(query_lower, repo_desc)):

                results.append({
                    "name": repo.get("name", ""),
                    "organization": repo.get("organization", "wso2-enterprise"),
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "No description available"),
                    "url": repo.get("url", ""),
                    "relevance_score": self._calculate_relevance(query_lower, repo_name, repo_desc),
                    "language": repo.get("language", ""),
                    "is_private": repo.get("is_private", True)
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        logger.info(f"Search for '{query}' found {len(results)} matching repositories")

        return results

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """
        Check if query words fuzzy match the text.

        Examples:
            - "project manager" matches "choreo-product-management"
            - "security token service" matches "choreo-sts" or "token-service"
        """
        query_words = query.split()
        text_lower = text.lower()

        # Check if all query words appear in text (in any order)
        matches = sum(1 for word in query_words if word in text_lower)

        # Enhanced synonym mapping for better matching
        synonyms = {
            'manager': ['management', 'mgmt', 'mgr', 'mgt'],
            'service': ['svc', 'srv', 'sts'],  # STS = Security Token Service
            'security': ['sec', 'auth', 'authz', 'authorization'],
            'token': ['tok'],
            'project': ['proj', 'product'],
            'built-in': ['builtin', 'built', 'internal'],
        }

        # Acronym detection for common patterns
        # "security token service" should match "sts"
        acronyms = {
            'sts': ['security token service', 'security token', 'token service'],
            'idp': ['identity provider'],
            'apim': ['api manager', 'api management'],
            'iam': ['identity access management'],
        }

        # Check if text contains an acronym that matches the query
        for acronym, expansions in acronyms.items():
            if acronym in text_lower:
                for expansion in expansions:
                    if expansion in query.lower():
                        matches += 3.0  # Strong match for acronym expansion
                        break

        # Check synonyms
        for word in query_words:
            if word in synonyms:
                for syn in synonyms[word]:
                    if syn in text_lower:
                        matches += 0.8  # Higher weight for synonyms

        # Return True if at least half the query words match
        return matches >= len(query_words) * 0.5

    def _calculate_relevance(self, query: str, name: str, description: str) -> float:
        """Calculate relevance score for search results."""
        score = 0.0
        query_lower = query.lower()
        name_lower = name.lower()
        description_lower = description.lower()

        # Exact match in name (highest priority)
        if query_lower == name_lower:
            score += 100.0
        # Query is in name
        elif query_lower in name_lower:
            score += 50.0

        # Exact match in description (high priority for finding specific services)
        if query_lower in description_lower:
            score += 30.0

        # Check for exact phrase match in description (very important)
        if query_lower in description_lower:
            score += 40.0

        # Bonus for choreo-prefixed repos when query contains "choreo"
        if 'choreo' in query_lower and name_lower.startswith('choreo-'):
            score += 25.0

        # Word matching
        query_words = set(query_lower.split())
        name_words = set(name_lower.replace('-', ' ').replace('_', ' ').split())
        desc_words = set(description_lower.split())

        common_with_name = len(query_words & name_words)
        common_with_desc = len(query_words & desc_words)

        score += common_with_name * 15.0
        score += common_with_desc * 10.0

        # Bonus for matching all query words
        if query_words.issubset(name_words):
            score += 60.0
        if query_words.issubset(desc_words):
            score += 50.0

        # Enhanced synonym and acronym matching
        synonyms = {
            'manager': ['management', 'mgmt', 'mgr', 'mgt'],
            'service': ['svc', 'srv', 'sts'],
            'security': ['sec', 'auth', 'authz'],
            'token': ['tok'],
            'project': ['proj', 'product'],
            'product': ['proj', 'project'],  # Bidirectional synonym
        }

        # Acronym bonus (very important for matching like "sts" to "security token service")
        acronyms = {
            'sts': 'security token service',
            'idp': 'identity provider',
            'apim': 'api manager',
        }

        # Check if name contains acronym and query is the expansion
        for acronym, expansion in acronyms.items():
            if acronym in name_lower and expansion in query_lower:
                score += 80.0  # Very high score for acronym match
            if acronym in name_lower and any(word in query_lower for word in expansion.split()):
                score += 40.0  # Partial acronym match

        # Check synonyms with higher weights
        for word in query_words:
            if word in synonyms:
                for syn in synonyms[word]:
                    if syn in name_lower:
                        score += 20.0
                    if syn in description_lower:
                        score += 15.0

        return score

    def generate_system_prompt_urls(self, use_dynamic: bool = True) -> str:
        """
        Generate a comprehensive system prompt section with all Choreo repository URLs.
        This ensures the LLM always uses the correct wso2-enterprise organization URLs.

        Args:
            use_dynamic: If True, fetch repos dynamically from GitHub. If False, use hardcoded list.

        Returns:
            Formatted string with repository URL instructions
        """
        prompt = """REPOSITORY URLS - CRITICAL RULES:
⚠️ ALWAYS use wso2-enterprise organization for ALL Choreo repositories
⚠️ NEVER use github.com/wso2/{repo} - it's WRONG and leads to 404 errors
⚠️ Each Choreo component has its OWN separate repository

CORRECT URL FORMAT:
https://github.com/wso2-enterprise/{repository-name}

"""

        # Get repositories dynamically or from hardcoded list
        if use_dynamic:
            try:
                repos = self.fetch_all_wso2_enterprise_repos(use_cache=True)
                prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, dynamically fetched):\n"
            except Exception as e:
                logger.error(f"Failed to fetch dynamic repos, using hardcoded list: {e}")
                repos = self._get_hardcoded_repos_as_list()
                prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, from fallback list):\n"
        else:
            repos = self._get_hardcoded_repos_as_list()
            prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, from static list):\n"

        # Group repos for better readability
        choreo_repos = [r for r in repos if 'choreo' in r['name'].lower()]
        other_repos = [r for r in repos if 'choreo' not in r['name'].lower()]

        if choreo_repos:
            prompt += "\nChoreo Platform Repositories:\n"
            for repo in sorted(choreo_repos, key=lambda x: x['name']):
                desc = repo.get('description', 'No description')
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                prompt += f"  • {repo['name']}: {repo['url']}\n    ({desc})\n"

        if other_repos:
            prompt += f"\nOther wso2-enterprise Repositories ({len(other_repos)}):\n"
            for repo in sorted(other_repos[:20], key=lambda x: x['name']):  # Limit to first 20 to avoid prompt overflow
                prompt += f"  • {repo['name']}: {repo['url']}\n"
            if len(other_repos) > 20:
                prompt += f"  ... and {len(other_repos) - 20} more repositories\n"

        prompt += """

CRITICAL REMINDERS:
✓ ONLY use wso2-enterprise organization URLs
✓ Format: https://github.com/wso2-enterprise/{repository-name}
✗ NEVER use: https://github.com/wso2/{anything} (this is PUBLIC org, not Choreo)
✗ Do NOT make up URLs - only use the ones listed above

If you need to reference a repository not listed above, say you don't have the URL rather than guessing.
"""

        return prompt


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

