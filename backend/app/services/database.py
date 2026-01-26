"""
Simple JSON-based Database for Development
In production, replace with PostgreSQL or MongoDB
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class Database:
    """Simple file-based database for development"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files
        self.files = {
            "students": os.path.join(data_dir, "students.json"),
            "results": os.path.join(data_dir, "results.json"),
            "certificates": os.path.join(data_dir, "certificates.json"),
            "users": os.path.join(data_dir, "users.json")
        }
        
        # Initialize empty files if not exist
        for name, filepath in self.files.items():
            if not os.path.exists(filepath):
                self._save_data(filepath, [])
        
        # Initialize with sample data if empty
        self._initialize_sample_data()
    
    def _load_data(self, filepath: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, filepath: str, data: List[Dict]):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== STUDENTS ====================
    
    def get_all_students(self) -> List[Dict]:
        """Get all students"""
        return self._load_data(self.files["students"])
    
    def get_student(self, index_number: str) -> Optional[Dict]:
        """Get student by index number"""
        students = self.get_all_students()
        for student in students:
            if student.get("index_number") == index_number:
                return student
        return None
    
    def add_student(self, student_data: Dict) -> Dict:
        """Add new student"""
        students = self.get_all_students()
        students.append(student_data)
        self._save_data(self.files["students"], students)
        return student_data
    
    def search_students(self, query: str) -> List[Dict]:
        """Search students by name or index number"""
        students = self.get_all_students()
        query = query.lower()
        return [
            s for s in students
            if query in s.get("index_number", "").lower()
            or query in s.get("full_name", "").lower()
            or query in s.get("nic_number", "").lower()
        ]
    
    # ==================== RESULTS ====================
    
    def get_all_results(self) -> List[Dict]:
        """Get all exam results"""
        return self._load_data(self.files["results"])
    
    def get_result(self, result_id: str) -> Optional[Dict]:
        """Get result by ID"""
        results = self.get_all_results()
        for result in results:
            if result.get("result_id") == result_id:
                return result
        return None
    
    def get_results_by_index(self, index_number: str) -> List[Dict]:
        """Get all results for a student"""
        results = self.get_all_results()
        return [r for r in results if r.get("index_number") == index_number]
    
    def get_results_by_year(self, exam_year: int, exam_type: str = None) -> List[Dict]:
        """Get results by exam year and optionally type"""
        results = self.get_all_results()
        filtered = [r for r in results if r.get("exam_year") == exam_year]
        if exam_type:
            filtered = [r for r in filtered if r.get("exam_type") == exam_type]
        return filtered
    
    def get_pending_results(self) -> List[Dict]:
        """Get results pending certification"""
        results = self.get_all_results()
        return [r for r in results if r.get("status") == "pending"]
    
    def add_result(self, result_data: Dict) -> Dict:
        """Add new exam result"""
        results = self.get_all_results()
        if not result_data.get("result_id"):
            result_data["result_id"] = str(uuid.uuid4())
        result_data["created_at"] = datetime.now().isoformat()
        results.append(result_data)
        self._save_data(self.files["results"], results)
        return result_data
    
    def update_result(self, result_id: str, updates: Dict) -> Optional[Dict]:
        """Update exam result"""
        results = self.get_all_results()
        for i, result in enumerate(results):
            if result.get("result_id") == result_id:
                results[i].update(updates)
                self._save_data(self.files["results"], results)
                return results[i]
        return None
    
    # ==================== CERTIFICATES ====================
    
    def get_all_certificates(self) -> List[Dict]:
        """Get all certificates"""
        return self._load_data(self.files["certificates"])
    
    def get_certificate(self, certificate_id: str) -> Optional[Dict]:
        """Get certificate by ID"""
        certificates = self.get_all_certificates()
        for cert in certificates:
            if cert.get("certificate_id") == certificate_id:
                return cert
        return None
    
    def get_certificate_by_hash(self, document_hash: str) -> Optional[Dict]:
        """Get certificate by document hash"""
        certificates = self.get_all_certificates()
        for cert in certificates:
            if cert.get("document_hash") == document_hash:
                return cert
        return None
    
    def get_certificates_by_index(self, index_number: str) -> List[Dict]:
        """Get all certificates for a student"""
        certificates = self.get_all_certificates()
        return [c for c in certificates if c.get("index_number") == index_number]
    
    def add_certificate(self, cert_data: Dict) -> Dict:
        """Add new certificate"""
        certificates = self.get_all_certificates()
        if not cert_data.get("certificate_id"):
            cert_data["certificate_id"] = str(uuid.uuid4())
        cert_data["issued_at"] = datetime.now().isoformat()
        certificates.append(cert_data)
        self._save_data(self.files["certificates"], certificates)
        return cert_data
    
    def update_certificate(self, certificate_id: str, updates: Dict) -> Optional[Dict]:
        """Update certificate"""
        certificates = self.get_all_certificates()
        for i, cert in enumerate(certificates):
            if cert.get("certificate_id") == certificate_id:
                certificates[i].update(updates)
                self._save_data(self.files["certificates"], certificates)
                return certificates[i]
        return None
    
    # ==================== USERS ====================
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self._load_data(self.files["users"])
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self.get_all_users()
        for user in users:
            if user.get("user_id") == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        users = self.get_all_users()
        for user in users:
            if user.get("username") == username:
                return user
        return None
    
    def add_user(self, user_data: Dict) -> Dict:
        """Add new user"""
        users = self.get_all_users()
        if not user_data.get("user_id"):
            user_data["user_id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.now().isoformat()
        users.append(user_data)
        self._save_data(self.files["users"], users)
        return user_data
    
    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update user"""
        users = self.get_all_users()
        for i, user in enumerate(users):
            if user.get("user_id") == user_id:
                users[i].update(updates)
                self._save_data(self.files["users"], users)
                return users[i]
        return None
    
    # ==================== SAMPLE DATA ====================
    
    def _initialize_sample_data(self):
        """Initialize with sample data for testing"""
        students = self.get_all_students()
        results = self.get_all_results()
        users = self.get_all_users()
        
        # Add sample students if empty
        if not students:
            sample_students = [
                {
                    "index_number": "2024-OL-123456",
                    "full_name": "Kamal Perera",
                    "name_with_initials": "K. Perera",
                    "nic_number": "200512345678",
                    "date_of_birth": "2005-03-15",
                    "gender": "Male",
                    "school_name": "Royal College, Colombo",
                    "school_code": "RC001",
                    "district": "Colombo",
                    "province": "Western",
                    "medium": "Sinhala"
                },
                {
                    "index_number": "2024-OL-123457",
                    "full_name": "Nimal Silva",
                    "name_with_initials": "N. Silva",
                    "nic_number": "200534567890",
                    "date_of_birth": "2005-07-22",
                    "gender": "Male",
                    "school_name": "Ananda College, Colombo",
                    "school_code": "AC001",
                    "district": "Colombo",
                    "province": "Western",
                    "medium": "Sinhala"
                },
                {
                    "index_number": "2023-AL-789012",
                    "full_name": "Sanduni Fernando",
                    "name_with_initials": "S. Fernando",
                    "nic_number": "200312345123",
                    "date_of_birth": "2003-11-08",
                    "gender": "Female",
                    "school_name": "Visakha Vidyalaya, Colombo",
                    "school_code": "VV001",
                    "district": "Colombo",
                    "province": "Western",
                    "medium": "Sinhala"
                }
            ]
            for student in sample_students:
                self.add_student(student)
        
        # Add sample results if empty
        if not results:
            sample_results = [
                {
                    "result_id": "RES-2024-OL-001",
                    "index_number": "2024-OL-123456",
                    "exam_type": "OL",
                    "exam_year": 2024,
                    "subjects": [
                        {"subject_code": "01", "subject_name": "Buddhism", "grade": "A"},
                        {"subject_code": "02", "subject_name": "Sinhala Language & Literature", "grade": "A"},
                        {"subject_code": "03", "subject_name": "English", "grade": "B"},
                        {"subject_code": "04", "subject_name": "History", "grade": "A"},
                        {"subject_code": "05", "subject_name": "Mathematics", "grade": "A"},
                        {"subject_code": "06", "subject_name": "Science", "grade": "A"},
                        {"subject_code": "07", "subject_name": "Geography", "grade": "B"},
                        {"subject_code": "08", "subject_name": "Civics", "grade": "A"},
                        {"subject_code": "09", "subject_name": "Information & Communication Technology", "grade": "A"}
                    ],
                    "status": "pending",
                    "attempt_number": 1,
                    "is_private_candidate": False
                },
                {
                    "result_id": "RES-2024-OL-002",
                    "index_number": "2024-OL-123457",
                    "exam_type": "OL",
                    "exam_year": 2024,
                    "subjects": [
                        {"subject_code": "01", "subject_name": "Buddhism", "grade": "B"},
                        {"subject_code": "02", "subject_name": "Sinhala Language & Literature", "grade": "B"},
                        {"subject_code": "03", "subject_name": "English", "grade": "C"},
                        {"subject_code": "04", "subject_name": "History", "grade": "B"},
                        {"subject_code": "05", "subject_name": "Mathematics", "grade": "A"},
                        {"subject_code": "06", "subject_name": "Science", "grade": "B"},
                        {"subject_code": "07", "subject_name": "Commerce", "grade": "A"},
                        {"subject_code": "08", "subject_name": "Accounting", "grade": "A"},
                        {"subject_code": "09", "subject_name": "Information & Communication Technology", "grade": "B"}
                    ],
                    "status": "pending",
                    "attempt_number": 1,
                    "is_private_candidate": False
                },
                {
                    "result_id": "RES-2023-AL-001",
                    "index_number": "2023-AL-789012",
                    "exam_type": "AL",
                    "exam_year": 2023,
                    "stream": "Biological Science",
                    "subjects": [
                        {"subject_code": "01", "subject_name": "Biology", "grade": "A"},
                        {"subject_code": "02", "subject_name": "Chemistry", "grade": "A"},
                        {"subject_code": "03", "subject_name": "Physics", "grade": "B"},
                        {"subject_code": "04", "subject_name": "General English", "grade": "B"}
                    ],
                    "status": "pending",
                    "attempt_number": 1,
                    "is_private_candidate": False,
                    "z_score": 1.8234,
                    "district_rank": 45,
                    "island_rank": 234
                }
            ]
            for result in sample_results:
                self.add_result(result)
        
        # Add default admin user if empty
        if not users:
            from app.models.user import User
            admin_password = User.hash_password("admin123")
            sample_users = [
                {
                    "user_id": "USR-001",
                    "username": "admin",
                    "email": "admin@doenets.lk",
                    "password_hash": admin_password,
                    "full_name": "System Administrator",
                    "role": "admin",
                    "designation": "System Administrator",
                    "department": "Department of Examinations",
                    "employee_id": "DOE-ADMIN-001",
                    "is_active": True
                },
                {
                    "user_id": "USR-002",
                    "username": "issuer",
                    "email": "issuer@doenets.lk",
                    "password_hash": User.hash_password("issuer123"),
                    "full_name": "Certificate Issuing Officer",
                    "role": "issuer",
                    "designation": "Senior Examinations Officer",
                    "department": "Department of Examinations",
                    "employee_id": "DOE-ISO-001",
                    "is_active": True
                }
            ]
            for user in sample_users:
                self.add_user(user)


# Global database instance
db = Database(data_dir=os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
