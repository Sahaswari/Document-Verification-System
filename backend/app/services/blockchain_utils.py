"""
Blockchain Certificate Registration Utility
Registers certificates on the blockchain during system initialization
"""
import json
import hashlib
from typing import Dict, List, Optional

def calculate_results_hash(subjects: list) -> str:
    """Calculate SHA-256 hash of exam results for integrity verification"""
    sorted_results = sorted(subjects, key=lambda x: x.get('subject_code', x.get('subject', '')))
    results_str = json.dumps(sorted_results, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(results_str.encode()).hexdigest()


def calculate_student_info_hash(student_info: dict) -> str:
    """Calculate SHA-256 hash of student personal info (for privacy)"""
    info_str = json.dumps(student_info, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(info_str.encode()).hexdigest()


def calculate_document_hash(cert_data: dict) -> str:
    """Calculate unique document hash from certificate data"""
    content = f"{cert_data['certificate_id']}{cert_data['result_id']}{cert_data['index_number']}{cert_data['verification_code']}"
    return hashlib.sha256(content.encode()).hexdigest()


def register_certificates_on_blockchain(certificates: List[Dict], results: List[Dict], students: List[Dict]):
    """
    Register certificates on the blockchain
    
    Args:
        certificates: List of certificate dictionaries
        results: List of exam result dictionaries  
        students: List of student dictionaries
    """
    try:
        from app.services.blockchain_service import get_blockchain_service
        blockchain = get_blockchain_service()
        print("\n📦 Registering certificates on blockchain...")
    except Exception as e:
        print(f"\n⚠️  Blockchain not available: {e}")
        print("   Certificates will be registered in database only.")
        print("   Run 'python register_blockchain.py' later to sync with blockchain.\n")
        return []
    
    # Create lookups
    results_by_id = {r['result_id']: r for r in results}
    students_by_index = {s['index_number']: s for s in students}
    
    registered = []
    failed = []
    
    for cert in certificates:
        try:
            # Get associated result and student
            result = results_by_id.get(cert['result_id'])
            student = students_by_index.get(cert['index_number'])
            
            if not result or not student:
                print(f"   ⚠️  Missing data for certificate {cert['certificate_id']}")
                continue
            
            # Calculate hashes
            document_hash = calculate_document_hash(cert)
            results_hash = calculate_results_hash(result.get('subjects', []))
            
            student_info = {
                'name': student.get('full_name'),
                'nic': student.get('nic_number'),
                'dob': student.get('date_of_birth'),
                'school': student.get('school_name')
            }
            student_info_hash = calculate_student_info_hash(student_info)
            
            # Register on blockchain
            tx_result = blockchain.register_document(
                document_hash=document_hash,
                results_hash=results_hash,
                verification_code=cert['verification_code'],
                student_info_hash=student_info_hash,
                owner_address='0x0000000000000000000000000000000000000000',
                document_type=cert['exam_type'].replace('OL', 'O/L').replace('AL', 'A/L'),
                student_index=cert['index_number'],
                exam_year=cert['exam_year'],
                exam_subject=result.get('stream', 'General')
            )
            
            if tx_result.get('success'):
                registered.append({
                    'certificate_id': cert['certificate_id'],
                    'verification_code': cert['verification_code'],
                    'document_hash': document_hash,
                    'results_hash': results_hash,
                    'tx_hash': tx_result['transaction_hash'],
                    'block': tx_result['block_number']
                })
                print(f"   ✓ Registered: {cert['certificate_id']} (Block #{tx_result['block_number']})")
            else:
                failed.append({
                    'certificate_id': cert['certificate_id'],
                    'error': tx_result.get('error')
                })
                print(f"   ✗ Failed: {cert['certificate_id']} - {tx_result.get('error')}")
                
        except Exception as e:
            failed.append({
                'certificate_id': cert.get('certificate_id'),
                'error': str(e)
            })
            print(f"   ✗ Error: {cert.get('certificate_id')} - {e}")
    
    print(f"\n   📊 Blockchain Registration Summary:")
    print(f"      ✓ Registered: {len(registered)}")
    print(f"      ✗ Failed: {len(failed)}")
    
    return registered


def verify_certificate_on_blockchain(verification_code: str = None, 
                                     student_index: str = None,
                                     document_hash: str = None) -> Dict:
    """
    Verify a certificate on the blockchain using any method
    
    Args:
        verification_code: Certificate verification code (Method 1)
        student_index: Student index number (Method 2)
        document_hash: Document hash (Method 3)
    
    Returns:
        Verification result dictionary
    """
    try:
        from app.services.blockchain_service import get_blockchain_service
        blockchain = get_blockchain_service()
    except Exception as e:
        return {'error': f'Blockchain not available: {e}'}
    
    if verification_code:
        return blockchain.verify_by_code(verification_code)
    elif student_index:
        return blockchain.verify_by_student_index(student_index)
    elif document_hash:
        return blockchain.verify_document(document_hash)
    else:
        return {'error': 'Must provide verification_code, student_index, or document_hash'}


def get_blockchain_statistics() -> Dict:
    """Get blockchain certificate statistics"""
    try:
        from app.services.blockchain_service import get_blockchain_service
        blockchain = get_blockchain_service()
        return blockchain.get_statistics()
    except Exception as e:
        return {'error': str(e)}
