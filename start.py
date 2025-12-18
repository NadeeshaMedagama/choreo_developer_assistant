#!/usr/bin/env python3
"""
Startup script for Choreo deployment
Uses PORT environment variable provided by Choreo platform
"""
import os
import sys
import subprocess

def main():
    # Get PORT from environment variable (Choreo sets this)
    port = os.environ.get('PORT', '9090')
    
    print(f"Starting Choreo AI Assistant on port {port}...")
    print(f"Binding to 0.0.0.0:{port}")
    
    # Start uvicorn with the PORT environment variable
    cmd = [
        'uvicorn',
        'backend.app:app',
        '--host', '0.0.0.0',
        '--port', port
    ]
    
    print(f"Command: {' '.join(cmd)}")
    sys.stdout.flush()
    
    # Execute uvicorn
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    main()

