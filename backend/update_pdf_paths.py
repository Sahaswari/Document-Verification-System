#!/usr/bin/env python
"""Update pdf_path for all certificates where the PDF file exists"""
import sys
import os
sys.path.insert(0, '/app')
os.chdir('/app')

from app.main import app, db_service as db

with app.app_context():
    certs = db.get_all_certificates()
    updated = 0
    
    for cert in certs:
        if cert.get('pdf_path'):
            continue  # Already has path
            
        idx = cert.get('index_number')
        exam_type = cert.get('exam_type')
        exam_year = cert.get('exam_year')
        expected_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{idx}.pdf'
        
        if os.path.exists(expected_path):
            db.update_certificate(cert.get('certificate_id'), {
                'pdf_path': expected_path
            })
            updated += 1
            print(f'Updated: {idx} -> {expected_path}')
    
    print(f'\nTotal updated: {updated}')
