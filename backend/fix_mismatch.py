#!/usr/bin/env python
"""Fix mismatched certificate by re-registering with correct hash"""
import sys
import os
import hashlib
sys.path.insert(0, '/app')
os.chdir('/app')

from app.main import app, db_service as db
from app.services.blockchain_service import BlockchainService

blockchain = BlockchainService()

with app.app_context():
    certs = db.get_certificates_by_index('2023-OL-100010')
    cert = certs[0] if certs else None
    if cert:
        # Get the current PDF hash
        idx = cert.get('index_number')
        exam_type = cert.get('exam_type')
        exam_year = cert.get('exam_year')
        pdf_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{idx}.pdf'
        
        with open(pdf_path, 'rb') as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()
        
        print(f'Certificate: {idx}')
        print(f'Current PDF Hash: {current_hash}')
        db_hash = cert.get('document_hash')
        print(f'DB Hash: {db_hash}')
        
        # Get result data for results hash
        result = db.get_result(cert.get('result_id'))
        subjects = result.get('subjects', []) if result else []
        results_hash = blockchain.calculate_results_hash(subjects)
        
        verification_code = cert.get('verification_code')
        print(f'Results Hash: {results_hash}')
        print(f'Verification Code: {verification_code}')
        
        # Register with correct hash
        print('\nRe-registering on blockchain...')
        tx_hash = blockchain.register_document(
            document_hash=current_hash,
            results_hash=results_hash,
            verification_code=verification_code,
            student_info_hash=blockchain.calculate_student_info_hash({
                'index_number': idx,
                'exam_type': exam_type,
                'exam_year': exam_year
            }),
            owner_address='0x0000000000000000000000000000000000000000',
            document_type=exam_type,
            student_index=idx,
            exam_year=exam_year,
            exam_subject=''
        )
        print(f'Registered! TX Hash: {tx_hash}')
        
        # Verify it worked
        bc_result = blockchain.verify_by_code(verification_code)
        print(f'\nVerification check:')
        print(f'Blockchain hash: {bc_result.get("document_hash")}')
        print(f'Match: {bc_result.get("document_hash") == current_hash}')
