# 🏗️ System Architecture Diagram

## Overall System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     DOCUMENT VERIFICATION SYSTEM                  │
│                  Sri Lankan O/L & A/L Certificates                │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                             │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      FRONTEND (React)                           │    │
│  │                                                                 │    │
│  │  • Upload Certificate Interface                                │    │
│  │  • Verification Results Display                                │    │
│  │  • Certificate History View                                    │    │
│  │  • MetaMask Integration (Future)                              │    │
│  │                                                                 │    │
│  │  Your Teammate's Part                                          │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
                            HTTP REST API
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                               │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    BACKEND (Flask/Python)                       │    │
│  │                                                                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐ │    │
│  │  │  API Endpoints (Flask Routes)                            │ │    │
│  │  │  • POST /api/certificate/register                        │ │    │
│  │  │  • POST /api/certificate/verify                          │ │    │
│  │  │  • POST /api/certificate/revoke                          │ │    │
│  │  │  • GET  /api/certificate/blockchain-status               │ │    │
│  │  └──────────────────────────────────────────────────────────┘ │    │
│  │                                                                 │    │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │    │
│  │  │ Document         │  │ AI/ML Services   │                   │    │
│  │  │ Extraction       │  │ (OCR, Forgery    │                   │    │
│  │  │ (Your teammate)  │  │  Detection)      │                   │    │
│  │  └──────────────────┘  └──────────────────┘                   │    │
│  │                                                                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐ │    │
│  │  │  Blockchain Service (blockchain_service.py)               │ │    │
│  │  │  • Connect to Ethereum                                    │ │    │
│  │  │  • Load Smart Contract                                    │ │    │
│  │  │  • Calculate Hashes (SHA-256)                            │ │    │
│  │  │  • Send Transactions                                      │ │    │
│  │  │  • Query Contract State                                   │ │    │
│  │  │                                                            │ │    │
│  │  │  YOUR PART (Python Integration Layer)                     │ │    │
│  │  └──────────────────────────────────────────────────────────┘ │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
                          Web3.py / HTTP RPC
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                          BLOCKCHAIN LAYER                                │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                Ethereum Network (Hardhat Local)                 │    │
│  │                                                                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐ │    │
│  │  │  Smart Contract (DocumentVerification.sol)                │ │    │
│  │  │                                                            │ │    │
│  │  │  struct Document {                                         │ │    │
│  │  │    string documentHash;     // SHA-256                    │ │    │
│  │  │    string ipfsHash;         // Metadata storage           │ │    │
│  │  │    address issuer;          // Who issued                 │ │    │
│  │  │    address owner;           // Student                    │ │    │
│  │  │    uint256 timestamp;       // When                       │ │    │
│  │  │    bool isValid;            // Status                     │ │    │
│  │  │    string documentType;     // O/L or A/L                │ │    │
│  │  │    string studentIndex;     // Student ID                 │ │    │
│  │  │    uint256 examYear;        // Year                       │ │    │
│  │  │    string examSubject;      // Subject/Stream             │ │    │
│  │  │  }                                                         │ │    │
│  │  │                                                            │ │    │
│  │  │  Functions:                                                │ │    │
│  │  │  • registerDocument()                                      │ │    │
│  │  │  • verifyDocument()                                        │ │    │
│  │  │  • verifyByStudentIndex()                                 │ │    │
│  │  │  • revokeDocument()                                        │ │    │
│  │  │  • getUserDocuments()                                      │ │    │
│  │  │                                                            │ │    │
│  │  │  YOUR PART (Smart Contract)                               │ │    │
│  │  └──────────────────────────────────────────────────────────┘ │    │
│  │                                                                 │    │
│  │  [Blockchain State - Immutable Storage]                        │    │
│  │  • mapping(hash => Document)                                   │    │
│  │  • mapping(address => documents[])                             │    │
│  │  • mapping(studentIndex => hash)                               │    │
│  │  • Event logs (audit trail)                                    │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Certificate Registration Flow

