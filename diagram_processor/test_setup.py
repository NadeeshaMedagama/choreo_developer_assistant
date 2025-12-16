#!/usr/bin/env python3
"""
Quick test script to verify the diagram processor setup.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from diagram_processor.utils import Config
        print("  ✓ Config")
    except ImportError as e:
        print(f"  ✗ Config: {e}")
        return False

    try:
        from diagram_processor.models import DiagramFile, FileType
        print("  ✓ Models")
    except ImportError as e:
        print(f"  ✗ Models: {e}")
        return False

    try:
        from diagram_processor.services.file_discovery import FileDiscoveryService
        print("  ✓ File Discovery Service")
    except ImportError as e:
        print(f"  ✗ File Discovery Service: {e}")
        return False

    try:
        from diagram_processor.services.text_extraction import TextExtractionService
        print("  ✓ Text Extraction Service")
    except ImportError as e:
        print(f"  ✗ Text Extraction Service: {e}")
        return False

    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from diagram_processor.utils import Config
        config = Config()

        print(f"  Data Directory: {config.DATA_DIR}")
        print(f"  Output Directory: {config.OUTPUT_DIR}")

        if config.OPENAI_API_KEY or config.AZURE_OPENAI_API_KEY:
            print("  ✓ OpenAI/Azure OpenAI API Key found")
        else:
            print("  ⚠️  OpenAI API Key not set")

        if config.MILVUS_URI and config.MILVUS_TOKEN:
            print("  ✓ Milvus URI and Token found")
        else:
            print("  ⚠️  Milvus configuration not set")

        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def test_file_discovery():
    """Test file discovery."""
    print("\nTesting file discovery...")

    try:
        from diagram_processor.utils import Config
        from diagram_processor.services.file_discovery import FileDiscoveryService

        config = Config()

        if not config.DATA_DIR.exists():
            print(f"  ⚠️  Data directory not found: {config.DATA_DIR}")
            return False

        discovery = FileDiscoveryService(config.DATA_DIR, config.MAX_FILE_SIZE)
        files = discovery.discover_all_files()

        print(f"  ✓ Discovered {len(files)} files")

        if files:
            stats = discovery.get_file_statistics(files)
            print(f"  Total size: {stats['total_size_mb']:.1f} MB")
            print(f"  File types: {len(stats['by_type'])} types")

        return True
    except Exception as e:
        print(f"  ✗ File discovery error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("DIAGRAM PROCESSOR - SETUP TEST")
    print("=" * 60)
    print()

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test configuration
    if not test_config():
        all_passed = False

    # Test file discovery
    if not test_file_discovery():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou're ready to process diagrams!")
        print("Run: python3 main.py --dry-run")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before processing.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

