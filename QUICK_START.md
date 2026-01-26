# 🚀 Quick Start Guide - Blockchain Part

## For First-Time Setup

### Step 1: Install Node.js
1. Download from https://nodejs.org/ (LTS version recommended)
2. Install it
3. Open PowerShell/Command Prompt and verify:
```bash
node --version
npm --version
```

### Step 2: Setup Blockchain

**Option A: Using Windows Script (Easiest)**
```bash
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\blockchain"
.\scripts\setup.bat
```

**Option B: Manual Setup**
```bash
# Navigate to blockchain folder
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\blockchain"

# Install dependencies
npm install

# Compile contracts
npm run compile

# Start blockchain (keep this terminal running)
npm run node
```

Then in a **NEW terminal**:
```bash
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\blockchain"

# Deploy contract
npm run deploy
```

### Step 3: Test It Works

```bash
# Run tests
npm run test
```

You should see: `✓ Should register O/L certificate successfully` (and many more passing tests)

### Step 4: Test Backend Integration

```bash
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\backend"

# Install Python dependencies
pip install -r requirements.txt

# Test blockchain connection
python test_blockchain.py
```

You should see:
```
✅ Connected: True
✅ Registration Successful!
✅ Certificate Found!
🎉 All Tests Completed Successfully!
```

---

## Daily Development Workflow

### Every Time You Start Working:

**Terminal 1: Start Blockchain**
```bash
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\blockchain"
npm run node
```
Leave this running. You'll see accounts with 10000 ETH each.

**Terminal 2: Start Backend (when ready)**
```bash
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\backend"
python app/main.py
```

---

## Testing Your Work

### Test Smart Contract
```bash
cd blockchain
npm run test
```

### Test Blockchain Connection
```bash
cd backend
python test_blockchain.py
```

### Test API Endpoints
Use Postman or curl:

**1. Check blockchain status:**
```bash
curl http://localhost:5000/api/certificate/blockchain-status
```

**2. Register a certificate:**
```bash
curl -X POST http://localhost:5000/api/certificate/register \
  -F "certificate=@path/to/certificate.pdf" \
  -F "student_address=0x70997970C51812dc3A010C7d01b50e0d17dc79C8" \
  -F "document_type=O/L" \
  -F "student_index=2023OL123456" \
  -F "exam_year=2023" \
  -F "exam_subject=General"
```

**3. Verify a certificate:**
```bash
curl -X POST http://localhost:5000/api/certificate/verify \
  -F "certificate=@path/to/certificate.pdf"
```

---

## Understanding What Each File Does

### Blockchain Files:
- `contracts/DocumentVerification.sol` - **Your smart contract** (the blockchain code)
- `scripts/deploy.js` - Deploys contract to blockchain
- `test/DocumentVerification.test.js` - Tests your contract
- `hardhat.config.js` - Blockchain configuration

### Backend Files:
- `app/services/blockchain_service.py` - **Python code to talk to blockchain**
- `app/api/certificate_routes.py` - API endpoints for certificates
- `app/main.py` - Main Flask application
- `test_blockchain.py` - Test script

### What Gets Generated:
- `blockchain/deployed/DocumentVerification.json` - Contract address and ABI
- `backend/app/contracts/DocumentVerification.json` - Copy for backend

---

## Common Commands Reference

### Blockchain Commands:
```bash
npm run node       # Start local blockchain
npm run compile    # Compile smart contracts
npm run deploy     # Deploy contracts
npm run test       # Run tests
```

### Backend Commands:
```bash
pip install -r requirements.txt   # Install dependencies
python app/main.py               # Start backend server
python test_blockchain.py        # Test blockchain connection
```

---

## Troubleshooting

### "Cannot connect to blockchain"
**Fix:** Make sure blockchain is running
```bash
cd blockchain
npm run node
```

### "Contract not deployed"
**Fix:** Deploy the contract
```bash
cd blockchain
npm run deploy
```

### "Port already in use"
**Fix:** Kill the process using the port
```bash
# On Windows (PowerShell as Admin):
netstat -ano | findstr :8545
taskkill /PID <PID_NUMBER> /F
```

### "Module not found"
**Fix:** Install dependencies
```bash
# For blockchain:
cd blockchain
npm install

# For backend:
cd backend
pip install -r requirements.txt
```

---

## Key Concepts You Need to Know

### 1. **Smart Contract = Code on Blockchain**
- Written in Solidity (like JavaScript)
- Stored permanently on blockchain
- Cannot be edited after deployment (in production)
- Functions can be called from anywhere

### 2. **Hash = Certificate Fingerprint**
- Same file → Same hash (always)
- Different file → Different hash
- We store hash, not the actual certificate
- SHA-256 produces 64 character hex string

### 3. **Transaction = Action on Blockchain**
- Registering certificate = Transaction
- Revoking certificate = Transaction
- Verifying certificate = NOT a transaction (just reading)
- Transactions cost gas (ETH)

### 4. **Local Blockchain (Hardhat)**
- Runs on your computer
- Fast and free
- Resets when you restart it
- 20 test accounts with 10000 ETH each

---

## What to Tell Your Teammates

### To Frontend Developer:
"I've created API endpoints at `http://localhost:5000/api/certificate/` that you can use:
- POST `/register` - Register a certificate
- POST `/verify` - Verify a certificate by uploading it
- POST `/verify-by-index` - Verify by student index
- GET `/user-documents/<address>` - Get all user certificates
- GET `/blockchain-status` - Check blockchain connection

Here's the contract ABI and address: `backend/app/contracts/DocumentVerification.json`"

### To Document Extraction Developer:
"After you extract the certificate data, send it to my API endpoint:
- Endpoint: POST `http://localhost:5000/api/certificate/register`
- Fields needed: student_address, document_type (O/L or A/L), student_index, exam_year, exam_subject
- File: The actual certificate PDF/image
- I'll handle storing the hash on blockchain"

---

## Next Steps for You

1. ✅ **Done:** Smart contract created
2. ✅ **Done:** Deployment scripts ready
3. ✅ **Done:** Backend integration code ready
4. ✅ **Done:** API endpoints created
5. ✅ **Done:** Test scripts ready

**Now do:**
1. Run through the Quick Start steps above
2. Test that everything works
3. Read `BLOCKCHAIN_GUIDE.md` for deep understanding
4. Coordinate with your teammates on integration
5. Test with real O/L/A/L certificate PDFs

---

## Getting Help

**If you get stuck:**
1. Check the error message carefully
2. Look in `BLOCKCHAIN_GUIDE.md` for explanations
3. Check "Troubleshooting" section above
4. Run the tests to see if something broke
5. Ask your team or search online

**Good resources:**
- Hardhat docs: https://hardhat.org/
- Solidity docs: https://docs.soliditylang.org/
- Web3.py docs: https://web3py.readthedocs.io/

---

## You're All Set! 🎉

Everything is prepared for you. Just follow the steps above and you'll have a working blockchain system for certificate verification!

Remember:
- **Local blockchain** = For development (what you're doing now)
- **Production blockchain** = For real deployment (later, when project is complete)

Good luck with your project! 💪
