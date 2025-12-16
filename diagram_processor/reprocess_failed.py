#!/usr/bin/env python3
"""
Reprocess Failed Files

This script will attempt to reprocess files that failed in the previous run.
It reads the processing log to identify failed files and processes only those.
"""

import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagram_processor.services import DiagramProcessorOrchestrator
from diagram_processor.utils import Config
from diagram_processor.utils.logger import get_logger

logger = get_logger(__name__)


def get_failed_files_from_log(log_path: Path):
    """Parse the processing log to find failed files."""
    failed_files = []
    
    if not log_path.exists():
        logger.warning(f"Log file not found: {log_path}")
        return failed_files
    
    with open(log_path, 'r') as f:
        for line in f:
            # Look for patterns like: "PPTX extraction failed" or "Insufficient content"
            if 'extraction failed' in line.lower() or 'insufficient content' in line.lower():
                # Try to extract filename from previous lines
                pass
            # Also look for file names with .pptx extension that had errors
            if '.pptx' in line.lower() and ('error' in line.lower() or 'failed' in line.lower()):
                # Extract filename
                match = re.search(r'([^/\\]+\.pptx)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1)
                    if filename not in failed_files:
                        failed_files.append(filename)
    
    return failed_files


def main():
    """Main entry point for reprocessing failed files."""
    
    print("=" * 80)
    print("REPROCESSING FAILED FILES")
    print("=" * 80)
    
    config = Config()
    
    # Check for failed files from log
    log_path = config.OUTPUT_DIR / "processing.log"
    failed_pptx = get_failed_files_from_log(log_path)
    
    if failed_pptx:
        print(f"\nFound {len(failed_pptx)} failed PPTX files:")
        for f in failed_pptx[:10]:  # Show first 10
            print(f"  - {f}")
        if len(failed_pptx) > 10:
            print(f"  ... and {len(failed_pptx) - 10} more")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print()
    print("Instead of running this script, simply run main.py again:")
    print()
    print("  python main.py")
    print()
    print("The processor will:")
    print("  1. ✓ Skip files that were already successfully processed")
    print("  2. ✓ Retry files that failed (now with python-pptx installed)")
    print("  3. ✓ Create new embeddings for previously failed files")
    print()
    print("OR, if you want to reprocess ALL files from scratch:")
    print()
    print("  1. Backup current output: mv output output_backup")
    print("  2. Run: python main.py")
    print()
    print("=" * 80)
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("  1. Run full processing (will skip already processed files)")
    print("  2. Exit (run manually)")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\nStarting full processing...")
            orchestrator = DiagramProcessorOrchestrator(config)
            result = orchestrator.process_all_diagrams()
            
            print("\n" + "=" * 80)
            print("✓ PROCESSING COMPLETE")
            print("=" * 80)
            print(f"Status: {result['status']}")
            print(f"Files Processed: {result['successful']}/{result['total_files']}")
            print(f"Summaries: {result['summaries_generated']}")
            print(f"Chunks: {result['total_chunks']}")
            print(f"Embeddings: {result['total_embeddings']}")
            print("=" * 80)
        else:
            print("\nExiting. Run 'python main.py' when ready.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()

