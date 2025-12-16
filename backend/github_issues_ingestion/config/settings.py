"""
Settings and configuration for GitHub Issues Ingestion.
Loads configuration from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Settings:
    """Configuration settings for GitHub Issues Ingestion."""

    # GitHub Settings
    github_token: str
    
    # Azure OpenAI Settings
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_embeddings_deployment: str
    azure_openai_api_version: str
    
    # Milvus Settings
    milvus_uri: str
    milvus_token: str
    milvus_collection_name: str
    milvus_dimension: int = 1536

    # Legacy Pinecone Settings (for backward compatibility)
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    pinecone_dimension: int = 1536
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_use_namespaces: bool = False

    # Chunking Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Processing Settings
    batch_size: int = 10
    max_workers: int = 5
    
    # Namespace for issues
    issues_namespace: str = "github-issues"

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Settings":
        """
        Load settings from environment variables.
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            Settings instance
        """
        # Load .env file if specified
        if env_file and os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        # Try to find .env in backend directory
        backend_dir = Path(__file__).parent.parent.parent
        default_env = backend_dir / ".env"
        if default_env.exists():
            from dotenv import load_dotenv
            load_dotenv(default_env)
        
        # Validate required variables
        required_vars = [
            "GITHUB_TOKEN",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "MILVUS_URI",
            "MILVUS_TOKEN",
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return cls(
            # GitHub
            github_token=os.getenv("GITHUB_TOKEN"),
            
            # Azure OpenAI
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_embeddings_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            
            # Milvus
            milvus_uri=os.getenv("MILVUS_URI"),
            milvus_token=os.getenv("MILVUS_TOKEN"),
            milvus_collection_name=os.getenv("MILVUS_COLLECTION_NAME", "github_issues"),
            milvus_dimension=int(os.getenv("MILVUS_DIMENSION", "1536")),

            # Legacy Pinecone (for backward compatibility)
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", "choreo-ai-assistant-v2"),
            pinecone_dimension=int(os.getenv("PINECONE_DIMENSION", "1536")),
            pinecone_cloud=os.getenv("PINECONE_CLOUD", "aws"),
            pinecone_region=os.getenv("PINECONE_REGION", "us-east-1"),
            pinecone_use_namespaces=os.getenv("PINECONE_USE_NAMESPACES", "false").lower() == "true",

            # Chunking
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            
            # Processing
            batch_size=int(os.getenv("BATCH_SIZE", "10")),
            max_workers=int(os.getenv("MAX_WORKERS", "5")),
            
            # Namespace
            issues_namespace=os.getenv("ISSUES_NAMESPACE", "github-issues"),
        )

    def __repr__(self) -> str:
        """String representation (hiding sensitive data)."""
        return (
            f"Settings("
            f"github_token=*****, "
            f"azure_endpoint={self.azure_openai_endpoint}, "
            f"milvus_collection={self.milvus_collection_name}, "
            f"chunk_size={self.chunk_size}, "
            f"batch_size={self.batch_size}"
            f")"
        )

