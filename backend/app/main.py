"""
Document Verification System - Flask Backend
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Document Verification API',
        'version': '1.0.0'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend service is running'
    })


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload a document for verification"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename
    })


@app.route('/api/verify', methods=['POST'])
def verify_document():
    """Verify a document's authenticity"""
    data = request.get_json()
    
    if not data or 'hash' not in data:
        return jsonify({'error': 'Document hash required'}), 400
    
    # Placeholder for blockchain verification
    return jsonify({
        'verified': False,
        'message': 'Verification service - blockchain integration pending',
        'hash': data['hash']
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
