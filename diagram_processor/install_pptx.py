#!/usr/bin/env python3
"""
Install python-pptx using the same Python interpreter as main.py
"""

import sys
import subprocess

print("=" * 80)
print("Installing python-pptx for PowerPoint processing")
print("=" * 80)
print()

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print()

# Install python-pptx
print("Installing python-pptx...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    print()
    print("✓ Installation complete!")
    print()
    
    # Verify
    print("Verifying installation...")
    try:
        import pptx
        print(f"✓ python-pptx is installed, version: {pptx.__version__}")
        print()
        print("=" * 80)
        print("✅ SUCCESS! You can now process PPTX files")
        print("=" * 80)
        print()
        print("Run this to process remaining files:")
        print("  python main.py --incremental")
        sys.exit(0)
    except ImportError as e:
        print(f"✗ Verification failed: {e}")
        sys.exit(1)
        
except subprocess.CalledProcessError as e:
    print(f"✗ Installation failed: {e}")
    print()
    print("Please try manually:")
    print("  pip install python-pptx")
    sys.exit(1)

