"""
Certificate Verification API Routes
Blockchain integration endpoints for O/L and A/L certificates

Supports Three Verification Methods:
1. By Verification Code (Certificate ID) - Human-readable code lookup
2. By Student Index Number - Shows all certificates and results for a student
3. By Document Hash (File Upload) - Compares file hash with blockchain
"""

import os
import hashlib
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.blockchain_service import get_blockchain_service, BlockchainService

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
    - student_address: Student's Ethereum address (optional, can be empty)
    - document_type: "O/L" or "A/L"
    - student_index: Student index number
    - exam_year: Year of examination
    - exam_subject: Subject/Stream
    - verification_code: Human-readable verification code
    - results: JSON string of exam results
    - student_info: JSON string of student information
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
        student_address = request.form.get('student_address', '0x0000000000000000000000000000000000000000')
        document_type = request.form.get('document_type')
        student_index = request.form.get('student_index')
        exam_year = request.form.get('exam_year')
        exam_subject = request.form.get('exam_subject', '')
        verification_code = request.form.get('verification_code')
        results_json = request.form.get('results', '[]')
        student_info_json = request.form.get('student_info', '{}')
        
        # Validate required fields
        if not all([document_type, student_index, exam_year, verification_code]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['document_type', 'student_index', 'exam_year', 'verification_code']
            }), 400
        
        # Validate document type
        if document_type not in ['O/L', 'A/L']:
            return jsonify({'error': 'Invalid document type. Must be "O/L" or "A/L"'}), 400
        
        # Parse results and student info
        try:
            results = json.loads(results_json) if results_json else []
            student_info = json.loads(student_info_json) if student_info_json else {}
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format for results or student_info'}), 400
        
        # Read file content and calculate hashes
        file_content = file.read()
        blockchain = get_blockchain_service()
        
        # Calculate all required hashes
        document_hash = blockchain.calculate_content_hash(file_content)
        results_hash = blockchain.calculate_results_hash(results)
        student_info_hash = blockchain.calculate_student_info_hash(student_info)
        
        # Save file locally (backup)
        filename = secure_filename(f"{student_index}_{document_hash[:16]}.{file.filename.rsplit('.', 1)[1]}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file.seek(0)
        file.save(file_path)
        
        # Register on blockchain with all data
        result = blockchain.register_document(
            document_hash=document_hash,
            results_hash=results_hash,
            verification_code=verification_code,
            student_info_hash=student_info_hash,
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
                    'results_hash': results_hash,
                    'verification_code': verification_code,
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
    METHOD 3: Verify a certificate by uploading it (File Upload)
    
    Compares the uploaded file's hash with blockchain records.
    Also verifies results integrity if results are provided.
    
    Expected form data:
    - certificate: PDF/Image file to verify
    - results: (Optional) JSON string of results to verify integrity
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
        
        if result.get('exists'):
            response = {
                'verified': result['is_valid'],
                'exists': True,
                'method': 'file_upload',
                'certificate_details': {
                    'document_hash': document_hash,
                    'document_type': result['document_type'],
                    'student_index': result.get('student_index'),
                    'exam_year': result.get('exam_year'),
                    'verification_code': result.get('verification_code'),
                    'results_hash': result.get('results_hash'),
                    'issued_by': result['issuer'],
                    'registration_timestamp': result['timestamp'],
                    'is_valid': result['is_valid']
                },
                'message': 'Certificate found on blockchain' if result['is_valid'] else 'Certificate has been revoked',
                'blockchain_verified': True
            }
            
            # If results provided, verify integrity
            results_json = request.form.get('results')
            if results_json:
                try:
                    results = json.loads(results_json)
                    integrity_result = blockchain.verify_results_integrity(document_hash, results)
                    response['results_integrity'] = integrity_result
                except json.JSONDecodeError:
                    response['results_integrity'] = {'error': 'Invalid results JSON'}
            
            return jsonify(response), 200
        else:
            return jsonify({
                'verified': False,
                'exists': False,
                'method': 'file_upload',
                'uploaded_hash': document_hash,
                'message': 'Certificate not found on blockchain',
                'warning': 'This certificate has not been registered or may be fraudulent'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@certificate_bp.route('/verify-by-code', methods=['POST'])
def verify_by_code():
    """
    METHOD 1: Verify a certificate using its verification code (Certificate ID)
    
    Expected JSON:
    {
        "verification_code": "DOE-OL2024-A1B2C3D4"
    }
    """
    try:
        data = request.get_json()
        verification_code = data.get('verification_code')
        
        if not verification_code:
            return jsonify({'error': 'verification_code is required'}), 400
        
        # Normalize code
        verification_code = verification_code.strip().upper()
        
        blockchain = get_blockchain_service()
        result = blockchain.verify_by_code(verification_code)
        
        if not result.get('exists'):
            return jsonify({
                'verified': False,
                'exists': False,
                'method': 'verification_code',
                'message': result.get('message', 'Certificate not found')
            }), 200
        
        return jsonify({
            'verified': result['is_valid'],
            'exists': True,
            'method': 'verification_code',
            'certificate_details': {
                'verification_code': verification_code,
                'document_hash': result.get('document_hash'),
                'results_hash': result.get('results_hash'),
                'document_type': result.get('document_type'),
                'student_index': result.get('student_index'),
                'exam_year': result.get('exam_year'),
                'exam_subject': result.get('exam_subject'),
                'timestamp': result.get('timestamp'),
                'issuer': result.get('issuer'),
                'is_valid': result['is_valid']
            },
            'message': 'Certificate verified on blockchain' if result['is_valid'] else 'Certificate has been revoked',
            'blockchain_verified': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/verify-by-hash', methods=['POST'])
def verify_by_hash():
    """
    Verify a certificate using its hash directly
    
    Expected JSON:
    {
        "document_hash": "abc123..."
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
            'verified': result.get('exists', False) and result.get('is_valid', False),
            'method': 'document_hash',
            'details': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/verify-by-index', methods=['POST'])
def verify_by_student_index():
    """
    METHOD 2: Verify certificate(s) by student index number
    
    Shows all certificates and results hash for a student.
    
    Expected JSON:
    {
        "student_index": "2024-OL-001234"
    }
    """
    try:
        data = request.get_json()
        student_index = data.get('student_index')
        
        if not student_index:
            return jsonify({'error': 'student_index is required'}), 400
        
        # Normalize student index
        student_index = student_index.strip().upper()
        
        blockchain = get_blockchain_service()
        result = blockchain.verify_by_student_index(student_index)
        
        if not result.get('exists'):
            return jsonify({
                'verified': False,
                'exists': False,
                'method': 'student_index',
                'message': result.get('message', f'No certificate found for index: {student_index}')
            }), 200
        
        # Get all certificates for this student
        all_certs = blockchain.get_student_certificates(student_index)
        
        return jsonify({
            'verified': result['is_valid'],
            'exists': True,
            'method': 'student_index',
            'certificate_details': {
                'student_index': student_index,
                'document_hash': result.get('document_hash'),
                'results_hash': result.get('results_hash'),
                'verification_code': result.get('verification_code'),
                'document_type': result.get('document_type'),
                'exam_year': result.get('exam_year'),
                'exam_subject': result.get('exam_subject'),
                'timestamp': result.get('timestamp'),
                'is_valid': result['is_valid'],
                'total_certificates': result.get('certificate_count', 1)
            },
            'all_certificate_hashes': all_certs,
            'message': 'Certificate(s) found on blockchain' if result['is_valid'] else 'Certificate has been revoked',
            'blockchain_verified': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/verify-results-integrity', methods=['POST'])
def verify_results_integrity():
    """
    Verify that exam results haven't been tampered with
    
    Expected JSON:
    {
        "document_hash": "abc123...",
        "results": [{"subject": "Mathematics", "grade": "A"}, ...]
    }
    """
    try:
        data = request.get_json()
        document_hash = data.get('document_hash')
        results = data.get('results', [])
        
        if not document_hash:
            return jsonify({'error': 'document_hash is required'}), 400
        
        if not results:
            return jsonify({'error': 'results array is required'}), 400
        
        blockchain = get_blockchain_service()
        result = blockchain.verify_results_integrity(document_hash, results)
        
        return jsonify({
            'integrity_verified': result.get('integrity_valid', False),
            'details': result,
            'message': result.get('message')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/revoke', methods=['POST'])
def revoke_certificate():
    """
    Revoke/invalidate a certificate (admin only)
    
    Expected JSON:
    {
        "document_hash": "abc123...",
        "reason": "Reason for revocation"
    }
    """
    try:
        data = request.get_json()
        document_hash = data.get('document_hash')
        reason = data.get('reason', 'Administrative revocation')
        
        if not document_hash:
            return jsonify({'error': 'document_hash is required'}), 400
        
        blockchain = get_blockchain_service()
        result = blockchain.revoke_document(document_hash, reason)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Certificate revoked successfully',
                'transaction_hash': result['transaction_hash'],
                'reason': reason
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/student-certificates/<student_index>', methods=['GET'])
def get_student_certificates(student_index):
    """
    Get all certificates for a student by index number
    """
    try:
        blockchain = get_blockchain_service()
        document_hashes = blockchain.get_student_certificates(student_index)
        
        certificates = []
        for doc_hash in document_hashes:
            result = blockchain.verify_document(doc_hash)
            if result.get('exists'):
                certificates.append({
                    'document_hash': doc_hash,
                    'document_type': result.get('document_type'),
                    'verification_code': result.get('verification_code'),
                    'exam_year': result.get('exam_year'),
                    'is_valid': result.get('is_valid'),
                    'timestamp': result.get('timestamp')
                })
        
        return jsonify({
            'student_index': student_index,
            'certificate_count': len(certificates),
            'certificates': certificates
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/user-documents/<address>', methods=['GET'])
def get_user_documents(address):
    """
    Get all certificates owned by a user wallet address
    """
    try:
        blockchain = get_blockchain_service()
        document_hashes = blockchain.get_user_documents(address)
        
        documents = []
        for doc_hash in document_hashes:
            result = blockchain.verify_document(doc_hash)
            if result.get('exists'):
                documents.append({
                    'document_hash': doc_hash,
                    'document_type': result.get('document_type'),
                    'student_index': result.get('student_index'),
                    'verification_code': result.get('verification_code'),
                    'exam_year': result.get('exam_year'),
                    'is_valid': result.get('is_valid'),
                    'timestamp': result.get('timestamp')
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
    Get blockchain connection status and statistics
    """
    try:
        blockchain = get_blockchain_service()
        stats = blockchain.get_statistics()
        
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
            'statistics': stats,
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
