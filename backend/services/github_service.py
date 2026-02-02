import requests
import base64
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from utils.logger import get_logger

logger = get_logger(__name__)

# Safety limits to prevent crashes
MAX_RECURSION_DEPTH = 10  # Limit directory depth
MAX_FILES_PER_SCAN = 1000  # Stop after finding this many files
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per file
API_CALL_DELAY = 0.02  # Reduced from 0.1 to 0.02 (20ms) for faster scanning
MAX_PARALLEL_REQUESTS = 10  # Number of parallel directory scans

# API Definition file patterns (keywords to look for in YAML/JSON file paths)
API_KEYWORDS_IN_PATH = [
    "openapi", "swagger", "api", "spec", "specification",
    "rest", "graphql", "grpc", "schema", "endpoint",
    "asyncapi", "raml", "wadl", "wsdl"
]

# Directories that typically contain API definitions
API_DIRECTORIES = [
    "api", "apis", "schema", "schemas", "graphql",
    "proto", "protos", "specification", "specifications",
    "openapi", "swagger", "grpc", "definitions"
]

# API Definition file extensions
API_DEFINITION_EXTENSIONS = (
    ".graphql",      # GraphQL schema files
    ".gql",          # GraphQL shorthand extension
    ".proto",        # Protocol Buffers (gRPC)
)


