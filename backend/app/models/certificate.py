"""
Certificate Model - Issued certificates with blockchain reference
"""
from datetime import datetime
import hashlib
import json


class Certificate:
    """Issued G.C.E Certificate with blockchain verification"""
    
    def __init__(
        self,
        certificate_id: str,
        result_id: str,
        index_number: str,
        exam_type: str,
        exam_year: int,
        document_hash: str = None,
        blockchain_tx_hash: str = None,
        ipfs_hash: str = None,
        pdf_path: str = None,
        issued_at: str = None,
        issued_by: str = None,
        issuer_designation: str = None,
        status: str = "pending",  # pending, issued, revoked
        revoked_at: str = None,
        revoked_by: str = None,
        revocation_reason: str = None
    ):
        self.certificate_id = certificate_id
        self.result_id = result_id
        self.index_number = index_number
        self.exam_type = exam_type
        self.exam_year = exam_year
        self.document_hash = document_hash
        self.blockchain_tx_hash = blockchain_tx_hash
        self.ipfs_hash = ipfs_hash
        self.pdf_path = pdf_path
        self.issued_at = issued_at or datetime.now().isoformat()
        self.issued_by = issued_by
        self.issuer_designation = issuer_designation
        self.status = status
        self.revoked_at = revoked_at
        self.revoked_by = revoked_by
        self.revocation_reason = revocation_reason
    
    def generate_document_hash(self, student_data: dict, result_data: dict) -> str:
        """Generate SHA-256 hash of certificate data"""
        certificate_data = {
            "certificate_id": self.certificate_id,
            "index_number": self.index_number,
            "exam_type": self.exam_type,
            "exam_year": self.exam_year,
            "student": student_data,
            "results": result_data,
            "issued_at": self.issued_at
        }
        data_string = json.dumps(certificate_data, sort_keys=True)
        self.document_hash = hashlib.sha256(data_string.encode()).hexdigest()
        return self.document_hash
    
    def get_verification_code(self) -> str:
        """Generate human-readable verification code"""
        # Format: DOE-{EXAM_TYPE}-{YEAR}-{INDEX}-{HASH_PREFIX}
        hash_prefix = self.document_hash[:8].upper() if self.document_hash else "PENDING"
        exam_code = "OL" if self.exam_type == "OL" else "AL"
        return f"DOE-{exam_code}-{self.exam_year}-{self.index_number}-{hash_prefix}"
    
    def to_dict(self):
        return {
            "certificate_id": self.certificate_id,
            "result_id": self.result_id,
            "index_number": self.index_number,
            "exam_type": self.exam_type,
            "exam_year": self.exam_year,
            "document_hash": self.document_hash,
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "ipfs_hash": self.ipfs_hash,
            "pdf_path": self.pdf_path,
            "issued_at": self.issued_at,
            "issued_by": self.issued_by,
            "issuer_designation": self.issuer_designation,
            "status": self.status,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "revocation_reason": self.revocation_reason,
            "verification_code": self.get_verification_code()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        # Remove computed fields
        data.pop('verification_code', None)
        return cls(**data)
