"""
Exam Result Model - Stores G.C.E O/L and A/L examination results
"""
from datetime import datetime
from typing import List, Dict
from enum import Enum


class ExamType(Enum):
    OL = "G.C.E. Ordinary Level"
    AL = "G.C.E. Advanced Level"


class Grade(Enum):
    """Sri Lankan G.C.E Grading System"""
    A = "A"      # 75-100
    B = "B"      # 65-74
    C = "C"      # 55-64
    S = "S"      # 35-54 (Satisfactory/Simple Pass)
    W = "W"      # Below 35 (Weak/Fail)
    AB = "Ab"    # Absent


class Subject:
    """Subject with grade for G.C.E exams"""
    
    # O/L Subjects
    OL_SUBJECTS = [
        "Mathematics", "Science", "English", "Sinhala", "Tamil",
        "History", "Geography", "Civics", "Health Science",
        "Buddhism", "Hinduism", "Christianity", "Islam",
        "Commerce", "Accounting", "Information & Communication Technology",
        "Art", "Music", "Dancing", "Drama & Theatre",
        "Agriculture", "Home Economics", "Health & Physical Education"
    ]
    
    # A/L Subject Streams
    AL_STREAMS = {
        "Physical Science": ["Combined Mathematics", "Physics", "Chemistry"],
        "Biological Science": ["Biology", "Physics", "Chemistry"],
        "Commerce": ["Accounting", "Business Studies", "Economics"],
        "Arts": ["Political Science", "Geography", "History", "Economics", "Logic"],
        "Technology": ["Engineering Technology", "Bio Systems Technology", "Science for Technology"],
    }
    
    AL_COMMON_SUBJECTS = ["General English", "Common General Test"]
    
    def __init__(self, subject_code: str, subject_name: str, grade: str):
        self.subject_code = subject_code
        self.subject_name = subject_name
        self.grade = grade
    
    def to_dict(self):
        return {
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "grade": self.grade
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class ExamResult:
    """G.C.E Examination Result"""
    
    def __init__(
        self,
        result_id: str,
        index_number: str,
        exam_type: str,  # "OL" or "AL"
        exam_year: int,
        subjects: List[Dict],
        attempt_number: int = 1,
        is_private_candidate: bool = False,
        status: str = "pending",  # pending, certified, issued
        z_score: float = None,  # For A/L only
        district_rank: int = None,  # For A/L only
        island_rank: int = None,  # For A/L only
        stream: str = None,  # For A/L only (Physical Science, Bio Science, Commerce, Arts, Technology)
        created_at: str = None,
        certified_at: str = None,
        certified_by: str = None
    ):
        self.result_id = result_id
        self.index_number = index_number
        self.exam_type = exam_type
        self.exam_year = exam_year
        self.subjects = [Subject.from_dict(s) if isinstance(s, dict) else s for s in subjects]
        self.attempt_number = attempt_number
        self.is_private_candidate = is_private_candidate
        self.status = status
        self.z_score = z_score
        self.district_rank = district_rank
        self.island_rank = island_rank
        self.stream = stream
        self.created_at = created_at or datetime.now().isoformat()
        self.certified_at = certified_at
        self.certified_by = certified_by
    
    def calculate_passes(self) -> int:
        """Count number of passes (A, B, C, S grades)"""
        passing_grades = ['A', 'B', 'C', 'S']
        return sum(1 for s in self.subjects if s.grade in passing_grades)
    
    def has_minimum_qualification(self) -> bool:
        """Check if student has minimum qualification"""
        if self.exam_type == "OL":
            # Minimum 6 passes including Maths, Language, and pass in all subjects
            return self.calculate_passes() >= 6
        elif self.exam_type == "AL":
            # Minimum 3 passes in stream subjects
            stream_passes = sum(1 for s in self.subjects if s.grade in ['A', 'B', 'C', 'S'])
            return stream_passes >= 3
        return False
    
    def to_dict(self):
        return {
            "result_id": self.result_id,
            "index_number": self.index_number,
            "exam_type": self.exam_type,
            "exam_year": self.exam_year,
            "subjects": [s.to_dict() for s in self.subjects],
            "attempt_number": self.attempt_number,
            "is_private_candidate": self.is_private_candidate,
            "status": self.status,
            "z_score": self.z_score,
            "district_rank": self.district_rank,
            "island_rank": self.island_rank,
            "stream": self.stream,
            "created_at": self.created_at,
            "certified_at": self.certified_at,
            "certified_by": self.certified_by,
            "passes": self.calculate_passes(),
            "qualified": self.has_minimum_qualification()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
