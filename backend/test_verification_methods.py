#!/usr/bin/env python3
"""
Test script for certificate verification methods
Tests Method 3 (Student Index) and Method 4 (File Upload)
"""

import requests
import json
import hashlib
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5000"
BLOCKCHAIN_API = f"{API_BASE_URL}/api/certificate"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_verify_by_student_index(student_index):
    """
    Test Method 3: Verify certificate by student index
    """
    print_header("METHOD 3: Verify by Student Index")
    print(f"Student Index: {student_index}")
    
    try:
        # Make API request
        response = requests.post(
            f"{BLOCKCHAIN_API}/verify-by-index",
            json={"student_index": student_index},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            
            if data.get('verified'):
                print_result(True, "Certificate verified successfully!")
                print(f"\n📋 Certificate Details:")
                details = data.get('details', {})
                print(f"  • Document Hash: {details.get('document_hash', 'N/A')}")
                print(f"  • Exam Type: {details.get('document_type', 'N/A')}")
                print(f"  • Exam Year: {details.get('exam_year', 'N/A')}")
                print(f"  • Subject/Stream: {details.get('exam_subject', 'N/A')}")
                print(f"  • Valid: {details.get('is_valid', False)}")
                print(f"  • Timestamp: {details.get('timestamp', 'N/A')}")
                return True
            else:
                print_result(False, data.get('message', 'Certificate not found'))
                return False
        else:
            print_result(False, f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_verify_by_file_upload(file_path):
    """
    Test Method 4: Verify certificate by uploading file
    """
    print_header("METHOD 4: Verify by File Upload")
    print(f"File: {file_path}")
    
    try:
        # Check if file exists
        if not Path(file_path).exists():
            print_result(False, f"File not found: {file_path}")
            return False
        
        # Calculate hash locally (for comparison)
        with open(file_path, 'rb') as f:
            file_content = f.read()
            local_hash = hashlib.sha256(file_content).hexdigest()
        
        print(f"Local Hash: {local_hash}")
        
        # Upload file to API
        with open(file_path, 'rb') as f:
            files = {'certificate': f}
            response = requests.post(
                f"{BLOCKCHAIN_API}/verify",
                files=files
            )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            
            if data.get('verified'):
                print_result(True, "Certificate file verified successfully!")
                print(f"\n📋 Certificate Details:")
                details = data.get('certificate_details', {})
                print(f"  • Document Hash: {details.get('document_hash', 'N/A')}")
                print(f"  • Exam Type: {details.get('document_type', 'N/A')}")
                print(f"  • Exam Year: {details.get('exam_year', 'N/A')}")
                print(f"  • Student Index: {details.get('student_index', 'N/A')}")
                print(f"  • Valid: {details.get('is_valid', False)}")
                
                # Compare hashes
                blockchain_hash = details.get('document_hash', '')
                if blockchain_hash == local_hash:
                    print_result(True, "Hash matches! File is authentic.")
                else:
                    print_result(False, "Hash mismatch! File may be tampered.")
                
                return True
            elif data.get('exists') is False:
                print_result(False, "Certificate not registered on blockchain")
                print(f"⚠️  {data.get('warning', '')}")
                return False
            else:
                print_result(False, data.get('message', 'Certificate invalid'))
                return False
        else:
            print_result(False, f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_verify_by_hash(document_hash):
    """
    Bonus test: Verify by document hash directly
    """
    print_header("BONUS: Verify by Document Hash")
    print(f"Hash: {document_hash}")
    
    try:
        response = requests.post(
            f"{BLOCKCHAIN_API}/verify-by-hash",
            json={"document_hash": document_hash},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            
            if data.get('verified'):
                print_result(True, "Certificate verified by hash!")
                return True
            else:
                print_result(False, "Certificate not found or invalid")
                return False
        else:
            print_result(False, f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def check_backend_health():
    """Check if backend is running"""
    print_header("Backend Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "Backend is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print_result(False, "Backend returned error")
            return False
    except Exception as e:
        print_result(False, f"Cannot connect to backend: {str(e)}")
        print("\n💡 Make sure the backend is running:")
        print("   docker-compose up")
        print("   or")
        print("   cd backend && python app/main.py")
        return False

def check_blockchain_status():
    """Check if blockchain is connected"""
    print_header("Blockchain Connection Check")
    try:
        response = requests.get(f"{BLOCKCHAIN_API}/blockchain-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Blockchain is connected")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_result(False, "Blockchain not connected")
            return False
    except Exception as e:
        print_result(False, f"Cannot check blockchain: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("\n" + "🔬 CERTIFICATE VERIFICATION TEST SUITE".center(70))
    print("Testing Method 3 (Student Index) and Method 4 (File Upload)".center(70))
    
    # Check prerequisites
    if not check_backend_health():
        sys.exit(1)
    
    if not check_blockchain_status():
        print("\n⚠️  Warning: Blockchain not connected. Tests may fail.")
    
    # Test results
    results = []
    
    # TEST 1: Verify by Student Index
    print("\n" + "TEST 1: Student Index Verification".center(70, "-"))
    test_index = input("\nEnter student index to test (e.g., 2023OL123456): ").strip()
    if test_index:
        result = test_verify_by_student_index(test_index)
        results.append(("Student Index Verification", result))
    else:
        print("⏭️  Skipping test...")
    
    # TEST 2: Verify by File Upload
    print("\n" + "TEST 2: File Upload Verification".center(70, "-"))
    test_file = input("\nEnter path to certificate file (or press Enter to skip): ").strip()
    if test_file:
        result = test_verify_by_file_upload(test_file)
        results.append(("File Upload Verification", result))
    else:
        print("⏭️  Skipping test...")
    
    # TEST 3: Verify by Hash (if we have one from previous tests)
    print("\n" + "TEST 3: Document Hash Verification".center(70, "-"))
    test_hash = input("\nEnter document hash to test (or press Enter to skip): ").strip()
    if test_hash:
        result = test_verify_by_hash(test_hash)
        results.append(("Hash Verification", result))
    else:
        print("⏭️  Skipping test...")
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_result(result, test_name)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("\n🎉 All tests passed! Both verification methods are working correctly.")
    elif passed > 0:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
    else:
        print(f"\n❌ All tests failed or no tests run. Please check your setup.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user.")
        sys.exit(0)
