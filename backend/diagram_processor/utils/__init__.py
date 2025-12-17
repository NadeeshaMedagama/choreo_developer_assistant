"""
Configuration Management for Diagram Processor

Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from backend/.env (local) or system environment (cloud)
# For Choreo deployment, environment variables are injected by the platform
env_path = Path(__file__).resolve().parent.parent.parent / "backend" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # In cloud deployment (Choreo), .env might not exist - use system environment
    load_dotenv()  # Load from system environment


class Config:
    """Configuration settings for the diagram processor."""

    # Project paths - Fixed to point to correct locations
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # choreo-ai-assistant directory
    DATA_DIR = BASE_DIR / "data" / "diagrams"
    OUTPUT_DIR = BASE_DIR / "diagram_processor" / "output"
    CREDENTIALS_DIR = BASE_DIR / "credentials"

    # Milvus settings
    MILVUS_URI: str = os.getenv("MILVUS_URI", "")
    MILVUS_TOKEN: str = os.getenv("MILVUS_TOKEN", "")
    MILVUS_COLLECTION_NAME: str = os.getenv("MILVUS_COLLECTION_NAME", "")
    MILVUS_DIMENSION: int = int(os.getenv("MILVUS_DIMENSION", "1536"))
    MILVUS_METRIC: str = os.getenv("MILVUS_METRIC", "COSINE")

    # Azure OpenAI settings (primary)
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "")
    AZURE_OPENAI_EMBEDDINGS_VERSION: str = os.getenv("AZURE_OPENAI_EMBEDDINGS_VERSION", "2024-02-01")

    # Legacy OpenAI settings (fallback)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY", ""))
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_VISION_API_KEY: str = os.getenv("GOOGLE_VISION_API_KEY", "")

    @classmethod
    def _load_google_credentials(cls):
        """Load Google Cloud credentials from environment or credentials directory."""
        # Option 1: Check if credentials are provided as JSON string (Choreo secrets)
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            # Write JSON string to temp file for google-cloud-vision
            import json
            temp_creds_path = Path("/tmp/google-vision-creds.json")
            try:
                # Validate it's valid JSON
                json.loads(creds_json)
                temp_creds_path.write_text(creds_json)
                cls.GOOGLE_APPLICATION_CREDENTIALS = str(temp_creds_path)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(temp_creds_path)
                return
            except json.JSONDecodeError:
                pass  # Fall through to other methods

        # Option 2: Check if GOOGLE_APPLICATION_CREDENTIALS is set in .env (file path)
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and Path(creds_path).exists():
            # Use the path from environment variable
            cls.GOOGLE_APPLICATION_CREDENTIALS = creds_path
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            return

        # Option 3: Look for credentials file in credentials directory
        if cls.CREDENTIALS_DIR.exists():
            # Look for Google Cloud service account JSON files
            json_files = list(cls.CREDENTIALS_DIR.glob("*.json"))
            if json_files:
                # Use the first JSON file found
                cls.GOOGLE_APPLICATION_CREDENTIALS = str(json_files[0])
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(json_files[0])
                return

        # No credentials found - will rely on GOOGLE_VISION_API_KEY if available
        cls.GOOGLE_APPLICATION_CREDENTIALS = None

    # GitHub Token
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    # Processing settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "3000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))

    # OCR settings
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD")  # Path to tesseract executable

    # File size limits (in bytes)
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB default

    # Summary settings
    MAX_SUMMARY_LENGTH: int = int(os.getenv("MAX_SUMMARY_LENGTH", "500"))

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        # Load Google credentials
        cls._load_google_credentials()

        required_keys = [
            "MILVUS_URI",
        ]

        # Check for either Azure OpenAI or standard OpenAI
        has_azure = cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT
        has_openai = cls.OPENAI_API_KEY and not cls.AZURE_OPENAI_API_KEY

        if not (has_azure or has_openai):
            required_keys.append("OPENAI_API_KEY or AZURE_OPENAI_API_KEY")

        missing = []
        for key in required_keys:
            if " or " in key:
                # Special handling for OR conditions
                continue
            if not getattr(cls, key):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True

    @classmethod
    def ensure_directories(cls):
        """Ensure output directories exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (cls.OUTPUT_DIR / "summaries").mkdir(exist_ok=True)
        (cls.OUTPUT_DIR / "graphs").mkdir(exist_ok=True)
        (cls.OUTPUT_DIR / "extracted_text").mkdir(exist_ok=True)
        cls.CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
