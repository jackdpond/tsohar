from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the scripts directory to the path so we can import scribe
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from scribe import Index

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Index object once when the server starts
print("Loading database...")
index = Index()
index.load_database('../scripts/database/bp_db')
print("Database loaded successfully!")

@app.route('/search', methods=['GET'])
def search():
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
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 