```
┌──────────┐
│ Examiner │  (Department of Examinations)
│ Officer  │
└────┬─────┘
     │
     │ 1. Upload O/L/A/L Certificate PDF
     ↓
┌─────────────────────────────────────────────┐
│         FRONTEND (React)                     │
│  • File upload form                          │
│  • Student info input                        │
└────┬────────────────────────────────────────┘
     │
     │ 2. HTTP POST /api/certificate/register
     │    + PDF file
     │    + student_address, document_type,
     │      student_index, exam_year, subject
     ↓
┌─────────────────────────────────────────────┐
│         BACKEND (Flask)                      │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 3. Extract Data (OCR/AI)               │ │
│  │    - Student Index                      │ │
│  │    - Exam Year                          │ │
│  │    - Subjects & Grades                  │ │
│  │    (Your teammate's code)               │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 4. Calculate Hash                       │ │
│  │    PDF → SHA256 → 0xabc123...          │ │
│  │    (64 character hex string)            │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 5. Call Blockchain Service              │ │
│  │    blockchain.register_document(...)    │ │
│  │    (YOUR Python code)                   │ │
│  └────┬───────────────────────────────────┘ │
└───────┼──────────────────────────────────────┘
        │
        │ 6. Send Transaction (Web3.py)
        ↓
┌─────────────────────────────────────────────┐
│    ETHEREUM BLOCKCHAIN (Hardhat)             │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 7. Smart Contract Execution             │ │
│  │    (YOUR Solidity code)                 │ │
│  │                                          │ │
│  │  function registerDocument(              │ │
│  │    hash, ipfs, owner,                    │ │
│  │    type, index, year, subject            │ │
│  │  ) {                                     │ │
│  │    // Validate inputs                    │ │
│  │    require(type == "O/L" || "A/L")      │ │
│  │    require(!exists(hash))                │ │
│  │                                          │ │
│  │    // Store on blockchain                │ │
│  │    documents[hash] = Document(...)       │ │
│  │    userDocs[owner].push(hash)            │ │
│  │    indexMap[index] = hash                │ │
│  │                                          │ │
│  │    // Emit event                         │ │
│  │    emit DocumentRegistered(...)          │ │
│  │  }                                       │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 8. Store Permanently                    │ │
│  │    Block #: 123                         │ │
│  │    TX Hash: 0xdef456...                 │ │
│  │    Gas Used: 250,000                    │ │
│  │    Status: ✅ Success                   │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
        │
        │ 9. Return Transaction Receipt
        ↓
┌─────────────────────────────────────────────┐
│         BACKEND (Flask)                      │
│  • Process receipt                           │
│  • Save file to uploads/                     │
│  • Return success response                   │
└────┬────────────────────────────────────────┘
     │
     │ 10. JSON Response
     ↓
┌──────────────────────────────────────────┐
│         FRONTEND (React)                  │
│  • Display success message                │
│  • Show transaction hash                  │
│  • Certificate hash: 0xabc123...         │
└──────────────────────────────────────────┘
```

---

## Certificate Verification Flow

```
┌──────────┐
│ Employer │  (Wants to verify certificate)
└────┬─────┘
     │
     │ 1. Upload Certificate PDF
     ↓
┌─────────────────────────────────────────────┐
│         FRONTEND (React)                     │
│  • File upload for verification              │
└────┬────────────────────────────────────────┘
     │
     │ 2. HTTP POST /api/certificate/verify
     │    + PDF file
     ↓
┌─────────────────────────────────────────────┐
│         BACKEND (Flask)                      │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 3. Calculate Hash                       │ │
│  │    Uploaded PDF → SHA256 → 0xabc123... │ │
│  │    (Same file = Same hash)              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 4. Query Blockchain                     │ │
│  │    blockchain.verify_document(hash)     │ │
│  │    (YOUR Python code)                   │ │
│  └────┬───────────────────────────────────┘ │
└───────┼──────────────────────────────────────┘
        │
        │ 5. Read from Blockchain (No transaction)
        ↓
┌─────────────────────────────────────────────┐
│    ETHEREUM BLOCKCHAIN (Hardhat)             │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 6. Smart Contract Query                 │ │
│  │    (YOUR Solidity code)                 │ │
│  │                                          │ │
│  │  function verifyDocument(hash)           │ │
│  │    returns (                             │ │
│  │      exists, isValid, issuer,            │ │
│  │      owner, timestamp, type,             │ │
│  │      ipfsHash, studentIndex,             │ │
│  │      examYear, examSubject               │ │
│  │    )                                     │ │
│  │  {                                       │ │
│  │    Document doc = documents[hash];       │ │
│  │                                          │ │
│  │    if (doc exists) {                     │ │
│  │      return all details;                 │ │
│  │    } else {                              │ │
│  │      return empty/false;                 │ │
│  │    }                                     │ │
│  │  }                                       │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 7. Return Data (READ ONLY - FREE)      │ │
│  │    exists: true                         │ │
│  │    isValid: true                        │ │
│  │    documentType: "O/L"                  │ │
│  │    studentIndex: "2023OL123456"         │ │
│  │    examYear: 2023                       │ │
│  │    issuer: 0xDeptOfExam...              │ │
│  │    timestamp: 1674123456                │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
        │
        │ 8. Return verification result
        ↓
┌─────────────────────────────────────────────┐
│         BACKEND (Flask)                      │
│  • Format response                           │
│  • Add additional checks                     │
│  • Return JSON                               │
└────┬────────────────────────────────────────┘
     │
     │ 9. JSON Response
     │    {
     │      "verified": true,
     │      "certificate_details": {...}
     │    }
     ↓
┌──────────────────────────────────────────┐
│         FRONTEND (React)                  │
│  • Parse response                         │
│  • Display verification status            │
│  • Show certificate details               │
│                                           │
│  ✅ VERIFIED CERTIFICATE                 │
│  Student: 2023OL123456                    │
│  Type: O/L Certificate                    │
│  Year: 2023                               │
│  Issued: Jan 19, 2023                     │
│  Status: Valid                            │
└──────────────────────────────────────────┘
```

