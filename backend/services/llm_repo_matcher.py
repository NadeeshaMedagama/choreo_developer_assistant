"""
LLM-Powered Repository Matcher

This service uses the LLM to intelligently match user queries to Choreo repositories
by analyzing the context retrieved from the knowledge base (which contains all 154 repos).
"""

import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class LLMRepoMatcher:
    """
    Intelligently matches user queries to repository URLs using LLM and RAG context.

    This replaces the hardcoded registry approach with a dynamic, context-aware system
    that can work with all 154 Choreo repositories in wso2-enterprise.
    """

    def __init__(self):
        self.github_url_pattern = re.compile(
            r'https://github\.com/wso2-enterprise/[\w\-]+',
            re.IGNORECASE
        )
        # Import registry for fallback
        self._registry = None

    def _get_registry(self):
        """Lazy load the choreo registry."""
        if self._registry is None:
            try:
                from services.choreo_repo_registry import get_choreo_registry
                self._registry = get_choreo_registry()
            except ImportError:
                try:
                    from backend.services.choreo_repo_registry import get_choreo_registry
                    self._registry = get_choreo_registry()
                except ImportError:
                    logger.warning("Could not import choreo_repo_registry - registry features disabled")
                    return None
        return self._registry

    def extract_repo_urls_from_context(self, context: str) -> List[str]:
        """
        Extract all GitHub repository URLs from the RAG context.

        Args:
            context: The retrieved context from the knowledge base

        Returns:
            List of unique repository URLs found in the context
        """
        if not context:
            return []

        # Find all wso2-enterprise repo URLs
        urls = self.github_url_pattern.findall(context)

        # Deduplicate and sort
        unique_urls = sorted(set(urls))

        logger.info(f"Extracted {len(unique_urls)} repository URLs from context")
        return unique_urls

    def extract_repo_urls_from_sources(self, sources: List[Dict]) -> List[str]:
        """
        Extract repository URLs from source documents.

        Args:
            sources: List of source document dictionaries with metadata

        Returns:
            List of unique repository URLs from source metadata
        """
        urls = set()

        for source in sources:
            metadata = source.get('metadata', {})

            # Check metadata for repository URL
            repo_url = metadata.get('repository_url') or metadata.get('url')
            if repo_url and 'github.com/wso2-enterprise' in repo_url:
                # Normalize to base repo URL (remove file paths, branches, etc.)
                base_url = self._normalize_repo_url(repo_url)
                if base_url:
                    urls.add(base_url)

            # Also check repository field (might be org/repo format)
            repository = metadata.get('repository', '')
            if repository and '/' in repository:
                # Convert "wso2-enterprise/choreo-console" to URL
                if repository.startswith('wso2-enterprise/'):
                    repo_name = repository.split('/', 1)[1]
                    urls.add(f"https://github.com/wso2-enterprise/{repo_name}")

        logger.info(f"Extracted {len(urls)} repository URLs from {len(sources)} sources")
        return sorted(list(urls))

    def _normalize_repo_url(self, url: str) -> Optional[str]:
        """
        Normalize a GitHub URL to its base repository URL.

        Examples:
            https://github.com/wso2-enterprise/choreo-console/blob/main/README.md
            -> https://github.com/wso2-enterprise/choreo-console

        Args:
            url: GitHub URL (may include paths, branches, etc.)

        Returns:
            Base repository URL or None if invalid
        """
        match = re.match(r'(https://github\.com/wso2-enterprise/[\w\-]+)', url)
        if match:
            return match.group(1)
        return None

    def create_repository_context_for_llm(
        self,
        context_urls: List[str],
        source_urls: List[str],
        include_registry: bool = True
    ) -> str:
        """
        Create a formatted list of available repositories for the LLM prompt.

        CRITICAL: Always includes the complete Choreo repository registry to ensure
        the LLM has access to ALL correct URLs and never generates wrong ones.

        Args:
            context_urls: URLs extracted from RAG context
            source_urls: URLs extracted from source metadata
            include_registry: Whether to include the full registry (default True)

        Returns:
            Formatted string with available repository URLs
        """
        # Combine and deduplicate context URLs
        context_all_urls = sorted(set(context_urls + source_urls))

        # Get the full registry for CORRECT URLs
        registry = self._get_registry()

        # Build comprehensive URL guidance
        output = """🔴 CRITICAL: CHOREO REPOSITORY URL RULES 🔴

⚠️ ALL Choreo repositories are in the PRIVATE wso2-enterprise organization
⚠️ NEVER use github.com/wso2/choreo-* URLs - they are WRONG (404 errors)
⚠️ ALWAYS use github.com/wso2-enterprise/{repo-name} format

"""

        # Add context-specific URLs if found
        if context_all_urls:
            output += f"""📌 URLs FROM CURRENT CONTEXT (highest priority):
"""
            for url in context_all_urls:
                output += f"  ✓ {url}\n"
            output += "\n"

        # Include the COMPLETE registry to prevent wrong URL generation
        if include_registry and registry:
            output += """📚 COMPLETE CHOREO REPOSITORY REGISTRY (use ONLY these URLs):

"""
            # Get all repos from registry
            repos = registry._get_hardcoded_repos_as_list()

            # Group by category for clarity
            choreo_core = []
            choreo_ai = []
            choreo_apim = []
            choreo_dp = []
            choreo_other = []

            for repo in repos:
                name = repo.get('name', '').lower()
                url = repo.get('url', '')
                desc = repo.get('description', '')[:60]

                if 'choreo-ai' in name:
                    choreo_ai.append((name, url, desc))
                elif 'choreo-apim' in name or 'apim' in name:
                    choreo_apim.append((name, url, desc))
                elif 'choreodp' in name or 'choreo-dp' in name or 'dataplane' in name:
                    choreo_dp.append((name, url, desc))
                elif 'choreo' in name:
                    choreo_core.append((name, url, desc))
                else:
                    choreo_other.append((name, url, desc))

            if choreo_core:
                output += "CORE CHOREO REPOSITORIES:\n"
                for name, url, desc in sorted(choreo_core)[:30]:
                    output += f"  • {name}: {url}\n"
                output += "\n"

            if choreo_ai:
                output += "AI SERVICE REPOSITORIES:\n"
                for name, url, desc in sorted(choreo_ai):
                    output += f"  • {name}: {url}\n"
                output += "\n"

            if choreo_apim:
                output += "API MANAGEMENT REPOSITORIES:\n"
                for name, url, desc in sorted(choreo_apim):
                    output += f"  • {name}: {url}\n"
                output += "\n"

            if choreo_dp:
                output += "DATA PLANE REPOSITORIES:\n"
                for name, url, desc in sorted(choreo_dp):
                    output += f"  • {name}: {url}\n"
                output += "\n"

        output += """
🚫 DO NOT:
- Generate URLs that are not in the registry above
- Use github.com/wso2/ for Choreo repos (WRONG organization)
- Make up repository names or guess URLs
- Provide URLs that will result in 404 errors

✅ DO:
- Use ONLY URLs from the registry above
- Use wso2-enterprise organization for ALL Choreo repos
- If a repo is not listed, say it's not in the knowledge base
"""

        return output

    def generate_enhanced_system_prompt(
        self,
        base_context: str,
        context_urls: List[str],
        source_urls: List[str]
    ) -> str:
        """
        Generate an enhanced system prompt with available repository URLs.

        Args:
            base_context: The RAG context content
            context_urls: URLs extracted from context
            source_urls: URLs extracted from sources

        Returns:
            Enhanced system prompt with repository URL guidance
        """
        repo_context = self.create_repository_context_for_llm(context_urls, source_urls)

        prompt = f"""You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- You have access to BOTH public documentation AND internal/private repositories
- ALWAYS use the provided context from the knowledge base to answer accurately
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Only say information is not available if it's truly not in the provided context
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

🔴 CRITICAL RULES FOR GITHUB REPOSITORY URLs (STRICTLY ENFORCED):

1. ✅ ONLY Use URLs From the Available List Below
   - You will see a list of "AVAILABLE REPOSITORY URLs" 
   - ONLY mention URLs that appear in that list
   - These URLs were found in the ingested knowledge base content

2. ❌ NEVER Generate, Guess, or Construct URLs
   - Do NOT create URLs like github.com/wso2-enterprise/choreo-*
   - Do NOT assume a repository exists based on component names
   - If a repo is not in the available list, it's not in the knowledge base

3. 🔒 These Are PRIVATE Repositories
   - ALL Choreo repositories are in the private wso2-enterprise organization
   - Users need proper GitHub authentication to access them
   - Even valid URLs may return 404 for unauthorized users

4. ✅ When Repository IS in Available List:
   - Provide the URL from the list
   - Share details from the context about that repository
   - Explain what the repository contains

5. ✅ When Repository is NOT in Available List:
   - Do NOT mention the repository URL at all
   - Do NOT say the URL is "not available" or provide placeholder text
   - Simply omit the URL and provide other helpful information from the context
   - You can still mention the component name without the URL

6. 🎯 What You CAN Always Share:
   - Component names and descriptions
   - Architectural information from context
   - API endpoints and configurations
   - Implementation details from context
   - Links to public documentation (wso2.com/choreo/docs/...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{repo_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CONTEXT FROM KNOWLEDGE BASE:
{base_context if base_context else "No specific context found for this query."}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ REMEMBER: Only use repository URLs from the "AVAILABLE REPOSITORY URLs" list above.
If a URL is not in that list, simply omit it - do not mention it or say it's unavailable.
"""
        return prompt

    def get_all_choreo_repos_from_db(self, vector_client, top_k: int = 100) -> List[str]:
        """
        Query the vector database to find ALL Choreo repositories.

        This performs a broad search to find as many Choreo repos as possible,
        not just those relevant to a specific query.

        Args:
            vector_client: The vector database client
            top_k: Number of documents to retrieve

        Returns:
            List of unique repository URLs found in the database
        """
        try:
            # Search with broad Choreo-related queries to get diversity
            search_queries = [
                "choreo repository",
                "wso2-enterprise choreo",
                "choreo component",
            ]

            all_urls = set()

            for query in search_queries:
                try:
                    results = vector_client.search(
                        query_text=query,
                        top_k=top_k,
                        filter_expr=None
                    )

                    # Extract URLs from results
                    for result in results:
                        # Check metadata
                        metadata = result.get('metadata', {})
                        repo = metadata.get('repository', '')
                        repo_url = metadata.get('repository_url', '') or metadata.get('url', '')

                        if repo and 'wso2-enterprise' in repo:
                            if '/' in repo:
                                repo_name = repo.split('/', 1)[1]
                                all_urls.add(f"https://github.com/wso2-enterprise/{repo_name}")
                            else:
                                all_urls.add(f"https://github.com/wso2-enterprise/{repo}")

                        if repo_url and 'github.com/wso2-enterprise' in repo_url:
                            base_url = self._normalize_repo_url(repo_url)
                            if base_url:
                                all_urls.add(base_url)

                        # Check content for URLs
                        content = result.get('content', '')
                        content_urls = self.github_url_pattern.findall(content)
                        all_urls.update(content_urls)

                except Exception as e:
                    logger.warning(f"Error searching with query '{query}': {e}")
                    continue

            logger.info(f"Found {len(all_urls)} unique Choreo repos in vector database")
            return sorted(list(all_urls))

        except Exception as e:
            logger.error(f"Error querying vector database for repos: {e}")
            return []

    def enhance_with_registry_fallback(self, extracted_urls: List[str]) -> List[str]:
        """
        If only a few URLs were extracted, add known repos from the registry.

        Args:
            extracted_urls: URLs extracted from RAG context

        Returns:
            Enhanced list with registry repos if extraction was limited
        """
        # If we found enough URLs, use them
        if len(extracted_urls) >= 10:
            return extracted_urls

        # Otherwise, supplement with registry
        logger.info(f"Only {len(extracted_urls)} URLs extracted, adding registry repos")

        registry = self._get_registry()
        registry_components = registry.get_all_components()
        registry_urls = [comp['url'] for comp in registry_components]

        # Combine and deduplicate
        all_urls = set(extracted_urls + registry_urls)

        logger.info(f"Enhanced to {len(all_urls)} URLs with registry fallback")
        return sorted(list(all_urls))

    def get_all_wso2_enterprise_repos(self, keyword: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get ALL repositories from wso2-enterprise organization dynamically via GitHub API.

        This is used when user asks for "all repos" or "all choreo repos".

        Args:
            keyword: Optional keyword filter (e.g., "choreo" to get only choreo repos)

        Returns:
            List of repository info dicts with name, url, description, etc.
        """
        registry = self._get_registry()

        if keyword:
            logger.info(f"Fetching repositories with keyword: {keyword}")
            if keyword.lower() == "choreo":
                return registry.fetch_choreo_repos_only(use_cache=True)
            else:
                # For other keywords, fetch all and filter
                all_repos = registry.fetch_all_wso2_enterprise_repos(use_cache=True)
                keyword_lower = keyword.lower()
                filtered = [
                    r for r in all_repos
                    if keyword_lower in r['name'].lower() or keyword_lower in r.get('description', '').lower()
                ]
                logger.info(f"Filtered to {len(filtered)} repos matching '{keyword}'")
                return filtered
        else:
            logger.info("Fetching ALL wso2-enterprise repositories")
            return registry.fetch_all_wso2_enterprise_repos(use_cache=True)

    def find_repository_by_name(self, query: str) -> Optional[Dict[str, str]]:
        """
        Find a specific repository by name or description.
        Uses dynamic search across all repos.

        Examples:
            - "project manager" -> finds "choreo-product-management"
            - "security token service" -> finds "choreo-sts" or similar
            - "choreo console" -> finds "choreo-console"

        Args:
            query: Repository name or description to search for

        Returns:
            Repository info dict if found, None otherwise
        """
        registry = self._get_registry()

        # Search using enhanced search with fuzzy matching
        results = registry.search_components(query, use_dynamic=True)

        if results:
            logger.info(f"Found {len(results)} matches for '{query}', returning best match")
            return results[0]  # Return best match
        else:
            logger.warning(f"No repository found matching '{query}'")
            return None

    def format_single_repo_response(self, repo: Dict[str, str], query: str = "") -> str:
        """
        Format a single repository for display.

        Args:
            repo: Repository dictionary
            query: Original query (for context)

        Returns:
            Formatted string
        """
        if not repo:
            return f"Repository not found for query: '{query}'"

        response = f"**Repository Found: {repo.get('name', 'Unknown')}**\n\n"
        response += f"- **URL**: {repo.get('url', 'N/A')}\n"
        response += f"- **Organization**: {repo.get('organization', 'wso2-enterprise')}\n"

        if repo.get('description'):
            response += f"- **Description**: {repo.get('description')}\n"

        if repo.get('language'):
            response += f"- **Language**: {repo.get('language')}\n"

        response += f"- **Private**: {'Yes' if repo.get('is_private', True) else 'No'}\n"

        if repo.get('relevance_score'):
            response += f"- **Match Score**: {repo.get('relevance_score'):.2f}\n"

        response += f"\n*Note: This is a private repository requiring wso2-enterprise organization access.*\n"

        return response

    def format_repos_for_response(self, repos: List[Dict[str, str]], query_context: str = "") -> str:
        """
        Format repository list for LLM response.

        Args:
            repos: List of repository dicts
            query_context: Optional context about what the user asked for

        Returns:
            Formatted string with repository information
        """
        if not repos:
            return "No repositories found matching the criteria."

        header = f"Found {len(repos)} repositories"
        if query_context:
            header += f" {query_context}"
        header += " in the wso2-enterprise organization:\n\n"

        # Group by choreo and non-choreo
        choreo_repos = [r for r in repos if 'choreo' in r['name'].lower()]
        other_repos = [r for r in repos if 'choreo' not in r['name'].lower()]

        result = header

        if choreo_repos:
            result += f"**Choreo Repositories ({len(choreo_repos)}):**\n\n"
            for repo in sorted(choreo_repos, key=lambda x: x['name']):
                result += f"- **{repo['name']}**: {repo['url']}\n"
                if repo.get('description'):
                    result += f"  - {repo['description']}\n"
                result += "\n"

        if other_repos:
            result += f"\n**Other wso2-enterprise Repositories ({len(other_repos)}):**\n\n"
            for repo in sorted(other_repos, key=lambda x: x['name']):
                result += f"- **{repo['name']}**: {repo['url']}\n"
                if repo.get('description'):
                    result += f"  - {repo['description']}\n"
                result += "\n"

        result += f"\n**Total: {len(repos)} repositories**\n"
        result += "\n*Note: All these repositories are private and require wso2-enterprise organization access.*\n"

        return result


# Singleton instance
_matcher_instance: Optional[LLMRepoMatcher] = None


def get_llm_repo_matcher() -> LLMRepoMatcher:
    """
    Get the singleton instance of the LLM repository matcher.

    Returns:
        LLMRepoMatcher instance
    """
    global _matcher_instance

    if _matcher_instance is None:
        _matcher_instance = LLMRepoMatcher()
        logger.info("LLM repository matcher initialized")

    return _matcher_instance
