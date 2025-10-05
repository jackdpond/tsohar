#!/usr/bin/env python3
"""
Production WSGI application for pod-search web app.
This file serves both the Flask API and static files for deployment.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# Add the scripts directory to the path so we can import scribe
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from scribe import Index

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize the Index object once when the server starts
print("Loading database...")
index = Index()
# Database path relative to the site directory
index.load_database('../scripts/database/bp_db')
print("Database loaded successfully!")

@app.route('/')
def index_page():
    """Serve the main index.html page"""
    return send_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, JSON, etc.)"""
    return send_from_directory('.', filename)

@app.route('/search', methods=['GET'])
def search():
    """Search API endpoint"""
    query = request.args.get('q', '')
    k = request.args.get('k', 5, type=int)
    
    if not query:
        return jsonify([])
    
    try:
        results = index.search(query, k=k)
        # Convert numpy types to native Python types for JSON serialization
        serializable_results = []
        for result in results:
            serializable_result = {}
            for key, value in result.items():
                if hasattr(value, 'item'):  # numpy scalar
                    serializable_result[key] = value.item()
                else:
                    serializable_result[key] = value
            serializable_results.append(serializable_result)
        return jsonify(serializable_results)
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
