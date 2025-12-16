"""
Example usage of GitHub Issues Ingestion System.

This script demonstrates various ways to use the system.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


def example_basic_ingestion():
    """Example 1: Basic ingestion of a repository."""
    print("="*80)
    print("Example 1: Basic Ingestion")
    print("="*80)

    from github_issues_ingestion import create_ingestion_pipeline

    # Create pipeline with default settings from .env
    orchestrator = create_ingestion_pipeline()

    # Ingest a small number of issues
    stats = orchestrator.ingest_repository(
        owner="wso2",
        repo="choreo",
        max_issues=5  # Just 5 issues for testing
    )

    print(f"\nIngestion completed!")
    print(f"Total issues processed: {stats['total_issues']}")
    print(f"Total chunks created: {stats['total_chunks']}")
    print(f"Total embeddings: {stats['total_embeddings']}")


def example_filtered_ingestion():
    """Example 2: Filtered ingestion with labels and state."""
    print("\n" + "="*80)
    print("Example 2: Filtered Ingestion")
    print("="*80)

    from github_issues_ingestion import create_ingestion_pipeline

    orchestrator = create_ingestion_pipeline()

    # Ingest only open bugs
    stats = orchestrator.ingest_repository(
        owner="wso2",
        repo="choreo",
        state="open",
        labels=["bug"],
        max_issues=10
    )

    print(f"\nFiltered ingestion completed!")
    print(f"Processed {stats['total_issues']} open bug issues")


def example_querying():
    """Example 3: Query the vector database."""
    print("\n" + "="*80)
    print("Example 3: Querying Issues")
    print("="*80)

    from github_issues_ingestion import create_ingestion_pipeline

    orchestrator = create_ingestion_pipeline()

    # Query for authentication-related issues
    query = "authentication error with OAuth"
    print(f"\nQuerying for: '{query}'")

    results = orchestrator.query_issues(
        query=query,
        top_k=5
    )

    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"{i}. Issue #{metadata.get('issue_number')}: {metadata.get('issue_title', 'N/A')}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Repository: {metadata.get('repository')}")
        print(f"   State: {metadata.get('state')}")
        print(f"   Chunk: {metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}")
        print(f"   Preview: {result['content'][:150]}...")
        print()


def example_custom_configuration():
    """Example 4: Custom configuration."""
    print("\n" + "="*80)
    print("Example 4: Custom Configuration")
    print("="*80)

    from github_issues_ingestion import (
        Settings,
        GitHubIssueFetcher,
        TextProcessorService,
        ChunkingService,
        AzureEmbeddingService,
        PineconeVectorStore,
        IngestionOrchestrator,
    )

    # Load settings
    settings = Settings.from_env()

    # Create custom components
    issue_fetcher = GitHubIssueFetcher(token=settings.github_token)

    # Exclude code blocks from processing
    text_processor = TextProcessorService(include_code_blocks=False)

    # Use smaller chunks
    chunker = ChunkingService(chunk_size=500, overlap=100)

    embedding_service = AzureEmbeddingService(
        api_key=settings.azure_openai_api_key,
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_embeddings_deployment,
        api_version=settings.azure_openai_api_version
    )

    # Use Milvus vector store
    vector_store = MilvusVectorStore(
        uri=settings.milvus_uri,
        token=settings.milvus_token,
        collection_name=settings.milvus_collection_name,
        dimension=settings.milvus_dimension,
        metric=settings.milvus_metric
    )

    # Create orchestrator with custom components
    orchestrator = IngestionOrchestrator(
        issue_fetcher=issue_fetcher,
        text_processor=text_processor,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
        batch_size=5
    )

    print("Created orchestrator with custom configuration:")
    print(f"  - Chunk size: 500")
    print(f"  - Overlap: 100")
    print(f"  - Batch size: 5")
    print(f"  - Code blocks: Excluded")
    print(f"  - Namespace: custom-issues")


def example_incremental_updates():
    """Example 5: Incremental updates (only new issues)."""
    print("\n" + "="*80)
    print("Example 5: Incremental Updates")
    print("="*80)

    from github_issues_ingestion import create_ingestion_pipeline
    from datetime import datetime, timedelta

    orchestrator = create_ingestion_pipeline()

    # Get issues updated in the last 7 days
    since_date = datetime.utcnow() - timedelta(days=7)
    since_timestamp = since_date.isoformat() + "Z"

    print(f"Fetching issues updated since: {since_date.strftime('%Y-%m-%d')}")

    stats = orchestrator.ingest_repository(
        owner="wso2",
        repo="choreo",
        since=since_timestamp,
        max_issues=20
    )

    print(f"\nIncremental update completed!")
    print(f"Updated with {stats['total_issues']} recent issues")


def example_query_with_filters():
    """Example 6: Query with metadata filters."""
    print("\n" + "="*80)
    print("Example 6: Query with Metadata Filters")
    print("="*80)

    from github_issues_ingestion import create_ingestion_pipeline

    orchestrator = create_ingestion_pipeline()

    # Query only open issues
    results = orchestrator.query_issues(
        query="deployment error",
        top_k=5,
        filter_dict={
            "state": "open",
            # "labels": ["bug"]  # Can also filter by labels
        }
    )

    print(f"Found {len(results)} open issues matching 'deployment error'")

    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\n{i}. Issue #{metadata.get('issue_number')}")
        print(f"   Title: {metadata.get('issue_title', 'N/A')}")
        print(f"   Score: {result['score']:.4f}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("GitHub Issues Ingestion - Usage Examples")
    print("="*80)
    print("\nThese examples demonstrate different ways to use the system.")
    print("You can run each example individually or all together.")
    print()

    examples = [
        ("Basic Ingestion", example_basic_ingestion),
        ("Filtered Ingestion", example_filtered_ingestion),
        ("Querying Issues", example_querying),
        ("Custom Configuration", example_custom_configuration),
        ("Incremental Updates", example_incremental_updates),
        ("Query with Filters", example_query_with_filters),
    ]

    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nNote: Examples 1, 2, 3, 5, and 6 will actually ingest/query data.")
    print("      Example 4 only shows configuration without running ingestion.")

    choice = input("\nEnter example number to run (or 'all' for all examples): ").strip()

    if choice.lower() == 'all':
        for name, func in examples:
            try:
                func()
            except KeyboardInterrupt:
                print("\n\nExamples interrupted by user")
                break
            except Exception as e:
                print(f"\n✗ Error in {name}: {e}")
                import traceback
                traceback.print_exc()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice. Exiting.")
        return 1

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80)
    return 0


if __name__ == "__main__":
    sys.exit(main())

