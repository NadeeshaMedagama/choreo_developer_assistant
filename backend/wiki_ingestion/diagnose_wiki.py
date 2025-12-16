#!/usr/bin/env python3
"""
Wiki URL Diagnostic Tool
Helps diagnose why the .env file isn't being read and checks if wiki exists
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 80)
print("WIKI INGESTION DIAGNOSTIC TOOL")
print("=" * 80)
print()

# Check 1: .env file location
print("📁 Step 1: Checking .env file location")
print("-" * 80)

backend_dir = Path(__file__).parent.parent
env_file = backend_dir / '.env'

print(f"Script location: {__file__}")
print(f"Backend directory: {backend_dir}")
print(f"Expected .env path: {env_file}")
print(f".env file exists: {env_file.exists()}")
print()

# Check 2: Load .env file
print("📋 Step 2: Loading .env file")
print("-" * 80)

if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded .env from: {env_file}")
else:
    print(f"❌ .env file not found at: {env_file}")
    print()
    print("Please create the .env file with:")
    print("WIKI_URL=https://github.com/your-org/your-repo/wiki")
    sys.exit(1)

print()

# Check 3: Read environment variables
print("🔍 Step 3: Reading environment variables")
print("-" * 80)

wiki_url = os.getenv('WIKI_URL')
github_token = os.getenv('GITHUB_TOKEN')

print(f"WIKI_URL: {wiki_url}")
print(f"WIKI_MAX_DEPTH: {os.getenv('WIKI_MAX_DEPTH')}")
print(f"WIKI_MAX_PAGES: {os.getenv('WIKI_MAX_PAGES')}")
print(f"WIKI_FETCH_LINKED: {os.getenv('WIKI_FETCH_LINKED')}")
print(f"WIKI_MAX_LINKED_URLS: {os.getenv('WIKI_MAX_LINKED_URLS')}")
print(f"GITHUB_TOKEN: {'Set ✅' if github_token else 'Not set ❌'}")
print()

if not wiki_url:
    print("❌ WIKI_URL not found in .env file!")
    print("Please add this line to your .env file:")
    print("WIKI_URL=https://github.com/your-org/your-repo/wiki")
    sys.exit(1)

# Check 4: Validate wiki URL format
print("✅ Step 4: Validating wiki URL format")
print("-" * 80)

if not wiki_url.startswith('https://github.com/'):
    print(f"⚠️  Warning: URL doesn't start with https://github.com/")
    print(f"   Current: {wiki_url}")

if not wiki_url.endswith('/wiki'):
    print(f"⚠️  Warning: URL doesn't end with /wiki")
    print(f"   Current: {wiki_url}")

# Extract owner and repo
parts = wiki_url.replace('https://github.com/', '').replace('/wiki', '').split('/')
if len(parts) >= 2:
    owner, repo = parts[0], parts[1]
    print(f"Owner: {owner}")
    print(f"Repository: {repo}")
else:
    print(f"❌ Invalid URL format: {wiki_url}")
    sys.exit(1)

print()

# Check 5: Test repository access
print("🌐 Step 5: Testing repository access")
print("-" * 80)

headers = {}
if github_token:
    headers['Authorization'] = f'token {github_token}'

try:
    # Check repository
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    print(f"Checking: {repo_url}")
    
    resp = requests.get(repo_url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Repository exists: {data.get('full_name')}")
        print(f"   Private: {data.get('private', False)}")
        print(f"   Has wiki: {data.get('has_wiki', False)}")
        
        if not data.get('has_wiki', False):
            print()
            print("❌ WARNING: This repository has wiki DISABLED!")
            print("   You need to enable wiki in the repository settings.")
            print()
    elif resp.status_code == 404:
        print(f"❌ Repository not found: {owner}/{repo}")
        print("   Possible reasons:")
        print("   - Repository doesn't exist")
        print("   - Repository is private and you don't have access")
        print("   - Typo in repository name")
    elif resp.status_code == 401:
        print(f"❌ Authentication failed")
        print("   Check your GITHUB_TOKEN")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.text[:200]}")
    
except Exception as e:
    print(f"❌ Error connecting to GitHub: {e}")

print()

# Check 6: Test wiki access
print("📚 Step 6: Testing wiki access")
print("-" * 80)

try:
    wiki_test_url = wiki_url
    print(f"Testing: {wiki_test_url}")
    
    resp = requests.get(wiki_test_url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"✅ Wiki is accessible!")
        print(f"   Content length: {len(resp.content)} bytes")
    elif resp.status_code == 404:
        print(f"❌ Wiki not found (404)")
        print()
        print("   Possible reasons:")
        print("   1. Wiki doesn't exist or has no pages")
        print("   2. Repository is private (wiki requires authentication)")
        print("   3. Wiki is disabled in repository settings")
        print()
        print("   Solutions:")
        print("   - Enable wiki in repository settings")
        print("   - Create at least one wiki page")
        print("   - Check repository permissions")
    else:
        print(f"❌ Error: {resp.status_code}")
        
except Exception as e:
    print(f"❌ Error accessing wiki: {e}")

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print()

# Summary
print("📊 SUMMARY")
print("-" * 80)
print(f"✅ .env file: {'Found' if env_file.exists() else 'Not found'}")
print(f"✅ WIKI_URL: {wiki_url if wiki_url else 'Not set'}")
print(f"✅ GitHub Token: {'Set' if github_token else 'Not set'}")
print()
print("Next steps:")
print("1. If wiki is accessible, run: python -m wiki_ingestion.examples.ingest_to_milvus")
print("2. If wiki is not found, check repository settings and enable wiki")
print("3. If repository is private, ensure your GITHUB_TOKEN has access")
print()

