#!/usr/bin/env python3
"""
Migration script to generate PNG images for existing certificates
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

# Check if pdf2image is available
try:
    from pdf2image import convert_from_bytes
    from io import BytesIO
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("WARNING: pdf2image not available. Cannot generate images.")

def generate_image_from_pdf(pdf_path, image_path):
    """Generate PNG image from PDF file and return hash"""
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Convert PDF to image (300 DPI for high quality)
    images = convert_from_bytes(pdf_bytes, dpi=300)
    
    if not images:
        return None
    
    # Get the first page (certificate is single page)
    img = images[0]
    
    # Save image to bytes for hashing
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG', optimize=True)
    img_bytes = img_buffer.getvalue()
    img_buffer.close()
    
    # Calculate image hash
    image_hash = hashlib.sha256(img_bytes).hexdigest()
    
    # Save image to file
    with open(image_path, 'wb') as f:
        f.write(img_bytes)
    
    return image_hash

def generate_images_for_existing_certificates():
    """Generate PNG images for certificates that don't have them"""
    if not PDF2IMAGE_AVAILABLE:
        print("❌ Cannot proceed without pdf2image")
        return
    
    with app.app_context():
        print("=" * 60)
        print("Generating Images for Existing Certificates")
        print("=" * 60)
        
        # Find certificates without images
        certificates = Certificate.query.filter(
            (Certificate.image_hash == None) | (Certificate.image_hash == '')
        ).all()
        
        total = len(certificates)
        print(f"\nFound {total} certificates without images")
        
        if total == 0:
            print("Nothing to do!")
            return
        
        success_count = 0
        error_count = 0
        
        for i, cert in enumerate(certificates, 1):
            print(f"\n[{i}/{total}] Processing {cert.certificate_id}...")
            
            try:
                # Check if PDF exists
                if not cert.pdf_path:
                    print(f"   ⚠ No PDF path set, skipping")
                    error_count += 1
                    continue
                
                if not os.path.exists(cert.pdf_path):
                    print(f"   ⚠ PDF file not found at {cert.pdf_path}, skipping")
                    error_count += 1
                    continue
                
                # Generate image path (same as PDF but with .png extension)
                image_path = cert.pdf_path.replace('.pdf', '.png')
                
                # Generate image from PDF
                image_hash = generate_image_from_pdf(cert.pdf_path, image_path)
                
                if image_hash and os.path.exists(image_path):
                    # Update database
                    cert.image_hash = image_hash
                    cert.image_path = image_path
                    db.session.commit()
                    
                    print(f"   ✓ Generated: {image_path}")
                    print(f"   ✓ Hash: {image_hash[:20]}...")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to generate image")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                error_count += 1
                db.session.rollback()
        
        print("\n" + "=" * 60)
        print(f"Migration Complete!")
        print(f"  ✓ Success: {success_count}")
        print(f"  ✗ Errors: {error_count}")
        print("=" * 60)

if __name__ == '__main__':
    generate_images_for_existing_certificates()
