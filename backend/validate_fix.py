#!/usr/bin/env python3
"""
Quick validation script for Milvus fix
Tests that the code changes are syntactically correct
"""

import sys
import ast

files_to_check = [
    "db/vector_client.py",
    "app.py"
]

print("🔍 Validating Python syntax...")
print()

all_valid = True

for filepath in files_to_check:
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Try to parse the file
        ast.parse(code)
        print(f"✅ {filepath} - Syntax OK")
        
    except SyntaxError as e:
        print(f"❌ {filepath} - Syntax Error:")
        print(f"   Line {e.lineno}: {e.msg}")
        all_valid = False
    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        all_valid = False

print()
if all_valid:
    print("✅ All files passed syntax validation!")
    print()
    print("Next steps:")
    print("1. Commit and push changes")
    print("2. Deploy to Choreo")
    print("3. Monitor logs for 'Milvus vector client initialized successfully'")
    print("4. Test /api/ask/stream endpoint")
    sys.exit(0)
else:
    print("❌ Some files have syntax errors. Please fix them before deploying.")
    sys.exit(1)

