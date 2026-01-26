"""
Student Model - Stores student information
"""
from datetime import datetime


class Student:
    """Student data model for G.C.E exam candidates"""
    
    def __init__(
        self,
        index_number: str,
        full_name: str,
        name_with_initials: str,
        nic_number: str,
        date_of_birth: str,
        gender: str,
        school_name: str,
        school_code: str,
        district: str,
        province: str,
        medium: str = "Sinhala",  # Sinhala, Tamil, English
        created_at: str = None
    ):
        self.index_number = index_number
        self.full_name = full_name
        self.name_with_initials = name_with_initials
        self.nic_number = nic_number
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.school_name = school_name
        self.school_code = school_code
        self.district = district
        self.province = province
        self.medium = medium
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "index_number": self.index_number,
            "full_name": self.full_name,
            "name_with_initials": self.name_with_initials,
            "nic_number": self.nic_number,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "school_name": self.school_name,
            "school_code": self.school_code,
            "district": self.district,
            "province": self.province,
            "medium": self.medium,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


# Sri Lankan Districts
SL_DISTRICTS = [
    "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya",
    "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
    "Mullaitivu", "Vavuniya", "Trincomalee", "Batticaloa", "Ampara",
    "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
    "Monaragala", "Ratnapura", "Kegalle"
]

# Sri Lankan Provinces
SL_PROVINCES = [
    "Western", "Central", "Southern", "Northern", "Eastern",
    "North Western", "North Central", "Uva", "Sabaragamuwa"
]
