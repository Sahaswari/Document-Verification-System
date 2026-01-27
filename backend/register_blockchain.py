"""
Register existing certificates on the blockchain
Run this script after the smart contract has been deployed
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services.database import db, Certificate, ExamResult, Student
from app.services.blockchain_utils import (
    calculate_document_hash, 
    calculate_results_hash, 
    calculate_student_info_hash
)

def register_all_certificates():
    """Register all existing certificates on the blockchain"""
    with app.app_context():
        try:
            from app.services.blockchain_service import get_blockchain_service
            blockchain = get_blockchain_service()
            print(f"✅ Connected to blockchain at {blockchain.provider_url}")
            print(f"📍 Contract address: {blockchain.contract_address}")
        except Exception as e:
            print(f"❌ Failed to connect to blockchain: {e}")
            return
        
        # Get all certificates with their related data
        certificates = Certificate.query.all()
        print(f"\n📋 Found {len(certificates)} certificates to register\n")
        
        registered = 0
        failed = 0
        
        for cert in certificates:
            try:
                # Get related result and student
                result = ExamResult.query.filter_by(result_id=cert.result_id).first()
                student = Student.query.filter_by(index_number=cert.index_number).first()
                
                if not result or not student:
                    print(f"⚠️  Missing data for {cert.certificate_id}")
                    failed += 1
                    continue
                
                # Calculate hashes
                cert_data = {
                    'certificate_id': cert.certificate_id,
                    'result_id': cert.result_id,
                    'index_number': cert.index_number,
                    'verification_code': cert.verification_code
                }
                document_hash = calculate_document_hash(cert_data)
                results_hash = calculate_results_hash(result.subjects)
                
                student_info = {
                    'name': student.full_name,
                    'nic': student.nic_number,
                    'dob': student.date_of_birth.isoformat() if student.date_of_birth else None,
                    'school': student.school_name
                }
                student_info_hash = calculate_student_info_hash(student_info)
                
                # Format document type
                doc_type = "O/L" if cert.exam_type == "OL" else "A/L"
                
                # Register on blockchain
                tx_result = blockchain.register_document(
                    document_hash=document_hash,
                    results_hash=results_hash,
                    verification_code=cert.verification_code,
                    student_info_hash=student_info_hash,
                    owner_address='0x0000000000000000000000000000000000000000',
                    document_type=doc_type,
                    student_index=cert.index_number,
                    exam_year=cert.exam_year,
                    exam_subject=result.stream or 'General'
                )
                
                if tx_result.get('success'):
                    # Update certificate with blockchain tx hash
                    cert.blockchain_tx_hash = tx_result['transaction_hash']
                    cert.document_hash = document_hash
                    db.session.commit()
                    
                    print(f"✓ {cert.certificate_id} | {cert.verification_code} | Block #{tx_result['block_number']}")
                    registered += 1
                else:
                    print(f"✗ {cert.certificate_id} - {tx_result.get('error')}")
                    failed += 1
                    
            except Exception as e:
                print(f"✗ {cert.certificate_id} - Error: {e}")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Registration Complete:")
        print(f"   ✓ Registered: {registered}")
        print(f"   ✗ Failed: {failed}")
        
        # Get blockchain statistics
        stats = blockchain.get_statistics()
        print(f"\n🔗 Blockchain Statistics:")
        print(f"   Total Certificates: {stats.get('total_certificates', 0)}")
        print(f"   Active: {stats.get('active_certificates', 0)}")
        print(f"   Revoked: {stats.get('revoked_certificates', 0)}")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    register_all_certificates()
