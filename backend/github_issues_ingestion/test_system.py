#!/usr/bin/env python3
"""
Test script for GitHub Issues Ingestion System.
Tests individual components and the complete pipeline.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        from github_issues_ingestion.config import Settings
        settings = Settings.from_env()
        print(f"✓ Configuration loaded: {settings}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_github_fetcher():
    """Test GitHub issue fetcher."""
    print("\nTesting GitHub issue fetcher...")
    try:
        from github_issues_ingestion.config import Settings
        from github_issues_ingestion.services import GitHubIssueFetcher
        
        settings = Settings.from_env()
        fetcher = GitHubIssueFetcher(token=settings.github_token)
        
        # Test rate limit check
        rate_limit = fetcher.get_rate_limit_status()
        print(f"  Rate limit: {rate_limit.get('remaining', 0)}/{rate_limit.get('limit', 0)}")
        
        # Fetch a small number of issues for testing
        print("  Fetching 3 issues from wso2/choreo...")
        issues = fetcher.fetch_issues("wso2", "choreo", max_issues=3)
        
        if issues:
            print(f"✓ Successfully fetched {len(issues)} issues")
            print(f"  Example: #{issues[0].number} - {issues[0].title[:50]}...")
            print(f"  Comments: {len(issues[0].comments)}")
            return True
        else:
            print("✗ No issues fetched")
            return False
            
    except Exception as e:
        print(f"✗ GitHub fetcher error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_processor():
    """Test text processor."""
    print("\nTesting text processor...")
    try:
        from github_issues_ingestion.services import TextProcessorService
        from github_issues_ingestion.models import GitHubIssue
        from datetime import datetime
        
        processor = TextProcessorService()
        
        # Create a test issue
        test_issue = GitHubIssue(
            number=123,
            title="Test Issue",
            body="This is a test issue with some **markdown** and `code`.",
            state="open",
            owner="test",
            repo="repo",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            labels=["bug", "test"],
            comments=[
                {
                    "user": "testuser",
                    "body": "This is a test comment",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        )
        
        processed = processor.process_issue(test_issue)
        
        if processed and len(processed) > 0:
            print(f"✓ Text processed successfully ({len(processed)} characters)")
            print(f"  Preview: {processed[:100]}...")
            return True
        else:
            print("✗ Text processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Text processor error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunker():
    """Test chunking service."""
    print("\nTesting chunking service...")
    try:
        from github_issues_ingestion.services import ChunkingService
        
        chunker = ChunkingService(chunk_size=500, overlap=100)
        
        test_text = "This is a test. " * 100  # Create a long text
        chunks = chunker.chunk_text(test_text, metadata={"test": "value"})
        
        if chunks:
            print(f"✓ Created {len(chunks)} chunks")
            print(f"  Chunk size: {chunker.get_chunk_size()}")
            print(f"  Overlap: {chunker.get_overlap()}")
            print(f"  First chunk: {chunks[0].content[:50]}...")
            return True
        else:
            print("✗ Chunking failed")
            return False
            
    except Exception as e:
        print(f"✗ Chunker error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_service():
    """Test Azure embedding service."""
    print("\nTesting Azure embedding service...")
    try:
        from github_issues_ingestion.config import Settings
        from github_issues_ingestion.services import AzureEmbeddingService
        
        settings = Settings.from_env()
        embedding_service = AzureEmbeddingService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_embeddings_deployment,
            api_version=settings.azure_openai_api_version
        )
        
        # Test single embedding
        test_text = "This is a test for embedding generation."
        embedding = embedding_service.create_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✓ Created embedding with dimension {len(embedding)}")
            
            # Test batch embeddings
            test_texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = embedding_service.create_embeddings_batch(test_texts)
            
            if len(embeddings) == len(test_texts):
                print(f"✓ Batch embeddings created successfully ({len(embeddings)} embeddings)")
                return True
            else:
                print("✗ Batch embedding count mismatch")
                return False
        else:
            print("✗ Embedding creation failed")
            return False
            
    except Exception as e:
        print(f"✗ Embedding service error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test Pinecone vector store."""
    print("\nTesting Pinecone vector store...")
    try:
        from github_issues_ingestion.config import Settings
        from github_issues_ingestion.services import PineconeVectorStore
        
        settings = Settings.from_env()
        vector_store = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index_name,
            dimension=settings.pinecone_dimension,
            namespace="test-namespace"
        )
        
        # Get stats
        stats = vector_store.get_stats()
        print(f"✓ Connected to Pinecone")
        print(f"  Index stats: {stats}")
        return True
            
    except Exception as e:
        print(f"✗ Vector store error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_pipeline():
    """Test the complete pipeline with a single issue."""
    print("\nTesting complete pipeline...")
    try:
        from github_issues_ingestion import create_ingestion_pipeline
        
        orchestrator = create_ingestion_pipeline(batch_size=5)
        
        print("  Running ingestion for 1 issue from wso2/choreo...")
        stats = orchestrator.ingest_repository(
            owner="wso2",
            repo="choreo",
            max_issues=1
        )
        
        if stats["total_issues"] > 0 and stats["total_chunks"] > 0:
            print(f"✓ Pipeline completed successfully")
            print(f"  Issues: {stats['total_issues']}")
            print(f"  Chunks: {stats['total_chunks']}")
            print(f"  Embeddings: {stats['total_embeddings']}")
            
            # Test query
            print("\n  Testing query...")
            results = orchestrator.query_issues("test query", top_k=3)
            print(f"✓ Query returned {len(results)} results")
            
            return True
        else:
            print("✗ Pipeline produced no results")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("GitHub Issues Ingestion System - Test Suite")
    print("="*80)
    
    tests = [
        ("Configuration", test_configuration),
        ("GitHub Fetcher", test_github_fetcher),
        ("Text Processor", test_text_processor),
        ("Chunker", test_chunker),
        ("Embedding Service", test_embedding_service),
        ("Vector Store", test_vector_store),
        ("Complete Pipeline", test_complete_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    print("="*80)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

