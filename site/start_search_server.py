#!/usr/bin/env python3
"""
Startup script for the BibleProject search API server.
This script starts the Flask API server that provides search functionality.
"""

import subprocess
import sys
import os

def main():
    print("Starting BibleProject Search API Server...")
    print("Make sure you have the required dependencies installed:")
    print("pip install -r requirements_api.txt")
    print()
    
    # Check if the database files exist
    db_path = "../scripts/database/bp_db"
    if not os.path.exists(f"{db_path}.index") or not os.path.exists(f"{db_path}.json"):
        print(f"Error: Database files not found at {db_path}")
        print("Please make sure bp_db.index and bp_db.json exist in scripts/database/")
        sys.exit(1)
    
    try:
        # Start the Flask server
        subprocess.run([sys.executable, "search_api.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 