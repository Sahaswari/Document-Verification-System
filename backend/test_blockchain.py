"""
Blockchain Integration Test Script
Test the blockchain service without running the full backend
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.blockchain_service import BlockchainService

def main():
    print("=" * 60)
    print("🧪 Blockchain Service Test")
    print("=" * 60)
    print()
    
    try:
        # Initialize blockchain service
        print("1️⃣  Connecting to blockchain...")
        blockchain = BlockchainService()
        print()
        
        # Check connection
        print("2️⃣  Connection Status:")
        print(f"   ✅ Connected: {blockchain.w3.is_connected()}")
        print(f"   📍 Contract Address: {blockchain.contract_address}")
        print(f"   🌐 Network: {blockchain.provider_url}")
        print(f"   ⛓️  Chain ID: {blockchain.w3.eth.chain_id}")
        print(f"   📦 Block Number: {blockchain.w3.eth.block_number}")
        print()
        
        # Account info
        print("3️⃣  Account Information:")
        default_account = blockchain.w3.eth.default_account
        print(f"   👤 Default Account: {default_account}")
        balance = blockchain.get_account_balance()
        print(f"   💰 Balance: {balance:.4f} ETH")
        print()
        
        # Test certificate registration
        print("4️⃣  Testing Certificate Registration...")
        test_hash = "0x" + "a" * 64  # Dummy hash for testing
        test_ipfs = "QmTestIPFS123"
        test_student = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"  # Test account
        
        result = blockchain.register_document(
            document_hash=test_hash,
            ipfs_hash=test_ipfs,
            owner_address=test_student,
            document_type="O/L",
            student_index="2023OL999999",
            exam_year=2023,
            exam_subject="General"
        )
        
        if result['success']:
            print(f"   ✅ Registration Successful!")
            print(f"   📝 Transaction Hash: {result['transaction_hash']}")
            print(f"   🧱 Block Number: {result['block_number']}")
            print(f"   ⛽ Gas Used: {result['gas_used']}")
        else:
            print(f"   ❌ Registration Failed: {result.get('error')}")
        print()
        
        # Test certificate verification
        print("5️⃣  Testing Certificate Verification...")
        verify_result = blockchain.verify_document(test_hash)
        
        if verify_result['exists']:
            print(f"   ✅ Certificate Found!")
            print(f"   📜 Document Type: {verify_result['document_type']}")
            print(f"   🎓 Student Index: {verify_result.get('student_index')}")
            print(f"   📅 Exam Year: {verify_result.get('exam_year')}")
            print(f"   ✔️  Valid: {verify_result['is_valid']}")
            print(f"   👤 Owner: {verify_result['owner']}")
            print(f"   🏢 Issuer: {verify_result['issuer']}")
        else:
            print(f"   ❌ Certificate Not Found")
        print()
        
        # Test get user documents
        print("6️⃣  Testing Get User Documents...")
        user_docs = blockchain.get_user_documents(test_student)
        print(f"   📚 Total Documents: {len(user_docs)}")
        for i, doc in enumerate(user_docs[:5], 1):  # Show first 5
            print(f"   {i}. {doc[:20]}...")
        print()
        
        print("=" * 60)
        print("🎉 All Tests Completed Successfully!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("  1. Start the backend: python app/main.py")
        print("  2. Test API endpoints with Postman or curl")
        print("  3. Integrate with frontend")
        
    except FileNotFoundError as e:
        print("❌ Error: Contract not deployed")
        print()
        print("Please deploy the contract first:")
        print("  1. cd blockchain")
        print("  2. npm run node  (keep running)")
        print("  3. npm run deploy  (in new terminal)")
        print()
        print(f"Details: {e}")
        
    except ConnectionError as e:
        print("❌ Error: Cannot connect to blockchain")
        print()
        print("Please start the blockchain node:")
        print("  1. cd blockchain")
        print("  2. npm run node")
        print()
        print(f"Details: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
