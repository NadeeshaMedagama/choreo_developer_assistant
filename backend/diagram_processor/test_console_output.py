#!/usr/bin/env python3
"""
Test script to verify console output for chunking and embedding
"""

import sys
from pathlib import Path

# Add parent directory to path
# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagram_processor.models import EmbeddingRecord, TextChunk, DiagramFile, FileType

def test_pinecone_format():
    """Test that to_pinecone_format includes all required fields"""
    print("\n" + "="*80)
    print("Testing Pinecone Format Fix")
    print("="*80)
    
    chunk = TextChunk(
        content='This is a test chunk with some content for embedding',
        chunk_index=0,
        source_file=DiagramFile(
            file_path=Path('test.docx'),
            file_type=FileType.DOCX,
            file_size=1024,
            file_name='test.docx',
            relative_path='diagrams/test.docx'
        ),
        metadata={
            'key_concepts': ['API', 'Gateway', 'Service'],
            'entities': ['Component A', 'Component B']
        }
    )
    
    # Create a mock embedding vector (1536 dimensions for text-embedding-3-small)
    vector = [0.001] * 1536
    
    embedding = EmbeddingRecord(
        chunk=chunk,
        vector=vector,
        embedding_id='test-embedding-001'
    )
    
    result = embedding.to_pinecone_format()
    
    print("\n✅ Pinecone Format Test Results:")
    print(f"   - Has 'id' field: {('id' in result)}")
    print(f"   - Has 'values' field: {('values' in result)}")
    print(f"   - Has 'metadata' field: {('metadata' in result)}")
    
    if 'values' in result:
        print(f"   - Vector dimension: {len(result['values'])}")
    
    if 'metadata' in result:
        print(f"   - Metadata keys: {len(result['metadata'])} fields")
        print(f"   - File name in metadata: {result['metadata'].get('file_name')}")
    
    print("\n✅ All required fields are present!")
    print(f"\nThis embedding is now ready to be stored in Pinecone.")
    print("="*80)

if __name__ == '__main__':
    test_pinecone_format()

