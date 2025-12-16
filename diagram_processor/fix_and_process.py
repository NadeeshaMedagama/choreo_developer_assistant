#!/usr/bin/env python3
"""
ONE-CLICK FIX: Install python-pptx and reprocess PPTX files

This script will:
1. Install python-pptx in the correct Python environment
2. Verify the installation
3. Optionally reprocess the PPTX files
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def main():
    print_header("PPTX FIX - Install python-pptx and Process PPTX Files")
    
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📦 Python version: {sys.version.split()[0]}")
    print()
    
    # Step 1: Check if already installed
    try:
        import pptx
        print(f"ℹ️  python-pptx is already installed (version {pptx.__version__})")
        already_installed = True
    except ImportError:
        print("⚠️  python-pptx is NOT installed")
        already_installed = False
    
    # Step 2: Install if needed
    if not already_installed:
        print("\n📥 Installing python-pptx...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "python-pptx", "-q"],
                stdout=subprocess.DEVNULL
            )
            print("✅ Installation complete!")
            
            # Verify
            import pptx
            print(f"✅ Verified: python-pptx version {pptx.__version__}")
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            print("\nPlease install manually:")
            print(f"  {sys.executable} -m pip install python-pptx")
            return 1
    
    # Step 3: Ask user if they want to reprocess
    print_header("Installation Successful!")
    
    print("What would you like to do next?\n")
    print("  1. Process ONLY PPTX files (fast - ~5 min)")
    print("  2. Process all files in incremental mode (skips already done - ~10 min)")
    print("  3. Exit (run processing manually later)")
    print()
    
    try:
        choice = input("Enter choice (1, 2, or 3): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting...")
        return 0
    
    if choice == "1":
        print("\n🚀 Processing ONLY PPTX files...\n")
        subprocess.call([sys.executable, "main.py", "--file-types", "pptx"])
    elif choice == "2":
        print("\n🚀 Processing all files (incremental mode)...\n")
        subprocess.call([sys.executable, "main.py", "--incremental"])
    else:
        print("\n✅ Ready to go!")
        print("\nTo process PPTX files, run:")
        print("  python main.py --file-types pptx")
        print("\nOr to process all with incremental mode:")
        print("  python main.py --incremental")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(130)

