#!/usr/bin/env python3
"""
Main Entry Point for Diagram Processor

Run this script to process all diagrams in the data/diagrams directory.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagram_processor.utils import Config
from diagram_processor.utils.logger import setup_logger
from diagram_processor.services import DiagramProcessorOrchestrator
from diagram_processor.models import FileType

# Set up logging
logger = setup_logger(
    'diagram_processor',
    log_file=str(Path(__file__).parent / 'output' / 'processing.log')
)


def main():
    """Main function to run the diagram processor."""
    parser = argparse.ArgumentParser(
        description='Process Choreo architecture diagrams: extract text, generate summaries, create embeddings, and build knowledge graph'
    )

    parser.add_argument(
        '--file-types',
        nargs='+',
        choices=['png', 'jpg', 'jpeg', 'svg', 'pdf', 'drawio', 'docx', 'xlsx', 'pptx'],
        help='Process only specific file types (default: all)'
    )

    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Skip files that already have summaries (incremental mode)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Discover files without processing them'
    )

    args = parser.parse_args()

    try:
        # Initialize configuration
        config = Config()

        logger.info("=" * 80)
        logger.info("CHOREO DIAGRAM PROCESSOR")
        logger.info("=" * 80)
        logger.info(f"Data Directory: {config.DATA_DIR}")
        logger.info(f"Output Directory: {config.OUTPUT_DIR}")
        logger.info(f"Milvus Collection: {config.MILVUS_COLLECTION_NAME}")
        logger.info("=" * 80)

        if args.dry_run:
            logger.info("\n🔍 DRY RUN MODE - Discovering files only...\n")
            from diagram_processor.services.file_discovery import FileDiscoveryService

            discovery = FileDiscoveryService(config.DATA_DIR, config.MAX_FILE_SIZE)
            files = discovery.discover_all_files()
            stats = discovery.get_file_statistics(files)

            logger.info(f"\nDiscovered {stats['total_files']} files ({stats['total_size_mb']:.1f} MB)")
            logger.info("\nBreakdown by type:")
            for file_type, type_stats in stats['by_type'].items():
                logger.info(f"  {file_type}: {type_stats['count']} files ({type_stats['size_mb']:.1f} MB)")

            logger.info("\n✓ Dry run complete")
            return 0

        # Parse file types if provided
        file_types = None
        if args.file_types:
            file_types = [FileType[ft.upper()] for ft in args.file_types]
            logger.info(f"Filtering to file types: {', '.join(args.file_types)}")

        # Check incremental mode
        if args.incremental:
            logger.info("📝 Incremental mode: Will skip already processed files")

        # Initialize orchestrator
        orchestrator = DiagramProcessorOrchestrator(config)

        # Process all diagrams
        result = orchestrator.process_all_diagrams(
            file_types=file_types,
            incremental_mode=args.incremental
        )

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("✓ PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Status: {result['status']}")
        logger.info(f"Files Processed: {result['successful']}/{result['total_files']}")
        logger.info(f"Summaries Generated: {result['summaries_generated']}")
        logger.info(f"Chunks Created: {result['total_chunks']}")
        logger.info(f"Total Embeddings: {result['total_embeddings']}")
        logger.info(f"Knowledge Graph Nodes: {result['knowledge_graph']['nodes']}")
        logger.info(f"Knowledge Graph Edges: {result['knowledge_graph']['edges']}")
        logger.info(f"Total Time: {result['processing_time']:.1f}s")
        logger.info("=" * 80)

        if result.get('report_path'):
            logger.info(f"\n📄 Full report: {result['report_path']}")

        logger.info(f"\n📁 Output directory: {config.OUTPUT_DIR}")
        logger.info("  - summaries/     : Individual file summaries")
        logger.info("  - graphs/        : Knowledge graph visualizations")
        logger.info("  - processing.log : Detailed processing log")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Processing interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

