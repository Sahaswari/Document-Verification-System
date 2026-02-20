"""
Seed Data Generator for Document Verification System
Generates 100 students, 100 results, and sample certificates for testing
"""
import random
from datetime import datetime, date
from typing import List, Dict

# Sri Lankan Names Database
SINHALA_FIRST_NAMES_MALE = [
    "Kamal", "Nimal", "Sunil", "Amal", "Rohan", "Chaminda", "Asanka", "Lasith",
    "Mahela", "Kumar", "Dilshan", "Thisara", "Nuwan", "Dinesh", "Kasun", "Chamara",
    "Thilina", "Supun", "Hasitha", "Lakmal", "Ruwan", "Janaka", "Pradeep", "Sanjeewa",
    "Chathura", "Dimuthu", "Sachith", "Pathum", "Isuru", "Tharindu", "Malinda", "Ravindu"
]

SINHALA_FIRST_NAMES_FEMALE = [
    "Sanduni", "Kumari", "Nadeeka", "Chamari", "Dilini", "Sachini", "Hashini", "Thilini",
    "Nethmi", "Oshadi", "Kavindi", "Sewwandi", "Hansani", "Rashmi", "Tharushi", "Buddhini",
    "Shanika", "Nirasha", "Gayani", "Madhavi", "Chathurika", "Hiruni", "Pooja", "Sachitha",
    "Amaya", "Dulani", "Ishara", "Malsha", "Gimhani", "Shehani", "Lakshika", "Ruwanthi"
]

TAMIL_FIRST_NAMES_MALE = [
    "Kugan", "Thilan", "Rajan", "Mohan", "Arun", "Vijay", "Suren", "Gajan",
    "Karthik", "Pradeesh", "Dinesh", "Ramesh", "Suresh", "Ganesh", "Mahesh", "Naresh"
]

TAMIL_FIRST_NAMES_FEMALE = [
    "Priya", "Kavitha", "Lakshmi", "Saranya", "Deepika", "Nithya", "Pavithra", "Janani",
    "Dharshini", "Abinaya", "Ramya", "Sangeetha", "Anusha", "Divya", "Meena", "Shalini"
]

SINHALA_LAST_NAMES = [
    "Perera", "Silva", "Fernando", "Jayawardena", "Wickramasinghe", "Bandara", "Gunasekara",
    "Dissanayake", "Rathnayake", "Senaratne", "Wijesinghe", "Jayasuriya", "Karunaratne",
    "Liyanage", "Senanayake", "Amarasinghe", "Weerasinghe", "Herath", "Kumarasinghe",
    "Rajapaksha", "Gunawardena", "Samaraweera", "Tennakoon", "Ekanayake", "Abeywickrama"
]

TAMIL_LAST_NAMES = [
    "Rajendran", "Krishnan", "Subramaniam", "Shanmuganathan", "Selvarajah", "Nadarajah",
    "Sivarajah", "Balasubramaniam", "Rajaratnam", "Kandasamy", "Yogarajah", "Mahendran"
]

