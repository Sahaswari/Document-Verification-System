"""
SQLAlchemy Database Service for Document Verification System
PostgreSQL database for Students, Results, Certificates, and Users
"""
import os
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import or_

db = SQLAlchemy()


# ==================== MODELS ====================

class Student(db.Model):
    """Student model for G.C.E exam candidates"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    index_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False)
    full_name_sinhala = db.Column(db.String(200))
    full_name_tamil = db.Column(db.String(200))
    name_with_initials = db.Column(db.String(100))
    nic_number = db.Column(db.String(20), index=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    school_name = db.Column(db.String(200))
    school_code = db.Column(db.String(20))
    district = db.Column(db.String(50))
    province = db.Column(db.String(50))
    medium = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = db.relationship('ExamResult', backref='student', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'index_number': self.index_number,
            'full_name': self.full_name,
            'full_name_sinhala': self.full_name_sinhala,
            'full_name_tamil': self.full_name_tamil,
            'name_with_initials': self.name_with_initials,
            'nic_number': self.nic_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'school_name': self.school_name,
            'school_code': self.school_code,
            'district': self.district,
            'province': self.province,
            'medium': self.medium,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExamResult(db.Model):
    """Exam result model for O/L and A/L exams"""
    __tablename__ = 'exam_results'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    index_number = db.Column(db.String(50), nullable=False, index=True)
    exam_type = db.Column(db.String(10), nullable=False)  # OL or AL
    exam_year = db.Column(db.Integer, nullable=False)
    stream = db.Column(db.String(50))  # For A/L: Science, Commerce, Arts, etc.
    subjects = db.Column(JSON, nullable=False)  # List of subject results
    status = db.Column(db.String(20), default='pending')  # pending, certified, revoked
    attempt_number = db.Column(db.Integer, default=1)
    is_private_candidate = db.Column(db.Boolean, default=False)
    z_score = db.Column(db.Float)  # For A/L
    district_rank = db.Column(db.Integer)
    island_rank = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    certificate = db.relationship('Certificate', backref='result', uselist=False)
    
    def to_dict(self, include_student=False):
        data = {
            'id': self.id,
            'result_id': self.result_id,
            'student_id': self.student_id,
            'index_number': self.index_number,
            'exam_type': self.exam_type,
            'exam_year': self.exam_year,
            'stream': self.stream,
            'subjects': self.subjects,
            'status': self.status,
            'attempt_number': self.attempt_number,
            'is_private_candidate': self.is_private_candidate,
            'z_score': self.z_score,
            'district_rank': self.district_rank,
            'island_rank': self.island_rank,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_student and self.student:
            data['student'] = self.student.to_dict()
        return data


class Certificate(db.Model):
    """Certificate model for issued certificates"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    result_id = db.Column(db.String(50), db.ForeignKey('exam_results.result_id'), nullable=False)
    index_number = db.Column(db.String(50), nullable=False, index=True)
    exam_type = db.Column(db.String(10), nullable=False)
    exam_year = db.Column(db.Integer, nullable=False)
    verification_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    document_hash = db.Column(db.String(128), unique=True, nullable=False, index=True)
    image_hash = db.Column(db.String(128), index=True)  # Hash of PNG certificate image
    blockchain_tx_hash = db.Column(db.String(128))
    issued_by = db.Column(db.String(50))  # User ID who issued
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, revoked
    revoked_at = db.Column(db.DateTime)
    revoked_by = db.Column(db.String(50))
    revocation_reason = db.Column(db.Text)
    pdf_path = db.Column(db.String(500))
    image_path = db.Column(db.String(500))  # Path to PNG certificate image
    
    def to_dict(self, include_result=False):
        data = {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'result_id': self.result_id,
            'index_number': self.index_number,
            'exam_type': self.exam_type,
            'exam_year': self.exam_year,
            'verification_code': self.verification_code,
            'document_hash': self.document_hash,
            'image_hash': self.image_hash,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'issued_by': self.issued_by,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'status': self.status,
            'image_path': self.image_path
        }
        if include_result and self.result:
            data['result'] = self.result.to_dict(include_student=True)
        return data
    
    @staticmethod
    def generate_verification_code(exam_type: str, exam_year: int) -> str:
        """Generate unique verification code"""
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"DOE-{exam_type}{exam_year}-{unique_id}"
    
    @staticmethod
    def generate_document_hash(data: dict) -> str:
        """Generate document hash from certificate data"""
        content = str(sorted(data.items())).encode()
        return hashlib.sha256(content).hexdigest()


