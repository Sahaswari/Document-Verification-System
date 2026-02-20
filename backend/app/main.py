"""
Document Verification System - Flask Backend
Sri Lanka Department of Examinations Certificate System
"""
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['CERTIFICATES_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'certificates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://docverify:docverify123@localhost:5432/document_verification'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CERTIFICATES_FOLDER'], exist_ok=True)

# Import services and initialize database
from app.services.database import db, DatabaseService, init_sample_data, User
from app.services.pdf_generator import CertificatePDFGenerator
from app.services.blockchain_service import get_blockchain_service

# Initialize SQLAlchemy with app
db.init_app(app)

# Register blockchain certificate routes
try:
    from app.api.certificate_routes import certificate_bp
    app.register_blueprint(certificate_bp)
    print("Blockchain certificate routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not load blockchain certificate routes: {e}")
    print("   Make sure blockchain is running and contracts are deployed")
except Exception as e:
    print(f"Warning: Error registering blockchain routes: {e}")

# Create database service instance
db_service = None

# Initialize PDF generator
pdf_generator = CertificatePDFGenerator(output_dir=app.config['CERTIFICATES_FOLDER'])

# Create tables and initialize data
with app.app_context():
    db.create_all()
    db_service = DatabaseService(db)
    init_sample_data(db_service)


# ==================== AUTH HELPERS ====================

def generate_token(user_data: dict) -> str:
    """Generate JWT token"""
    payload = {
        'user_id': user_data['user_id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check Authorization header first
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Also check query parameter (for PDF viewing in new tabs)
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db_service.get_user(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


def issuer_required(f):
    """Decorator for issuer-only routes"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] not in ['admin', 'issuer']:
            return jsonify({'error': 'Issuer permission required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Sri Lanka DOE Certificate Verification API',
        'version': '1.0.0',
        'database': 'PostgreSQL'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend service is running',
        'timestamp': datetime.now().isoformat()
    })


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = db_service.get_user_by_username(username)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password using static method
    password_hash = User.hash_password(password)
    if password_hash != user.get('password_hash', ''):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.get('is_active', False):
        return jsonify({'error': 'Account is disabled'}), 401
    
    # Update last login
    db_service.update_last_login(user['user_id'])
    
    # Generate token
    token = generate_token(user)
    
    # Return user info (without sensitive data)
    user_info = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user_info
    })


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    user_info = {k: v for k, v in current_user.items() if k != 'password_hash'}
    return jsonify({'user': user_info})


# ==================== STUDENT ROUTES ====================

@app.route('/api/students', methods=['GET'])
@token_required
def get_students(current_user):
    """Get all students"""
    students = db_service.get_all_students()
    return jsonify({'students': students, 'count': len(students)})


@app.route('/api/students/search', methods=['GET'])
@token_required
def search_students(current_user):
    """Search students"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Search query too short'}), 400
    
    students = db_service.search_students(query)
    return jsonify({'students': students, 'count': len(students)})


@app.route('/api/students/<index_number>', methods=['GET'])
@token_required
def get_student(current_user, index_number):
    """Get student by index number"""
    student = db_service.get_student(index_number)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get student's results
    results = db_service.get_results_by_index(index_number)
    
    # Get student's certificates
    certificates = db_service.get_certificates_by_index(index_number)
    
    return jsonify({
        'student': student,
        'results': results,
        'certificates': certificates
    })


# ==================== RESULTS ROUTES ====================

@app.route('/api/results', methods=['GET'])
@token_required
def get_results(current_user):
    """Get all results with optional filters"""
    exam_year = request.args.get('year', type=int)
    exam_type = request.args.get('type')
    status = request.args.get('status')
    
    results = db_service.get_all_results()
    
    if exam_year:
        results = [r for r in results if r.get('exam_year') == exam_year]
    if exam_type:
        results = [r for r in results if r.get('exam_type') == exam_type]
    if status:
        results = [r for r in results if r.get('status') == status]
    
    return jsonify({'results': results, 'count': len(results)})


@app.route('/api/results/pending', methods=['GET'])
@token_required
@issuer_required
def get_pending_results(current_user):
    """Get results pending certification"""
    results = db_service.get_pending_results()
    
    # Results already include student data from the service
    enriched_results = results
    
    return jsonify({'results': enriched_results, 'count': len(enriched_results)})


@app.route('/api/results/<result_id>', methods=['GET'])
@token_required
def get_result(current_user, result_id):
    """Get result by ID"""
    result = db_service.get_result(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    student = result.get('student')
    
    return jsonify({
        'result': result,
        'student': student
    })


# ==================== CERTIFICATE ROUTES ====================

@app.route('/api/certificates', methods=['GET'])
@token_required
def get_certificates(current_user):
    """Get all certificates"""
    certificates = db_service.get_all_certificates()
    return jsonify({'certificates': certificates, 'count': len(certificates)})


@app.route('/api/certificates/<certificate_id>', methods=['GET'])
@token_required
def get_certificate(current_user, certificate_id):
    """Get certificate by ID"""
    certificate = db_service.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    # Certificate already includes result with student from service
    return jsonify({
        'certificate': certificate
    })


@app.route('/api/certificates/issue', methods=['POST'])
@token_required
@issuer_required
def issue_certificate(current_user):
    """Issue a new certificate for a result"""
    from app.services.database import Certificate as CertModel
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result_id = data.get('result_id')
    if not result_id:
        return jsonify({'error': 'Result ID required'}), 400
    
    # Get result
    result = db_service.get_result(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    if result.get('status') == 'issued':
        return jsonify({'error': 'Certificate already issued for this result'}), 400
    
    # Get student from result (included by service)
    student = result.get('student')
    if not student:
        student = db_service.get_student(result.get('index_number'))
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Create certificate data
    certificate_id = f"CERT-{result.get('exam_type')}-{result.get('exam_year')}-{str(uuid.uuid4())[:8].upper()}"
    verification_code = CertModel.generate_verification_code(
        result.get('exam_type'),
        result.get('exam_year')
    )
    
    cert_data = {
        'certificate_id': certificate_id,
        'result_id': result_id,
        'index_number': result.get('index_number'),
        'exam_type': result.get('exam_type'),
        'exam_year': result.get('exam_year'),
        'verification_code': verification_code,
        'issued_by': current_user.get('user_id'),
        'status': 'pending'
    }
    
    # Generate document hash
    cert_data['document_hash'] = CertModel.generate_document_hash({
        'student': student,
        'result': result,
        'certificate_id': certificate_id
    })
    
    # Generate PDF and PNG image
    try:
        result_tuple = pdf_generator.generate_certificate(
            student_data=student,
            result_data=result,
            certificate_data=cert_data
        )
        
        # Handle both old (3 values) and new (5 values) return format
        if len(result_tuple) == 5:
            pdf_bytes, doc_hash, filepath, image_hash, image_path = result_tuple
        else:
            pdf_bytes, doc_hash, filepath = result_tuple
            image_hash, image_path = None, None
        
        cert_data['document_hash'] = doc_hash
        cert_data['pdf_path'] = filepath
        cert_data['status'] = 'active'
        
        # Store image hash and path if available
        if image_hash:
            cert_data['image_hash'] = image_hash
        if image_path:
            cert_data['image_path'] = image_path
        
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
    
    # Save certificate
    saved_cert = db_service.add_certificate(cert_data)
    
    # Register certificate on blockchain
    blockchain_registered = False
    blockchain_tx = None
    try:
        blockchain_service = get_blockchain_service()
        if blockchain_service:
            # Calculate results hash for integrity verification
            import json
            import hashlib
            subjects = result.get('subjects', [])
            sorted_results = sorted(subjects, key=lambda x: x.get('subject_code', ''))
            results_string = json.dumps(sorted_results, sort_keys=True, separators=(',', ':'))
            results_hash = hashlib.sha256(results_string.encode()).hexdigest()
            
            # Calculate student info hash
            student_info = f"{student.get('full_name', '')}|{student.get('school_name', '')}"
            student_info_hash = hashlib.sha256(student_info.encode()).hexdigest()
            
            # Convert exam_type to blockchain format (OL -> O/L, AL -> A/L)
            exam_type = result.get('exam_type', 'OL')
            doc_type = 'O/L' if exam_type == 'OL' else 'A/L' if exam_type == 'AL' else exam_type
            
            # Handle None values for stream (OL exams don't have streams)
            exam_subject = result.get('stream')
            if exam_subject is None:
                exam_subject = ''
                
            # Register on blockchain with document hash
            blockchain_result = blockchain_service.register_document(
                document_hash=doc_hash,
                results_hash=results_hash,
                verification_code=verification_code,
                student_info_hash=student_info_hash,
                owner_address='0x0000000000000000000000000000000000000000',
                document_type=doc_type,
                student_index=result.get('index_number', ''),
                exam_year=int(result.get('exam_year', 2024)),
                exam_subject=exam_subject
            )
            if blockchain_result.get('success'):
                blockchain_registered = True
                blockchain_tx = blockchain_result.get('transaction_hash')
                print(f"Certificate registered on blockchain: {verification_code}, TX: {blockchain_tx}")
                
                # Update certificate with blockchain transaction hash
                db_service.update_certificate(saved_cert.get('certificate_id'), {
                    'blockchain_tx_hash': blockchain_tx
                })
                saved_cert['blockchain_tx_hash'] = blockchain_tx
            else:
                print(f"Blockchain registration failed: {blockchain_result.get('error')}")
    except Exception as e:
        print(f"Warning: Failed to register certificate on blockchain: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continue even if blockchain registration fails - certificate is still valid in database
    
    # Update result status
    db_service.update_result(result_id, {
        'status': 'issued'
    })
    
    return jsonify({
        'message': 'Certificate issued successfully',
        'certificate': saved_cert,
        'verification_code': verification_code,
        'blockchain_registered': blockchain_registered,
        'transaction_hash': blockchain_tx
    }), 201


def generate_certificate_pdf_if_missing(certificate):
    """Generate PDF for a certificate if it doesn't exist"""
    pdf_path = certificate.get('pdf_path')
    
    # If PDF exists at stored path, return it
    if pdf_path and os.path.exists(pdf_path):
        return pdf_path, None
    
    # Also check if PDF exists at expected location based on naming convention
    exam_type = certificate.get('exam_type', 'OL')
    exam_year = certificate.get('exam_year', 2024)
    index_number = certificate.get('index_number', '')
    expected_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{index_number}.pdf'
    
    if os.path.exists(expected_path):
        # PDF exists, update the database with the correct path and return
        db_service.update_certificate(certificate.get('certificate_id'), {
            'pdf_path': expected_path
        })
        return expected_path, None
    
    # Get the result data for this certificate
    result = db_service.get_result(certificate.get('result_id'))
    if not result:
        return None, "Result data not found for certificate"
    
    student = result.get('student')
    if not student:
        return None, "Student data not found for certificate"
    
    # Prepare data for PDF generation
    student_data = {
        'full_name': student.get('full_name', 'Unknown'),
        'name_with_initials': student.get('name_with_initials', ''),
        'date_of_birth': student.get('date_of_birth', ''),
        'school_name': student.get('school_name', ''),
        'index_number': certificate.get('index_number', '')
    }
    
    result_data = {
        'exam_type': certificate.get('exam_type', 'OL'),
        'exam_year': certificate.get('exam_year', 2024),
        'subjects': result.get('subjects', []),
        'stream': result.get('stream', ''),
        'z_score': result.get('z_score'),
        'district_rank': result.get('district_rank'),
        'island_rank': result.get('island_rank')
    }
    
    # Prepare certificate data for PDF (must be a dict, not string)
    certificate_data = {
        'certificate_id': certificate.get('certificate_id', ''),
        'verification_code': certificate.get('verification_code', ''),
        'document_hash': certificate.get('document_hash', ''),
        'issued_at': certificate.get('issued_at', ''),
        'issued_by': certificate.get('issued_by', '')
    }
    
    try:
        # Generate the PDF
        pdf_bytes, doc_hash, filepath = pdf_generator.generate_certificate(
            student_data, result_data, certificate_data
        )
        
        # Update the certificate record with the PDF path
        # IMPORTANT: Only update document_hash if it doesn't already exist
        # (to avoid breaking blockchain verification)
        update_data = {'pdf_path': filepath}
        existing_hash = certificate.get('document_hash')
        if not existing_hash:
            update_data['document_hash'] = doc_hash
        else:
            # Log warning if hashes don't match (PDF was regenerated with different hash)
            if existing_hash != doc_hash:
                print(f"WARNING: Regenerated PDF hash ({doc_hash[:16]}...) differs from stored hash ({existing_hash[:16]}...) for certificate {certificate.get('certificate_id')}")
        
        db_service.update_certificate(certificate.get('certificate_id'), update_data)
        
        return filepath, None
    except Exception as e:
        return None, f"PDF generation failed: {str(e)}"


@app.route('/api/certificates/<certificate_id>/download', methods=['GET'])
@token_required
def download_certificate(current_user, certificate_id):
    """Download certificate PDF"""
    certificate = db_service.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    # Generate PDF if it doesn't exist
    pdf_path, error = generate_certificate_pdf_if_missing(certificate)
    if error:
        return jsonify({'error': error}), 500
    if not pdf_path:
        return jsonify({'error': 'Failed to generate PDF'}), 500
    
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=os.path.basename(pdf_path)
    )


@app.route('/api/certificates/<certificate_id>/preview', methods=['GET'])
@token_required
def preview_certificate(current_user, certificate_id):
    """Preview certificate PDF (inline)"""
    certificate = db_service.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    # Generate PDF if it doesn't exist
    pdf_path, error = generate_certificate_pdf_if_missing(certificate)
    if error:
        return jsonify({'error': error}), 500
    if not pdf_path:
        return jsonify({'error': 'Failed to generate PDF'}), 500
    
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=False
    )


@app.route('/api/certificates/<certificate_id>/download-image', methods=['GET'])
@token_required
def download_certificate_image(current_user, certificate_id):
    """Download certificate as PNG image"""
    certificate = db_service.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    # Check if image exists
    image_path = certificate.get('image_path')
    
    # If not stored, try expected path
    if not image_path:
        exam_type = certificate.get('exam_type', 'OL')
        exam_year = certificate.get('exam_year', 2024)
        index_number = certificate.get('index_number', '')
        image_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{index_number}.png'
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Certificate image not found. Please download the PDF first to generate the image.'}), 404
    
    return send_file(
        image_path,
        mimetype='image/png',
        as_attachment=True,
        download_name=os.path.basename(image_path)
    )


@app.route('/api/certificates/<certificate_id>/preview-image', methods=['GET'])
@token_required
def preview_certificate_image(current_user, certificate_id):
    """Preview certificate image (inline)"""
    certificate = db_service.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    # Check if image exists
    image_path = certificate.get('image_path')
    
    # If not stored, try expected path
    if not image_path:
        exam_type = certificate.get('exam_type', 'OL')
        exam_year = certificate.get('exam_year', 2024)
        index_number = certificate.get('index_number', '')
        image_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{index_number}.png'
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Certificate image not found. Please download the PDF first to generate the image.'}), 404
    
    return send_file(
        image_path,
        mimetype='image/png',
        as_attachment=False
    )


# ==================== HELPER FUNCTIONS ====================

def _format_date(date_value):
    """Format date value to string, handling both datetime and string inputs"""
    if date_value is None:
        return None
    if isinstance(date_value, str):
        return date_value
    try:
        return date_value.strftime('%Y-%m-%d')
    except AttributeError:
        return str(date_value)


# ==================== PUBLIC VERIFICATION ROUTES ====================

@app.route('/api/verify', methods=['POST'])
def verify_certificate():
    """
    Public endpoint to verify a certificate by verification code
    Verifies in both database and blockchain for double authenticity
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Support multiple verification methods
    verification_code = data.get('verification_code') or data.get('verificationCode')
    document_hash = data.get('document_hash')
    certificate_id = data.get('certificate_id')
    
    certificate = None
    
    # Find certificate in database
    if document_hash:
        certificate = db_service.get_certificate_by_hash(document_hash)
    elif certificate_id:
        certificate = db_service.get_certificate(certificate_id)
    elif verification_code:
        # Search by verification code
        certificate = db_service.get_certificate_by_verification_code(verification_code)
    
    if not certificate:
        return jsonify({
            'valid': False,
            'verified': False,
            'message': 'Certificate not found in the system',
            'status': 'NOT_FOUND'
        }), 200
    
    # Check if revoked in database
    if certificate.get('status') == 'revoked':
        return jsonify({
            'valid': False,
            'verified': False,
            'message': 'This certificate has been revoked',
            'status': 'REVOKED',
            'revoked_at': certificate.get('revoked_at'),
            'reason': certificate.get('revocation_reason')
        }), 200
    
    # Get associated data (included in certificate from service)
    result = certificate.get('result', {})
    student = result.get('student', {})
    
    # Verify on blockchain if available
    blockchain_verified = False
    blockchain_status = None
    
    try:
        from app.services.blockchain_service import get_blockchain_service
        blockchain = get_blockchain_service()
        
        # Get document hash from certificate
        cert_hash = certificate.get('document_hash')
        
        if cert_hash:
            # Verify on blockchain
            blockchain_result = blockchain.verify_document(cert_hash)
            blockchain_verified = blockchain_result.get('exists') and blockchain_result.get('is_valid')
            blockchain_status = {
                'verified_on_blockchain': blockchain_verified,
                'blockchain_timestamp': blockchain_result.get('timestamp'),
                'blockchain_issuer': blockchain_result.get('issuer')
            }
    except Exception as e:
        print(f"Warning: Blockchain verification failed: {e}")
        blockchain_status = {
            'verified_on_blockchain': None,
            'error': 'Blockchain verification unavailable'
        }
    
    # Return comprehensive verification result
    return jsonify({
        'valid': True,
        'verified': True,
        'message': 'Certificate is valid and authentic',
        'status': 'VALID',
        'certificate': {
            'certificate_id': certificate.get('certificate_id'),
            'verification_code': certificate.get('verification_code'),
            'document_hash': certificate.get('document_hash'),
            'exam_type': certificate.get('exam_type'),
            'exam_year': certificate.get('exam_year'),
            'issued_at': certificate.get('issued_at'),
            'result': {
                'index_number': result.get('index_number') if result else None,
                'exam_type': result.get('exam_type') if result else None,
                'exam_year': result.get('exam_year') if result else None,
                'subjects': result.get('subjects', []) if result else []
            },
            'student': {
                'full_name': student.get('full_name') if student else None,
                'full_name_sinhala': student.get('full_name_sinhala') if student else None,
                'full_name_tamil': student.get('full_name_tamil') if student else None,
                'name_with_initials': student.get('name_with_initials') if student else None,
                'date_of_birth': _format_date(student.get('date_of_birth')) if student else None,
                'school_name': student.get('school_name') if student else None,
                'district': student.get('district') if student else None
            },
            'blockchain': blockchain_status
        }
    }), 200


# ==================== STATS ROUTES ====================

@app.route('/api/stats/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics"""
    stats = db_service.get_stats()
    return jsonify({'stats': stats})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
