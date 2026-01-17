#!/usr/bin/env python3
"""
Debug script to check what repository metadata exists in the vector database.
This helps understand why only one repo URL is being extracted.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db.vector_client import VectorClient
from utils.config import load_config

def check_metadata_structure():
    """Check the metadata structure in the vector database."""
    print("="*80)
    print("CHECKING VECTOR DATABASE METADATA")
    print("="*80)

    # Load config
    config = load_config()

    # Connect to Milvus
    client = VectorClient(
        uri=config['MILVUS_URI'],
        token=config['MILVUS_TOKEN'],
        collection_name=config['MILVUS_COLLECTION_NAME']
    )

    print(f"\n✓ Connected to collection: {config['MILVUS_COLLECTION_NAME']}")

    # Query for some sample data
    print("\n" + "-"*80)
    print("QUERYING SAMPLE DATA...")
    print("-"*80)

    try:
        # Search with a generic query to get some results
        results = client.search(
            query_text="choreo repository",
            top_k=20,
            filter_expr=None
        )

        if not results:
            print("❌ No results found")
            return

        print(f"\n✓ Found {len(results)} results\n")

        # Analyze metadata structure
        unique_repos = set()
        metadata_fields = set()
        sample_metadata = []

        for i, result in enumerate(results[:10], 1):
            metadata = result.get('metadata', {})

            # Collect all metadata field names
            metadata_fields.update(metadata.keys())

            # Store sample
            if i <= 3:
                sample_metadata.append(metadata)

            # Extract repository info
            repo = metadata.get('repository', '')
            repo_url = metadata.get('repository_url', '') or metadata.get('url', '')

            if repo:
                unique_repos.add(repo)
            if repo_url and 'github.com' in repo_url:
                unique_repos.add(repo_url)

        # Display results
        print("METADATA FIELDS FOUND:")
        print("-"*80)
        for field in sorted(metadata_fields):
            print(f"  • {field}")

        print(f"\nUNIQUE REPOSITORIES FOUND (from {len(results)} results):")
        print("-"*80)
        for repo in sorted(unique_repos)[:20]:
            print(f"  • {repo}")

        if len(unique_repos) > 20:
            print(f"  ... and {len(unique_repos) - 20} more")

        print(f"\nTotal unique repositories: {len(unique_repos)}")

        # Show sample metadata
        print("\nSAMPLE METADATA STRUCTURES:")
        print("-"*80)
        for i, meta in enumerate(sample_metadata, 1):
            print(f"\nSample {i}:")
            for key, value in meta.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {key}: {value}")

        # Check for GitHub URLs in content
        print("\nCHECKING FOR URLs IN CONTENT TEXT:")
        print("-"*80)
        urls_in_content = set()
        for result in results[:20]:
            content = result.get('content', '')
            if 'github.com/wso2-enterprise' in content:
                # Extract URLs from content
                import re
                pattern = r'https://github\.com/wso2-enterprise/[\w\-]+'
                found_urls = re.findall(pattern, content)
                urls_in_content.update(found_urls)

        if urls_in_content:
            print(f"\n✓ Found {len(urls_in_content)} unique repo URLs in content text:")
            for url in sorted(urls_in_content)[:10]:
                print(f"  • {url}")
            if len(urls_in_content) > 10:
                print(f"  ... and {len(urls_in_content) - 10} more")
        else:
            print("\n⚠️  No GitHub URLs found in content text")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Metadata fields: {len(metadata_fields)}")
        print(f"Unique repositories (from metadata): {len(unique_repos)}")
        print(f"URLs in content text: {len(urls_in_content)}")

        print("\nRECOMMENDATION:")
        if len(unique_repos) < 10:
            print("⚠️  Only a few repositories found in metadata.")
            print("   This explains why only one URL is being extracted.")
            print("\n   Possible solutions:")
            print("   1. Metadata might not include repository URLs")
            print("   2. Need to increase top_k in RAG retrieval")
            print("   3. Need to look for URLs in content text (not just metadata)")
        else:
            print("✓ Good amount of repository data in metadata")
            print("  The LLM matcher should work well")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_metadata_structure()