# Sri Lankan Schools by District
SCHOOLS_BY_DISTRICT = {
    "Colombo": [
        ("Royal College, Colombo", "RC001"),
        ("Ananda College, Colombo", "AC001"),
        ("Nalanda College, Colombo", "NC001"),
        ("Visakha Vidyalaya, Colombo", "VV001"),
        ("Devi Balika Vidyalaya, Colombo", "DBV001"),
        ("Methodist College, Colombo", "MC001"),
        ("St. Joseph's College, Colombo", "SJC001"),
        ("St. Peter's College, Colombo", "SPC001"),
        ("Isipathana College, Colombo", "IC001"),
        ("Thurstan College, Colombo", "TC001"),
    ],
    "Gampaha": [
        ("St. Anne's College, Kurunegala", "SAC001"),
        ("Bandaranayake College, Gampaha", "BCG001"),
        ("Taxila Central College, Horana", "TCC001"),
        ("St. Sebastian's College, Moratuwa", "SSC001"),
        ("Gurukula College, Kelaniya", "GCK001"),
    ],
    "Kandy": [
        ("Trinity College, Kandy", "TCK001"),
        ("Dharmaraja College, Kandy", "DCK001"),
        ("Kingswood College, Kandy", "KCK001"),
        ("Mahamaya Girls' College, Kandy", "MGC001"),
        ("Girls' High School, Kandy", "GHS001"),
    ],
    "Galle": [
        ("Richmond College, Galle", "RCG001"),
        ("Mahinda College, Galle", "MCG001"),
        ("Southlands College, Galle", "SCG001"),
        ("Sanghamitta Balika Vidyalaya, Galle", "SBV001"),
    ],
    "Matara": [
        ("Rahula College, Matara", "RCM001"),
        ("Sujatha Vidyalaya, Matara", "SVM001"),
        ("St. Thomas' College, Matara", "STC001"),
    ],
    "Jaffna": [
        ("Jaffna Hindu College", "JHC001"),
        ("St. John's College, Jaffna", "SJJ001"),
        ("Chundikuli Girls' College, Jaffna", "CGC001"),
        ("Jaffna Central College", "JCC001"),
    ],
    "Kurunegala": [
        ("Maliyadeva College, Kurunegala", "MCK001"),
        ("St. Anne's College, Kurunegala", "SACK001"),
        ("Wayamba Royal College", "WRC001"),
    ],
    "Ratnapura": [
        ("Sivali Central College, Ratnapura", "SCCR001"),
        ("St. Aloysius College, Ratnapura", "SACR001"),
    ],
    "Badulla": [
        ("Badulla Central College", "BCC001"),
        ("St. Joseph's College, Badulla", "SJCB001"),
    ],
    "Anuradhapura": [
        ("Central College, Anuradhapura", "CCA001"),
        ("Swarnamali Girls' College", "SGC001"),
    ],
}

DISTRICTS_BY_PROVINCE = {
    "Western": ["Colombo", "Gampaha", "Kalutara"],
    "Central": ["Kandy", "Matale", "Nuwara Eliya"],
    "Southern": ["Galle", "Matara", "Hambantota"],
    "Northern": ["Jaffna", "Kilinochchi", "Mannar", "Mullaitivu", "Vavuniya"],
    "Eastern": ["Ampara", "Batticaloa", "Trincomalee"],
    "North Western": ["Kurunegala", "Puttalam"],
    "North Central": ["Anuradhapura", "Polonnaruwa"],
    "Uva": ["Badulla", "Monaragala"],
    "Sabaragamuwa": ["Ratnapura", "Kegalle"],
}

# O/L Subjects
OL_SUBJECTS = [
    ("01", "Buddhism"),
    ("02", "Sinhala Language & Literature"),
    ("03", "English"),
    ("04", "History"),
    ("05", "Mathematics"),
    ("06", "Science"),
    ("07", "Geography"),
    ("08", "Civics"),
    ("09", "Health & Physical Education"),
    ("10", "Information & Communication Technology"),
    ("11", "Commerce"),
    ("12", "Accounting"),
    ("13", "Art"),
    ("14", "Music"),
    ("15", "Dancing"),
    ("16", "Drama"),
]

# A/L Streams and Subjects
AL_STREAMS = {
    "Physical Science": [
        ("01", "Combined Mathematics"),
        ("02", "Physics"),
        ("03", "Chemistry"),
    ],
    "Biological Science": [
        ("01", "Biology"),
        ("02", "Chemistry"),
        ("03", "Physics"),
    ],
    "Commerce": [
        ("01", "Accounting"),
        ("02", "Economics"),
        ("03", "Business Studies"),
    ],
    "Arts": [
        ("01", "Political Science"),
        ("02", "Geography"),
        ("03", "Economics"),
    ],
    "Technology": [
        ("01", "Engineering Technology"),
        ("02", "Science for Technology"),
        ("03", "Information & Communication Technology"),
    ],
}

