"""
File Discovery Service

Responsible for discovering and cataloging diagram files in the data directory.
Follows Single Responsibility Principle - only handles file discovery.
"""

from pathlib import Path
from typing import List, Set
from datetime import datetime

from ..models import DiagramFile, FileType
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileDiscoveryService:
    """Service for discovering diagram files in a directory."""

    # Supported file extensions mapped to FileType
    SUPPORTED_EXTENSIONS = {
        '.png': FileType.PNG,
        '.jpg': FileType.JPG,
        '.jpeg': FileType.JPEG,
        '.svg': FileType.SVG,
        '.pdf': FileType.PDF,
        '.drawio': FileType.DRAWIO,
        '.docx': FileType.DOCX,
        '.xlsx': FileType.XLSX,
        '.pptx': FileType.PPTX,
    }

    def __init__(self, base_directory: Path, max_file_size: int = 50 * 1024 * 1024):
        """
        Initialize file discovery service.

        Args:
            base_directory: Root directory to search for files
            max_file_size: Maximum file size in bytes (default 50MB)
        """
        self.base_directory = Path(base_directory)
        self.max_file_size = max_file_size

        if not self.base_directory.exists():
            raise ValueError(f"Directory does not exist: {self.base_directory}")

    def discover_all_files(self) -> List[DiagramFile]:
        """
        Discover all supported diagram files in the directory.

        Returns:
            List of DiagramFile objects
        """
        logger.info(f"Starting file discovery in: {self.base_directory}")

        discovered_files = []
        skipped_files = []

        for extension, file_type in self.SUPPORTED_EXTENSIONS.items():
            files = self._find_files_by_extension(extension, file_type)
            discovered_files.extend(files)

        logger.info(f"Discovered {len(discovered_files)} files")
        logger.info(f"File type breakdown:")

        # Log statistics by file type
        type_counts = {}
        for file in discovered_files:
            type_counts[file.file_type] = type_counts.get(file.file_type, 0) + 1

        for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {file_type.value}: {count} files")

        return discovered_files

    def _find_files_by_extension(self, extension: str, file_type: FileType) -> List[DiagramFile]:
        """
        Find all files with a specific extension.

        Args:
            extension: File extension (e.g., '.png')
            file_type: FileType enum value

        Returns:
            List of DiagramFile objects
        """
        files = []
        pattern = f"**/*{extension}"

        for file_path in self.base_directory.glob(pattern):
            if not file_path.is_file():
                continue

            try:
                file_size = file_path.stat().st_size

                # Skip files that are too large
                if file_size > self.max_file_size:
                    logger.warning(f"Skipping large file ({file_size / 1024 / 1024:.1f}MB): {file_path.name}")
                    continue

                # Skip hidden files
                if file_path.name.startswith('.'):
                    continue

                # Get relative path from base directory
                relative_path = str(file_path.relative_to(self.base_directory))

                # Get last modified time
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

                diagram_file = DiagramFile(
                    file_path=file_path,
                    file_type=file_type,
                    file_size=file_size,
                    file_name=file_path.name,
                    relative_path=relative_path,
                    last_modified=last_modified
                )

                files.append(diagram_file)

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue

        return files

    def filter_by_type(self, files: List[DiagramFile], file_types: Set[FileType]) -> List[DiagramFile]:
        """
        Filter files by type.

        Args:
            files: List of DiagramFile objects
            file_types: Set of FileType to include

        Returns:
            Filtered list of DiagramFile objects
        """
        return [f for f in files if f.file_type in file_types]

    def get_file_statistics(self, files: List[DiagramFile]) -> dict:
        """
        Get statistics about discovered files.

        Args:
            files: List of DiagramFile objects

        Returns:
            Dictionary with statistics
        """
        total_size = sum(f.file_size for f in files)

        type_stats = {}
        for file in files:
            if file.file_type not in type_stats:
                type_stats[file.file_type] = {
                    'count': 0,
                    'total_size': 0,
                    'files': []
                }
            type_stats[file.file_type]['count'] += 1
            type_stats[file.file_type]['total_size'] += file.file_size
            type_stats[file.file_type]['files'].append(file.file_name)

        return {
            'total_files': len(files),
            'total_size_mb': total_size / 1024 / 1024,
            'by_type': {
                ft.value: {
                    'count': stats['count'],
                    'size_mb': stats['total_size'] / 1024 / 1024
                }
                for ft, stats in type_stats.items()
            }
        }