class GitHubService:
    """Service for interacting with GitHub API to fetch markdown files."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub service.

        Args:
            token: GitHub personal access token (optional but recommended for higher rate limits)
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            # Use Bearer token format (newer GitHub API standard)
            self.headers["Authorization"] = f"Bearer {token}"
            logger.info("GitHub service initialized with authentication token")
        else:
            logger.warning("GitHub service initialized without token - rate limits will be lower (60/hour)")

        # Cache for directory contents to avoid redundant API calls
        self._cache = {}
        self._cache_lock = threading.Lock()

    def _make_request(self, url: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Make a GET request to GitHub API with optional caching."""
        # Check cache first
        if use_cache:
            with self._cache_lock:
                if url in self._cache:
                    logger.debug(f"Cache hit for: {url}")
                    return self._cache[url]

        try:
            # Reduced delay for faster scanning
            time.sleep(API_CALL_DELAY)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            # Cache the result
            if use_cache:
                with self._cache_lock:
                    self._cache[url] = result

            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise

    def get_repo_contents(self, owner: str, repo: str, path: str = "", use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get contents of a repository path.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within the repository (empty string for root)
            use_cache: Whether to use cached results

        Returns:
            List of file/directory information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        logger.debug(f"Fetching contents from: {url}")
        return self._make_request(url, use_cache=use_cache)

    def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """
        Get the content of a specific file.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to the file

        Returns:
            Decoded file content as string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        logger.info(f"Fetching file: {path}")

        data = self._make_request(url)

        if data and "content" in data:
            # Check file size before decoding
            file_size = data.get("size", 0)
            if file_size > MAX_FILE_SIZE_BYTES:
                logger.warning(f"⚠️  File too large ({file_size} bytes), skipping: {path}")
                raise ValueError(f"File exceeds maximum size ({MAX_FILE_SIZE_BYTES} bytes): {path}")

            # Content is base64 encoded
            content = base64.b64decode(data["content"]).decode("utf-8")
            logger.debug(f"Fetched {len(content)} characters from {path}")
            return content
        else:
            raise ValueError(f"Could not retrieve content for {path}")

    def get_file_bytes(self, owner: str, repo: str, path: str) -> bytes:
        """
        Get the raw bytes of a file (useful for binary files like images).

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to the file

        Returns:
            Raw file bytes
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        logger.debug(f"Fetching raw bytes for file: {path}")

        data = self._make_request(url)

        if data and "content" in data:
            # Check file size
            file_size = data.get("size", 0)
            if file_size > MAX_FILE_SIZE_BYTES:
                logger.warning(f"⚠️  File too large ({file_size} bytes), skipping: {path}")
                raise ValueError(f"File exceeds maximum size ({MAX_FILE_SIZE_BYTES} bytes): {path}")

            # Content is base64 encoded
            content_bytes = base64.b64decode(data["content"])
            return content_bytes
        else:
            raise ValueError(f"Could not retrieve bytes for {path}")

    def get_file_metadata(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file including SHA hash.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to the file

        Returns:
            File metadata including sha, size, and download_url
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        data = self._make_request(url)

        return {
            "sha": data.get("sha", ""),
            "size": data.get("size", 0),
            "path": path,
            "download_url": data.get("download_url", "")
        }

    def find_all_markdown_files(self, owner: str, repo: str, path: str = "", _depth: int = 0, _files_found: List = None) -> List[Dict[str, str]]:
        """
        Recursively find all .md files ONLY in a repository with safety limits.

        NOTE: This method ONLY searches for .md (markdown) files.
        API definition files (.yaml, .yml, .json) are NOT included.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Starting path (empty for root)
            _depth: Current recursion depth (internal)
            _files_found: Shared list for tracking total files (internal)

        Returns:
            List of dicts with 'path', 'name', 'sha', and 'url' for each .md file
        """
        # Initialize shared files list on first call
        if _files_found is None:
            _files_found = []
            logger.info(f"🔍 Searching for MARKDOWN FILES ONLY (.md extension)")
            logger.info(f"ℹ️  API definition files (.yaml, .yml, .json) will be SKIPPED")
            logger.info(f"⚡ Using FAST PARALLEL SEARCH for speed optimization")

        markdown_files = []

        # Safety check: prevent infinite recursion
        if _depth > MAX_RECURSION_DEPTH:
            logger.warning(f"⚠️  Max recursion depth ({MAX_RECURSION_DEPTH}) reached at path: {path}")
            return markdown_files

        # Safety check: prevent too many files
        if len(_files_found) >= MAX_FILES_PER_SCAN:
            logger.warning(f"⚠️  Max file limit ({MAX_FILES_PER_SCAN}) reached, stopping scan")
            return markdown_files

        try:
            contents = self.get_repo_contents(owner, repo, path)

            if not contents:
                logger.warning(f"No contents returned for path: {path}")
                return []

            # Separate files and directories
            directories = []

            for item in contents:
                # Check file limit again
                if len(_files_found) >= MAX_FILES_PER_SCAN:
                    logger.warning(f"⚠️  Max file limit reached during scan")
                    break

                item_path = item.get("path", "")
                item_type = item.get("type", "")
                item_name = item.get("name", "")
                item_size = item.get("size", 0)

                # ONLY PROCESS .md FILES - NO API DEFINITION FILES
                if item_type == "file" and item_name.endswith(".md"):
                    # Check file size before adding
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  Skipping large file ({item_size} bytes): {item_path}")
                        continue

                    markdown_files.append({
                        "path": item_path,
                        "name": item_name,
                        "url": item.get("html_url", ""),
                        "sha": item.get("sha", ""),
                        "size": item_size
                    })
                    _files_found.append(item_path)
                    logger.info(f"✓ Found markdown file: {item_path} ({item_size} bytes)")

                elif item_type == "dir":
                    directories.append(item_path)

            # Process directories in parallel for speed (only at depth 0 and 1)
            if directories and _depth <= 1:
                logger.info(f"⚡ Scanning {len(directories)} directories in parallel...")
                with ThreadPoolExecutor(max_workers=MAX_PARALLEL_REQUESTS) as executor:
                    future_to_dir = {
                        executor.submit(
                            self.find_all_markdown_files,
                            owner, repo, dir_path,
                            _depth + 1, _files_found
                        ): dir_path
                        for dir_path in directories
                    }

                    for future in as_completed(future_to_dir):
                        dir_path = future_to_dir[future]
                        try:
                            sub_files = future.result()
                            markdown_files.extend(sub_files)
                        except Exception as e:
                            logger.error(f"Error scanning directory {dir_path}: {e}")
            else:
                # For deeper levels, use sequential scanning to avoid too many threads
                for dir_path in directories:
                    logger.debug(f"Searching directory (depth {_depth + 1}): {dir_path}")
                    sub_files = self.find_all_markdown_files(
                        owner, repo, dir_path,
                        _depth=_depth + 1,
                        _files_found=_files_found
                    )
                    markdown_files.extend(sub_files)

        except Exception as e:
            logger.error(f"Error processing path {path}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            # Re-raise to propagate the error instead of silently returning empty list
            if path == "":  # Only raise for root path
                raise

        return markdown_files

    def find_all_markdown_files_fast(self, owner: str, repo: str) -> List[Dict[str, str]]:
        """
        ULTRA-FAST version: Find all .md files using GitHub Tree API (single API call).
        This is much faster than recursive directory scanning.

        NOTE: Only works for repositories, requires recursive tree API access.
        Falls back to regular method if tree API fails.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of dicts with 'path', 'name', 'sha', and 'url' for each .md file
        """
        logger.info(f"🚀 Using ULTRA-FAST tree API to find markdown files in {owner}/{repo}")

        try:
            # Get the default branch
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._make_request(repo_url)
            default_branch = repo_data.get("default_branch", "main")

            # Get the tree recursively (single API call for entire repo!)
            tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            logger.info(f"📡 Fetching entire repository tree in ONE API call...")

            tree_data = self._make_request(tree_url, use_cache=False)
            tree_items = tree_data.get("tree", [])

            logger.info(f"✓ Retrieved {len(tree_items)} items from repository tree")

            # Filter for .md files only
            markdown_files = []
            for item in tree_items:
                if item.get("type") == "blob" and item.get("path", "").endswith(".md"):
                    item_path = item.get("path", "")
                    item_size = item.get("size", 0)

                    # Check file size
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  Skipping large file ({item_size} bytes): {item_path}")
                        continue

                    # Extract filename from path
                    file_name = item_path.split("/")[-1] if "/" in item_path else item_path

                    markdown_files.append({
                        "path": item_path,
                        "name": file_name,
                        "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                        "sha": item.get("sha", ""),
                        "size": item_size
                    })

                    logger.debug(f"✓ Found markdown file: {item_path} ({item_size} bytes)")

            logger.info(f"🎉 ULTRA-FAST search complete! Found {len(markdown_files)} markdown files")
            return markdown_files

        except Exception as e:
            logger.warning(f"⚠️  Tree API failed: {e}")
            logger.info(f"📂 Falling back to traditional directory scanning...")
            # Fallback to regular method
            return self.find_all_markdown_files(owner, repo)

    def find_all_api_files_fast(self, owner: str, repo: str) -> List[Dict[str, str]]:
        """
        ULTRA-FAST version: Find all API definition files using GitHub Tree API (single API call).

        Searches for:
        - GraphQL schema files: .graphql, .gql
        - Protocol Buffer files: .proto (gRPC definitions)
        - OpenAPI/Swagger files: .yaml, .yml, .json (with API-related keywords in path)
        - AsyncAPI, RAML, WADL, WSDL specification files

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of dicts with 'path', 'name', 'sha', 'url', and 'file_type' for each API file
        """
        logger.info(f"🚀 Using ULTRA-FAST tree API to find API definition files in {owner}/{repo}")
        logger.info(f"📋 Searching for: .graphql, .gql, .proto, and API-related .yaml/.yml/.json files")

        try:
            # Get the default branch
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._make_request(repo_url)
            default_branch = repo_data.get("default_branch", "main")

            # Get the tree recursively (single API call for entire repo!)
            tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            logger.info(f"📡 Fetching entire repository tree in ONE API call...")

            tree_data = self._make_request(tree_url, use_cache=False)
            tree_items = tree_data.get("tree", [])

            logger.info(f"✓ Retrieved {len(tree_items)} items from repository tree")

            # Filter for API definition files
            api_files = []
            graphql_count = 0
            proto_count = 0
            yaml_json_count = 0

            for item in tree_items:
                if item.get("type") == "blob":
                    original_path = item.get("path", "")
                    item_path_lower = original_path.lower()
                    item_size = item.get("size", 0)

                    # Check if it's an API definition file
                    is_api_file = False
                    file_type_detail = "api_definition"

                    # 1. GraphQL schema files (.graphql, .gql) - ALWAYS include
                    if item_path_lower.endswith((".graphql", ".gql")):
                        is_api_file = True
                        file_type_detail = "graphql_schema"
                        graphql_count += 1

                    # 2. Protocol Buffer files (.proto) - ALWAYS include
                    elif item_path_lower.endswith(".proto"):
                        is_api_file = True
                        file_type_detail = "protobuf"
                        proto_count += 1

                    # 3. YAML/YML/JSON files with API indicators
                    elif item_path_lower.endswith((".yaml", ".yml", ".json")):
                        # Check for API-related keywords in path or filename
                        if any(keyword in item_path_lower for keyword in API_KEYWORDS_IN_PATH):
                            is_api_file = True
                            yaml_json_count += 1
                        # Also check if file is in an API-related directory
                        elif any(f"/{api_dir}/" in item_path_lower or item_path_lower.startswith(f"{api_dir}/")
                                 for api_dir in API_DIRECTORIES):
                            is_api_file = True
                            yaml_json_count += 1

                    if is_api_file:
                        # Check file size
                        if item_size > MAX_FILE_SIZE_BYTES:
                            logger.warning(f"⚠️  Skipping large API file ({item_size} bytes): {original_path}")
                            continue

                        file_name = original_path.split("/")[-1] if "/" in original_path else original_path

                        api_files.append({
                            "path": original_path,
                            "name": file_name,
                            "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{original_path}",
                            "sha": item.get("sha", ""),
                            "size": item_size,
                            "file_type": file_type_detail
                        })

                        logger.debug(f"✓ Found API file [{file_type_detail}]: {original_path} ({item_size} bytes)")

            logger.info(f"🎉 ULTRA-FAST API search complete! Found {len(api_files)} API definition files:")
            logger.info(f"   📊 GraphQL schemas: {graphql_count}")
            logger.info(f"   📊 Protocol Buffers: {proto_count}")
            logger.info(f"   📊 YAML/JSON API specs: {yaml_json_count}")
            return api_files

        except Exception as e:
            logger.warning(f"⚠️  Tree API failed for API files: {e}")
            logger.info(f"📂 Falling back to traditional directory scanning...")
            # Fallback to regular method
            return self.find_all_api_files(owner, repo)

    def find_all_api_files(self, owner: str, repo: str, path: str = "", _depth: int = 0, _files_found: List = None) -> List[Dict[str, str]]:
        """
        Recursively find all API definition files in a repository with safety limits.

        Searches for:
        - GraphQL schema files: .graphql, .gql
        - Protocol Buffer files: .proto (gRPC definitions)
        - OpenAPI/Swagger files: .yaml, .yml, .json (with API-related keywords in path)
        - AsyncAPI, RAML, WADL, WSDL specification files

        Args:
            owner: Repository owner
            repo: Repository name
            path: Starting path (empty for root)
            _depth: Current recursion depth (internal)
            _files_found: Shared list for tracking total files (internal)

        Returns:
            List of dicts with 'path', 'name', 'sha', 'url', and 'file_type' for each API file
        """
        # Initialize shared files list on first call
        if _files_found is None:
            _files_found = []
            logger.info(f"🔍 Searching for API DEFINITION FILES")
            logger.info(f"📋 File types: .graphql, .gql, .proto, .yaml, .yml, .json (with API keywords)")
            logger.info(f"⚡ Using FAST PARALLEL SEARCH for speed optimization")

        api_files = []

        # Safety check: prevent infinite recursion
        if _depth > MAX_RECURSION_DEPTH:
            logger.warning(f"⚠️  Max recursion depth ({MAX_RECURSION_DEPTH}) reached at path: {path}")
            return api_files

        # Safety check: prevent too many files
        if len(_files_found) >= MAX_FILES_PER_SCAN:
            logger.warning(f"⚠️  Max file limit ({MAX_FILES_PER_SCAN}) reached, stopping scan")
            return api_files

        try:
            contents = self.get_repo_contents(owner, repo, path)

            if not contents:
                logger.warning(f"No contents returned for path: {path}")
                return []

            # Separate files and directories
            directories = []

            for item in contents:
                # Check file limit again
                if len(_files_found) >= MAX_FILES_PER_SCAN:
                    logger.warning(f"⚠️  Max file limit reached during scan")
                    break

                item_path = item.get("path", "")
                item_type = item.get("type", "")
                item_name = item.get("name", "").lower()
                item_path_lower = item_path.lower()
                item_size = item.get("size", 0)

                # Check for API definition files
                if item_type == "file":
                    is_api_file = False
                    file_type_detail = "api_definition"

                    # 1. GraphQL schema files (.graphql, .gql) - ALWAYS include
                    if item_name.endswith((".graphql", ".gql")):
                        is_api_file = True
                        file_type_detail = "graphql_schema"

                    # 2. Protocol Buffer files (.proto) - ALWAYS include
                    elif item_name.endswith(".proto"):
                        is_api_file = True
                        file_type_detail = "protobuf"

                    # 3. YAML/YML/JSON files with API indicators
                    elif item_name.endswith((".yaml", ".yml", ".json")):
                        # Look for API-related keywords
                        if any(keyword in item_path_lower for keyword in API_KEYWORDS_IN_PATH):
                            is_api_file = True
                        # Also check if file is in an API-related directory
                        elif any(f"/{api_dir}/" in item_path_lower or item_path_lower.startswith(f"{api_dir}/")
                                 for api_dir in API_DIRECTORIES):
                            is_api_file = True

                    if is_api_file:
                        # Check file size before adding
                        if item_size > MAX_FILE_SIZE_BYTES:
                            logger.warning(f"⚠️  Skipping large API file ({item_size} bytes): {item_path}")
                            continue

                        api_files.append({
                            "path": item_path,
                            "name": item.get("name", ""),  # Use original case
                            "url": item.get("html_url", ""),
                            "sha": item.get("sha", ""),
                            "size": item_size,
                            "file_type": file_type_detail
                        })
                        _files_found.append(item_path)
                        logger.info(f"✓ Found API file [{file_type_detail}]: {item_path} ({item_size} bytes)")

                elif item_type == "dir":
                    directories.append(item_path)

            # Process directories in parallel for speed (only at depth 0 and 1)
            if directories and _depth <= 1:
                logger.info(f"⚡ Scanning {len(directories)} directories in parallel for API files...")
                with ThreadPoolExecutor(max_workers=MAX_PARALLEL_REQUESTS) as executor:
                    future_to_dir = {
                        executor.submit(
                            self.find_all_api_files,
                            owner, repo, dir_path,
                            _depth + 1, _files_found
                        ): dir_path
                        for dir_path in directories
                    }

                    for future in as_completed(future_to_dir):
                        dir_path = future_to_dir[future]
                        try:
                            sub_files = future.result()
                            api_files.extend(sub_files)
                        except Exception as e:
                            logger.error(f"Error scanning directory {dir_path}: {e}")
            else:
                # For deeper levels, use sequential scanning to avoid too many threads
                for dir_path in directories:
                    logger.debug(f"Searching directory (depth {_depth + 1}): {dir_path}")
                    sub_files = self.find_all_api_files(
                        owner, repo, dir_path,
                        _depth=_depth + 1,
                        _files_found=_files_found
                    )
                    api_files.extend(sub_files)

        except Exception as e:
            logger.error(f"Error processing path {path}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            # Re-raise to propagate the error instead of silently returning empty list
            if path == "":  # Only raise for root path
                raise

        return api_files

    def find_all_markdown_and_api_files_fast(self, owner: str, repo: str) -> Dict[str, List[Dict[str, str]]]:
        """
        ULTRA-FAST version: Find both .md files AND API definition files using GitHub Tree API.
        Uses a single API call to get entire repository tree.

        Searches for API files:
        - GraphQL schema files: .graphql, .gql
        - Protocol Buffer files: .proto (gRPC definitions)
        - OpenAPI/Swagger files: .yaml, .yml, .json (with API-related keywords in path)

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dict with 'markdown_files' and 'api_files' lists
        """
        logger.info(f"🚀 Using ULTRA-FAST tree API to find ALL files (markdown + API) in {owner}/{repo}")
        logger.info(f"📋 API files include: .graphql, .gql, .proto, and API-related .yaml/.yml/.json")

        try:
            # Get the default branch
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._make_request(repo_url)
            default_branch = repo_data.get("default_branch", "main")

            # Get the tree recursively (single API call for entire repo!)
            tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            logger.info(f"📡 Fetching entire repository tree in ONE API call...")

            tree_data = self._make_request(tree_url, use_cache=False)
            tree_items = tree_data.get("tree", [])

            logger.info(f"✓ Retrieved {len(tree_items)} items from repository tree")

            # Filter for both markdown and API files
            markdown_files = []
            api_files = []
            graphql_count = 0
            proto_count = 0
            yaml_json_count = 0

            for item in tree_items:
                if item.get("type") == "blob":
                    item_path = item.get("path", "")
                    item_path_lower = item_path.lower()
                    item_size = item.get("size", 0)

                    # Check file size first
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  Skipping large file ({item_size} bytes): {item_path}")
                        continue

                    # Extract filename from path
                    file_name = item_path.split("/")[-1] if "/" in item_path else item_path

                    # Check if it's a markdown file
                    if item_path_lower.endswith(".md"):
                        markdown_files.append({
                            "path": item_path,
                            "name": file_name,
                            "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                            "sha": item.get("sha", ""),
                            "size": item_size,
                            "file_type": "markdown"
                        })
                        logger.debug(f"✓ Found markdown file: {item_path} ({item_size} bytes)")

                    # 1. GraphQL schema files (.graphql, .gql) - ALWAYS include
                    elif item_path_lower.endswith((".graphql", ".gql")):
                        api_files.append({
                            "path": item_path,
                            "name": file_name,
                            "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                            "sha": item.get("sha", ""),
                            "size": item_size,
                            "file_type": "graphql_schema"
                        })
                        graphql_count += 1
                        logger.debug(f"✓ Found GraphQL schema: {item_path} ({item_size} bytes)")

                    # 2. Protocol Buffer files (.proto) - ALWAYS include
                    elif item_path_lower.endswith(".proto"):
                        api_files.append({
                            "path": item_path,
                            "name": file_name,
                            "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                            "sha": item.get("sha", ""),
                            "size": item_size,
                            "file_type": "protobuf"
                        })
                        proto_count += 1
                        logger.debug(f"✓ Found Proto file: {item_path} ({item_size} bytes)")

                    # 3. YAML/YML/JSON files with API indicators
                    elif item_path_lower.endswith((".yaml", ".yml", ".json")):
                        is_api_file = False
                        # Check for API-related keywords in path or filename
                        if any(keyword in item_path_lower for keyword in API_KEYWORDS_IN_PATH):
                            is_api_file = True
                        # Also check if file is in an API-related directory
                        elif any(f"/{api_dir}/" in item_path_lower or item_path_lower.startswith(f"{api_dir}/")
                                 for api_dir in API_DIRECTORIES):
                            is_api_file = True

                        if is_api_file:
                            api_files.append({
                                "path": item_path,
                                "name": file_name,
                                "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                                "sha": item.get("sha", ""),
                                "size": item_size,
                                "file_type": "api_definition"
                            })
                            yaml_json_count += 1
                            logger.debug(f"✓ Found API file: {item_path} ({item_size} bytes)")

            logger.info(f"🎉 ULTRA-FAST search complete!")
            logger.info(f"   📄 Markdown files: {len(markdown_files)}")
            logger.info(f"   📊 GraphQL schemas: {graphql_count}")
            logger.info(f"   📊 Protocol Buffers: {proto_count}")
            logger.info(f"   📊 YAML/JSON API specs: {yaml_json_count}")
            logger.info(f"   📊 Total API files: {len(api_files)}")

            return {
                "markdown_files": markdown_files,
                "api_files": api_files
            }

        except Exception as e:
            logger.warning(f"⚠️  Tree API failed: {e}")
            logger.info(f"📂 Falling back to traditional directory scanning...")
            # Fallback: call both methods separately
            return {
                "markdown_files": self.find_all_markdown_files(owner, repo),
                "api_files": self.find_all_api_files(owner, repo)
            }

    def find_all_files_fast(self, owner: str, repo: str, include_binary: bool = False) -> List[Dict[str, str]]:
        """
        ULTRA-FAST version: Find ALL files in a repository using GitHub Tree API.
        Uses a single API call to get entire repository tree.

        This method retrieves ALL file types including:
        - Source code files (.py, .js, .ts, .java, .go, .rs, .c, .cpp, .rb, .php, .bal, etc.)
        - Configuration files (.yaml, .yml, .json, .toml, .ini, .cfg, .conf, .env, etc.)
        - Documentation files (.md, .rst, .txt, .adoc, etc.)
        - API definition files (.graphql, .gql, .proto, .wsdl, etc.)
        - Build files (Dockerfile, Makefile, pom.xml, build.gradle, package.json, etc.)
        - Shell scripts (.sh, .bash, .zsh, etc.)
        - And many more text-based files

        Binary files (images, archives, executables) are excluded by default.

        Args:
            owner: Repository owner
            repo: Repository name
            include_binary: Whether to include binary files (default: False)

        Returns:
            List of dicts with 'path', 'name', 'sha', 'url', 'size', and 'file_type' for each file
        """
        logger.info(f"🚀 Using ULTRA-FAST tree API to find ALL files in {owner}/{repo}")
        logger.info(f"📋 Retrieving all text-based files (code, config, docs, etc.)")

        # File extensions that are typically binary and should be skipped by default
        BINARY_EXTENSIONS = (
            # Images
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp', '.tiff', '.tif',
            # Archives
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.jar', '.war', '.ear',
            # Executables and binaries
            '.exe', '.dll', '.so', '.dylib', '.bin', '.o', '.a', '.lib', '.class', '.pyc', '.pyo',
            # Media
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.wav', '.ogg', '.webm',
            # Fonts
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
            # Documents (binary)
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Database
            '.db', '.sqlite', '.sqlite3', '.mdb',
            # Other binary
            '.lock', '.map', '.wasm',
        )

        # Text file extensions we explicitly want (for clarity in logs)
        TEXT_EXTENSIONS = (
            # Programming languages
            '.py', '.pyw', '.pyx',  # Python
            '.js', '.mjs', '.cjs', '.jsx',  # JavaScript
            '.ts', '.tsx', '.mts', '.cts',  # TypeScript
            '.java',  # Java
            '.go',  # Go
            '.rs',  # Rust
            '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hxx',  # C/C++
            '.cs',  # C#
            '.rb', '.rake', '.gemspec',  # Ruby
            '.php', '.phtml',  # PHP
            '.swift',  # Swift
            '.kt', '.kts',  # Kotlin
            '.scala', '.sc',  # Scala
            '.bal',  # Ballerina
            '.lua',  # Lua
            '.r', '.rmd',  # R
            '.pl', '.pm',  # Perl
            '.ex', '.exs',  # Elixir
            '.erl', '.hrl',  # Erlang
            '.hs', '.lhs',  # Haskell
            '.clj', '.cljs', '.cljc', '.edn',  # Clojure
            '.dart',  # Dart
            '.groovy', '.gvy', '.gy', '.gsh',  # Groovy
            # Web
            '.html', '.htm', '.xhtml',
            '.css', '.scss', '.sass', '.less', '.styl',
            '.vue', '.svelte',
            # Configuration
            '.yaml', '.yml',
            '.json', '.jsonc', '.json5',
            '.toml',
            '.ini', '.cfg', '.conf', '.config',
            '.env', '.env.example', '.env.sample', '.env.local',
            '.properties',
            '.xml', '.xsd', '.xsl', '.xslt',
            # Documentation
            '.md', '.markdown', '.mdx',
            '.rst', '.txt', '.text',
            '.adoc', '.asciidoc',
            '.org',
            '.tex', '.latex',
            # API definitions
            '.graphql', '.gql',
            '.proto',
            '.wsdl', '.wadl',
            # Shell and scripts
            '.sh', '.bash', '.zsh', '.fish',
            '.ps1', '.psm1', '.psd1',  # PowerShell
            '.bat', '.cmd',  # Windows batch
            # Build and CI/CD
            '.gradle',
            '.cmake',
            # Data formats
            '.csv', '.tsv',
            '.sql',
            # Other
            '.tf', '.tfvars',  # Terraform
            '.hcl',  # HashiCorp
            '.nix',  # Nix
            '.vim', '.vimrc',
            '.el', '.elisp',  # Emacs Lisp
        )

        # Files without extension that are typically text
        TEXT_FILENAMES = (
            'dockerfile', 'makefile', 'gnumakefile', 'rakefile', 'gemfile', 'guardfile',
            'procfile', 'vagrantfile', 'jenkinsfile', 'berksfile', 'brewfile',
            'cakefile', 'fastfile', 'podfile', 'cartfile', 'snapfile', 'appfile',
            '.gitignore', '.gitattributes', '.gitmodules', '.dockerignore', '.npmignore',
            '.eslintignore', '.prettierignore', '.hgignore', '.bzrignore',
            'license', 'licence', 'copying', 'readme', 'changelog', 'history',
            'authors', 'contributors', 'maintainers', 'thanks', 'credits',
            'todo', 'fixme', 'notes', 'news', 'install', 'hacking',
            '.editorconfig', '.babelrc', '.eslintrc', '.prettierrc', '.stylelintrc',
            'requirements', 'requirements-dev', 'constraints',
            'cargo.lock', 'package-lock', 'yarn.lock', 'go.sum', 'go.mod',
            'pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle',
        )

        try:
            # Get the default branch
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._make_request(repo_url)
            default_branch = repo_data.get("default_branch", "main")

            # Get the tree recursively (single API call for entire repo!)
            tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            logger.info(f"📡 Fetching entire repository tree in ONE API call...")

            tree_data = self._make_request(tree_url, use_cache=False)
            tree_items = tree_data.get("tree", [])

            logger.info(f"✓ Retrieved {len(tree_items)} items from repository tree")

            # File counters by category
            all_files = []
            file_counts = {
                "code": 0,
                "config": 0,
                "docs": 0,
                "api_definition": 0,
                "build": 0,
                "other": 0,
                "binary_skipped": 0,
            }

            for item in tree_items:
                if item.get("type") == "blob":
                    item_path = item.get("path", "")
                    item_path_lower = item_path.lower()
                    item_size = item.get("size", 0)

                    # Extract filename from path
                    file_name = item_path.split("/")[-1] if "/" in item_path else item_path
                    file_name_lower = file_name.lower()

                    # Check file size first
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  Skipping large file ({item_size} bytes): {item_path}")
                        continue

                    # Check if it's a binary file
                    if not include_binary and item_path_lower.endswith(BINARY_EXTENSIONS):
                        file_counts["binary_skipped"] += 1
                        logger.debug(f"⏭️  Skipping binary file: {item_path}")
                        continue

                    # Determine file type for categorization
                    file_type = "code"  # Default
                    if item_path_lower.endswith(('.md', '.markdown', '.mdx', '.rst', '.txt', '.adoc')):
                        file_type = "documentation"
                        file_counts["docs"] += 1
                    elif item_path_lower.endswith(('.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf', '.properties', '.xml', '.env')):
                        file_type = "configuration"
                        file_counts["config"] += 1
                    elif item_path_lower.endswith(('.graphql', '.gql', '.proto', '.wsdl', '.wadl')):
                        file_type = "api_definition"
                        file_counts["api_definition"] += 1
                    elif file_name_lower in ('dockerfile', 'makefile', 'jenkinsfile', 'vagrantfile') or item_path_lower.endswith(('.gradle', '.cmake')):
                        file_type = "build"
                        file_counts["build"] += 1
                    elif item_path_lower.endswith(TEXT_EXTENSIONS):
                        file_type = "code"
                        file_counts["code"] += 1
                    elif file_name_lower in TEXT_FILENAMES or any(file_name_lower.startswith(prefix) for prefix in ('.git', '.docker', '.eslint', '.prettier')):
                        file_type = "other"
                        file_counts["other"] += 1
                    else:
                        # Check if file has no extension or unknown extension
                        # Include files without extension (often text files) unless they look binary
                        if '.' not in file_name or item_path_lower.endswith(TEXT_EXTENSIONS):
                            file_type = "other"
                            file_counts["other"] += 1
                        else:
                            # Unknown extension - skip if we're being conservative
                            # But let's include it anyway as "other" for completeness
                            file_type = "other"
                            file_counts["other"] += 1

                    all_files.append({
                        "path": item_path,
                        "name": file_name,
                        "url": f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item_path}",
                        "sha": item.get("sha", ""),
                        "size": item_size,
                        "file_type": file_type
                    })

                    logger.debug(f"✓ Found [{file_type}]: {item_path} ({item_size} bytes)")

            logger.info(f"🎉 ULTRA-FAST search complete! Found {len(all_files)} files:")
            logger.info(f"   💻 Code files: {file_counts['code']}")
            logger.info(f"   📄 Documentation: {file_counts['docs']}")
            logger.info(f"   ⚙️  Configuration: {file_counts['config']}")
            logger.info(f"   🔧 API definitions: {file_counts['api_definition']}")
            logger.info(f"   🏗️  Build files: {file_counts['build']}")
            logger.info(f"   📁 Other: {file_counts['other']}")
            if file_counts['binary_skipped'] > 0:
                logger.info(f"   ⏭️  Binary skipped: {file_counts['binary_skipped']}")

            return all_files

        except Exception as e:
            logger.warning(f"⚠️  Tree API failed: {e}")
            logger.info(f"📂 Falling back to traditional directory scanning...")
            # Fallback to regular directory scanning for all files
            return self._find_all_files_recursive(owner, repo)

    def _find_all_files_recursive(self, owner: str, repo: str, path: str = "", _depth: int = 0, _files_found: List = None) -> List[Dict[str, str]]:
        """
        Fallback method: Recursively find all text files in a repository.
        Used when the tree API is not available.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Starting path (empty for root)
            _depth: Current recursion depth (internal)
            _files_found: Shared list for tracking total files (internal)

        Returns:
            List of dicts with file information
        """
        if _files_found is None:
            _files_found = []
            logger.info(f"🔍 Using fallback recursive search for all files")

        all_files = []

        # Same binary extensions as above
        BINARY_EXTENSIONS = (
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.jar',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.o', '.a', '.class', '.pyc',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.ogg',
            '.ttf', '.otf', '.woff', '.woff2',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.db', '.sqlite', '.sqlite3',
            '.lock', '.map', '.wasm',
        )

        if _depth > MAX_RECURSION_DEPTH:
            logger.warning(f"⚠️  Max recursion depth reached at path: {path}")
            return all_files

        if len(_files_found) >= MAX_FILES_PER_SCAN:
            logger.warning(f"⚠️  Max file limit reached")
            return all_files

        try:
            contents = self.get_repo_contents(owner, repo, path)

            if not contents:
                return []

            directories = []

            for item in contents:
                if len(_files_found) >= MAX_FILES_PER_SCAN:
                    break

                item_path = item.get("path", "")
                item_type = item.get("type", "")
                item_name = item.get("name", "")
                item_size = item.get("size", 0)

                if item_type == "file":
                    # Skip binary files
                    if item_path.lower().endswith(BINARY_EXTENSIONS):
                        continue

                    # Skip large files
                    if item_size > MAX_FILE_SIZE_BYTES:
                        continue

                    file_type = "code"  # Default
                    if item_path.lower().endswith(('.md', '.rst', '.txt', '.adoc')):
                        file_type = "documentation"
                    elif item_path.lower().endswith(('.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.xml')):
                        file_type = "configuration"

                    all_files.append({
                        "path": item_path,
                        "name": item_name,
                        "url": item.get("html_url", ""),
                        "sha": item.get("sha", ""),
                        "size": item_size,
                        "file_type": file_type
                    })
                    _files_found.append(item_path)

                elif item_type == "dir":
                    directories.append(item_path)

            # Process directories
            for dir_path in directories:
                sub_files = self._find_all_files_recursive(owner, repo, dir_path, _depth + 1, _files_found)
                all_files.extend(sub_files)

        except Exception as e:
            logger.error(f"Error processing path {path}: {e}")

        return all_files

    def fetch_all_markdown_contents(self, owner: str, repo: str) -> List[Dict[str, str]]:
        """
        Fetch all markdown files and their contents from a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of dicts with 'path', 'name', 'content', and 'url' for each .md file
        """
        logger.info(f"Starting to fetch all markdown files from {owner}/{repo}")

        # Find all .md files
        md_files = self.find_all_markdown_files(owner, repo)
        logger.info(f"Found {len(md_files)} markdown files")

        # Fetch content for each file
        results = []
        for i, file_info in enumerate(md_files, 1):
            try:
                logger.info(f"Fetching content {i}/{len(md_files)}: {file_info['path']}")
                content = self.get_file_content(owner, repo, file_info["path"])

                results.append({
                    "path": file_info["path"],
                    "name": file_info["name"],
                    "url": file_info["url"],
                    "content": content
                })
            except Exception as e:
                logger.error(f"Failed to fetch {file_info['path']}: {e}")
                continue

        logger.info(f"Successfully fetched {len(results)} markdown files")
        return results

    def search_org_repositories(self, org: str, keyword: str = "", per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Search for all repositories (public and private) under an organization, optionally filtered by keyword.

        Args:
            org: Organization name
            keyword: Optional keyword to filter repositories
            per_page: Number of results per page (max 100)

        Returns:
            List of repository information including name, description, url, etc.
        """
        logger.info(f"Searching repositories in organization '{org}' with keyword '{keyword}'")

        repositories = []
        page = 1

        while True:
            # Use the organization repos endpoint with type=all to get both public and private repos
            url = f"{self.base_url}/orgs/{org}/repos?type=all&per_page={per_page}&page={page}"

            try:
                logger.info(f"Fetching page {page} of repositories...")
                repos_data = self._make_request(url)

                if not repos_data or len(repos_data) == 0:
                    # No more repositories
                    break

                # Filter by keyword if provided
                for repo in repos_data:
                    repo_name = repo.get("name", "").lower()
                    repo_desc = repo.get("description", "") or ""
                    repo_desc_lower = repo_desc.lower()

                    # If keyword is provided, check if it matches name or description
                    if keyword:
                        keyword_lower = keyword.lower()
                        if keyword_lower not in repo_name and keyword_lower not in repo_desc_lower:
                            continue

                    # Add repository info
                    repositories.append({
                        "name": repo.get("name", ""),
                        "full_name": repo.get("full_name", ""),
                        "description": repo_desc,
                        "url": repo.get("html_url", ""),
                        "api_url": repo.get("url", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "default_branch": repo.get("default_branch", "main"),
                        "is_private": repo.get("private", False),
                        "owner": repo.get("owner", {}).get("login", "")
                    })

                # Check if there are more pages
                if len(repos_data) < per_page:
                    # Last page reached
                    break

                page += 1

            except Exception as e:
                logger.error(f"Error fetching repositories from organization: {e}")
                break

        logger.info(f"Found {len(repositories)} repositories matching criteria")
        return repositories

    def get_readme_content(self, owner: str, repo: str) -> Optional[Dict[str, str]]:
        """
        Get the README file content from a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dict with readme content and metadata, or None if no README found
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"

        try:
            logger.info(f"Fetching README for {owner}/{repo}")
            data = self._make_request(url)

            if data and "content" in data:
                # Content is base64 encoded
                content = base64.b64decode(data["content"]).decode("utf-8")

                return {
                    "name": data.get("name", "README.md"),
                    "path": data.get("path", ""),
                    "content": content,
                    "size": data.get("size", 0),
                    "sha": data.get("sha", ""),
                    "url": data.get("html_url", "")
                }
            else:
                logger.warning(f"No README found for {owner}/{repo}")
                return None

        except Exception as e:
            logger.warning(f"Could not fetch README for {owner}/{repo}: {e}")
            return None

    def find_all_image_files(self, owner: str, repo: str, path: str = "", _depth: int = 0, _files_found: List = None) -> List[Dict[str, str]]:
        """
        Recursively find all image files in a repository with safety limits.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Starting path (empty for root)
            _depth: Current recursion depth (internal)
            _files_found: Shared list for tracking total files (internal)

        Returns:
            List of dicts with 'path', 'name', 'sha', and 'url' for each image file
        """
        # Initialize shared files list on first call
        if _files_found is None:
            _files_found = []

        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')
        image_files = []

        # Safety check: prevent infinite recursion
        if _depth > MAX_RECURSION_DEPTH:
            logger.warning(f"⚠️  Max recursion depth ({MAX_RECURSION_DEPTH}) reached at path: {path}")
            return image_files

        # Safety check: prevent too many files
        if len(_files_found) >= MAX_FILES_PER_SCAN:
            logger.warning(f"⚠️  Max file limit ({MAX_FILES_PER_SCAN}) reached, stopping scan")
            return image_files

        try:
            contents = self.get_repo_contents(owner, repo, path)

            if not contents:
                logger.warning(f"No contents returned for path: {path}")
                return []

            for item in contents:
                # Check file limit
                if len(_files_found) >= MAX_FILES_PER_SCAN:
                    logger.warning(f"⚠️  Max file limit reached during image scan")
                    break

                item_path = item.get("path", "")
                item_type = item.get("type", "")
                item_name = item.get("name", "")
                item_size = item.get("size", 0)

                if item_type == "file" and item_name.lower().endswith(image_extensions):
                    # Check file size
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  Skipping large image ({item_size} bytes): {item_path}")
                        continue

                    image_files.append({
                        "path": item_path,
                        "name": item_name,
                        "url": item.get("html_url", ""),
                        "sha": item.get("sha", ""),
                        "size": item_size
                    })
                    _files_found.append(item_path)
                    logger.info(f"Found image file: {item_path} ({item_size} bytes)")

                elif item_type == "dir":
                    # Recursively search directories
                    logger.debug(f"Searching directory for images (depth {_depth + 1}): {item_path}")
                    sub_images = self.find_all_image_files(
                        owner, repo, item_path,
                        _depth=_depth + 1,
                        _files_found=_files_found
                    )
                    image_files.extend(sub_images)

        except Exception as e:
            logger.error(f"Error processing path {path} for images: {e}")
            if path == "":  # Only raise for root path
                raise

        return image_files

    def find_readme_file(self, owner: str, repo: str) -> Optional[Dict[str, str]]:
        """
        Find the README.md file in a repository (searches common locations).

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dict with 'path', 'name', 'sha', and 'url' for README.md file, or None if not found
        """
        # Common README file names and locations
        readme_variations = [
            "README.md",
            "readme.md",
            "Readme.md",
            "README.MD",
            "docs/README.md",
            "doc/README.md"
        ]

        for readme_path in readme_variations:
            try:
                logger.debug(f"Checking for README at: {readme_path}")
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{readme_path}"
                data = self._make_request(url)

                if data and data.get("type") == "file":
                    item_size = data.get("size", 0)

                    # Check file size
                    if item_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"⚠️  README file too large ({item_size} bytes), skipping: {readme_path}")
                        continue

                    logger.info(f"Found README file: {readme_path} ({item_size} bytes)")
                    return {
                        "path": readme_path,
                        "name": data.get("name", "README.md"),
                        "url": data.get("html_url", ""),
                        "sha": data.get("sha", ""),
                        "size": item_size
                    }
            except Exception as e:
                # File doesn't exist at this path, try next variation
                logger.debug(f"README not found at {readme_path}: {e}")
                continue

        logger.warning(f"No README.md found in repository {owner}/{repo}")
        return None