GRADES = ["A", "B", "C", "S", "W"]
GRADE_WEIGHTS = [0.15, 0.25, 0.30, 0.20, 0.10]  # Distribution weights


def generate_nic(birth_year: int, gender: str) -> str:
    """Generate a realistic Sri Lankan NIC number"""
    # New NIC format: YYYYDDDNNNV (12 digits)
    year = str(birth_year)
    day_of_year = random.randint(1, 365)
    if gender == "Female":
        day_of_year += 500
    serial = random.randint(1000, 9999)
    return f"{year}{day_of_year:03d}{serial}"


def generate_date_of_birth(exam_type: str, exam_year: int) -> date:
    """Generate appropriate DOB based on exam type and year"""
    if exam_type == "OL":
        # O/L students are typically 15-16 years old
        birth_year = exam_year - random.randint(15, 17)
    else:
        # A/L students are typically 17-19 years old
        birth_year = exam_year - random.randint(17, 20)
    
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(birth_year, month, day)


def get_random_school(district: str):
    """Get a random school from the district, with fallback"""
    if district in SCHOOLS_BY_DISTRICT:
        return random.choice(SCHOOLS_BY_DISTRICT[district])
    # Fallback for districts without specific schools
    all_schools = []
    for schools in SCHOOLS_BY_DISTRICT.values():
        all_schools.extend(schools)
    return random.choice(all_schools)


def generate_ol_subjects() -> List[Dict]:
    """Generate O/L subject results (9 subjects)"""
    # Compulsory subjects (first 6)
    compulsory = OL_SUBJECTS[:6]
    # Optional subjects (pick 3 from the rest)
    optional = random.sample(OL_SUBJECTS[6:], 3)
    
    subjects = []
    for code, name in compulsory + optional:
        grade = random.choices(GRADES, weights=GRADE_WEIGHTS)[0]
        subjects.append({
            "subject_code": code,
            "subject_name": name,
            "grade": grade
        })
    return subjects


def generate_al_subjects(stream: str) -> List[Dict]:
    """Generate A/L subject results for a stream"""
    stream_subjects = AL_STREAMS.get(stream, AL_STREAMS["Physical Science"])
    
    subjects = []
    for code, name in stream_subjects:
        grade = random.choices(GRADES, weights=GRADE_WEIGHTS)[0]
        subjects.append({
            "subject_code": code,
            "subject_name": name,
            "grade": grade
        })
    
    # Add General English
    subjects.append({
        "subject_code": "04",
        "subject_name": "General English",
        "grade": random.choices(GRADES, weights=GRADE_WEIGHTS)[0]
    })
    
    return subjects


def generate_z_score() -> float:
    """Generate a realistic Z-score for A/L"""
    return round(random.uniform(-1.5, 2.5), 4)