class User(db.Model):
    """User model for system users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), default='verifier')  # admin, issuer, verifier, data_entry
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'designation': self.designation,
            'department': self.department,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return self.password_hash == self.hash_password(password)


# ==================== DATABASE SERVICE CLASS ====================

class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self, db_instance):
        self.db = db_instance
    
    # ==================== STUDENTS ====================
    
    def get_all_students(self) -> List[Dict]:
        students = Student.query.all()
        return [s.to_dict() for s in students]
    
    def get_student(self, index_number: str) -> Optional[Dict]:
        student = Student.query.filter_by(index_number=index_number).first()
        return student.to_dict() if student else None
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        return Student.query.get(student_id)
    
    def add_student(self, student_data: Dict) -> Dict:
        # Convert date string to date object if needed
        if 'date_of_birth' in student_data and isinstance(student_data['date_of_birth'], str):
            student_data['date_of_birth'] = datetime.strptime(
                student_data['date_of_birth'], '%Y-%m-%d'
            ).date()
        
        student = Student(**student_data)
        self.db.session.add(student)
        self.db.session.commit()
        return student.to_dict()
    
    def search_students(self, query: str) -> List[Dict]:
        search = f"%{query}%"
        students = Student.query.filter(
            or_(
                Student.index_number.ilike(search),
                Student.full_name.ilike(search),
                Student.nic_number.ilike(search)
            )
        ).all()
        return [s.to_dict() for s in students]
    
    # ==================== RESULTS ====================
    
    def get_all_results(self) -> List[Dict]:
        results = ExamResult.query.all()
        return [r.to_dict(include_student=True) for r in results]
    
    def get_result(self, result_id: str) -> Optional[Dict]:
        result = ExamResult.query.filter_by(result_id=result_id).first()
        return result.to_dict(include_student=True) if result else None
    
    def get_result_obj(self, result_id: str) -> Optional[ExamResult]:
        return ExamResult.query.filter_by(result_id=result_id).first()
    
    def get_results_by_index(self, index_number: str) -> List[Dict]:
        results = ExamResult.query.filter_by(index_number=index_number).all()
        return [r.to_dict(include_student=True) for r in results]
    
    def get_results_by_year(self, exam_year: int, exam_type: str = None) -> List[Dict]:
        query = ExamResult.query.filter_by(exam_year=exam_year)
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        return [r.to_dict(include_student=True) for r in query.all()]
    
    def get_pending_results(self) -> List[Dict]:
        results = ExamResult.query.filter_by(status='pending').all()
        return [r.to_dict(include_student=True) for r in results]
    
    def add_result(self, result_data: Dict) -> Dict:
        # Get student ID if only index_number provided
        if 'student_id' not in result_data:
            student = Student.query.filter_by(
                index_number=result_data.get('index_number')
            ).first()
            if student:
                result_data['student_id'] = student.id
            else:
                raise ValueError("Student not found for the given index number")
        
        if not result_data.get('result_id'):
            result_data['result_id'] = f"RES-{uuid.uuid4().hex[:12].upper()}"
        
        result = ExamResult(**result_data)
        self.db.session.add(result)
        self.db.session.commit()
        return result.to_dict(include_student=True)
    
    def update_result(self, result_id: str, updates: Dict) -> Optional[Dict]:
        result = ExamResult.query.filter_by(result_id=result_id).first()
        if result:
            for key, value in updates.items():
                if hasattr(result, key):
                    setattr(result, key, value)
            self.db.session.commit()
            return result.to_dict(include_student=True)
        return None
    
    # ==================== CERTIFICATES ====================
    
    def get_all_certificates(self) -> List[Dict]:
        certificates = Certificate.query.order_by(Certificate.issued_at.desc()).all()
        return [c.to_dict() for c in certificates]
    
    def get_certificate(self, certificate_id: str) -> Optional[Dict]:
        cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
        return cert.to_dict(include_result=True) if cert else None
    
    def get_certificate_obj(self, certificate_id: str) -> Optional[Certificate]:
        return Certificate.query.filter_by(certificate_id=certificate_id).first()
    
    def get_certificate_by_verification_code(self, code: str) -> Optional[Dict]:
        cert = Certificate.query.filter_by(verification_code=code).first()
        return cert.to_dict(include_result=True) if cert else None
    
    def get_certificate_by_hash(self, document_hash: str) -> Optional[Dict]:
        cert = Certificate.query.filter_by(document_hash=document_hash).first()
        return cert.to_dict(include_result=True) if cert else None
    
    def get_certificates_by_index(self, index_number: str) -> List[Dict]:
        certificates = Certificate.query.filter_by(index_number=index_number).all()
        return [c.to_dict() for c in certificates]
    
    def add_certificate(self, cert_data: Dict) -> Dict:
        if not cert_data.get('certificate_id'):
            cert_data['certificate_id'] = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        if not cert_data.get('verification_code'):
            cert_data['verification_code'] = Certificate.generate_verification_code(
                cert_data.get('exam_type', 'OL'),
                cert_data.get('exam_year', datetime.now().year)
            )
        
        if not cert_data.get('document_hash'):
            cert_data['document_hash'] = Certificate.generate_document_hash(cert_data)
        
        cert = Certificate(**cert_data)
        self.db.session.add(cert)
        self.db.session.commit()
        return cert.to_dict()
    
    def update_certificate(self, certificate_id: str, updates: Dict) -> Optional[Dict]:
        cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
        if cert:
            for key, value in updates.items():
                if hasattr(cert, key):
                    setattr(cert, key, value)
            self.db.session.commit()
            return cert.to_dict()
        return None
    
    # ==================== USERS ====================
    
    def get_all_users(self) -> List[Dict]:
        users = User.query.all()
        return [u.to_dict() for u in users]
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        user = User.query.filter_by(user_id=user_id).first()
        return user.to_dict(include_sensitive=True) if user else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        user = User.query.filter_by(username=username).first()
        return user.to_dict(include_sensitive=True) if user else None
    
    def get_user_obj(self, user_id: str) -> Optional[User]:
        return User.query.filter_by(user_id=user_id).first()
    
    def add_user(self, user_data: Dict) -> Dict:
        if not user_data.get('user_id'):
            user_data['user_id'] = f"USR-{uuid.uuid4().hex[:8].upper()}"
        
        user = User(**user_data)
        self.db.session.add(user)
        self.db.session.commit()
        return user.to_dict()
    
    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.session.commit()
            return user.to_dict()
        return None
    
    def update_last_login(self, user_id: str):
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            self.db.session.commit()
    
    # ==================== STATS ====================
    
    def get_stats(self) -> Dict:
        return {
            'total_students': Student.query.count(),
            'total_results': ExamResult.query.count(),
            'pending_certification': ExamResult.query.filter_by(status='pending').count(),
            'certificates_issued': Certificate.query.filter_by(status='active').count(),
            'ol_results': ExamResult.query.filter_by(exam_type='OL').count(),
            'al_results': ExamResult.query.filter_by(exam_type='AL').count()
        }


# ==================== SAMPLE DATA INITIALIZATION ====================

def init_sample_data(db_service: DatabaseService, student_count: int = 100):
    """
    Initialize database with sample data if empty.
    Automatically generates 100 students, 100 results, and sample certificates for testing.
    
    Args:
        db_service: DatabaseService instance
        student_count: Number of students to generate (default 100)
    """
    
    # Check if data already exists
    if Student.query.first() is not None:
        print("Database already contains data. Skipping seed data initialization.")
        return
    
    print(f"=" * 60)
    print("DATABASE SEED: Initializing test data...")
    print(f"Generating {student_count} students, results, and certificates...")
    print(f"=" * 60)
    
    # Import seed data generator
    from app.services.seed_data import get_seed_data
    
    # Generate seed data
    seed_data = get_seed_data(student_count=student_count)
    
    # ==================== ADD STUDENTS ====================
    print(f"\n[1/4] Adding {len(seed_data['students'])} students...")
    students_created = 0
    students_map = {}  # index_number -> student_id mapping
    
    for student_data in seed_data['students']:
        try:
            student = db_service.add_student(student_data)
            students_map[student['index_number']] = student['id']
            students_created += 1
            if students_created % 20 == 0:
                print(f"      Created {students_created} students...")
        except Exception as e:
            print(f"      Error creating student {student_data.get('index_number')}: {e}")
    
    print(f"      ✓ Successfully created {students_created} students")
    
    # ==================== ADD RESULTS ====================
    print(f"\n[2/4] Adding {len(seed_data['results'])} exam results...")
    results_created = 0
    
    for result_data in seed_data['results']:
        try:
            # Get student ID from map
            index_number = result_data['index_number']
            if index_number in students_map:
                result_data['student_id'] = students_map[index_number]
                db_service.add_result(result_data)
                results_created += 1
                if results_created % 20 == 0:
                    print(f"      Created {results_created} results...")
        except Exception as e:
            print(f"      Error creating result {result_data.get('result_id')}: {e}")
    
    print(f"      ✓ Successfully created {results_created} exam results")
    
    # ==================== ADD CERTIFICATES ====================
    print(f"\n[3/4] Adding {len(seed_data['certificates'])} sample certificates...")
    certs_created = 0
    
    for cert_data in seed_data['certificates']:
        try:
            db_service.add_certificate(cert_data)
            certs_created += 1
        except Exception as e:
            print(f"      Error creating certificate {cert_data.get('certificate_id')}: {e}")
    
    print(f"      ✓ Successfully created {certs_created} certificates")
    
    # ==================== REGISTER ON BLOCKCHAIN ====================
    print(f"\n[4/5] Registering certificates on blockchain...")
    try:
        from app.services.blockchain_utils import register_certificates_on_blockchain
        blockchain_results = register_certificates_on_blockchain(
            certificates=seed_data['certificates'],
            results=seed_data['results'],
            students=seed_data['students']
        )
    except Exception as e:
        print(f"      ⚠️  Blockchain registration skipped: {e}")
        blockchain_results = []
    
    # ==================== ADD SYSTEM USERS ====================
    print(f"\n[5/5] Adding system users...")
    
    sample_users = [
        {
            'user_id': 'USR-001',
            'username': 'admin',
            'email': 'admin@doenets.lk',
            'password_hash': User.hash_password('admin123'),
            'full_name': 'System Administrator',
            'role': 'admin',
            'designation': 'System Administrator',
            'department': 'Department of Examinations',
            'employee_id': 'DOE-ADMIN-001',
            'is_active': True
        },
        {
            'user_id': 'USR-002',
            'username': 'issuer',
            'email': 'issuer@doenets.lk',
            'password_hash': User.hash_password('issuer123'),
            'full_name': 'Certificate Issuing Officer',
            'role': 'issuer',
            'designation': 'Senior Examinations Officer',
            'department': 'Department of Examinations',
            'employee_id': 'DOE-ISO-001',
            'is_active': True
        },
        {
            'user_id': 'USR-003',
            'username': 'dataentry',
            'email': 'dataentry@doenets.lk',
            'password_hash': User.hash_password('data123'),
            'full_name': 'Data Entry Operator',
            'role': 'data_entry',
            'designation': 'Data Entry Operator',
            'department': 'Department of Examinations',
            'employee_id': 'DOE-DEO-001',
            'is_active': True
        },
        {
            'user_id': 'USR-004',
            'username': 'verifier',
            'email': 'verifier@doenets.lk',
            'password_hash': User.hash_password('verify123'),
            'full_name': 'Verification Officer',
            'role': 'verifier',
            'designation': 'Verification Officer',
            'department': 'Department of Examinations',
            'employee_id': 'DOE-VER-001',
            'is_active': True
        }
    ]
    
    users_created = 0
    for user_data in sample_users:
        try:
            db_service.add_user(user_data)
            users_created += 1
            print(f"      Created user: {user_data['username']} ({user_data['role']})")
        except Exception as e:
            print(f"      Error creating user {user_data['username']}: {e}")
    
    print(f"      ✓ Successfully created {users_created} users")
    
    # ==================== SUMMARY ====================
    stats = db_service.get_stats()
    print(f"\n{'=' * 60}")
    print("DATABASE SEED COMPLETE - Summary:")
    print(f"{'=' * 60}")
    print(f"  • Students:           {stats['total_students']}")
    print(f"  • Exam Results:       {stats['total_results']}")
    print(f"    - O/L Results:      {stats['ol_results']}")
    print(f"    - A/L Results:      {stats['al_results']}")
    print(f"  • Pending Certs:      {stats['pending_certification']}")
    print(f"  • Issued Certificates: {stats['certificates_issued']}")
    print(f"  • System Users:       {users_created}")
    print(f"{'=' * 60}")
    print("\nDefault Login Credentials:")
    print(f"  • admin / admin123    (Administrator)")
    print(f"  • issuer / issuer123  (Certificate Issuer)")
    print(f"  • dataentry / data123 (Data Entry)")
    print(f"  • verifier / verify123 (Verifier)")
    print(f"{'=' * 60}\n")
