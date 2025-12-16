"""
Verify Milvus Data - Check if wiki data was ingested successfully
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from db.vector_client import VectorClient


def main():
    """Verify data in Milvus collection."""
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(env_path)

    # Configuration
    MILVUS_URI = os.getenv('MILVUS_URI')
    MILVUS_TOKEN = os.getenv('MILVUS_TOKEN')
    MILVUS_COLLECTION = os.getenv('MILVUS_COLLECTION_NAME', 'choreo_developer_assistant')

    if not all([MILVUS_URI, MILVUS_TOKEN]):
        print("❌ Missing required environment variables:")
        print("   - MILVUS_URI")
        print("   - MILVUS_TOKEN")
        return 1

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              MILVUS DATA VERIFICATION                        ║
╚══════════════════════════════════════════════════════════════╝

Collection: {MILVUS_COLLECTION}
""")

    # Connect to Milvus
    print("🔧 Connecting to Milvus...")
    try:
        vector_client = VectorClient(
            uri=MILVUS_URI,
            token=MILVUS_TOKEN,
            collection_name=MILVUS_COLLECTION
        )
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}\n")
        return 1

    # Test connection
    print("🔍 Testing connection...")
    try:
        is_healthy = vector_client.test_connection()
        if is_healthy:
            print("✅ Connection is healthy\n")
        else:
            print("⚠️  Connection test failed\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")

    # Get collection stats
    print("📊 Getting collection statistics...")
    try:
        stats = vector_client.client.get_collection_stats(collection_name=MILVUS_COLLECTION)
        
        row_count = stats.get('row_count', 0)
        print(f"✅ Collection Statistics:")
        print(f"   • Total entities: {row_count:,}")
        
        if row_count == 0:
            print("\n⚠️  No data found in collection!")
            print("   Run the ingestion script to add data:")
            print("   python -m wiki_ingestion.examples.ingest_to_milvus")
            return 0
        
        print()
    except Exception as e:
        print(f"❌ Failed to get stats: {e}\n")
        return 1

    # Query sample data
    print("📄 Fetching sample records...")
    try:
        # Query first 5 records
        results = vector_client.client.query(
            collection_name=MILVUS_COLLECTION,
            filter="",
            output_fields=["content", "source_title", "source_url", "source_type"],
            limit=5
        )
        
        if results:
            print(f"✅ Found {len(results)} sample records:\n")
            for i, entity in enumerate(results, 1):
                print(f"Record {i}:")
                print(f"  Title: {entity.get('source_title', 'N/A')}")
                print(f"  Type: {entity.get('source_type', 'N/A')}")
                print(f"  URL: {entity.get('source_url', 'N/A')}")
                print(f"  Content: {entity.get('content', '')[:100]}...")
                print()
        else:
            print("⚠️  No records found\n")
    except Exception as e:
        print(f"❌ Failed to query data: {e}\n")

    # Test search functionality
    print("🔍 Testing search functionality...")
    try:
        from openai import AzureOpenAI
        
        AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        AZURE_EMBEDDING_DEPLOYMENT = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT', 'choreo-ai-embedding')
        AZURE_API_VERSION = os.getenv('AZURE_OPENAI_EMBEDDINGS_VERSION', '2024-02-01')
        
        if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
            print("⚠️  Skipping search test - Azure OpenAI not configured\n")
        else:
            # Create OpenAI client
            openai_client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            
            # Create test query embedding
            test_query = "What is Choreo?"
            print(f"   Query: '{test_query}'")
            
            response = openai_client.embeddings.create(
                model=AZURE_EMBEDDING_DEPLOYMENT,
                input=[test_query]
            )
            query_embedding = response.data[0].embedding
            
            # Search in Milvus
            search_results = vector_client.query_similar(
                vector=query_embedding,
                top_k=3
            )
            
            if search_results:
                print(f"✅ Search returned {len(search_results)} results:\n")
                for i, result in enumerate(search_results, 1):
                    print(f"Result {i}:")
                    print(f"  Score: {result['score']:.4f}")
                    print(f"  Content: {result['content'][:150]}...")
                    print()
            else:
                print("⚠️  Search returned no results\n")
    except Exception as e:
        print(f"⚠️  Search test failed: {e}\n")

    # Summary
    print("="*80)
    print("✅ VERIFICATION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Collection: {MILVUS_COLLECTION}")
    print(f"   • Total records: {row_count:,}")
    print(f"   • Status: {'✅ Healthy' if is_healthy else '⚠️  Check connection'}")
    print("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

