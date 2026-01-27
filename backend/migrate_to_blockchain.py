#!/usr/bin/env python3
"""
Migration Script: Register existing database certificates on blockchain

This script reads all certificates from the database and registers them
on the blockchain for verification purposes.

Usage:
    docker exec -it doc-verify-backend python migrate_to_blockchain.py
"""

import os
import sys
import hashlib
import json
import time

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app.services.database import db, DatabaseService
from app.services.blockchain_service import get_blockchain_service


def create_app():
    """Create Flask app for database context"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://doc_user:doc_password@db:5432/doc_verify_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file"""
    if not os.path.exists(filepath):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_results_hash(results):
    """Calculate hash of exam results for integrity verification"""
    if not results:
        return hashlib.sha256(b"").hexdigest()
    
    # Sort and serialize results consistently
    sorted_results = sorted(results, key=lambda x: x.get('subject_code', ''))
    results_string = json.dumps(sorted_results, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(results_string.encode()).hexdigest()


def migrate_certificates():
    """Main migration function"""
    print("=" * 60)
    print("Certificate Migration to Blockchain")
    print("=" * 60)
    
    # Initialize Flask app and services
    app = create_app()
    
    with app.app_context():
        db_service = DatabaseService(db)
        blockchain = get_blockchain_service()
        
        if not blockchain:
            print("ERROR: Could not connect to blockchain service")
            return False
        
        print(f"\n✓ Connected to blockchain at: {blockchain.w3.provider.endpoint_uri}")
        print(f"✓ Contract address: {blockchain.contract_address}")
        
        # Get all certificates from database
        certificates = db_service.get_all_certificates()
        print(f"\n📋 Found {len(certificates)} certificates in database")
        
        if not certificates:
            print("No certificates to migrate.")
            return True
        
        # Track results
        successful = 0
        failed = 0
        skipped = 0
        
        for i, cert in enumerate(certificates, 1):
            cert_id = cert.get('certificate_id', 'Unknown')
            verification_code = cert.get('verification_code', '')
            index_number = cert.get('index_number', '')
            exam_type = cert.get('exam_type', 'OL')
            exam_year = cert.get('exam_year', 2024)
            pdf_path = cert.get('pdf_path', '')
            
            print(f"\n[{i}/{len(certificates)}] Processing: {verification_code}")
            print(f"    Index: {index_number}, Type: {exam_type}, Year: {exam_year}")
            
            # Check if already on blockchain
            try:
                existing = blockchain.verify_by_code(verification_code)
                if existing.get('exists'):
                    print(f"    ⏭️  Already on blockchain - skipping")
                    skipped += 1
                    continue
            except Exception as e:
                print(f"    ⚠️  Could not check blockchain: {e}")
            
            # Get document hash
            document_hash = cert.get('document_hash')
            
            # If no hash stored, try to calculate from PDF
            if not document_hash and pdf_path:
                # Try different path combinations
                possible_paths = [
                    pdf_path,
                    os.path.join('/app/certificates', os.path.basename(pdf_path)),
                    os.path.join('certificates', os.path.basename(pdf_path)),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        document_hash = calculate_file_hash(path)
                        print(f"    📄 Calculated hash from: {path}")
                        break
            
            if not document_hash:
                # Generate a hash from certificate data if no file
                cert_string = f"{verification_code}|{index_number}|{exam_type}|{exam_year}"
                document_hash = hashlib.sha256(cert_string.encode()).hexdigest()
                print(f"    ⚠️  No PDF found, using generated hash")
            
            # Get result data for results hash
            result_id = cert.get('result_id')
            results_hash = ""
            
            if result_id:
                result = db_service.get_result(result_id)
                if result and result.get('subjects'):
                    results_hash = calculate_results_hash(result.get('subjects', []))
                    print(f"    📊 Results hash calculated from {len(result.get('subjects', []))} subjects")
            
            if not results_hash:
                results_hash = hashlib.sha256(b"").hexdigest()
            
            # Get student info for additional data
            student_name = ""
            school_name = ""
            
            if result_id:
                result = db_service.get_result(result_id)
                if result and result.get('student'):
                    student = result.get('student', {})
                    student_name = student.get('full_name', '')
                    school_name = student.get('school_name', '')
            
            # Register on blockchain
            try:
                # Convert exam type to expected format (OL -> O/L, AL -> A/L)
                doc_type = exam_type
                if exam_type == 'OL':
                    doc_type = 'O/L'
                elif exam_type == 'AL':
                    doc_type = 'A/L'
                
                result = blockchain.register_document(
                    document_hash=document_hash,
                    results_hash=results_hash,
                    verification_code=verification_code,
                    student_info_hash=hashlib.sha256(student_name.encode()).hexdigest() if student_name else "",
                    owner_address="0x0000000000000000000000000000000000000000",
                    document_type=doc_type,
                    student_index=index_number,
                    exam_year=int(exam_year) if exam_year else 2024,
                    exam_subject=""
                )
                
                if result.get('success'):
                    print(f"    ✅ Registered on blockchain!")
                    print(f"       TX: {result.get('transaction_hash', 'N/A')[:20]}...")
                    successful += 1
                else:
                    print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                    failed += 1
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                failed += 1
            
            # Small delay to avoid overwhelming the blockchain node
            time.sleep(0.5)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print(f"  ✅ Successful: {successful}")
        print(f"  ⏭️  Skipped:    {skipped}")
        print(f"  ❌ Failed:     {failed}")
        print(f"  📋 Total:      {len(certificates)}")
        print("=" * 60)
        
        return failed == 0


if __name__ == "__main__":
    try:
        success = migrate_certificates()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
