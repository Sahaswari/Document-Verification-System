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

@certificate_bp.route('/demo/blockchain-info', methods=['GET'])
def demo_blockchain_info():
    """
    DEMO: Show comprehensive blockchain information
    Demonstrates: Network connectivity, block structure, accounts
    """
    try:
        blockchain = get_blockchain_service()
        w3 = blockchain.w3
        
        # Get latest block details
        latest_block = w3.eth.get_block('latest')
        
        # Get all Hardhat test accounts
        accounts = w3.eth.accounts[:5]  # First 5 accounts
        account_balances = []
        for acc in accounts:
            balance = w3.eth.get_balance(acc)
            account_balances.append({
                'address': acc,
                'balance_wei': str(balance),
                'balance_eth': str(w3.from_wei(balance, 'ether'))
            })
        
        return jsonify({
            'demo_title': 'Blockchain Network Information',
            'concepts_demonstrated': [
                'Distributed Ledger - All nodes share same data',
                'Consensus - Blocks validated by network',
                'Cryptographic Hashing - Each block has unique hash',
                'Chain Structure - Blocks linked by parent hash'
            ],
            'network': {
                'name': 'Hardhat Local Network (Simulates Ethereum)',
                'chain_id': w3.eth.chain_id,
                'is_connected': w3.is_connected(),
                'protocol_version': w3.eth.protocol_version if hasattr(w3.eth, 'protocol_version') else 'N/A'
            },
            'latest_block': {
                'number': latest_block['number'],
                'hash': latest_block['hash'].hex() if latest_block['hash'] else None,
                'parent_hash': latest_block['parentHash'].hex(),
                'timestamp': latest_block['timestamp'],
                'transactions_count': len(latest_block['transactions']),
                'gas_used': latest_block['gasUsed'],
                'gas_limit': latest_block['gasLimit'],
                'miner': latest_block['miner']
            },
            'accounts': {
                'description': 'Hardhat provides test accounts with 10000 ETH each',
                'total_accounts': len(w3.eth.accounts),
                'sample_accounts': account_balances
            },
            'smart_contract': {
                'address': blockchain.contract_address,
                'description': 'DocumentVerification contract deployed on this network'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/hash-demonstration', methods=['POST'])
def demo_hash():
    """
    DEMO: Demonstrate SHA-256 hashing
    Shows how even small changes completely change the hash
    """
    try:
        original_text = request.json.get('text', 'Sample Certificate Data')
        
        # Original hash
        original_hash = hashlib.sha256(original_text.encode()).hexdigest()
        
        # Modified versions
        demos = []
        
        # Demo 1: Add a space
        modified1 = original_text + ' '
        hash1 = hashlib.sha256(modified1.encode()).hexdigest()
        demos.append({
            'modification': 'Added single space at end',
            'original': original_text,
            'modified': modified1,
            'original_hash': original_hash,
            'modified_hash': hash1,
            'hashes_match': original_hash == hash1
        })
        
        # Demo 2: Change one character
        if len(original_text) > 0:
            modified2 = original_text[:-1] + ('X' if original_text[-1] != 'X' else 'Y')
            hash2 = hashlib.sha256(modified2.encode()).hexdigest()
            demos.append({
                'modification': 'Changed last character',
                'original': original_text,
                'modified': modified2,
                'original_hash': original_hash,
                'modified_hash': hash2,
                'hashes_match': original_hash == hash2
            })
        
        # Demo 3: Change case
        modified3 = original_text.upper()
        hash3 = hashlib.sha256(modified3.encode()).hexdigest()
        demos.append({
            'modification': 'Changed to uppercase',
            'original': original_text,
            'modified': modified3,
            'original_hash': original_hash,
            'modified_hash': hash3,
            'hashes_match': original_hash == hash3
        })
        
        return jsonify({
            'demo_title': 'Cryptographic Hashing (SHA-256) Demonstration',
            'concepts_demonstrated': [
                'Deterministic - Same input always produces same hash',
                'Avalanche Effect - Small change = completely different hash',
                'One-Way Function - Cannot reverse hash to get original',
                'Fixed Length - Output always 64 hex characters (256 bits)'
            ],
            'original_input': original_text,
            'original_hash': original_hash,
            'hash_length': f'{len(original_hash)} characters (256 bits)',
            'modifications': demos,
            'security_implication': 'If anyone modifies a certificate, the hash changes completely, making tampering detectable!'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/transaction-details/<tx_hash>', methods=['GET'])
def demo_transaction_details(tx_hash):
    """
    DEMO: Show detailed transaction information
    Demonstrates: Transaction structure, gas, signatures
    """
    try:
        blockchain = get_blockchain_service()
        w3 = blockchain.w3
        
        # Get transaction
        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        return jsonify({
            'demo_title': 'Blockchain Transaction Details',
            'concepts_demonstrated': [
                'Digital Signature - Transaction signed by sender',
                'Gas System - Computational cost of operations',
                'Immutability - Transaction permanently recorded',
                'Transparency - Anyone can view transaction details'
            ],
            'transaction': {
                'hash': tx['hash'].hex(),
                'block_number': tx['blockNumber'],
                'from_address': tx['from'],
                'to_address': tx['to'],
                'value_wei': str(tx['value']),
                'gas_limit': tx['gas'],
                'gas_price_wei': str(tx['gasPrice']),
                'nonce': tx['nonce'],
                'input_data_length': len(tx['input'].hex()) if tx['input'] else 0
            },
            'receipt': {
                'status': 'Success' if receipt['status'] == 1 else 'Failed',
                'gas_used': receipt['gasUsed'],
                'effective_gas_price': str(receipt.get('effectiveGasPrice', 0)),
                'logs_count': len(receipt['logs']),
                'contract_address': receipt.get('contractAddress')
            },
            'digital_signature': {
                'v': tx.get('v'),
                'r': tx.get('r').hex() if tx.get('r') else None,
                's': tx.get('s').hex() if tx.get('s') else None,
                'explanation': 'These v, r, s values form the ECDSA digital signature proving the sender authorized this transaction'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/immutability-test', methods=['POST'])
def demo_immutability():
    """
    DEMO: Demonstrate blockchain immutability
    Try to modify existing data - it should fail!
    """
    try:
        document_hash = request.json.get('document_hash')
        if not document_hash:
            return jsonify({'error': 'document_hash required'}), 400
        
        blockchain = get_blockchain_service()
        
        # First verify the certificate exists
        original = blockchain.verify_document(document_hash)
        
        if not original.get('exists'):
            return jsonify({
                'error': 'Certificate not found. Register one first to test immutability.'
            }), 404
        
        # Try to register again with same hash (should fail)
        try:
            result = blockchain.register_document(
                document_hash=document_hash,
                results_hash='0x' + '00' * 32,
                verification_code='FAKE-CODE-123',
                student_info_hash='0x' + '00' * 32,
                owner_address='0x0000000000000000000000000000000000000000',
                document_type='FAKE',
                student_index='FAKE/INDEX/000',
                exam_year=9999,
                exam_subject='Fake Subject'
            )
            modification_blocked = not result.get('success', False)
        except Exception as e:
            modification_blocked = True
            error_message = str(e)
        
        return jsonify({
            'demo_title': 'Blockchain Immutability Demonstration',
            'concepts_demonstrated': [
                'Once Written, Cannot Be Changed - Data is permanent',
                'Smart Contract Enforces Rules - Duplicate registration blocked',
                'Cryptographic Security - Hash uniquely identifies data',
                'Trustless System - No admin can modify records'
            ],
            'test_document_hash': document_hash,
            'original_certificate': {
                'document_type': original.get('document_type'),
                'student_index': original.get('student_index'),
                'verification_code': original.get('verification_code'),
                'timestamp': original.get('timestamp')
            },
            'modification_attempt': {
                'action': 'Tried to register same document hash with different data',
                'result': 'BLOCKED' if modification_blocked else 'WARNING: Modification succeeded!',
                'explanation': 'Smart contract rejected duplicate registration - data is IMMUTABLE'
            },
            'security_implication': 'Even the system administrator cannot modify or delete existing certificates!'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/tamper-detection', methods=['POST'])
def demo_tamper_detection():
    """
    DEMO: Detect if exam results have been tampered with
    Compares stored hash with calculated hash of provided results
    """
    try:
        data = request.json
        document_hash = data.get('document_hash')
        original_results = data.get('original_results', [])
        tampered_results = data.get('tampered_results', [])
        
        if not document_hash:
            return jsonify({'error': 'document_hash required'}), 400
        
        blockchain = get_blockchain_service()
        
        # Get certificate from blockchain
        cert = blockchain.verify_document(document_hash)
        if not cert.get('exists'):
            return jsonify({'error': 'Certificate not found'}), 404
        
        stored_results_hash = cert.get('results_hash')
        
        # Calculate hash of original results
        original_hash = blockchain.calculate_results_hash(original_results)
        
        # Calculate hash of tampered results
        tampered_hash = blockchain.calculate_results_hash(tampered_results)
        
        return jsonify({
            'demo_title': 'Tamper Detection Using Cryptographic Hashing',
            'concepts_demonstrated': [
                'Data Integrity - Verify data hasn\'t been modified',
                'Hash Comparison - Original vs Current hash',
                'Tamper Evidence - Any change is immediately detectable',
                'Zero Knowledge - Don\'t need to store actual grades on blockchain'
            ],
            'stored_on_blockchain': {
                'results_hash': stored_results_hash,
                'explanation': 'Only the hash is stored, not actual grades (privacy protection)'
            },
            'original_results': {
                'data': original_results,
                'calculated_hash': original_hash,
                'matches_blockchain': original_hash == stored_results_hash
            },
            'tampered_results': {
                'data': tampered_results,
                'calculated_hash': tampered_hash,
                'matches_blockchain': tampered_hash == stored_results_hash
            },
            'verdict': {
                'original_verified': original_hash == stored_results_hash,
                'tamper_detected': tampered_hash != stored_results_hash if tampered_results else None,
                'message': 'TAMPERING DETECTED!' if (tampered_results and tampered_hash != stored_results_hash) else 'Results integrity verified'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/event-logs/<document_hash>', methods=['GET'])
def demo_event_logs(document_hash):
    """
    DEMO: Show blockchain event logs for audit trail
    Demonstrates: Transparency, immutable audit log
    """
    try:
        blockchain = get_blockchain_service()
        w3 = blockchain.w3
        
        # Convert string to bytes32 if needed
        if not document_hash.startswith('0x'):
            document_hash = '0x' + document_hash
        
        # Get registration events for this document
        registration_filter = blockchain.contract.events.DocumentRegistered.create_filter(
            from_block=0,
            argument_filters={'documentHash': document_hash}
        )
        registration_events = registration_filter.get_all_entries()
        
        # Get verification events
        verification_filter = blockchain.contract.events.DocumentVerified.create_filter(
            from_block=0,
            argument_filters={'documentHash': document_hash}
        )
        verification_events = verification_filter.get_all_entries()
        
        events = []
        
        for event in registration_events:
            events.append({
                'type': 'REGISTRATION',
                'block_number': event['blockNumber'],
                'transaction_hash': event['transactionHash'].hex(),
                'issuer': event['args'].get('issuer'),
                'timestamp': event['args'].get('timestamp'),
                'description': 'Certificate was registered on blockchain'
            })
        
        for event in verification_events:
            events.append({
                'type': 'VERIFICATION',
                'block_number': event['blockNumber'],
                'transaction_hash': event['transactionHash'].hex(),
                'verifier': event['args'].get('verifier'),
                'timestamp': event['args'].get('timestamp'),
                'description': 'Someone verified this certificate'
            })
        
        # Sort by block number
        events.sort(key=lambda x: x['block_number'])
        
        return jsonify({
            'demo_title': 'Blockchain Event Logs - Immutable Audit Trail',
            'concepts_demonstrated': [
                'Transparency - All actions are publicly logged',
                'Non-Repudiation - Issuer cannot deny registration',
                'Audit Trail - Complete history of all operations',
                'Immutability - Logs cannot be deleted or modified'
            ],
            'document_hash': document_hash,
            'total_events': len(events),
            'events': events,
            'explanation': 'Every registration and verification is permanently recorded as an event on the blockchain'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/digital-signature', methods=['GET'])
def demo_digital_signature():
    """
    DEMO: Explain digital signatures used in blockchain
    """
    try:
        blockchain = get_blockchain_service()
        w3 = blockchain.w3
        
        # Get the issuer account
        issuer_address = w3.eth.default_account
        
        return jsonify({
            'demo_title': 'Digital Signatures in Blockchain (ECDSA)',
            'concepts_demonstrated': [
                'Asymmetric Cryptography - Public/Private key pair',
                'Authentication - Proves identity of signer',
                'Non-Repudiation - Signer cannot deny signing',
                'Integrity - Detects if message was modified'
            ],
            'how_it_works': {
                'step_1': 'Issuer has a private key (secret) and public key (address)',
                'step_2': 'When registering certificate, transaction is signed with private key',
                'step_3': 'Anyone can verify signature using public key (address)',
                'step_4': 'If signature is valid, we know the issuer authorized it'
            },
            'current_issuer': {
                'address': issuer_address,
                'explanation': 'This address (derived from public key) signed all certificate registrations',
                'security': 'Only someone with the private key for this address can register certificates'
            },
            'blockchain_implementation': {
                'algorithm': 'ECDSA (Elliptic Curve Digital Signature Algorithm)',
                'curve': 'secp256k1 (same as Bitcoin)',
                'signature_components': ['v', 'r', 's'],
                'address_derivation': 'Keccak256(public_key)[-20 bytes]'
            },
            'academic_relevance': 'This is the same cryptography that secures billions of dollars in cryptocurrency!'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/gas-explanation', methods=['GET'])
def demo_gas_explanation():
    """
    DEMO: Explain gas and transaction costs
    """
    try:
        blockchain = get_blockchain_service()
        w3 = blockchain.w3
        
        # Get current gas price
        gas_price = w3.eth.gas_price
        
        # Estimate gas for a registration (approximate)
        estimated_gas = 250000  # Typical for our registration function
        
        # Calculate costs
        cost_wei = gas_price * estimated_gas
        cost_eth = w3.from_wei(cost_wei, 'ether')
        
        # Current ETH price (approximate for demo)
        eth_price_usd = 2000  # Example price
        cost_usd = float(cost_eth) * eth_price_usd
        
        return jsonify({
            'demo_title': 'Gas System - Blockchain Transaction Costs',
            'concepts_demonstrated': [
                'Computational Cost - Operations require gas',
                'Spam Prevention - Makes attacks expensive',
                'Resource Allocation - Miners prioritize higher gas',
                'Economic Incentive - Miners get paid for work'
            ],
            'gas_explained': {
                'what_is_gas': 'Unit measuring computational effort',
                'gas_price': 'Amount of ETH per unit of gas',
                'gas_limit': 'Maximum gas willing to spend',
                'actual_cost': 'gas_used × gas_price'
            },
            'current_network': {
                'gas_price_wei': str(gas_price),
                'gas_price_gwei': str(w3.from_wei(gas_price, 'gwei')),
                'note': 'Hardhat uses fixed low gas prices for testing'
            },
            'registration_cost_estimate': {
                'estimated_gas_units': estimated_gas,
                'cost_in_eth': str(cost_eth),
                'cost_in_usd': f'${cost_usd:.4f}',
                'note': 'On mainnet with ETH at $2000'
            },
            'why_hardhat': {
                'explanation': 'Hardhat provides free test ETH for development',
                'benefit': 'We can test without spending real money',
                'production': 'On mainnet, each registration would cost real ETH'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificate_bp.route('/demo/full-workflow', methods=['GET'])
def demo_full_workflow():
    """
    DEMO: Complete workflow explanation for presentation
    """
    return jsonify({
        'demo_title': 'Complete Certificate Verification Workflow',
        'system_overview': {
            'problem': 'Fake G.C.E O/L and A/L certificates in Sri Lanka',
            'solution': 'Blockchain-based verification system',
            'benefit': 'Instant, tamper-proof verification'
        },
        'workflow_steps': [
            {
                'step': 1,
                'title': 'Certificate Registration',
                'actor': 'Department of Examinations',
                'action': 'Register certificate with hash on blockchain',
                'blockchain_concept': 'Immutable storage, Digital signature'
            },
            {
                'step': 2,
                'title': 'Hash Storage',
                'actor': 'Smart Contract',
                'action': 'Store document hash, results hash, verification code',
                'blockchain_concept': 'Cryptographic hashing, Data integrity'
            },
            {
                'step': 3,
                'title': 'Verification Request',
                'actor': 'Employer/University',
                'action': 'Submit certificate for verification',
                'blockchain_concept': 'Trustless verification'
            },
            {
                'step': 4,
                'title': 'Blockchain Query',
                'actor': 'System',
                'action': 'Calculate hash and compare with blockchain',
                'blockchain_concept': 'Decentralized validation'
            },
            {
                'step': 5,
                'title': 'Result Display',
                'actor': 'System',
                'action': 'Show verification result with proof',
                'blockchain_concept': 'Transparency, Audit trail'
            }
        ],
        'security_features': {
            'immutability': 'Cannot modify registered certificates',
            'tamper_detection': 'Hash changes if document modified',
            'non_repudiation': 'Issuer signature on blockchain',
            'transparency': 'All verifications logged',
            'availability': 'Decentralized, no single point of failure'
        },
        'verification_methods': {
            'method_1': 'By Verification Code - Quick lookup',
            'method_2': 'By Student Index - All certificates for student',
            'method_3': 'By File Upload - Hash comparison'
        },
        'api_endpoints': {
            'register': 'POST /api/certificate/register',
            'verify_by_code': 'POST /api/certificate/verify-by-code',
            'verify_by_index': 'POST /api/certificate/verify-by-index',
            'verify_by_file': 'POST /api/certificate/verify',
            'demo_endpoints': 'GET /api/certificate/demo/*'
        }
    }), 200
