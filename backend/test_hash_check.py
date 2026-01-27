#!/usr/bin/env python
"""Check if hashes match between database, blockchain, and actual PDF files"""
import sys
import os
import hashlib

# Add app to path
sys.path.insert(0, '/app')
os.chdir('/app')

# Use Flask app context
from app.main import app, db_service as db
from app.services.blockchain_service import BlockchainService

blockchain = BlockchainService()

with app.app_context():
    # Check first few certificates
    certs = db.get_all_certificates()[:5]
    print("=== Hash Verification Check ===\n")

    mismatch_count = 0
    for cert in certs:
        idx = cert.get('index_number', 'N/A')
        db_hash = cert.get('document_hash', 'N/A')
        
        # Get blockchain hash
        try:
            blockchain_result = blockchain.verify_by_code(cert['verification_code'])
            blockchain_hash = blockchain_result.get('document_hash', 'NOT FOUND')
        except Exception as e:
            blockchain_hash = f'ERROR: {e}'
        
        # Check if PDF exists and get its actual hash
        pdf_path = cert.get('pdf_path', '')
        actual_hash = 'NO FILE'
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
        
        db_match = db_hash == actual_hash
        bc_match = str(blockchain_hash) == actual_hash
        
        print(f'Certificate: {idx}')
        print(f'  DB Hash:         {db_hash[:50]}...')
        print(f'  Blockchain Hash: {str(blockchain_hash)[:50]}...')
        print(f'  Actual PDF Hash: {actual_hash[:50]}...')
        print(f'  DB==PDF: {db_match}, Blockchain==PDF: {bc_match}')
        
        if not bc_match:
            mismatch_count += 1
            print('  ⚠️ MISMATCH - This certificate would FAIL verification!')
        else:
            print('  ✅ OK')
        print()

    print(f"\nTotal certificates with mismatch: {mismatch_count} out of {len(certs)}")
