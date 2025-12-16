#!/usr/bin/env python
"""Test script to debug GitHub API access"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
env_path = project_root / "backend" / ".env"
load_dotenv(env_path)

print("🔍 Testing GitHub API Access...")
print(f"GitHub Token present: {'Yes' if os.getenv('GITHUB_TOKEN') else 'No'}")
print()

try:
    from backend.services.github_service import GitHubService

    token = os.getenv('GITHUB_TOKEN')
    github = GitHubService(token=token)

    print("📡 Testing repository access...")
    owner = "NadeeshaMedagama"
    repo = "docs-choreo-dev"

    print(f"Fetching contents from: {owner}/{repo}")

    # Try to get repo contents
    try:
        contents = github.get_repo_contents(owner, repo, "")
        print(f"✓ Repository accessible!")
        print(f"✓ Found {len(contents)} items in root")

        # Try to find markdown files
        print("\n📄 Searching for .md files...")
        md_files = github.find_all_markdown_files(owner, repo)
        print(f"✓ Found {len(md_files)} markdown files")

        if md_files:
            print("\nFirst 5 markdown files:")
            for i, f in enumerate(md_files[:5], 1):
                print(f"  {i}. {f['path']}")
        else:
            print("\n⚠️  No markdown files found!")
            print("This could mean:")
            print("  1. Repository has no .md files")
            print("  2. Repository is private and token doesn't have access")
            print("  3. API rate limit exceeded")

    except Exception as e:
        print(f"✗ Error accessing repository: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"✗ Failed to initialize GitHub service: {e}")
    import traceback
    traceback.print_exc()

