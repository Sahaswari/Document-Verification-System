# Certificate Verification API Testing Guide

This guide shows how to test the two verification methods using curl commands.

## Prerequisites

1. Backend must be running on `http://localhost:5000`
2. Smart contract must be deployed on blockchain
3. At least one certificate registered on blockchain

## Method 3: Verify by Student Index

### Test Command:
```bash
curl -X POST http://localhost:5000/api/certificate/verify-by-index \
  -H "Content-Type: application/json" \
  -d "{\"student_index\": \"2023OL123456\"}"
```

### Expected Response (Success):
```json
{
  "verified": true,
  "exists": true,
  "details": {
    "exists": true,
    "is_valid": true,
    "issuer": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "owner": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "timestamp": 1737849600,
    "document_type": "OL",
    "ipfs_hash": "QmXxx...",
    "document_hash": "a1b2c3d4e5f6...",
    "student_index": "2023OL123456",
    "exam_year": 2023,
    "exam_subject": "General",
    "verified_on_blockchain": true
  }
}
```

### Expected Response (Not Found):
```json
{
  "verified": false,
  "exists": false,
  "message": "No certificate found for student index: 2023OL999999"
}
```

### Error Cases:
```bash
# Missing student_index
curl -X POST http://localhost:5000/api/certificate/verify-by-index \
  -H "Content-Type: application/json" \
  -d "{}"

# Response:
{
  "error": "student_index is required"
}
```

---

## Method 4: Verify by File Upload

### Test Command:
```bash
# Replace path/to/certificate.pdf with actual file path
curl -X POST http://localhost:5000/api/certificate/verify \
  -F "certificate=@path/to/certificate.pdf"
```

### Windows PowerShell:
```powershell
# Upload PDF file
curl.exe -X POST http://localhost:5000/api/certificate/verify `
  -F "certificate=@C:\path\to\certificate.pdf"

# Upload image file
curl.exe -X POST http://localhost:5000/api/certificate/verify `
  -F "certificate=@C:\path\to\certificate.jpg"
```

### Expected Response (Success):
```json
{
  "verified": true,
  "exists": true,
  "certificate_details": {
    "document_hash": "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
    "document_type": "OL",
    "student_index": "2023OL123456",
    "exam_year": 2023,
    "exam_subject": "General",
    "issued_by": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "owner": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "registration_timestamp": 1737849600,
    "is_valid": true,
    "ipfs_hash": "QmXxx..."
  },
  "message": "Certificate found on blockchain"
}
```

### Expected Response (Not Found):
```json
{
  "verified": false,
  "exists": false,
  "message": "Certificate not found on blockchain",
  "warning": "This certificate has not been registered or may be fraudulent"
}
```

### Expected Response (Revoked):
```json
{
  "verified": false,
  "exists": true,
  "certificate_details": {
    "document_hash": "...",
    "is_valid": false,
    ...
  },
  "message": "Certificate has been revoked"
}
```

### Error Cases:
```bash
# No file provided
curl -X POST http://localhost:5000/api/certificate/verify

# Response:
{
  "error": "No certificate file provided"
}

# Empty file
curl -X POST http://localhost:5000/api/certificate/verify \
  -F "certificate=@"

# Response:
{
  "error": "No file selected"
}
```

---

## Bonus: Verify by Document Hash

### Test Command:
```bash
curl -X POST http://localhost:5000/api/certificate/verify-by-hash \
  -H "Content-Type: application/json" \
  -d "{\"document_hash\": \"a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890\"}"
```

---

## Testing Workflow

### Step 1: Check Backend Health
```bash
curl http://localhost:5000/api/health
```

Expected:
```json
{
  "status": "healthy",
  "message": "Backend service is running"
}
```

### Step 2: Check Blockchain Status
```bash
curl http://localhost:5000/api/certificate/blockchain-status
```

Expected:
```json
{
  "connected": true,
  "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
  "network": "localhost",
  "block_number": 123
}
```

### Step 3: Get Sample Student Indexes
Check your database for test data:
```bash
# Using docker
docker exec -it doc-verify-backend python -c "
from app.models.exam_result import ExamResult
from app import db
results = ExamResult.query.limit(5).all()
for r in results:
    print(f'{r.index_number} - {r.exam_type} {r.exam_year}')
