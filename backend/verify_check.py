#!/usr/bin/env python
"""Check all certificates to see which would verify successfully"""
import sys
import os
import hashlib
sys.path.insert(0, '/app')
os.chdir('/app')

from app.main import app, db_service as db
from app.services.blockchain_service import BlockchainService

blockchain = BlockchainService()

with app.app_context():
    certs = db.get_all_certificates()
    print(f'Total certificates: {len(certs)}')
    
    verified = 0
    would_fail = 0
    no_pdf = 0
    
    for cert in certs:
        idx = cert['index_number']
        exam_type = cert['exam_type']
        exam_year = cert['exam_year']
        pdf_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{idx}.pdf'
        
        if not os.path.exists(pdf_path):
            no_pdf += 1
            continue
        
        # Get actual PDF hash
        with open(pdf_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Get blockchain hash
        bc = blockchain.verify_by_code(cert['verification_code'])
        bc_hash = bc.get('document_hash', 'N/A')
        
        if actual_hash == bc_hash:
            verified += 1
        else:
            would_fail += 1
            print(f'WOULD FAIL: {idx}')
            print(f'  PDF hash:        {actual_hash[:40]}...')
            bc_display = bc_hash[:40] if bc_hash != 'N/A' else 'N/A'
            print(f'  Blockchain hash: {bc_display}...')
    
    print()
    print(f'PDFs exist: {verified + would_fail}')
    print(f'No PDF: {no_pdf}')
    print(f'Would verify OK: {verified}')
    print(f'Would FAIL: {would_fail}')
