# 🔐 Blockchain Implementation Guide
## Sri Lankan O/L & A/L Certificate Verification System

### 📚 Table of Contents
1. [Introduction to Your Blockchain System](#introduction)
2. [Understanding the Architecture](#architecture)
3. [Smart Contract Explained](#smart-contract)
4. [Step-by-Step Implementation](#implementation)
5. [Testing Your Blockchain](#testing)
6. [Integration with Backend](#backend-integration)
7. [Common Issues & Solutions](#troubleshooting)

---

## 🎯 Introduction to Your Blockchain System {#introduction}

**What you're building:** A blockchain-based system to verify Sri Lankan O/L and A/L certificates. Think of blockchain as a **permanent, tamper-proof digital ledger** where certificate records are stored.

**Why blockchain?**
- **Immutable**: Once a certificate is registered, it cannot be altered
- **Transparent**: Anyone can verify a certificate
- **Decentralized**: No single authority controls all data
- **Tamper-proof**: Cryptographic hashing ensures integrity

**Your Role (Blockchain Developer):** You'll create smart contracts that:
1. Store certificate hashes (not the actual certificates)
2. Allow authorized issuers (Dept. of Examinations) to register certificates
3. Let anyone verify if a certificate is genuine
4. Track who issued certificates and when

---

## 🏗️ Understanding the Architecture {#architecture}

```
┌─────────────────┐
│    Frontend     │  ← Your teammate's part
│   (React.js)    │     (User interface)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│     Backend     │  ← Your teammate's part
│  (Flask/Python) │     (Document extraction, AI)
└────────┬────────┘
         │
         ↓  [Your Integration Point]
┌─────────────────┐
│   Blockchain    │  ← YOUR PART
│  Smart Contract │     (Certificate verification)
│   (Solidity)    │
└─────────────────┘
```

**How it works:**
1. **Department of Examinations** uploads certificate → Backend extracts data
2. **Backend** calculates certificate hash → Sends to blockchain
3. **Your Smart Contract** stores the hash permanently
4. **Anyone** can verify certificate → Query blockchain with hash

---

## 📜 Smart Contract Explained {#smart-contract}

### What is a Smart Contract?
A smart contract is **code that runs on the blockchain**. Think of it as:
- A vending machine: You put in money (input), it gives you snacks (output)
- Your contract: You give certificate data (input), it stores/verifies (output)

### Your Contract Structure

```solidity
// DocumentVerification.sol - Your Main Contract
contract DocumentVerification {
    // 1. DATA STRUCTURES
    struct Document {
        string documentHash;      // SHA-256 hash of certificate
        string ipfsHash;          // Metadata storage location
        address issuer;           // Who registered it
        address owner;            // Student's address
        uint256 timestamp;        // When registered
        bool isValid;             // Is it valid?
        string documentType;      // "O/L" or "A/L"
        string studentIndex;      // Student index number
        uint256 examYear;         // Year of exam
        string examSubject;       // Subject/Stream
    }
    
    // 2. STORAGE
    mapping(string => Document) private documents;
    
    // 3. FUNCTIONS
    function registerDocument(...) { }  // Add new certificate
    function verifyDocument(...) { }    // Check if valid
    function revokeDocument(...) { }    // Mark as invalid
}
```

### Key Concepts Explained

**1. Hash (Document Hash):**
```
Original Certificate (PDF) → SHA-256 → "0x1234abcd..." (64 characters)
```
- Like a fingerprint for the certificate
- Same file always produces same hash
- Even tiny change produces completely different hash
- We store the hash, not the actual certificate (privacy!)

**2. Address:**
```
Ethereum Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1
```
- Like a bank account number on blockchain
- Department of Examinations has an address (issuer)
- Each student has an address (owner)

**3. Mappings:**
```solidity
mapping(string => Document) private documents;
```
- Like a dictionary/hashmap in programming
- Key: document hash → Value: full certificate details
- Fast lookup: O(1) time complexity

---

## 🚀 Step-by-Step Implementation {#implementation}

### Step 1: Install Prerequisites

```bash
# On Windows (PowerShell as Administrator):
# Install Node.js from https://nodejs.org/ (LTS version)
node --version  # Should show v18.x.x or higher

# Navigate to blockchain folder
cd "f:\University of Ruhuna\Uni_Project\Document Verification System\blockchain"

# Install dependencies
npm install
```

**What this installs:**
- **Hardhat**: Development environment for Ethereum
- **Ethers.js**: Library to interact with blockchain
- **OpenZeppelin**: Security-tested contract templates

### Step 2: Compile Smart Contracts

```bash
npm run compile
```

**What happens:**
- Solidity code → Compiled to bytecode
- ABI (Application Binary Interface) generated
- Artifacts stored in `artifacts/` folder

**Understanding ABI:**
- ABI = "Instruction manual" for your contract
- Tells other programs how to interact with your contract
- Like an API specification

### Step 3: Start Local Blockchain

```bash
# Option 1: Run in foreground
npm run node

# Option 2: Use setup script (Windows)
.\scripts\setup.bat
```

**What you get:**
- Local Ethereum network running on `http://localhost:8545`
- 20 pre-funded test accounts
- Fast mining (instant transactions)
- Reset on restart (for development)

**Sample Output:**
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
...
```

### Step 4: Deploy Smart Contract

```bash
# In a new terminal (keep blockchain running)
npm run deploy
```

**What happens:**
1. Contract deployed to blockchain
2. Contract address generated (e.g., `0x5FbDB2315678afecb367f032d93F642f64180aa3`)
3. Contract data saved to:
   - `blockchain/deployed/DocumentVerification.json`
   - `backend/app/contracts/DocumentVerification.json`

**Understanding Deployment:**
```javascript
// What deploy.js does:
1. Read compiled contract
2. Send transaction to blockchain
3. Blockchain mines transaction
4. Contract gets permanent address
5. Save address & ABI for later use
```

### Step 5: Test Your Contract

```bash
npm run test
```

**What tests verify:**
- ✅ Certificate registration works
- ✅ Only authorized issuers can register
- ✅ Verification returns correct data
- ✅ Revocation works properly
- ✅ Invalid data is rejected

---

## 🧪 Testing Your Blockchain {#testing}

### Manual Testing with Hardhat Console

```bash
npx hardhat console --network localhost
```

**Example Test Session:**
```javascript
// 1. Get contract
const Contract = await ethers.getContractFactory("DocumentVerification");
const contract = await Contract.attach("YOUR_CONTRACT_ADDRESS");

// 2. Register a certificate
const [owner, issuer, student] = await ethers.getSigners();
await contract.registerDocument(
  "0x1234abcd...",           // document hash
  "QmIPFS123...",            // IPFS hash
  student.address,          // student address
  "O/L",                    // document type
  "2023OL123456",           // student index
  2023,                     // exam year
  "General"                 // subject
);

// 3. Verify certificate
const result = await contract.verifyDocument("0x1234abcd...");
console.log(result);

// Output:
// [
//   true,                    // exists
//   true,                    // isValid
//   '0xf39F...',            // issuer address
//   '0x7099...',            // owner address
//   1674123456,             // timestamp
//   'O/L',                  // document type
//   'QmIPFS123...',         // IPFS hash
//   '2023OL123456',         // student index
//   2023,                   // exam year
//   'General'               // subject
// ]
```

### Understanding Test Accounts

Hardhat gives you 20 test accounts:
```
Account #0: Contract Owner (You/Admin)
Account #1: Department of Examinations (Issuer)
Account #2: Student 1
Account #3: Student 2
...
```

Each has 10,000 test ETH for gas fees.

---

## 🔗 Integration with Backend {#backend-integration}

### How Backend Connects to Blockchain

```python
# backend/app/services/blockchain_service.py

from blockchain_service import BlockchainService

# 1. Initialize connection
blockchain = BlockchainService()

# 2. Register certificate
result = blockchain.register_document(
    document_hash="0xabc123...",
    ipfs_hash="QmXYZ...",
    owner_address="0xStudent123...",
    document_type="O/L"
)

# 3. Verify certificate
verification = blockchain.verify_document("0xabc123...")
if verification['exists'] and verification['is_valid']:
    print("✅ Certificate is genuine!")
else:
    print("❌ Certificate not found or invalid")
```

### Adding Web3 to Backend Requirements

```bash
# Update backend/requirements.txt
cd backend
echo "web3==6.11.0" >> requirements.txt
pip install -r requirements.txt
```

### Example API Endpoint

```python
# backend/app/main.py

from flask import Flask, request, jsonify
from services.blockchain_service import get_blockchain_service

@app.route('/api/verify-certificate', methods=['POST'])
def verify_certificate():
    """Verify a certificate on blockchain"""
    data = request.json
    file = request.files.get('certificate')
    
    # 1. Calculate hash from uploaded file
    blockchain = get_blockchain_service()
    doc_hash = blockchain.calculate_content_hash(file.read())
    
    # 2. Query blockchain
    result = blockchain.verify_document(doc_hash)
    
    # 3. Return result
    return jsonify({
        'verified': result['exists'] and result['is_valid'],
        'details': {
            'student_index': result.get('studentIndex'),
            'exam_year': result.get('examYear'),
            'document_type': result.get('documentType'),
            'issued_by': result.get('issuer'),
            'timestamp': result.get('timestamp')
        }
    })
```

---

## 🎓 Understanding Key Blockchain Concepts

### 1. Gas & Transactions

**What is Gas?**
- "Fuel" for blockchain operations
- Measured in Gwei (1 ETH = 1,000,000,000 Gwei)
- Prevents spam and pays miners

**Operations that cost gas:**
- ✍️ Writing data (registerDocument) - **Costs Gas**
- 🔒 Changing state (revokeDocument) - **Costs Gas**
- 👁️ Reading data (verifyDocument) - **FREE**

```javascript
// Writing (costs gas)
await contract.registerDocument(...);  // ⛽ ~200,000 gas

// Reading (free)
const result = await contract.verifyDocument(...);  // 🆓 No cost
```

### 2. Events

**What are Events?**
- Logs stored on blockchain
- Cheap way to store historical data
- Can be queried later

```solidity
event DocumentRegistered(
    string indexed documentHash,
    address indexed issuer,
    address indexed owner,
    uint256 timestamp
);

// When this fires, it creates a permanent log
```

**Why use events?**
- Track when certificates were registered
- Monitor who registered what
- Build audit trails

### 3. Access Control

```solidity
modifier onlyAuthorizedIssuer() {
    require(authorizedIssuers[msg.sender], "Not authorized");
    _;
}

function registerDocument(...) public onlyAuthorizedIssuer {
    // Only Department of Examinations can call this
}
```

**Security layers:**
1. Only authorized issuers can register certificates
2. Only issuer can revoke their own certificates
3. Anyone can verify (public access)

---

## 🛠️ Common Issues & Solutions {#troubleshooting}

### Issue 1: "Cannot connect to blockchain"

```
Error: Failed to connect to blockchain at http://blockchain:8545
```

**Solution:**
```bash
# Check if blockchain is running
curl http://localhost:8545

# If not, start it
cd blockchain
npm run node
```

### Issue 2: "Contract not deployed"

```
FileNotFoundError: Contract data not found
```

**Solution:**
```bash
# Deploy the contract
cd blockchain
npm run deploy

# Verify deployment
ls deployed/DocumentVerification.json
```

### Issue 3: "Transaction reverted"

```
Error: Transaction reverted: Only authorized issuers can register documents
```

**Solution:**
```python
# Authorize your backend address first
blockchain = BlockchainService()
# Use the correct issuer account
# Or authorize the address via contract owner
```

### Issue 4: "Out of gas"

```
Error: Transaction ran out of gas
```

**Solution:**
```python
# Increase gas limit in transaction
result = blockchain.register_document(
    ...,
    gas_limit=3000000  # Increase from default
)
```

---

## 📊 Certificate Registration Flow

```
1. Student uploads O/L certificate PDF
           ↓
2. Backend AI extracts data:
   - Student Index: 2023OL123456
   - Exam Year: 2023
   - Subjects & Grades
           ↓
3. Backend calculates SHA-256 hash of PDF
   PDF → Hash: 0xabc123def456...
           ↓
4. Backend calls your smart contract:
   registerDocument(hash, ipfs, student, "O/L", ...)
           ↓
5. Smart Contract validates:
   - Is caller authorized? ✅
   - Does document already exist? ❌
   - Is document type valid? ✅
           ↓
6. Smart Contract stores data permanently
   blockchain[hash] = {issuer, owner, timestamp, ...}
           ↓
7. Transaction confirmed, event emitted
   ✅ Certificate registered on blockchain!
```

---

## 🔄 Certificate Verification Flow

```
1. Employer uploads certificate for verification
           ↓
2. Backend calculates hash of uploaded file
   PDF → Hash: 0xabc123def456...
           ↓
3. Backend queries blockchain:
   verifyDocument(hash)
           ↓
4. Smart Contract returns:
   - exists: true
   - isValid: true
   - issuer: 0xDeptOfExam...
   - owner: 0xStudent...
   - timestamp: 1674123456
   - studentIndex: 2023OL123456
           ↓
5. Backend responds:
   ✅ Certificate is genuine!
   📅 Issued on: Jan 19, 2023
   🎓 Student Index: 2023OL123456
   📜 Type: O/L Certificate
```

---

## 🎯 Quick Reference Commands

```bash
# === Setup ===
cd blockchain
npm install                    # Install dependencies
npm run compile               # Compile contracts

# === Development ===
npm run node                  # Start local blockchain
npm run deploy                # Deploy contracts
npm run test                  # Run tests

# === Debugging ===
npx hardhat console           # Interactive console
npx hardhat clean            # Clean artifacts
npx hardhat compile --force  # Force recompile
```

---

## 📝 Next Steps for You

1. **✅ Already Done:**
   - Smart contract created
   - Deployment script ready
   - Test suite completed
   - Backend integration utilities prepared

2. **🚀 What to Do Next:**
   
   **Step 1:** Start the blockchain
   ```bash
   cd blockchain
   npm install
   npm run node  # Keep this running
   ```
   
   **Step 2:** Deploy contract (in new terminal)
   ```bash
   cd blockchain
   npm run deploy
   ```
   
   **Step 3:** Test it works
   ```bash
   npm run test  # Should see all tests passing
   ```
   
   **Step 4:** Integrate with backend
   ```python
   # In backend/app/main.py
   from services.blockchain_service import get_blockchain_service
   
   blockchain = get_blockchain_service()
   print(blockchain.get_account_balance())  # Should show balance
   ```

3. **🤝 Coordinate with Frontend Developer:**
   - They need the contract address
   - They need the ABI file
   - Both are in: `blockchain/deployed/DocumentVerification.json`

4. **📚 Learn More:**
   - Solidity docs: https://docs.soliditylang.org/
   - Hardhat docs: https://hardhat.org/getting-started/
   - Web3.py docs: https://web3py.readthedocs.io/

---

## 🎓 Blockchain Terminology Cheat Sheet

| Term | Simple Explanation | Example |
|------|-------------------|---------|
| **Smart Contract** | Code running on blockchain | Your DocumentVerification.sol |
| **Address** | Unique identifier (like email) | 0xf39Fd6e51aad... |
| **Hash** | Digital fingerprint | 0x1234abcd... (64 chars) |
| **Transaction** | Action on blockchain | Registering a certificate |
| **Gas** | Fee for transactions | Like postage stamp |
| **ABI** | Contract's instruction manual | How to call functions |
| **Hardhat** | Development toolkit | Like VS Code for blockchain |
| **Ethers.js** | JavaScript library | To interact with contracts |
| **Web3.py** | Python library | To interact with contracts |
| **Node** | Blockchain server | Runs on localhost:8545 |
| **Deployment** | Publishing contract | Making it live |
| **Minting** | Creating new record | Registering certificate |
| **Immutable** | Cannot be changed | Once stored, permanent |

---

## 💡 Tips for Your First Blockchain Project

1. **Start Simple:**
   - Test with one certificate first
   - Use Hardhat console to experiment
   - Don't worry about production yet

2. **Use the Tests:**
   - Run `npm run test` frequently
   - Tests show you how to use the contract
   - If tests pass, your code works!

3. **Read Error Messages:**
   - Solidity errors are very specific
   - "require" statements tell you what went wrong
   - Check the exact error message

4. **Ask for Help:**
   - Hardhat Discord: https://hardhat.org/discord
   - Stack Overflow: Tag [solidity] [hardhat]
   - Your project team!

5. **Keep Learning:**
   - You're doing great for a first blockchain project!
   - Blockchain is a skill that takes time
   - Every error teaches you something

---

## 🎉 You're Ready!

You now have:
- ✅ A working smart contract for O/L & A/L certificates
- ✅ Deployment scripts
- ✅ Test suite
- ✅ Backend integration code
- ✅ This comprehensive guide

**Remember:** Blockchain development is different from regular programming. It's:
- **Permanent**: Deployed code can't be edited easily
- **Transparent**: Everyone can see transactions
- **Costly**: Each write operation costs gas
- **Powerful**: Creates trust without intermediaries

Good luck with your project! 🚀

---

**Questions? Issues?**
- Check the test file: `blockchain/test/DocumentVerification.test.js`
- Review the Python service: `backend/app/services/blockchain_service.py`
- Re-read this guide section by section

You've got this! 💪
