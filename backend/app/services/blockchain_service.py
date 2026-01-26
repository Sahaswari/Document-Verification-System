"""
Blockchain Integration Module for Document Verification System
This module handles all interactions with the Ethereum smart contract
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
        Calculate SHA-256 hash of a document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks for memory efficiency
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
    
    def register_document(
        self,
        document_hash: str,
        ipfs_hash: str,
        owner_address: str,
        document_type: str,
        issuer_private_key: Optional[str] = None
    ) -> Dict:
        """
        Register a document on the blockchain
        
        Args:
            document_hash: SHA-256 hash of the document
            ipfs_hash: IPFS hash where document metadata is stored
            owner_address: Ethereum address of the document owner (student)
            document_type: Type of document (e.g., "O/L", "A/L")
            issuer_private_key: Private key of issuer (optional, uses default account if not provided)
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Prepare transaction
            tx_params = {
                'from': self.w3.eth.default_account,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            }
            
            # Build transaction
            transaction = self.contract.functions.registerDocument(
                document_hash,
                ipfs_hash,
                Web3.to_checksum_address(owner_address),
                document_type
            ).build_transaction(tx_params)
            
            # Sign and send transaction
            if issuer_private_key:
                signed_txn = self.w3.eth.account.sign_transaction(transaction, issuer_private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                # Use default account (works with Hardhat local node)
                tx_hash = self.contract.functions.registerDocument(
                    document_hash,
                    ipfs_hash,
                    Web3.to_checksum_address(owner_address),
                    document_type
                ).transact()
            
            # Wait for transaction confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed'],
                'document_hash': document_hash
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_document(self, document_hash: str) -> Dict:
        """
        Verify a document on the blockchain
        
        Args:
            document_hash: SHA-256 hash of the document
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Call smart contract view function
            result = self.contract.functions.verifyDocument(document_hash).call()
            
            exists, is_valid, issuer, owner, timestamp, doc_type, ipfs_hash = result
            
            return {
                'exists': exists,
                'is_valid': is_valid,
                'issuer': issuer,
                'owner': owner,
                'timestamp': timestamp,
                'document_type': doc_type,
                'ipfs_hash': ipfs_hash,
                'verified_on_blockchain': exists and is_valid
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def revoke_document(self, document_hash: str, issuer_private_key: Optional[str] = None) -> Dict:
        """
        Revoke a document (mark as invalid)
        
        Args:
            document_hash: SHA-256 hash of the document
            issuer_private_key: Private key of the issuer (optional)
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            if issuer_private_key:
                # Build and sign transaction
                transaction = self.contract.functions.revokeDocument(
                    document_hash
                ).build_transaction({
                    'from': self.w3.eth.default_account,
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': self.w3.eth.get_transaction_count(self.w3.eth.default_account)
                })
                
                signed_txn = self.w3.eth.account.sign_transaction(transaction, issuer_private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                # Use default account
                tx_hash = self.contract.functions.revokeDocument(document_hash).transact()
            
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
    
    def get_user_documents(self, user_address: str) -> list:
        """
        Get all documents owned by a user
        
        Args:
            user_address: Ethereum address of the user
            
        Returns:
            List of document hashes
        """
        try:
            documents = self.contract.functions.getUserDocuments(
                Web3.to_checksum_address(user_address)
            ).call()
            return documents
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    def get_account_balance(self, address: str = None) -> float:
        """
        Get ETH balance of an account
        
        Args:
            address: Account address (uses default if not provided)
            
        Returns:
            Balance in ETH
        """
        address = address or self.w3.eth.default_account
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
        return float(self.w3.from_wei(balance_wei, 'ether'))


# Singleton instance for easy import
_blockchain_service = None

def get_blockchain_service() -> BlockchainService:
    """Get or create blockchain service singleton"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service
