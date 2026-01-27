# Sri Lankan G.C.E Certificate Verification System
## Academic Project - Blockchain & Cyber Security Module

### 🎯 Project Demonstration Guide

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Blockchain Concepts Demonstrated](#blockchain-concepts-demonstrated)
3. [Cyber Security Features](#cyber-security-features)
4. [Setup Instructions](#setup-instructions)
5. [Demonstration Scenarios](#demonstration-scenarios)
6. [Demo API Endpoints](#demo-api-endpoints)
7. [Evaluation Criteria Mapping](#evaluation-criteria-mapping)

---

## 🎯 Project Overview

This system solves a **real-world problem** in Sri Lanka: The fraudulent use of fake G.C.E O/L and A/L certificates. By leveraging blockchain technology, we create an **immutable, transparent, and tamper-proof** verification system.

### The Problem
- Physical certificates can be easily forged
- Manual verification is time-consuming and unreliable
- No centralized, trustworthy database accessible to employers
- Department of Examinations has limited verification capacity

### Our Solution
A blockchain-based verification system that provides:
- **Immutable storage** of certificate hashes
- **Instant verification** via 3 different methods
- **Tamper detection** through cryptographic hashing
- **Audit trail** - all operations logged permanently

---

## 🔗 Blockchain Concepts Demonstrated

### 1. Immutability
```
Once a certificate is registered on the blockchain, it CANNOT be modified.
This is demonstrated by trying to register the same hash twice - it fails!
```

### 2. Local Ethereum Network (Hardhat)
```
Hardhat runs a local Ethereum Virtual Machine (EVM) that:
- Behaves exactly like real Ethereum mainnet
- Provides 20 test accounts with 10,000 ETH each
- Mines blocks instantly for fast testing
- Uses same Solidity smart contracts as production
```

### 3. Smart Contract
```solidity
// Our contract demonstrates:
- State management (certificate storage)
- Access control (authorized issuers only)
- Events for audit trail
- Gas optimization techniques
```

### 4. Cryptographic Hashing (SHA-256)
```
SHA-256 hashes are used for:
- Document verification (file integrity)
- Results hash (detect grade tampering)
- Personal info hash (privacy protection)
```

### 5. Digital Signatures (ECDSA)
```
Every transaction is signed with a private key:
- Proves identity of the issuer
- Non-repudiation (issuer cannot deny action)
- Uses secp256k1 curve (same as Bitcoin)
```

---

## 🔐 Cyber Security Features

### 1. Authentication & Authorization
- **Ownable pattern**: Only owner can authorize issuers
- **Role-based access**: Only authorized addresses can register certificates

### 2. Data Integrity
- **Document hash**: Verify certificate hasn't been altered
- **Results hash**: Detect tampering of grades
- **Blockchain immutability**: Data cannot be changed after storage

### 3. Non-Repudiation
- **Event logging**: All actions recorded with timestamps
- **Issuer tracking**: Every certificate linked to issuer address
- **Audit trail**: Anyone can verify transaction history

### 4. Privacy Protection
- **Student info hash**: Personal data not stored directly
- **Hash instead of plaintext**: GDPR-compliant approach
- **Selective disclosure**: Show only necessary information

### 5. Tamper Detection
```python
# If someone changes grades in database:
stored_hash = blockchain.get_results_hash(doc_hash)
current_hash = calculate_hash(current_grades)
if stored_hash != current_hash:
    alert("TAMPERING DETECTED!")
```

---

## 🚀 Setup Instructions

### Prerequisites
1. Docker & Docker Compose installed
2. Git installed

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd Document-Verification-System

# Start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:5000
# - Blockchain (Hardhat): http://localhost:8545
```

### Verify Setup
```bash
# Check blockchain status
curl http://localhost:5000/api/certificate/blockchain-status
```

---

## 🎬 Demonstration Scenarios

### Demo 1: Show Blockchain Network
```
Endpoint: GET /api/certificate/demo/blockchain-info

Shows:
- 20 test accounts with 10,000 ETH each
- Block information (hash, number, timestamp)
- Smart contract address
- Network configuration
```

### Demo 2: Hash Demonstration (IMPORTANT!)
```
Endpoint: POST /api/certificate/demo/hash-demonstration
Body: {"text": "Mathematics: A, Science: B"}

Shows:
- Original hash
- Adding ONE SPACE → completely different hash
- Changing ONE character → completely different hash
- AVALANCHE EFFECT demonstration
```

### Demo 3: Certificate Registration
```
Endpoint: POST /api/certificate/register

Shows:
- Certificate stored on blockchain
- Transaction hash generated
- Block number recorded
- Issuer address captured
```

### Demo 4: Three Verification Methods
```
Method 1: POST /api/certificate/verify-by-code
- Quick lookup by human-readable code

Method 2: POST /api/certificate/verify-by-index
- Find all certificates for a student

Method 3: POST /api/certificate/verify
- Upload file, compare hash with blockchain
```

### Demo 5: Tamper Detection
```
Endpoint: POST /api/certificate/demo/tamper-detection

Shows:
- Original results → hash matches blockchain
- Modified results → hash DOESN'T match
- "TAMPERING DETECTED!" message
```

### Demo 6: Immutability Test
```
Endpoint: POST /api/certificate/demo/immutability-test

Shows:
- Try to register same document hash twice
- Smart contract REJECTS duplicate
- Data is IMMUTABLE
```

### Demo 7: Digital Signatures
```
Endpoint: GET /api/certificate/demo/digital-signature

Shows:
- ECDSA algorithm explanation
- secp256k1 curve (same as Bitcoin!)
- How private key signs transactions
- Non-repudiation concept
```

---

## 📡 Demo API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/certificate/demo/blockchain-info` | GET | Network, blocks, accounts |
| `/api/certificate/demo/hash-demonstration` | POST | SHA-256 avalanche effect |
| `/api/certificate/demo/digital-signature` | GET | ECDSA signatures explained |
| `/api/certificate/demo/gas-explanation` | GET | Transaction costs |
| `/api/certificate/demo/immutability-test` | POST | Cannot modify data |
| `/api/certificate/demo/tamper-detection` | POST | Detect grade changes |
| `/api/certificate/demo/event-logs/{hash}` | GET | Audit trail |
| `/api/certificate/demo/full-workflow` | GET | Complete system explanation |

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Verification │  │  Dashboard  │  │     Admin Panel        │ │
│  │    Forms     │  │   Stats     │  │   (Certificate Mgmt)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────┐
│                      BACKEND (Flask + Web3.py)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Certificate │  │  Blockchain │  │      Hash Service       │ │
│  │   Service   │  │   Service   │  │    (SHA-256 Utils)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
┌────────────▼────────────┐    ┌──────────────▼──────────────────┐
│      PostgreSQL         │    │     Hardhat Local Blockchain    │
│    (Relational Data)    │    │  ┌─────────────────────────┐   │
│  ┌──────────────────┐   │    │  │ Ethereum Virtual Machine │   │
│  │ Students Table   │   │    │  │ 20 Test Accounts         │   │
│  │ Certificates     │   │    │  │ Instant Mining           │   │
│  │ Results Table    │   │    │  │ Same as Real Ethereum    │   │
│  └──────────────────┘   │    │  └─────────────────────────┘   │
└─────────────────────────┘    └─────────────────────────────────┘
```

---

## ✅ Evaluation Criteria Mapping

| Criteria | Feature | How We Demonstrate |
|----------|---------|-------------------|
| **Blockchain Understanding** | Hardhat EVM | Show blocks, accounts, transactions |
| **Smart Contract Development** | Solidity 0.8 | Show contract code, deployment |
| **Cryptographic Concepts** | SHA-256, ECDSA | Hash demo, signature demo |
| **Cyber Security** | Access control, tamper detection | Demo endpoints |
| **Real-World Application** | Certificate verification | Full workflow demo |
| **Immutability** | Cannot modify data | Immutability test endpoint |
| **Privacy** | Hashed personal data | Show hashing instead of plaintext |
| **Audit Trail** | Event logs | Event logs endpoint |

---

## 💡 Key Talking Points for Presentation

### Why Blockchain?
> "Traditional databases have a single admin who can modify data. With blockchain, once data is written, even the system owner cannot change it. This ensures the Department of Examinations cannot be pressured to modify certificates."

### Why Hashing?
> "We don't store the certificate file on blockchain (too expensive). Instead, we store its SHA-256 hash - a unique fingerprint. If even one pixel changes in the certificate, the hash completely changes. This is called the AVALANCHE EFFECT."

### Why Hardhat?
> "Hardhat is a professional Ethereum development environment used by companies like Aave and Uniswap. It runs an Ethereum Virtual Machine (EVM) that behaves identically to mainnet. The same smart contract code works on any Ethereum network."

### Digital Signatures?
> "Every transaction uses ECDSA (Elliptic Curve Digital Signature Algorithm) - the same cryptography that secures billions of dollars in Bitcoin and Ethereum. The issuer's private key signs each registration, providing non-repudiation."

---

## 🛠️ Technologies Used

| Tool | Purpose | Why |
|------|---------|-----|
| Hardhat | Local blockchain | Industry standard, EVM compatible |
| Solidity | Smart contracts | Ethereum's native language |
| Web3.py | Blockchain interaction | Python library for Ethereum |
| React | Frontend | Modern UI framework |
| Flask | Backend API | Lightweight Python framework |
| PostgreSQL | Database | Relational data storage |
| Docker | Containerization | Easy deployment |

---

## 📊 Project Statistics

- **Smart Contract**: ~200 lines of Solidity
- **Backend Services**: 4 Python modules
- **Demo Endpoints**: 8 specialized APIs
- **Verification Methods**: 3
- **Security Patterns**: Access Control, Event Logging, Hash Verification
- **Blockchain Concepts**: Immutability, Hashing, Signatures, Consensus

---

*This documentation is part of the academic project submission for the Blockchain & Cyber Security module.*
