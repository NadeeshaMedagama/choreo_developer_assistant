#!/usr/bin/env python
"""Test script to verify backend can start"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    print("Testing backend imports...")
    from backend.app import app
    print("✓ Backend app imported successfully!")
    print("✓ All services initialized!")
    print("\nBackend is ready to run!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

