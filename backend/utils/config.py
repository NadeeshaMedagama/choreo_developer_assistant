import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
# Find the backend/.env file relative to this config file
config_dir = Path(__file__).parent  # backend/utils/
backend_dir = config_dir.parent      # backend/
env_path = backend_dir / ".env"

if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")
else:
    print(f"⚠️  .env file not found at: {env_path}")
    # Try alternate location
    alt_env = Path.cwd() / "backend" / ".env"
    if alt_env.exists():
        load_dotenv(alt_env)
        print(f"✓ Loaded environment from: {alt_env}")


class Config:
    """Configuration management for the application."""

    # Milvus Configuration
    MILVUS_URI: str = os.getenv("MILVUS_URI", "")
    MILVUS_TOKEN: str = os.getenv("MILVUS_TOKEN", "")
    MILVUS_COLLECTION_NAME: str = os.getenv("MILVUS_COLLECTION_NAME", "choreo-docs")
    MILVUS_DIMENSION: Optional[int] = int(os.getenv("MILVUS_DIMENSION", "1536"))
    MILVUS_METRIC: str = os.getenv("MILVUS_METRIC", "COSINE")

    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")  # Optional but recommended
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # Google Vision API
    GOOGLE_VISION_API_KEY: Optional[str] = os.getenv("GOOGLE_VISION_API_KEY")

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Markdown Chunking Requirements (Maximum/Minimum)
    MIN_CHUNK_CHARS: int = int(os.getenv("MIN_CHUNK_CHARS", "100"))
    MAX_CHUNK_CHARS: int = int(os.getenv("MAX_CHUNK_CHARS", "100000"))
    CHUNK_OVERLAP_CHARS: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "200"))
    CHUNK_SIZE_THRESHOLD_BYTES: int = int(os.getenv("CHUNK_SIZE_THRESHOLD_BYTES", "20000"))  # 20KB

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.MILVUS_URI:
            raise ValueError("MILVUS_URI is required")
        if not cls.MILVUS_TOKEN:
            raise ValueError("MILVUS_TOKEN is required")
        return True

config = Config()

def load_config():
    """Load and return configuration as a dictionary."""
    load_dotenv()  # Ensure .env is loaded
    return {
        # Milvus
        "MILVUS_URI": os.getenv("MILVUS_URI", ""),
        "MILVUS_TOKEN": os.getenv("MILVUS_TOKEN", ""),
        "MILVUS_COLLECTION_NAME": os.getenv("MILVUS_COLLECTION_NAME", "readme_embeddings"),
        "MILVUS_DIMENSION": int(os.getenv("MILVUS_DIMENSION", "1536")),
        "MILVUS_METRIC": os.getenv("MILVUS_METRIC", "COSINE"),

        # GitHub
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),

        # Google Vision API
        "GOOGLE_VISION_API_KEY": os.getenv("GOOGLE_VISION_API_KEY"),

        # Azure OpenAI
        "AZURE_OPENAI_KEY": os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT": os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),

        # Embedding
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),

        # Chunking
        "CHUNK_SIZE": int(os.getenv("CHUNK_SIZE", "10000")),
        "CHUNK_OVERLAP": int(os.getenv("CHUNK_OVERLAP", "200")),
    }
