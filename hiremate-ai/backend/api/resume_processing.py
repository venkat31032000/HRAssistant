from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your API blueprints
from apis.resume_processing import resume_bp

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Register blueprints
app.register_blueprint(resume_bp, url_prefix='/api')

# Serve frontend
@app.route('/')
def serve_frontend():
    """Serve the resume processing frontend"""
    return send_from_directory(FRONTEND_DIR, 'resume-processing.html')

# Serve static files
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
    print("   - API: http://localhost:5000/api/")
    print("\n📌 Available API endpoints:")
    print("   GET  /api/resumes/pending")
    print("   POST /api/process-resume")
    print("   POST /api/send-bulk-emails")
    print("   POST /api/generate-sample-resumes")
    print("   POST /api/process-all")
    print("   GET  /api/processing-status")
    print("   GET  /api/results")
    print("   GET  /api/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, port=5000)