"""
Blockchain Integration Module for Document Verification System
This module handles all interactions with the Ethereum smart contract

Best Practices Implemented:
- Privacy: Personal data stored as hashes, not plain text
- Gas Efficiency: Minimal storage, using hashes for large data  
- Security: Only authorized issuers can register/revoke
- Verifiability: Multiple lookup methods (hash, code, index)
- Integrity: Results hash ensures grade tampering detection
"""

import json
import hashlib
import os
from pathlib import Path
from web3 import Web3
from typing import Dict, Tuple, Optional


class BlockchainService:
    """
    Service class for interacting with the DocumentVerification smart contract
    Supports three verification methods:
    1. By Verification Code (Certificate ID)
    2. By Student Index Number
    3. By Document Hash (File Upload)
    """
    
    def __init__(self, provider_url: str = None, contract_address: str = None):
        """
        Initialize blockchain connection
        
        Args:
            provider_url: Ethereum node URL (default: http://localhost:8545)
            contract_address: Deployed contract address (auto-loaded if not provided)
        """
        # Connect to Ethereum node
        self.provider_url = provider_url or os.getenv('BLOCKCHAIN_URL', 'http://blockchain:8545')
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to blockchain at {self.provider_url}")
        
        print(f"✅ Connected to blockchain at {self.provider_url}")
        
        # Load contract data
        contract_data = self._load_contract_data()
        self.contract_address = contract_address or contract_data['address']
        self.contract_abi = contract_data['abi']
        
        # Initialize contract instance
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )
        
        # Set default account (for transactions)
        accounts = self.w3.eth.accounts
        if accounts:
            self.w3.eth.default_account = accounts[0]
            print(f"👤 Default account: {accounts[0]}")
        
        print(f"📍 Contract loaded at: {self.contract_address}")
    
    def _load_contract_data(self) -> Dict:
        """Load contract ABI and address from deployed JSON file"""
        contract_file = Path(__file__).parent.parent / 'contracts' / 'DocumentVerification.json'
        
        if not contract_file.exists():
            raise FileNotFoundError(
                f"Contract data not found at {contract_file}. "
                "Please deploy the contract first using: cd blockchain && npm run deploy"
            )
        
        with open(contract_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def calculate_document_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of a document file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def calculate_content_hash(content: bytes) -> str:
        """
        Calculate SHA-256 hash of document content
        
        Args:
            content: Document content as bytes
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def calculate_results_hash(results: list) -> str:
        """
        Calculate SHA-256 hash of exam results for integrity verification
        
        Args:
            results: List of subject results (e.g., [{"subject": "Mathematics", "grade": "A"}])
            
        Returns:
            Hexadecimal hash string
        """
        # Sort results by subject for consistent hashing
        sorted_results = sorted(results, key=lambda x: x.get('subject', ''))
        results_str = json.dumps(sorted_results, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(results_str.encode()).hexdigest()
    
    @staticmethod
    def calculate_student_info_hash(student_info: dict) -> str:
        """
        Calculate SHA-256 hash of student personal info (for privacy)
        
        Args:
            student_info: Dict with student details (name, DOB, etc.)
            
        Returns:
            Hexadecimal hash string
        """
        info_str = json.dumps(student_info, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(info_str.encode()).hexdigest()
    
    def register_document(
        self,
        document_hash: str,
        results_hash: str,
        verification_code: str,
        student_info_hash: str,
        owner_address: str,
        document_type: str,
        student_index: str,
        exam_year: int,
        exam_subject: str,
        issuer_private_key: Optional[str] = None
    ) -> Dict:
        """
        Register a certificate on the blockchain with all verification data
        
        Args:
            document_hash: SHA-256 hash of the certificate PDF
            results_hash: SHA-256 hash of exam results JSON
            verification_code: Human-readable verification code
            student_info_hash: Hash of student personal info
            owner_address: Student's Ethereum address (or zero address)
            document_type: "O/L" or "A/L"
            student_index: Student index number
            exam_year: Year of examination
            exam_subject: Subject/Stream
            issuer_private_key: Private key of issuer (optional)
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Use zero address if no owner provided
            if not owner_address or owner_address == '0x0':
                owner_address = '0x0000000000000000000000000000000000000000'
            
            # Build and send transaction
            tx_hash = self.contract.functions.registerDocument(
                document_hash,
                results_hash,
                verification_code,
                student_info_hash,
                Web3.to_checksum_address(owner_address),
                document_type,
                student_index,
                int(exam_year),
                exam_subject
            ).transact()
            
            # Wait for transaction confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed'],
                'document_hash': document_hash,
                'verification_code': verification_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_document(self, document_hash: str) -> Dict:
        """
        Verify a certificate by its document hash (Method 3: File Upload)
        
        Args:
            document_hash: SHA-256 hash of the certificate PDF
            
        Returns:
            Dictionary with verification results
        """
        try:
            result = self.contract.functions.verifyDocument(document_hash).call()
            
            # Unpack return values
            exists, is_valid, issuer, owner, timestamp, doc_type, verification_code, results_hash, student_index, exam_year = result
            
            if not exists:
                return {
                    'exists': False,
                    'message': 'Certificate not found on blockchain'
                }
            
            return {
                'exists': exists,
                'is_valid': is_valid,
                'issuer': issuer,
                'owner': owner,
                'timestamp': timestamp,
                'document_type': doc_type,
                'verification_code': verification_code,
                'results_hash': results_hash,
                'student_index': student_index,
                'exam_year': exam_year,
                'verified_on_blockchain': exists and is_valid
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def verify_by_code(self, verification_code: str) -> Dict:
        """
        Verify a certificate by verification code (Method 1: Certificate ID)
        
        Args:
            verification_code: Human-readable verification code (e.g., "DOE-OL2024-A1B2C3D4")
            
        Returns:
            Dictionary with verification results
        """
        try:
            result = self.contract.functions.verifyByCode(verification_code).call()
            
            # Unpack return values
            exists, is_valid, doc_hash, results_hash, doc_type, student_index, exam_year, exam_subject, timestamp, issuer = result
            
            if not exists:
                return {
                    'exists': False,
                    'message': f'No certificate found with code: {verification_code}'
                }
            
            return {
                'exists': exists,
                'is_valid': is_valid,
                'document_hash': doc_hash,
                'results_hash': results_hash,
                'document_type': doc_type,
                'student_index': student_index,
                'exam_year': exam_year,
                'exam_subject': exam_subject,
                'timestamp': timestamp,
                'issuer': issuer,
                'verification_code': verification_code,
                'verified_on_blockchain': exists and is_valid
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def verify_by_student_index(self, student_index: str) -> Dict:
        """
        Verify a certificate by student index (Method 2: Student Index)
        
        Args:
            student_index: Student index number (e.g., "2024-OL-001234")
            
        Returns:
            Dictionary with verification results including results hash
        """
        try:
            result = self.contract.functions.verifyByStudentIndex(student_index).call()
            
            # Unpack return values
            exists, is_valid, doc_hash, results_hash, verification_code, doc_type, exam_year, exam_subject, timestamp, cert_count = result
            
            if not exists:
                return {
                    'exists': False,
                    'message': f'No certificate found for student index: {student_index}'
                }
            
            return {
                'exists': exists,
                'is_valid': is_valid,
                'document_hash': doc_hash,
                'results_hash': results_hash,
                'verification_code': verification_code,
                'document_type': doc_type,
                'exam_year': exam_year,
                'exam_subject': exam_subject,
                'timestamp': timestamp,
                'student_index': student_index,
                'certificate_count': cert_count,
                'verified_on_blockchain': exists and is_valid
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def verify_results_integrity(self, document_hash: str, results: list) -> Dict:
        """
        Verify that exam results haven't been tampered with
        
        Args:
            document_hash: Document hash to look up
            results: List of results to verify against stored hash
            
        Returns:
            Dictionary with integrity verification result
        """
        try:
            # Calculate hash of provided results
            provided_hash = self.calculate_results_hash(results)
            
            # Call contract to compare
            result = self.contract.functions.verifyResultsIntegrity(document_hash, provided_hash).call()
            matches, stored_hash = result
            
            return {
                'integrity_valid': matches,
                'provided_hash': provided_hash,
                'stored_hash': stored_hash,
                'message': 'Results integrity verified - no tampering detected' if matches else 'WARNING: Results have been modified!'
            }
            
        except Exception as e:
            return {
                'integrity_valid': False,
                'error': str(e)
            }
    
    def get_student_certificates(self, student_index: str) -> list:
        """
        Get all certificates for a student
        
        Args:
            student_index: Student index number
            
        Returns:
            List of document hashes
        """
        try:
            return self.contract.functions.getStudentCertificates(student_index).call()
        except Exception as e:
            print(f"Error getting student certificates: {e}")
            return []
    
    def revoke_document(self, document_hash: str, reason: str = "Administrative revocation", issuer_private_key: Optional[str] = None) -> Dict:
        """
        Revoke a certificate
        
        Args:
            document_hash: SHA-256 hash of the certificate
            reason: Reason for revocation
            issuer_private_key: Private key of the issuer (optional)
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            tx_hash = self.contract.functions.revokeDocument(document_hash, reason).transact()
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get contract statistics"""
        try:
            total, revoked, active = self.contract.functions.getStatistics().call()
            return {
                'total_certificates': total,
                'revoked_certificates': revoked,
                'active_certificates': active
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_user_documents(self, user_address: str) -> list:
        """Get all documents owned by a user"""
        try:
            return self.contract.functions.getUserDocuments(
                Web3.to_checksum_address(user_address)
            ).call()
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    def get_account_balance(self, address: str = None) -> float:
        """Get ETH balance of an account"""
        address = address or self.w3.eth.default_account
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
        return float(self.w3.from_wei(balance_wei, 'ether'))


# Singleton instance
_blockchain_service = None

def get_blockchain_service() -> BlockchainService:
    """Get or create blockchain service singleton"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service
