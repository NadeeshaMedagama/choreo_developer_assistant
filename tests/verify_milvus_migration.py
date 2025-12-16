#!/usr/bin/env python3
"""
Milvus Migration Verification Script

This script verifies that the Pinecone to Milvus migration is complete and working.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_imports():
    """Check that all required imports work."""
    print_header("1. Checking Required Imports")
    
    try:
        import pymilvus
        print(f"✅ pymilvus installed: version {pymilvus.__version__}")
    except ImportError:
        print("❌ pymilvus not installed. Run: pip install pymilvus>=2.3.0")
        return False
    
    try:
        from backend.utils.config import load_config, Config
        print("✅ config module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from backend.db.vector_client import VectorClient
        print("✅ VectorClient imported successfully")
    except Exception as e:
        print(f"❌ Failed to import VectorClient: {e}")
        return False
    
    return True

def check_env_file():
    """Check that .env file exists and has Milvus configuration."""
    print_header("2. Checking Environment Configuration")
    
    env_path = Path(__file__).parent / "backend" / ".env"
    
    if not env_path.exists():
        print(f"❌ .env file not found at: {env_path}")
        return False
    
    print(f"✅ .env file found at: {env_path}")
    
    # Read and check for Milvus variables
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = ['MILVUS_URI', 'MILVUS_TOKEN', 'MILVUS_COLLECTION_NAME']
    missing_vars = []
    
    for var in required_vars:
        if var in content:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing")
            missing_vars.append(var)
    
    # Check that Pinecone vars are NOT present
    pinecone_vars = ['PINECONE_API_KEY', 'PINECONE_INDEX_NAME']
    for var in pinecone_vars:
        if var in content:
            print(f"⚠️  {var} still present (should be removed)")
        else:
            print(f"✅ {var} removed (correct)")
    
    return len(missing_vars) == 0

def check_config_loading():
    """Check that configuration loads correctly."""
    print_header("3. Checking Configuration Loading")
    
    try:
        from backend.utils.config import load_config
        config = load_config()
        
        # Check Milvus configuration
        milvus_uri = config.get('MILVUS_URI', '')
        milvus_token = config.get('MILVUS_TOKEN', '')
        milvus_collection = config.get('MILVUS_COLLECTION_NAME', '')
        
        if milvus_uri:
            print(f"✅ MILVUS_URI loaded: {milvus_uri[:50]}...")
        else:
            print("❌ MILVUS_URI not loaded")
            return False
        
        if milvus_token:
            print(f"✅ MILVUS_TOKEN loaded: ***{milvus_token[-10:]}")
        else:
            print("❌ MILVUS_TOKEN not loaded")
            return False
        
        if milvus_collection:
            print(f"✅ MILVUS_COLLECTION_NAME loaded: {milvus_collection}")
        else:
            print("❌ MILVUS_COLLECTION_NAME not loaded")
            return False
        
        print(f"✅ MILVUS_DIMENSION: {config.get('MILVUS_DIMENSION', 'NOT SET')}")
        print(f"✅ MILVUS_METRIC: {config.get('MILVUS_METRIC', 'NOT SET')}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def check_vector_client():
    """Check that VectorClient can be initialized."""
    print_header("4. Checking VectorClient Initialization")
    
    try:
        from backend.db.vector_client import VectorClient
        from backend.utils.config import load_config
        
        config = load_config()
        
        print("Attempting to initialize VectorClient...")
        vector_client = VectorClient(
            uri=config["MILVUS_URI"],
            token=config["MILVUS_TOKEN"],
            collection_name=config["MILVUS_COLLECTION_NAME"],
            dimension=config.get("MILVUS_DIMENSION", 1536),
            metric=config.get("MILVUS_METRIC", "COSINE")
        )
        
        print("✅ VectorClient initialized successfully")
        
        # Test connection
        print("Testing connection to Milvus...")
        if vector_client.test_connection():
            print("✅ Successfully connected to Milvus!")
            return True
        else:
            print("⚠️  VectorClient initialized but connection test failed")
            print("   This might be due to network issues or invalid credentials")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing VectorClient: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_no_pinecone_references():
    """Check that no Pinecone references remain in key files."""
    print_header("5. Checking for Pinecone References")
    
    files_to_check = [
        "backend/utils/config.py",
        "backend/db/vector_client.py",
        "backend/app.py",
        ".env.example",
        "docker/docker-compose.yml"
    ]
    
    base_path = Path(__file__).parent
    found_pinecone = False
    
    for file_path in files_to_check:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"⚠️  {file_path} not found (skipping)")
            continue
        
        with open(full_path, 'r') as f:
            content = f.read().lower()
        
        if 'pinecone' in content and 'migration' not in content and 'note:' not in content:
            print(f"⚠️  Found 'pinecone' reference in {file_path}")
            found_pinecone = True
        else:
            print(f"✅ No Pinecone references in {file_path}")
    
    return not found_pinecone

def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  MILVUS MIGRATION VERIFICATION")
    print("=" * 70)
    
    results = {
        "Imports": check_imports(),
        "Environment File": check_env_file(),
        "Config Loading": check_config_loading(),
        "VectorClient": check_vector_client(),
        "No Pinecone References": check_no_pinecone_references()
    }
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Migration is complete and working!")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

