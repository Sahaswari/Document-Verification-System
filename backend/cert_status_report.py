#!/usr/bin/env python
"""Generate a report of which certificates can be verified via file upload"""
import sys
import os
import hashlib
sys.path.insert(0, '/app')
os.chdir('/app')

from app.main import app, db_service as db
from app.services.blockchain_service import BlockchainService

blockchain = BlockchainService()

print("=" * 70)
print("CERTIFICATE VERIFICATION STATUS REPORT")
print("=" * 70)

with app.app_context():
    certs = db.get_all_certificates()
    
    working = []
    broken = []
    no_pdf = []
    
    for cert in certs:
        idx = cert['index_number']
        exam_type = cert['exam_type']
        exam_year = cert['exam_year']
        pdf_path = f'/app/certificates/GCE_{exam_type}_{exam_year}_{idx}.pdf'
        
        if not os.path.exists(pdf_path):
            no_pdf.append(idx)
            continue
        
        with open(pdf_path, 'rb') as f:
            pdf_hash = hashlib.sha256(f.read()).hexdigest()
        
        bc = blockchain.verify_by_code(cert['verification_code'])
        bc_hash = bc.get('document_hash')
        
        if pdf_hash == bc_hash:
            working.append(idx)
        else:
            broken.append(idx)
    
    print(f"\n✅ CERTIFICATES THAT WILL VERIFY CORRECTLY ({len(working)}):")
    print("-" * 70)
    for idx in working:
        print(f"  • {idx}")
    
    print(f"\n❌ CERTIFICATES WITH HASH MISMATCH ({len(broken)}):")
    print("-" * 70)
    for idx in broken:
        print(f"  • {idx}")
    
    print(f"\n⚠️  CERTIFICATES WITHOUT PDF FILE ({len(no_pdf)}):")
    print("-" * 70)
    for idx in no_pdf[:5]:
        print(f"  • {idx}")
    if len(no_pdf) > 5:
        print(f"  ... and {len(no_pdf) - 5} more")
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  • Total certificates: {len(certs)}")
    print(f"  • Will verify OK:     {len(working)}")
    print(f"  • Hash mismatch:      {len(broken)}")
    print(f"  • No PDF file:        {len(no_pdf)}")
    print("=" * 70)
    print("\nNOTE: Certificates without PDF files will have PDFs regenerated")
    print("when downloaded, which may result in hash mismatches.")
