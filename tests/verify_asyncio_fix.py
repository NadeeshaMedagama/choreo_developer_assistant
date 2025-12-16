#!/usr/bin/env python3
"""
Quick verification that asyncio import fix works
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_import():
    """Test that app.py imports correctly"""
    try:
        # This will fail if asyncio is not imported
        import app
        print("✅ app.py imports successfully")
        print("✅ asyncio import is present")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_asyncio_in_code():
    """Verify asyncio is imported in app.py"""
    app_file = Path(__file__).parent / "backend" / "app.py"
    
    with open(app_file, 'r') as f:
        content = f.read()
        
    if 'import asyncio' in content:
        print("✅ asyncio import found in app.py")
        return True
    else:
        print("❌ asyncio import NOT found in app.py")
        return False

if __name__ == "__main__":
    print("Verifying asyncio import fix...")
    print("-" * 50)
    
    test1 = test_asyncio_in_code()
    print()
    test2 = test_import()
    
    print("-" * 50)
    if test1 and test2:
        print("✅ All checks passed! Fix is working.")
        sys.exit(0)
    else:
        print("❌ Some checks failed.")
        sys.exit(1)