def generate_students_and_results(count: int = 100) -> tuple:
    """Generate sample students and their exam results"""
    students = []
    results = []
    
    # Distribute between O/L and A/L
    ol_count = int(count * 0.6)  # 60% O/L
    al_count = count - ol_count  # 40% A/L
    
    exam_years = [2023, 2024, 2025]
    
    for i in range(count):
        # Determine exam type
        is_ol = i < ol_count
        exam_type = "OL" if is_ol else "AL"
        exam_year = random.choice(exam_years)
        
        # Generate gender
        gender = random.choice(["Male", "Female"])
        
        # Generate name based on ethnicity (80% Sinhala, 20% Tamil)
        is_sinhala = random.random() < 0.8
        
        if is_sinhala:
            if gender == "Male":
                first_name = random.choice(SINHALA_FIRST_NAMES_MALE)
            else:
                first_name = random.choice(SINHALA_FIRST_NAMES_FEMALE)
            last_name = random.choice(SINHALA_LAST_NAMES)
            medium = "Sinhala"
        else:
            if gender == "Male":
                first_name = random.choice(TAMIL_FIRST_NAMES_MALE)
            else:
                first_name = random.choice(TAMIL_FIRST_NAMES_FEMALE)
            last_name = random.choice(TAMIL_LAST_NAMES)
            medium = "Tamil"
        
        full_name = f"{first_name} {last_name}"
        name_with_initials = f"{first_name[0]}. {last_name}"
        
        # Generate DOB and NIC
        dob = generate_date_of_birth(exam_type, exam_year)
        nic = generate_nic(dob.year, gender)
        
        # Select district and province
        province = random.choice(list(DISTRICTS_BY_PROVINCE.keys()))
        district = random.choice(DISTRICTS_BY_PROVINCE[province])
        
        # Get school
        school_name, school_code = get_random_school(district)
        
        # Generate index number
        index_number = f"{exam_year}-{exam_type}-{100000 + i}"
        
        # Create student record
        student = {
            "index_number": index_number,
            "full_name": full_name,
            "full_name_sinhala": f"{first_name} {last_name}" if is_sinhala else None,
            "full_name_tamil": f"{first_name} {last_name}" if not is_sinhala else None,
            "name_with_initials": name_with_initials,
            "nic_number": nic,
            "date_of_birth": dob.isoformat(),
            "gender": gender,
            "school_name": school_name,
            "school_code": school_code,
            "district": district,
            "province": province,
            "medium": medium,
        }
        students.append(student)
        
        # Generate result
        result_id = f"RES-{exam_year}-{exam_type}-{1000 + i}"
        
        if is_ol:
            subjects = generate_ol_subjects()
            result = {
                "result_id": result_id,
                "index_number": index_number,
                "exam_type": "OL",
                "exam_year": exam_year,
                "subjects": subjects,
                "status": random.choice(["pending", "pending", "pending", "issued"]),  # 75% pending
                "attempt_number": random.randint(1, 2),
                "is_private_candidate": random.random() < 0.1,  # 10% private
            }
        else:
            stream = random.choice(list(AL_STREAMS.keys()))
            subjects = generate_al_subjects(stream)
            z_score = generate_z_score()
            
            result = {
                "result_id": result_id,
                "index_number": index_number,
                "exam_type": "AL",
                "exam_year": exam_year,
                "stream": stream,
                "subjects": subjects,
                "status": random.choice(["pending", "pending", "pending", "issued"]),
                "attempt_number": 1,
                "is_private_candidate": random.random() < 0.05,
                "z_score": z_score,
                "district_rank": random.randint(1, 500),
                "island_rank": random.randint(1, 5000),
            }
        
        results.append(result)
    
    return students, results


def generate_sample_certificates(results: List[Dict], issued_count: int = 10) -> List[Dict]:
    """Generate sample certificates for some issued results"""
    import hashlib
    import uuid
    
    # Get results that are marked as issued
    issued_results = [r for r in results if r.get("status") == "issued"][:issued_count]
    
    certificates = []
    for result in issued_results:
        cert_id = f"CERT-{result['exam_type']}-{result['exam_year']}-{uuid.uuid4().hex[:8].upper()}"
        verification_code = f"DOE-{result['exam_type']}{result['exam_year']}-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate document hash
        hash_content = f"{cert_id}{result['result_id']}{result['index_number']}"
        document_hash = hashlib.sha256(hash_content.encode()).hexdigest()
        
        cert = {
            "certificate_id": cert_id,
            "result_id": result["result_id"],
            "index_number": result["index_number"],
            "exam_type": result["exam_type"],
            "exam_year": result["exam_year"],
            "verification_code": verification_code,
            "document_hash": document_hash,
            "issued_by": "USR-002",  # Issuer user
            "status": "active",
        }
        certificates.append(cert)
    
    return certificates


def get_seed_data(student_count: int = 100) -> Dict:
    """Get all seed data for database initialization"""
    students, results = generate_students_and_results(student_count)
    certificates = generate_sample_certificates(results, issued_count=15)
    
    return {
        "students": students,
        "results": results,
        "certificates": certificates,
    }