"
```

### Step 4: Test Student Index Verification
```bash
# Replace with actual index from Step 3
curl -X POST http://localhost:5000/api/certificate/verify-by-index \
  -H "Content-Type: application/json" \
  -d "{\"student_index\": \"YOUR_INDEX_HERE\"}"
```

### Step 5: Test File Upload Verification
```bash
# Create a test file (if you don't have one)
echo "Test Certificate Content" > test_cert.txt

# Upload it
curl -X POST http://localhost:5000/api/certificate/verify \
  -F "certificate=@test_cert.txt"

# Should return "not found" since it's not registered
```

---

## Common Issues and Solutions

### Issue 1: Connection Refused
```
curl: (7) Failed to connect to localhost port 5000
```

**Solution:** Backend is not running. Start it:
```bash
docker-compose up backend
# or
cd backend && python app/main.py
```

### Issue 2: 404 Not Found
```json
{
  "error": "404: Not Found"
}
```

**Solution:** Check the endpoint URL. Make sure routes are registered in `main.py`:
```python
from api.certificate_routes import certificate_bp
app.register_blueprint(certificate_bp)
```

### Issue 3: Blockchain Not Connected
```json
{
  "error": "Failed to connect to blockchain"
}
```

**Solution:** 
1. Check blockchain is running: `docker ps | grep blockchain`
2. Deploy contract: `docker exec -it doc-verify-blockchain npm run deploy`
3. Check connection in backend logs

### Issue 4: Certificate Not Found
```json
{
  "verified": false,
  "exists": false
}
```

**Solution:** You need to register a certificate first. Check:
1. Is smart contract deployed?
2. Are there certificates in database?
3. Were certificates registered on blockchain?

---

## Quick Test Script (Copy-Paste)

### Windows CMD:
```cmd
@echo off
echo Testing Certificate Verification...
echo.

echo 1. Health Check
curl http://localhost:5000/api/health
echo.
echo.

echo 2. Blockchain Status
curl http://localhost:5000/api/certificate/blockchain-status
echo.
echo.

echo 3. Verify by Student Index (2023OL123456)
curl -X POST http://localhost:5000/api/certificate/verify-by-index -H "Content-Type: application/json" -d "{\"student_index\": \"2023OL123456\"}"
echo.
echo.

echo Tests completed!
pause
```

### Linux/Mac:
```bash
#!/bin/bash
echo "Testing Certificate Verification..."
echo ""

echo "1. Health Check"
curl http://localhost:5000/api/health
echo -e "\n"

echo "2. Blockchain Status"
curl http://localhost:5000/api/certificate/blockchain-status
echo -e "\n"

echo "3. Verify by Student Index"
curl -X POST http://localhost:5000/api/certificate/verify-by-index \
  -H "Content-Type: application/json" \
  -d '{"student_index": "2023OL123456"}'
echo -e "\n"

echo "Tests completed!"
```

---

## Python Test Script

Use the provided Python script for comprehensive testing:

```bash
cd backend
python test_verification_methods.py
```

The script will:
1. Check backend health
2. Check blockchain connection
3. Test student index verification
4. Test file upload verification
5. Provide detailed results

---

## Expected Performance

- **Student Index Verification:** < 100ms (blockchain query)
- **File Upload Verification:** < 500ms (includes hash calculation)
- **Hash Verification:** < 100ms (blockchain query)

---

## Security Notes

1. **Student Index** - Semi-public data, acceptable to expose
2. **Document Hash** - Safe to expose (one-way function)
3. **File Upload** - Validate file types and sizes (already implemented)
4. **No Personal Data** - Blockchain only stores hashes and metadata

---

## Summary

✅ **Method 3 (Student Index):**
- Endpoint: `POST /api/certificate/verify-by-index`
- Input: `{"student_index": "2023OL123456"}`
- Fast, direct blockchain lookup

✅ **Method 4 (File Upload):**
- Endpoint: `POST /api/certificate/verify`
- Input: Form data with file
- Detects tampering, cryptographically secure

Both methods are **backend-ready** and tested! 🎉
