"""
Domain Models for Diagram Processing

Represents the core entities in the diagram processing domain.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class FileType(Enum):
    """Supported file types for processing."""
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    SVG = "svg"
    PDF = "pdf"
    DRAWIO = "drawio"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    UNKNOWN = "unknown"


@dataclass
class DiagramFile:
    """Represents a diagram file to be processed."""

    file_path: Path
    file_type: FileType
    file_size: int
    file_name: str
    relative_path: str
    last_modified: Optional[datetime] = None

    def __post_init__(self):
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

    @property
    def is_image(self) -> bool:
        """Check if file is an image type."""
        return self.file_type in [FileType.PNG, FileType.JPG, FileType.JPEG, FileType.SVG]

    @property
    def is_document(self) -> bool:
        """Check if file is a document type."""
        return self.file_type in [FileType.DOCX, FileType.XLSX, FileType.PPTX, FileType.PDF]


@dataclass
class ExtractedContent:
    """Represents content extracted from a diagram."""

    source_file: DiagramFile
    raw_text: str
    confidence_score: Optional[float] = None
    extraction_method: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)

    def __len__(self):
        return len(self.raw_text)


@dataclass
class Summary:
    """Represents a generated summary of diagram content."""

    source_file: DiagramFile
    summary_text: str
    key_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __len__(self):
        return len(self.summary_text)


@dataclass
class TextChunk:
    """Represents a chunk of text for embedding."""

    content: str
    chunk_index: int
    source_file: DiagramFile
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "chunk_index": self.chunk_index,
            "source_file": str(self.source_file.file_path),
            "file_name": self.source_file.file_name,
            "file_type": self.source_file.file_type.value,
            "metadata": self.metadata
        }


@dataclass
class EmbeddingRecord:
    """Represents an embedding ready for storage."""

    chunk: TextChunk
    vector: List[float]
    embedding_id: str

    def to_milvus_format(self) -> Dict[str, Any]:
        """Convert to Milvus-compatible format."""
        # Convert string ID to int64 for Milvus
        # Use hash to generate consistent numeric ID from string
        # Use 15 hex chars to stay within signed int64 range (max: 2^63-1)
        import hashlib
        hash_hex = hashlib.sha256(self.embedding_id.encode()).hexdigest()
        numeric_id = int(hash_hex[:15], 16)  # 15 hex chars = 60 bits, safely under 63-bit limit

        # Prepare metadata for Milvus
        data = {
            "id": numeric_id,
            "embedding_id": self.embedding_id,  # Store original string ID as metadata
            "vector": self.vector,
            "source": "diagram_processor",
            "file_path": str(self.chunk.source_file.file_path),
            "file_name": self.chunk.source_file.file_name,
            "file_type": self.chunk.source_file.file_type.value,
            "chunk_index": self.chunk.chunk_index,
            "content": self.chunk.content[:1000],  # Store content in Milvus
            "content_length": len(self.chunk.content),
        }

        # Add chunk metadata
        for key, value in self.chunk.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                data[f"chunk_{key}"] = value
            elif isinstance(value, list):
                # Milvus supports lists
                data[f"chunk_{key}"] = value
            else:
                # Convert complex types to JSON string
                import json
                data[f"chunk_{key}"] = json.dumps(value)

        return data

    def to_pinecone_format(self) -> Dict[str, Any]:
        """Convert to Pinecone-compatible format (deprecated - use to_milvus_format)."""
        # Flatten metadata to avoid nested dictionaries (Pinecone requirement)
        metadata = {
            "source": "diagram_processor",
            "file_path": str(self.chunk.source_file.file_path),
            "file_name": self.chunk.source_file.file_name,
            "file_type": self.chunk.source_file.file_type.value,
            "chunk_index": self.chunk.chunk_index,
            "content_preview": self.chunk.content[:200],  # First 200 chars
            "content_length": len(self.chunk.content),
        }

        # Flatten chunk metadata (convert nested dicts to JSON strings)
        for key, value in self.chunk.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                metadata[f"chunk_{key}"] = value
            elif isinstance(value, list) and all(isinstance(x, str) for x in value):
                metadata[f"chunk_{key}"] = value  # List of strings is OK
            else:
                # Convert complex types to JSON string
                import json
                metadata[f"chunk_{key}"] = json.dumps(value)

        return {
            "id": self.embedding_id,
            "values": self.vector,
            "metadata": metadata
        }


@dataclass
class ProcessingResult:
    """Represents the result of processing a diagram."""

    source_file: DiagramFile
    success: bool
    extracted_content: Optional[ExtractedContent] = None
    summary: Optional[Summary] = None
    chunks_created: int = 0
    embeddings_stored: int = 0
    error_message: Optional[str] = None
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "file_name": self.source_file.file_name,
            "file_path": str(self.source_file.file_path),
            "file_type": self.source_file.file_type.value,
            "success": self.success,
            "chunks_created": self.chunks_created,
            "embeddings_stored": self.embeddings_stored,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "has_summary": self.summary is not None,
            "summary_length": len(self.summary.summary_text) if self.summary else 0
        }


@dataclass
class KnowledgeNode:
    """Represents a node in the knowledge graph."""

    node_id: str
    label: str
    node_type: str  # e.g., "component", "service", "concept"
    source_files: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.node_id)

    def __eq__(self, other):
        return isinstance(other, KnowledgeNode) and self.node_id == other.node_id


@dataclass
class KnowledgeEdge:
    """Represents an edge in the knowledge graph."""

    source_node_id: str
    target_node_id: str
    relationship_type: str
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)

