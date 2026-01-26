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

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CERTIFICATES_FOLDER'], exist_ok=True)

# Import services
from app.services.database import db
from app.services.pdf_generator import CertificatePDFGenerator
from app.models.user import User
from app.models.certificate import Certificate

# Initialize PDF generator
pdf_generator = CertificatePDFGenerator(output_dir=app.config['CERTIFICATES_FOLDER'])


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
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.get_user(data['user_id'])
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
        'version': '1.0.0'
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
    
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not User.verify_password(password, user.get('password_hash', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.get('is_active', False):
        return jsonify({'error': 'Account is disabled'}), 401
    
    # Update last login
    db.update_user(user['user_id'], {'last_login': datetime.now().isoformat()})
    
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
    students = db.get_all_students()
    return jsonify({'students': students, 'count': len(students)})


@app.route('/api/students/search', methods=['GET'])
@token_required
def search_students(current_user):
    """Search students"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Search query too short'}), 400
    
    students = db.search_students(query)
    return jsonify({'students': students, 'count': len(students)})


@app.route('/api/students/<index_number>', methods=['GET'])
@token_required
def get_student(current_user, index_number):
    """Get student by index number"""
    student = db.get_student(index_number)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get student's results
    results = db.get_results_by_index(index_number)
    
    # Get student's certificates
    certificates = db.get_certificates_by_index(index_number)
    
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
    
    results = db.get_all_results()
    
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
    results = db.get_pending_results()
    
    # Enrich with student data
    enriched_results = []
    for result in results:
        student = db.get_student(result.get('index_number'))
        enriched_results.append({
            **result,
            'student': student
        })
    
    return jsonify({'results': enriched_results, 'count': len(enriched_results)})


@app.route('/api/results/<result_id>', methods=['GET'])
@token_required
def get_result(current_user, result_id):
    """Get result by ID"""
    result = db.get_result(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    student = db.get_student(result.get('index_number'))
    
    return jsonify({
        'result': result,
        'student': student
    })


# ==================== CERTIFICATE ROUTES ====================

@app.route('/api/certificates', methods=['GET'])
@token_required
def get_certificates(current_user):
    """Get all certificates"""
    certificates = db.get_all_certificates()
    return jsonify({'certificates': certificates, 'count': len(certificates)})


@app.route('/api/certificates/<certificate_id>', methods=['GET'])
@token_required
def get_certificate(current_user, certificate_id):
    """Get certificate by ID"""
    certificate = db.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    result = db.get_result(certificate.get('result_id'))
    student = db.get_student(certificate.get('index_number'))
    
    return jsonify({
        'certificate': certificate,
        'result': result,
        'student': student
    })


@app.route('/api/certificates/issue', methods=['POST'])
@token_required
@issuer_required
def issue_certificate(current_user):
    """Issue a new certificate for a result"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result_id = data.get('result_id')
    if not result_id:
        return jsonify({'error': 'Result ID required'}), 400
    
    # Get result
    result = db.get_result(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    if result.get('status') == 'issued':
        return jsonify({'error': 'Certificate already issued for this result'}), 400
    
    # Get student
    student = db.get_student(result.get('index_number'))
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Create certificate record
    certificate_id = f"CERT-{result.get('exam_type')}-{result.get('exam_year')}-{str(uuid.uuid4())[:8].upper()}"
    
    cert = Certificate(
        certificate_id=certificate_id,
        result_id=result_id,
        index_number=result.get('index_number'),
        exam_type=result.get('exam_type'),
        exam_year=result.get('exam_year'),
        issued_by=current_user.get('user_id'),
        issuer_designation=current_user.get('designation'),
        status='pending'
    )
    
    # Generate document hash
    cert.generate_document_hash(student, result)
    
    # Generate PDF
    try:
        pdf_bytes, doc_hash, filepath = pdf_generator.generate_certificate(
            student_data=student,
            result_data=result,
            certificate_data=cert.to_dict()
        )
        
        cert.document_hash = doc_hash
        cert.pdf_path = filepath
        cert.status = 'issued'
        
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
    
    # Save certificate
    cert_data = cert.to_dict()
    db.add_certificate(cert_data)
    
    # Update result status
    db.update_result(result_id, {
        'status': 'issued',
        'certified_at': datetime.now().isoformat(),
        'certified_by': current_user.get('user_id')
    })
    
    return jsonify({
        'message': 'Certificate issued successfully',
        'certificate': cert_data,
        'verification_code': cert.get_verification_code()
    }), 201


@app.route('/api/certificates/<certificate_id>/download', methods=['GET'])
@token_required
def download_certificate(current_user, certificate_id):
    """Download certificate PDF"""
    certificate = db.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    pdf_path = certificate.get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404
    
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
    certificate = db.get_certificate(certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificate not found'}), 404
    
    pdf_path = certificate.get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404
    
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=False
    )


# ==================== PUBLIC VERIFICATION ROUTES ====================

@app.route('/api/verify', methods=['POST'])
def verify_certificate():
    """Public endpoint to verify a certificate"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Can verify by verification_code, document_hash, or certificate_id
    verification_code = data.get('verification_code')
    document_hash = data.get('document_hash')
    certificate_id = data.get('certificate_id')
    
    certificate = None
    
    if document_hash:
        certificate = db.get_certificate_by_hash(document_hash)
    elif certificate_id:
        certificate = db.get_certificate(certificate_id)
    elif verification_code:
        # Parse verification code to find certificate
        # Format: DOE-{EXAM_TYPE}-{YEAR}-{INDEX}-{HASH_PREFIX}
        certificates = db.get_all_certificates()
        for cert in certificates:
            if cert.get('document_hash', '')[:8].upper() in verification_code.upper():
                certificate = cert
                break
    
    if not certificate:
        return jsonify({
            'verified': False,
            'message': 'Certificate not found in the system',
            'status': 'NOT_FOUND'
        }), 404
    
    if certificate.get('status') == 'revoked':
        return jsonify({
            'verified': False,
            'message': 'This certificate has been revoked',
            'status': 'REVOKED',
            'revoked_at': certificate.get('revoked_at'),
            'reason': certificate.get('revocation_reason')
        })
    
    # Get associated data
    result = db.get_result(certificate.get('result_id'))
    student = db.get_student(certificate.get('index_number'))
    
    # Return verification success (limited public info)
    return jsonify({
        'verified': True,
        'message': 'Certificate is valid and authentic',
        'status': 'VALID',
        'certificate': {
            'certificate_id': certificate.get('certificate_id'),
            'exam_type': certificate.get('exam_type'),
            'exam_year': certificate.get('exam_year'),
            'issued_at': certificate.get('issued_at'),
            'verification_code': certificate.get('verification_code')
        },
        'student': {
            'name_with_initials': student.get('name_with_initials') if student else None,
            'index_number': certificate.get('index_number'),
            'school_name': student.get('school_name') if student else None
        },
        'result': {
            'exam_type': result.get('exam_type') if result else None,
            'exam_year': result.get('exam_year') if result else None,
            'subjects_count': len(result.get('subjects', [])) if result else 0
        }
    })


# ==================== STATS ROUTES ====================

@app.route('/api/stats/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics"""
    results = db.get_all_results()
    certificates = db.get_all_certificates()
    students = db.get_all_students()
    
    pending_count = len([r for r in results if r.get('status') == 'pending'])
    issued_count = len([c for c in certificates if c.get('status') == 'issued'])
    
    ol_results = len([r for r in results if r.get('exam_type') == 'OL'])
    al_results = len([r for r in results if r.get('exam_type') == 'AL'])
    
    return jsonify({
        'stats': {
            'total_students': len(students),
            'total_results': len(results),
            'pending_certification': pending_count,
            'certificates_issued': issued_count,
            'ol_results': ol_results,
            'al_results': al_results
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
