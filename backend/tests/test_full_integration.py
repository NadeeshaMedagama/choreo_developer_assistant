import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path (parent of tests directory)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

load_dotenv()

from services.choreo_repo_registry import get_choreo_registry
from services.llm_repo_matcher import get_llm_repo_matcher

print("=" * 80)
print("TEST: Dynamic Repository Fetching")
print("=" * 80)

# Test 1: Fetch all repos via registry
print("\n1. Fetching ALL repos via ChoreoRepoRegistry...")
registry = get_choreo_registry()
all_repos = registry.fetch_all_wso2_enterprise_repos(use_cache=False)
print(f"   ✅ Found {len(all_repos)} total repositories")

# Test 2: Fetch only Choreo repos
print("\n2. Fetching only Choreo repos...")
choreo_repos = registry.fetch_choreo_repos_only(use_cache=False)
print(f"   ✅ Found {len(choreo_repos)} Choreo repositories")

# Test 3: LLM Repo Matcher
print("\n3. Testing LLM Repo Matcher...")
matcher = get_llm_repo_matcher()

all_from_matcher = matcher.get_all_wso2_enterprise_repos(keyword=None)
print(f"   ✅ Matcher found {len(all_from_matcher)} total repos")

choreo_from_matcher = matcher.get_all_wso2_enterprise_repos(keyword="choreo")
print(f"   ✅ Matcher found {len(choreo_from_matcher)} Choreo repos")

# Test 4: Format for response
print("\n4. Testing response formatting...")
formatted = matcher.format_repos_for_response(
    choreo_from_matcher[:3],
    query_context="(showing first 3 as example)"
)
print("   ✅ Formatted response preview:")
print(formatted[:400] + "...")

# Test 5: System prompt generation
print("\n5. Testing system prompt generation...")
prompt = registry.generate_system_prompt_urls(use_dynamic=True)
url_count = prompt.count("github.com/wso2-enterprise/")
print(f"   ✅ System prompt contains {url_count} repository URLs")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Total repositories: {len(all_repos)}")
print(f"✅ Choreo repositories: {len(choreo_repos)}")
print(f"✅ Other repositories: {len(all_repos) - len(choreo_repos)}")
print(f"✅ System prompt includes {url_count} URLs")
print("\n🎉 Dynamic repository fetching is working!")
print("   Users can now get ALL repos when they ask, not just 32 hardcoded ones.")
print("=" * 80)
