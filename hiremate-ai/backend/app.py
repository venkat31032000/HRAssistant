
from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your API blueprints
from api.process_runner import process_runner_bp

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")  # frontend is inside backend

# Register blueprints
app.register_blueprint(process_runner_bp, url_prefix='/api/process')

# Serve frontend files
@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory(FRONTEND_DIR, 'live-view.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend directory"""
    return send_from_directory(FRONTEND_DIR, path)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    print("🚀 Starting HireMate Backend Server...")
    print("📁 Frontend directory:", FRONTEND_DIR)
    print("\n✅ Server endpoints:")
    print("   - UI: http://localhost:5000")
    print("   - API: http://localhost:5000/api/process/")
    print("\n📌 Available API endpoints:")
    print("   POST /api/process/start - Start the HR workflow")
    print("   GET  /api/process/status - Get current status")
    print("   GET  /api/process/logs - Stream live logs")
    print("   GET  /api/process/results - Get final results")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, port=5000)