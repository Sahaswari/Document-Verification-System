"""
Certificate Verification API Routes
Blockchain integration endpoints for O/L and A/L certificates
"""

import os
import hashlib
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services.blockchain_service import get_blockchain_service

# Create blueprint
certificate_bp = Blueprint('certificate', __name__, url_prefix='/api/certificate')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@certificate_bp.route('/register', methods=['POST'])
def register_certificate():
    """
    Register a new O/L or A/L certificate on the blockchain
    
    Expected form data:
    - certificate: PDF/Image file
    - student_address: Student's Ethereum address
    - document_type: "O/L" or "A/L"
    - student_index: Student index number (e.g., "2023OL123456")
    - exam_year: Year of examination (e.g., 2023)
    - exam_subject: Subject/Stream (e.g., "General", "Physical Science")
    - ipfs_hash: IPFS hash for metadata (optional, can be empty string)
    """
    try:
        # Validate file upload
        if 'certificate' not in request.files:
            return jsonify({'error': 'No certificate file provided'}), 400
        
        file = request.files['certificate']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PDF, JPG, PNG'}), 400
        
        # Get form data
        student_address = request.form.get('student_address')
        document_type = request.form.get('document_type')
        student_index = request.form.get('student_index')
        exam_year = request.form.get('exam_year')
        exam_subject = request.form.get('exam_subject', '')
        ipfs_hash = request.form.get('ipfs_hash', '')
        
        # Validate required fields
        if not all([student_address, document_type, student_index, exam_year]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['student_address', 'document_type', 'student_index', 'exam_year']
            }), 400
        
        # Validate document type
        if document_type not in ['O/L', 'A/L']:
            return jsonify({'error': 'Invalid document type. Must be "O/L" or "A/L"'}), 400
        
        # Read file content and calculate hash
        file_content = file.read()
        blockchain = get_blockchain_service()
        document_hash = blockchain.calculate_content_hash(file_content)
        
        # Save file (optional - for backup)
        filename = secure_filename(f"{student_index}_{document_hash[:16]}.{file.filename.rsplit('.', 1)[1]}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Reset file pointer and save
        file.seek(0)
        file.save(file_path)
        
        # Register on blockchain
        result = blockchain.register_document(
            document_hash=document_hash,
            ipfs_hash=ipfs_hash or f"local:{filename}",
            owner_address=student_address,
            document_type=document_type,
            student_index=student_index,
            exam_year=int(exam_year),
            exam_subject=exam_subject
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Certificate registered successfully on blockchain',
                'data': {
                    'document_hash': document_hash,
                    'transaction_hash': result['transaction_hash'],
                    'block_number': result['block_number'],
                    'student_index': student_index,
                    'document_type': document_type,
                    'saved_file': filename
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to register on blockchain')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@certificate_bp.route('/verify', methods=['POST'])
def verify_certificate():
    """
    Verify a certificate by uploading it
    
    Expected form data:
    - certificate: PDF/Image file to verify
    """
    try:
        # Validate file upload
        if 'certificate' not in request.files:
            return jsonify({'error': 'No certificate file provided'}), 400
        
        file = request.files['certificate']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Calculate hash of uploaded file
        file_content = file.read()
        blockchain = get_blockchain_service()
        document_hash = blockchain.calculate_content_hash(file_content)
        
        # Query blockchain
        result = blockchain.verify_document(document_hash)
        
        if result['exists']:
            return jsonify({
                'verified': result['is_valid'],
                'exists': True,
                'certificate_details': {
                    'document_hash': document_hash,
                    'document_type': result['document_type'],
                    'student_index': result.get('student_index'),
                    'exam_year': result.get('exam_year'),
                    'exam_subject': result.get('exam_subject'),
                    'issued_by': result['issuer'],
                    'owner': result['owner'],
                    'registration_timestamp': result['timestamp'],
                    'is_valid': result['is_valid'],
                    'ipfs_hash': result.get('ipfs_hash')
                },
                'message': 'Certificate found on blockchain' if result['is_valid'] else 'Certificate has been revoked'
            }), 200
        else:
            return jsonify({
                'verified': False,
                'exists': False,
                'message': 'Certificate not found on blockchain',
                'warning': 'This certificate has not been registered or may be fraudulent'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@certificate_bp.route('/verify-by-hash', methods=['POST'])
def verify_by_hash():
    """
    Verify a certificate using its hash directly
    
    Expected JSON:
    {
        "document_hash": "0xabc123..."
    }
    """
    try:
        data = request.get_json()
        document_hash = data.get('document_hash')
        
        if not document_hash:
            return jsonify({'error': 'document_hash is required'}), 400
        
        blockchain = get_blockchain_service()
        result = blockchain.verify_document(document_hash)
        
        return jsonify({
            'verified': result['exists'] and result['is_valid'],
            'details': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/verify-by-index', methods=['POST'])
def verify_by_student_index():
    """
    Verify a certificate using student index number
    
    Expected JSON:
    {
        "student_index": "2023OL123456"
    }
    
    Response:
    {
        "verified": true/false,
        "exists": true/false,
        "details": {
            "document_hash": "...",
            "student_index": "...",
            "exam_year": 2023,
            "exam_type": "OL",
            "is_valid": true,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        student_index = data.get('student_index')
        
        if not student_index:
            return jsonify({'error': 'student_index is required'}), 400
        
        # Validate student index format (basic validation)
        student_index = student_index.strip().upper()
        
        blockchain = get_blockchain_service()
        
        # Use the new verify_by_student_index method
        result = blockchain.verify_by_student_index(student_index)
        
        if not result['exists']:
            return jsonify({
                'verified': False,
                'exists': False,
                'message': result.get('message', 'No certificate found for this student index')
            }), 200
        
        return jsonify({
            'verified': result['is_valid'],
            'exists': True,
            'details': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/revoke', methods=['POST'])
def revoke_certificate():
    """
    Revoke/invalidate a certificate (admin only)
    
    Expected JSON:
    {
        "document_hash": "0xabc123..."
    }
    """
    try:
        data = request.get_json()
        document_hash = data.get('document_hash')
        
        if not document_hash:
            return jsonify({'error': 'document_hash is required'}), 400
        
        blockchain = get_blockchain_service()
        result = blockchain.revoke_document(document_hash)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Certificate revoked successfully',
                'transaction_hash': result['transaction_hash']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/user-documents/<address>', methods=['GET'])
def get_user_documents(address):
    """
    Get all certificates owned by a user
    
    URL Parameter:
    - address: Ethereum address of the user
    """
    try:
        blockchain = get_blockchain_service()
        document_hashes = blockchain.get_user_documents(address)
        
        # Get details for each document
        documents = []
        for doc_hash in document_hashes:
            result = blockchain.verify_document(doc_hash)
            if result['exists']:
                documents.append({
                    'document_hash': doc_hash,
                    'document_type': result['document_type'],
                    'student_index': result.get('student_index'),
                    'exam_year': result.get('exam_year'),
                    'is_valid': result['is_valid'],
                    'timestamp': result['timestamp']
                })
        
        return jsonify({
            'address': address,
            'document_count': len(documents),
            'documents': documents
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/blockchain-status', methods=['GET'])
def blockchain_status():
    """
    Get blockchain connection status and information
    """
    try:
        blockchain = get_blockchain_service()
        
        return jsonify({
            'connected': blockchain.w3.is_connected(),
            'network': {
                'url': blockchain.provider_url,
                'chain_id': blockchain.w3.eth.chain_id,
                'block_number': blockchain.w3.eth.block_number
            },
            'contract': {
                'address': blockchain.contract_address
            },
            'account': {
                'address': blockchain.w3.eth.default_account,
                'balance': blockchain.get_account_balance()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500
