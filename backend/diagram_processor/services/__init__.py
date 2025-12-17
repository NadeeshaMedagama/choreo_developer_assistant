"""
Diagram Processor Orchestrator

Main orchestrator that coordinates all services to process diagrams end-to-end.
Follows the Facade pattern to provide a simple interface for complex operations.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from datetime import datetime

from ..models import DiagramFile, ProcessingResult, FileType
from ..utils import Config
from ..utils.logger import setup_logger, get_logger
from .file_discovery import FileDiscoveryService
from .text_extraction import TextExtractionService
from .summary_generation import SummaryGenerationService
from .chunking import ChunkingService
from .embedding import EmbeddingService
from .knowledge_graph import KnowledgeGraphService
from ..repositories import VectorStoreRepository

logger = get_logger(__name__)


class DiagramProcessorOrchestrator:
    """
    Main orchestrator for the diagram processing pipeline.

    Coordinates all services to:
    1. Discover diagram files
    2. Extract text using OCR/parsing
    3. Generate summaries
    4. Create chunks
    5. Generate embeddings
    6. Store in Pinecone
    7. Build knowledge graph
    """

    def __init__(self, config: Config = None):
        """
        Initialize the orchestrator with all required services.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()

        # Validate configuration
        self.config.validate()
        self.config.ensure_directories()

        # Initialize services
        logger.info("Initializing Diagram Processor services...")

        self.file_discovery = FileDiscoveryService(
            base_directory=self.config.DATA_DIR,
            max_file_size=self.config.MAX_FILE_SIZE
        )

        self.text_extraction = TextExtractionService(
            google_credentials=self.config.GOOGLE_APPLICATION_CREDENTIALS
        )

        # Initialize summary generation with Azure OpenAI support
        if self.config.AZURE_OPENAI_API_KEY and self.config.AZURE_OPENAI_ENDPOINT:
            self.summary_generation = SummaryGenerationService(
                openai_api_key=self.config.AZURE_OPENAI_API_KEY,
                model=self.config.AZURE_OPENAI_CHAT_DEPLOYMENT or self.config.OPENAI_MODEL,
                max_summary_length=self.config.MAX_SUMMARY_LENGTH,
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
                azure_api_version=self.config.AZURE_OPENAI_API_VERSION,
                azure_deployment=self.config.AZURE_OPENAI_CHAT_DEPLOYMENT
            )
        else:
            self.summary_generation = SummaryGenerationService(
                openai_api_key=self.config.OPENAI_API_KEY,
                model=self.config.OPENAI_MODEL,
                max_summary_length=self.config.MAX_SUMMARY_LENGTH
            )

        self.chunking = ChunkingService(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )

        # Initialize embedding service with Azure OpenAI support
        if self.config.AZURE_OPENAI_API_KEY and self.config.AZURE_OPENAI_ENDPOINT:
            self.embedding = EmbeddingService(
                openai_api_key=self.config.AZURE_OPENAI_API_KEY,
                embedding_model=self.config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT or self.config.EMBEDDING_MODEL,
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
                azure_api_version=self.config.AZURE_OPENAI_EMBEDDINGS_VERSION or self.config.AZURE_OPENAI_API_VERSION,
                azure_deployment=self.config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT
            )
        else:
            self.embedding = EmbeddingService(
                openai_api_key=self.config.OPENAI_API_KEY,
                embedding_model=self.config.EMBEDDING_MODEL
            )

        self.vector_store = VectorStoreRepository(
            uri=self.config.MILVUS_URI,
            token=self.config.MILVUS_TOKEN,
            collection_name=self.config.MILVUS_COLLECTION_NAME
        )

        self.knowledge_graph = KnowledgeGraphService(
            output_dir=self.config.OUTPUT_DIR / "graphs"
        )

        logger.info("✓ All services initialized successfully")

    def process_all_diagrams(self, file_types: Optional[List[FileType]] = None, incremental_mode: bool = False) -> Dict[str, Any]:
        """
        Process all diagrams in the data directory.

        Args:
            file_types: Optional list of file types to process (processes all if None)
            incremental_mode: If True, skip files that already have summaries

        Returns:
            Dictionary with processing statistics and results
        """
        start_time = time.time()

        logger.info("=" * 80)
        if incremental_mode:
            logger.info("STARTING INCREMENTAL DIAGRAM PROCESSING (skipping already processed files)")
        else:
            logger.info("STARTING COMPREHENSIVE DIAGRAM PROCESSING")
        logger.info("=" * 80)

        # Step 1: Discover files
        logger.info("\n[STEP 1/7] Discovering diagram files...")
        all_files = self.file_discovery.discover_all_files()

        if not all_files:
            logger.warning("No files found to process")
            return {"status": "no_files_found", "processing_time": 0}

        # Filter by type if specified
        if file_types:
            all_files = self.file_discovery.filter_by_type(all_files, set(file_types))
            logger.info(f"Filtered to {len(all_files)} files of requested types")

        # Get statistics
        stats = self.file_discovery.get_file_statistics(all_files)
        logger.info(f"Total files: {stats['total_files']} ({stats['total_size_mb']:.1f} MB)")

        # Step 2-6: Process each file
        logger.info(f"\n[STEP 2-6/7] Processing {len(all_files)} files...")
        results = []
        summaries = []
        total_embeddings = 0
        skipped_count = 0

        for i, file in enumerate(all_files, 1):
            logger.info(f"\n--- Processing {i}/{len(all_files)}: {file.file_name} ---")
            result = self._process_single_file(file, skip_if_exists=incremental_mode)
            results.append(result)

            if result.error_message and "already processed" in result.error_message.lower():
                skipped_count += 1

            if result.success and result.summary:
                summaries.append(result.summary)
                total_embeddings += result.embeddings_stored

        # Step 7: Build knowledge graph
        logger.info(f"\n[STEP 7/7] Building knowledge graph from {len(summaries)} summaries...")
        graph_outputs = {}
        nodes = []
        edges = []
        if summaries:
            nodes, edges = self.knowledge_graph.build_graph(summaries)
            graph_outputs = self.knowledge_graph.visualize_graph(
                nodes, edges,
                output_filename="choreo_architecture_knowledge_graph"
            )

        # Calculate final statistics
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        logger.info("\n" + "=" * 80)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total files: {len(all_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        if incremental_mode and skipped_count > 0:
            logger.info(f"Skipped (already processed): {skipped_count}")
        logger.info(f"Summaries generated: {len(summaries)}")
        logger.info(f"Total chunks created: {sum(r.chunks_created for r in results)}")
        logger.info(f"Total embeddings: {total_embeddings}")
        logger.info(f"Knowledge graph nodes: {len(nodes) if summaries else 0}")
        logger.info(f"Knowledge graph edges: {len(edges) if summaries else 0}")
        logger.info(f"Processing time: {elapsed_time:.1f} seconds")
        logger.info("=" * 80)

        # Print summary to console as well
        print("\n" + "=" * 80)
        print("📊 PROCESSING SUMMARY")
        print("=" * 80)
        print(f"✓ Files Processed: {successful}/{len(all_files)}")
        if incremental_mode and skipped_count > 0:
            print(f"⏭️  Files Skipped: {skipped_count}")
        print(f"✓ Summaries Generated: {len(summaries)}")
        print(f"✓ Chunks Created: {sum(r.chunks_created for r in results)}")
        print(f"✓ Embeddings Stored: {total_embeddings}")
        print(f"✓ Knowledge Graph: {len(nodes) if summaries else 0} nodes, {len(edges) if summaries else 0} edges")
        print(f"⏱️  Total Time: {elapsed_time:.1f}s")
        print("=" * 80)

        # Save detailed report
        report = self._generate_report(results, graph_outputs, elapsed_time)

        return {
            "status": "completed",
            "total_files": len(all_files),
            "successful": successful,
            "failed": failed,
            "summaries_generated": len(summaries),
            "total_chunks": sum(r.chunks_created for r in results),
            "total_embeddings": total_embeddings,
            "knowledge_graph": {
                "nodes": len(nodes) if summaries else 0,
                "edges": len(edges) if summaries else 0,
                "visualizations": list(graph_outputs.keys())
            },
            "processing_time": elapsed_time,
            "results": [r.to_dict() for r in results],
            "report_path": str(report)
        }

    def _should_skip_file(self, file: DiagramFile) -> bool:
        """
        Check if a file should be skipped (already processed).

        Args:
            file: DiagramFile to check

        Returns:
            True if file should be skipped, False otherwise
        """
        # Check if summary file exists
        summary_dir = self.config.OUTPUT_DIR / "summaries"
        safe_name = file.file_name.replace('/', '_').replace(' ', '_')
        summary_file = summary_dir / f"{safe_name}_summary.txt"

        return summary_file.exists()

    def _process_single_file(self, file: DiagramFile, skip_if_exists: bool = False) -> ProcessingResult:
        """
        Process a single diagram file through the entire pipeline.

        Args:
            file: DiagramFile to process
            skip_if_exists: If True, skip files that already have summaries

        Returns:
            ProcessingResult with details of processing
        """
        start_time = time.time()

        # Check if should skip
        if skip_if_exists and self._should_skip_file(file):
            logger.info(f"  ⏭️  Skipping (already processed)")
            return ProcessingResult(
                source_file=file,
                success=True,
                error_message="Skipped - already processed",
                processing_time=0.0
            )

        try:
            # Extract text
            logger.info(f"  [1/5] Extracting text...")
            extracted_content = self.text_extraction.extract_text(file)

            if not extracted_content.raw_text or len(extracted_content.raw_text.strip()) < 20:
                logger.warning(f"  Insufficient content extracted, skipping")
                return ProcessingResult(
                    source_file=file,
                    success=False,
                    error_message="Insufficient content extracted",
                    processing_time=time.time() - start_time
                )

            logger.info(f"    ✓ Extracted {len(extracted_content.raw_text)} characters")

            # Generate summary
            logger.info(f"  [2/5] Generating summary...")
            summary = self.summary_generation.generate_summary(extracted_content)
            logger.info(f"    ✓ Summary: {len(summary.summary_text)} chars, "
                       f"{len(summary.key_concepts)} concepts, {len(summary.entities)} entities")

            # Save summary to file
            self._save_summary(summary)

            # Create chunks
            logger.info(f"  [3/5] Creating chunks...")
            chunks = self.chunking.chunk_summary(summary)
            logger.info(f"    ✓ Created {len(chunks)} chunks (avg size: {sum(len(c.content) for c in chunks) // len(chunks) if chunks else 0} chars)")
            print(f"    ✓ Created {len(chunks)} chunks from summary")

            # Generate embeddings
            logger.info(f"  [4/5] Generating embeddings...")
            embeddings = self.embedding.generate_embeddings(chunks)
            logger.info(f"    ✓ Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0].vector) if embeddings else 0})")
            print(f"    ✓ Generated {len(embeddings)} embeddings")

            # Store in Milvus
            logger.info(f"  [5/5] Storing in Milvus...")
            stored_count = self.vector_store.store_embeddings(embeddings, batch_size=self.config.BATCH_SIZE)
            logger.info(f"    ✓ Stored {stored_count} embeddings in Milvus collection '{self.config.MILVUS_COLLECTION_NAME}'")
            print(f"    ✓ Stored {stored_count} embeddings in Milvus")

            return ProcessingResult(
                source_file=file,
                success=True,
                extracted_content=extracted_content,
                summary=summary,
                chunks_created=len(chunks),
                embeddings_stored=stored_count,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            logger.error(f"  ❌ Error processing file: {e}")
            return ProcessingResult(
                source_file=file,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )

    def _save_summary(self, summary):
        """Save summary to a text file."""
        summary_dir = self.config.OUTPUT_DIR / "summaries"
        summary_dir.mkdir(exist_ok=True)

        # Create filename from source file
        safe_name = summary.source_file.file_name.replace('/', '_').replace(' ', '_')
        output_file = summary_dir / f"{safe_name}_summary.txt"

        # Format summary content
        content = f"""
{'=' * 80}
SUMMARY: {summary.source_file.file_name}
{'=' * 80}
File Type: {summary.source_file.file_type.value}
Path: {summary.source_file.relative_path}
Generated: {summary.created_at.strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

{summary.summary_text}

{'=' * 80}
KEY CONCEPTS ({len(summary.key_concepts)})
{'=' * 80}
{', '.join(summary.key_concepts) if summary.key_concepts else 'None'}

{'=' * 80}
ENTITIES ({len(summary.entities)})
{'=' * 80}
{', '.join(summary.entities) if summary.entities else 'None'}

{'=' * 80}
RELATIONSHIPS ({len(summary.relationships)})
{'=' * 80}
"""
        if summary.relationships:
            for rel in summary.relationships:
                content += f"{rel.get('source', '?')} --[{rel.get('type', 'relates to')}]--> {rel.get('target', '?')}\n"
        else:
            content += "None\n"

        output_file.write_text(content.strip())
        logger.debug(f"    Saved summary to: {output_file}")

    def _generate_report(self, results: List[ProcessingResult], graph_outputs: Dict, elapsed_time: float) -> Path:
        """Generate a comprehensive processing report."""
        report_path = self.config.OUTPUT_DIR / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        lines = [
            "=" * 80,
            "DIAGRAM PROCESSING REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Processing Time: {elapsed_time:.1f} seconds",
            "",
            "=" * 80,
            "SUMMARY STATISTICS",
            "=" * 80,
            f"Total Files Processed: {len(results)}",
            f"Successful: {sum(1 for r in results if r.success)}",
            f"Failed: {sum(1 for r in results if not r.success)}",
            f"Total Chunks Created: {sum(r.chunks_created for r in results)}",
            f"Total Embeddings Stored: {sum(r.embeddings_stored for r in results)}",
            "",
            "=" * 80,
            "KNOWLEDGE GRAPH",
            "=" * 80,
        ]

        for viz_type, path in graph_outputs.items():
            lines.append(f"{viz_type.upper()}: {path}")

        lines.extend([
            "",
            "=" * 80,
            "DETAILED RESULTS",
            "=" * 80,
            ""
        ])

        for i, result in enumerate(results, 1):
            status = "✓ SUCCESS" if result.success else "✗ FAILED"
            lines.append(f"{i}. {result.source_file.file_name} - {status}")
            lines.append(f"   Type: {result.source_file.file_type.value}")
            lines.append(f"   Time: {result.processing_time:.2f}s")

            if result.success:
                lines.append(f"   Chunks: {result.chunks_created}")
                lines.append(f"   Embeddings: {result.embeddings_stored}")
            else:
                lines.append(f"   Error: {result.error_message}")

            lines.append("")

        report_content = "\n".join(lines)
        report_path.write_text(report_content)

        logger.info(f"\n📄 Detailed report saved to: {report_path}")
        return report_path

