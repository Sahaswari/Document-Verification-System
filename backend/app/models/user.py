"""
User Model - System users (Issuing officers and admins)
"""
from datetime import datetime
import hashlib
import secrets


class User:
    """Department of Examinations staff user"""
    
    ROLES = {
        "admin": "System Administrator",
        "issuer": "Certificate Issuing Officer",
        "verifier": "Certificate Verification Officer",
        "data_entry": "Data Entry Operator"
    }
    
    DESIGNATIONS = [
        "Commissioner of Examinations",
        "Deputy Commissioner of Examinations", 
        "Assistant Commissioner of Examinations",
        "Senior Examinations Officer",
        "Examinations Officer",
        "Administrative Officer",
        "Data Entry Operator"
    ]
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        password_hash: str = None,
        full_name: str = None,
        role: str = "verifier",
        designation: str = None,
        department: str = "Department of Examinations",
        employee_id: str = None,
        is_active: bool = True,
        created_at: str = None,
        last_login: str = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.designation = designation
        self.department = department
        self.employee_id = employee_id
        self.is_active = is_active
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{pwd_hash}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return pwd_hash == stored_hash
        except:
            return False
    
    def can_issue_certificates(self) -> bool:
        """Check if user has certificate issuing permission"""
        return self.role in ["admin", "issuer"]
    
    def can_verify_certificates(self) -> bool:
        """Check if user has certificate verification permission"""
        return self.role in ["admin", "issuer", "verifier"]
    
    def to_dict(self, include_sensitive: bool = False):
        data = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "role_description": self.ROLES.get(self.role, "Unknown"),
            "designation": self.designation,
            "department": self.department,
            "employee_id": self.employee_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
