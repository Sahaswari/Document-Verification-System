#!/usr/bin/env python3
"""
Test script to verify image generation support for certificates
"""

import os
import sys
import hashlib

# Add parent directory to path
sys.path.insert(0, '/app')

from flask import Flask
from app.services.database import db, Certificate, Student, ExamResult
from app.services.pdf_generator import CertificatePDFGenerator

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://docverify:docverify123@db:5432/document_verification'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def test_image_generation():
    """Test that certificate images are generated alongside PDFs"""
    with app.app_context():
        print("=" * 60)
        print("Testing Image Generation Support")
        print("=" * 60)
        
        # Get a sample student with results
        student = Student.query.first()
        if not student:
            print("❌ No students found in database")
            return False
        
        print(f"✓ Found student: {student.full_name}")
        
        result = ExamResult.query.filter_by(student_id=student.id).first()
        if not result:
            print("❌ No exam results found for student")
            return False
        
        print(f"✓ Found exam result: {result.result_id}")
        
        # Get the subjects from JSON column
        subjects = []
        if result.subjects:
            for subject_data in result.subjects:
                if isinstance(subject_data, dict):
                    subjects.append(subject_data)
                else:
                    subjects.append({
                        'subject_name': str(subject_data),
                        'grade': 'N/A'
                    })
        
        # Create certificate data matching the function signature
        student_data = {
            'full_name': student.full_name,
            'index_number': student.index_number,
            'nic_number': student.nic_number,
            'date_of_birth': student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else None,
            'school_name': student.school_name
        }
        
        result_data = {
            'exam_type': result.exam_type,
            'exam_year': result.exam_year,
            'subjects': result.subjects,
            'stream': result.stream
        }
        
        certificate_data = {
            'certificate_id': 'TEST-IMG-001',
            'verification_code': 'TEST-VERIFY-IMG-001'
        }
        
        print(f"\nGenerating certificate with image support...")
        
        # Generate certificate
        generator = CertificatePDFGenerator()
        gen_result = generator.generate_certificate(student_data, result_data, certificate_data)
        
        if len(gen_result) == 5:
            pdf_bytes, document_hash, pdf_path, image_hash, image_path = gen_result
            print(f"\n✅ Image generation supported!")
            print(f"   PDF Path: {pdf_path}")
            print(f"   PDF Hash: {document_hash[:20]}...")
            print(f"   Image Path: {image_path}")
            print(f"   Image Hash: {image_hash[:20] if image_hash else 'N/A'}...")
            
            # Check if files exist
            if pdf_path and os.path.exists(pdf_path):
                print(f"   ✓ PDF file exists ({os.path.getsize(pdf_path)} bytes)")
            else:
                print(f"   ❌ PDF file does not exist")
            
            if image_path and os.path.exists(image_path):
                print(f"   ✓ Image file exists ({os.path.getsize(image_path)} bytes)")
                
                # Verify image hash
                with open(image_path, 'rb') as f:
                    calculated_hash = hashlib.sha256(f.read()).hexdigest()
                if calculated_hash == image_hash:
                    print(f"   ✓ Image hash verified")
                else:
                    print(f"   ❌ Image hash mismatch!")
            else:
                print(f"   ⚠ Image file does not exist (pdf2image may not be available)")
            
            return True
        else:
            print(f"❌ Unexpected return value count: {len(result_data)}")
            return False

def check_existing_certificates():
    """Check image status of existing certificates"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("Existing Certificate Image Status")
        print("=" * 60)
        
        certificates = Certificate.query.limit(10).all()
        
        with_image = 0
        without_image = 0
        
        for cert in certificates:
            if cert.image_hash and cert.image_path:
                with_image += 1
                status = "✓"
            else:
                without_image += 1
                status = "✗"
            
            print(f"  {status} {cert.certificate_id}: image_hash={'Yes' if cert.image_hash else 'No'}, image_path={'Yes' if cert.image_path else 'No'}")
        
        print(f"\nTotal: {with_image} with images, {without_image} without images")

def check_pdf2image():
    """Check if pdf2image is available"""
    print("\n" + "=" * 60)
    print("Checking pdf2image availability")
    print("=" * 60)
    
    try:
        from pdf2image import convert_from_bytes
        print("✓ pdf2image is installed")
        
        # Check if poppler is available
        import subprocess
        result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True)
        if result.returncode == 0 or 'pdftoppm' in result.stderr:
            print("✓ poppler-utils is installed")
            return True
        else:
            print("❌ poppler-utils is NOT installed")
            return False
    except ImportError:
        print("❌ pdf2image is NOT installed")
        return False
    except FileNotFoundError:
        print("❌ poppler-utils (pdftoppm) is NOT installed")
        return False

if __name__ == '__main__':
    # Check dependencies
    pdf2image_available = check_pdf2image()
    
    # Test image generation
    test_image_generation()
    
    # Check existing certificates
    check_existing_certificates()