---

## Data Flow: Hash Comparison

```
REGISTRATION:
Certificate.pdf
     ↓
  SHA-256 Hash
     ↓
"0xabc123..." ──────────────> Stored on Blockchain
     ↓
  Saved locally


VERIFICATION:
Upload Certificate.pdf
     ↓
  SHA-256 Hash
     ↓
"0xabc123..." ──────────────> Query Blockchain
     ↓                             ↓
  Compare ←────────────────────────┘
     ↓
Match? ✅ Valid
No Match? ❌ Invalid/Not Found
```

---

## Component Responsibility Matrix

| Component | Your Part | Teammate's Part |
|-----------|-----------|-----------------|
| **Smart Contract** | ✅ 100% | - |
| **Deployment Script** | ✅ 100% | - |
| **Blockchain Service (Python)** | ✅ 100% | - |
| **API Endpoints** | ✅ 100% | - |
| **Document Extraction** | - | ✅ 100% |
| **OCR/AI Processing** | - | ✅ 100% |
| **Frontend UI** | - | ✅ 100% |
| **Integration** | 🤝 50% | 🤝 50% |

---

## Development Environment

```
┌─────────────────────────────────────────────┐
│      YOUR LOCAL MACHINE (Windows)            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Terminal 1: Blockchain Node            │ │
│  │  > cd blockchain                         │ │
│  │  > npm run node                          │ │
│  │                                          │ │
│  │  📊 Hardhat Network                      │ │
│  │  ⛓️  http://localhost:8545               │ │
│  │  💰 20 test accounts                     │ │
│  │  ⚡ Instant mining                       │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Terminal 2: Backend Server              │ │
│  │  > cd backend                            │ │
│  │  > python app/main.py                    │ │
│  │                                          │ │
│  │  🔌 Flask Server                         │ │
│  │  🌐 http://localhost:5000                │ │
│  │  📡 Connected to blockchain              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Terminal 3: Frontend Dev Server         │ │
│  │  > cd frontend                           │ │
│  │  > npm start                             │ │
│  │                                          │ │
│  │  ⚛️  React App                           │ │
│  │  🌐 http://localhost:3000                │ │
│  │  🔗 Calls backend API                    │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## File Dependencies

```
DocumentVerification.sol
        ↓ compile
    Artifacts/ABI
        ↓ deploy
DocumentVerification.json ──┬──> blockchain/deployed/
                            └──> backend/app/contracts/
                                        ↓
                            blockchain_service.py
                                        ↓
                            certificate_routes.py
                                        ↓
                                    main.py
                                        ↓
                                  Flask Server
                                        ↓
                                  HTTP REST API
                                        ↓
                                 Frontend (React)
```

---

## Technology Stack Visualization

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
│  Technologies: React, JavaScript, HTML, CSS              │
│  Tools: npm, Webpack, Babel                             │
└─────────────────────────────────────────────────────────┘
                           ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                         │
│  Technologies: Python, Flask, Web3.py                    │
│  Tools: pip, virtualenv                                  │
└─────────────────────────────────────────────────────────┘
                           ↕ RPC/Web3
┌─────────────────────────────────────────────────────────┐
│                  BLOCKCHAIN LAYER                        │
│  Technologies: Ethereum, Solidity, Hardhat               │
│  Tools: Node.js, npm, Ethers.js                         │
└─────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────┐
│               SECURITY LAYERS                         │
│                                                       │
│  1. Frontend Validation                              │
│     • File type checking                             │
│     • Size limits                                    │
│     • Input sanitization                             │
│                                                       │
│  2. Backend Authorization                            │
│     • API authentication                             │
│     • Role-based access                              │
│     • Rate limiting                                  │
│                                                       │
│  3. Smart Contract Access Control                    │
│     • onlyAuthorizedIssuer modifier                  │
│     • Owner-only functions                           │
│     • Input validation (require statements)          │
│                                                       │
│  4. Cryptographic Security                           │
│     • SHA-256 hashing                                │
│     • Ethereum signatures                            │
│     • Private key management                         │
│                                                       │
│  5. Blockchain Immutability                          │
│     • Cannot alter stored data                       │
│     • Permanent audit trail                          │
│     • Consensus verification                         │
└──────────────────────────────────────────────────────┘
```

---

This visual architecture helps you understand:
1. Where YOUR code fits in the system
2. How components communicate
3. Data flow through the system
4. Responsibilities of each layer
5. Technology stack relationships

Use this as a reference when developing and explaining your work!
