"""
Git-based Wiki Ingestion for Private Repositories
Uses git clone to access private wikis that require authentication
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from wiki_ingestion.services import WikiChunkingService
from wiki_ingestion.models.wiki_page import WikiPage
from wiki_ingestion.models.wiki_chunk import WikiChunk

# Import VectorClient
try:
    from db.vector_client import VectorClient
except ImportError:
    import sys
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from db.vector_client import VectorClient


def clone_private_wiki(repo_owner: str, repo_name: str, github_token: str, target_dir: str) -> bool:
    """Clone a private GitHub wiki using git."""
    wiki_repo = f"{repo_owner}/{repo_name}.wiki"
    clone_url = f"https://{github_token}@github.com/{wiki_repo}.git"
    
    print(f"📥 Cloning wiki: {repo_owner}/{repo_name}")
    
    # Remove existing directory
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    try:
        result = subprocess.run(
            ['git', 'clone', clone_url, target_dir],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully cloned wiki to {target_dir}")
            return True
        else:
            print(f"❌ Failed to clone wiki")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error cloning wiki: {e}")
        return False


def read_markdown_files(wiki_dir: str, repo_owner: str, repo_name: str) -> list:
    """Read all markdown files from the cloned wiki."""
    pages = []
    wiki_path = Path(wiki_dir)
    
    # Find all markdown files
    md_files = list(wiki_path.glob("*.md"))
    
    print(f"\n📄 Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create WikiPage object
            page = WikiPage(
                url=f"https://github.com/{repo_owner}/{repo_name}/wiki/{md_file.stem}",
                title=md_file.stem.replace('-', ' '),
                content=content,
                depth=0,
                internal_urls=set(),
                external_urls=set()
            )
            
            # Add metadata
            page.metadata['wiki_name'] = repo_name
            page.metadata['file_path'] = str(md_file.relative_to(wiki_path))
            page.metadata['repository'] = f"{repo_owner}/{repo_name}"
            page.metadata['owner'] = repo_owner
            
            pages.append(page)
            print(f"  ✓ {md_file.name} ({len(content)} chars)")
            
        except Exception as e:
            print(f"  ✗ Error reading {md_file.name}: {e}")
    
    return pages


def main():
    """Run git-based wiki ingestion for private repositories."""
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(env_path)
    
    # Configuration
    WIKI_URL = os.getenv('WIKI_URL', 'https://github.com/wso2-enterprise/choreo/wiki')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Milvus Configuration
    MILVUS_URI = os.getenv('MILVUS_URI')
    MILVUS_TOKEN = os.getenv('MILVUS_TOKEN')
    MILVUS_COLLECTION = os.getenv('MILVUS_COLLECTION_NAME', 'choreo_developer_assistant')
    MILVUS_DIMENSION = int(os.getenv('MILVUS_DIMENSION', '1536'))
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_EMBEDDING_DEPLOYMENT = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT', 'choreo-ai-embedding')
    AZURE_API_VERSION = os.getenv('AZURE_OPENAI_EMBEDDINGS_VERSION', '2024-02-01')
    
    # Validate required variables
    if not all([GITHUB_TOKEN, MILVUS_URI, MILVUS_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
        print("❌ Missing required environment variables")
        return 1
    
    # Parse wiki URL to get owner and repo
    # Format: https://github.com/owner/repo/wiki
    parts = WIKI_URL.replace('https://github.com/', '').replace('/wiki', '').split('/')
    if len(parts) < 2:
        print(f"❌ Invalid wiki URL: {WIKI_URL}")
        return 1
    
    repo_owner, repo_name = parts[0], parts[1]
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       GIT-BASED WIKI INGESTION (PRIVATE REPOS)               ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  📚 Repository: {repo_owner}/{repo_name}
  🔐 Authentication: GitHub Token
  
  🗄️  Milvus Collection: {MILVUS_COLLECTION}
  📏 Embedding Dimension: {MILVUS_DIMENSION}
  🤖 Embedding Model: {AZURE_EMBEDDING_DEPLOYMENT}
  
""")
    
    # Clone wiki to temp directory
    temp_dir = f"/tmp/choreo_wiki_{repo_name}"
    
    if not clone_private_wiki(repo_owner, repo_name, GITHUB_TOKEN, temp_dir):
        return 1
    
    # Read markdown files
    print("\n" + "="*80)
    print("READING WIKI FILES")
    print("="*80)
    
    pages = read_markdown_files(temp_dir, repo_owner, repo_name)
    
    if not pages:
        print("\n❌ No wiki pages found!")
        return 1
    
    print(f"\n✅ Read {len(pages)} wiki pages")
    
    # Chunk the pages
    print("\n" + "="*80)
    print("CHUNKING CONTENT")
    print("="*80)
    
    chunking_service = WikiChunkingService(
        chunk_size=1000,
        chunk_overlap=200,
        min_chunk_size=100
    )
    
    all_chunks = []
    for i, page in enumerate(pages, 1):
        print(f"  [{i}/{len(pages)}] Chunking: {page.title}")
        chunks = chunking_service.chunk_page(page)
        all_chunks.extend(chunks)
        print(f"     → {len(chunks)} chunks")
    
    print(f"\n✅ Created {len(all_chunks)} total chunks")
    
    # Initialize Milvus
    print("\n" + "="*80)
    print("CONNECTING TO MILVUS")
    print("="*80)
    
    try:
        vector_client = VectorClient(
            uri=MILVUS_URI,
            token=MILVUS_TOKEN,
            collection_name=MILVUS_COLLECTION,
            dimension=MILVUS_DIMENSION,
            metric="COSINE"
        )
        print("✅ Connected to Milvus")
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        return 1
    
    # Initialize Azure OpenAI
    print("\n🔧 Initializing Azure OpenAI...")
    try:
        from openai import AzureOpenAI
        
        openai_client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print("✅ Azure OpenAI initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI: {e}")
        return 1
    
    # Embed and store
    print("\n" + "="*80)
    print(f"EMBEDDING AND STORING {len(all_chunks)} CHUNKS")
    print("="*80)
    
    batch_size = 10
    stored_count = 0
    failed_count = 0
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(all_chunks) + batch_size - 1) // batch_size
        
        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        try:
            # Create embeddings
            texts = [chunk.text for chunk in batch]
            
            print(f"   🔄 Creating embeddings...")
            response = openai_client.embeddings.create(
                model=AZURE_EMBEDDING_DEPLOYMENT,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Prepare for Milvus
            items_to_insert = []
            for chunk, embedding in zip(batch, embeddings):
                metadata = chunk.to_vector_metadata()
                item = {
                    'content': chunk.text,
                    'vector': embedding,
                    'metadata': metadata
                }
                items_to_insert.append(item)
            
            # Insert to Milvus
            print(f"   💾 Storing in Milvus...")
            vector_client.insert_embeddings_batch(items_to_insert)
            
            stored_count += len(batch)
            print(f"   ✅ Batch complete ({stored_count}/{len(all_chunks)} total)")
            
        except Exception as e:
            failed_count += len(batch)
            print(f"   ❌ Error processing batch: {e}")
            continue
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    shutil.rmtree(temp_dir)
    
    # Summary
    print("\n" + "="*80)
    print("✅ GIT-BASED WIKI INGESTION COMPLETE")
    print("="*80)
    print(f"\n📊 Statistics:")
    print(f"   • Repository: {repo_owner}/{repo_name}")
    print(f"   • Wiki pages: {len(pages)}")
    print(f"   • Total chunks: {len(all_chunks)}")
    print(f"   • Chunks stored: {stored_count}")
    print(f"   • Failed chunks: {failed_count}")
    
    if len(all_chunks) > 0:
        success_rate = stored_count/len(all_chunks)*100
        print(f"   • Success rate: {success_rate:.1f}%")
    
    print(f"\n🗄️  Milvus Collection: {MILVUS_COLLECTION}")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

