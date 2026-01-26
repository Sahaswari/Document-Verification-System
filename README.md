# Document Verification System

A blockchain-based document verification system for Sri Lanka Department of Examinations (DOE) G.C.E. O/L and A/L certificate issuing and verification. This system uses smart contracts to ensure document authenticity and provides secure certificate management.

---

## 🔐 Default Login Credentials

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| **Admin** | `admin` | `admin123` | Full system access |
| **Issuer** | `issuer` | `issuer123` | Certificate issuing officer |
| **Data Entry** | `dataentry` | `data123` | Data entry operator |
| **Verifier** | `verifier` | `verify123` | Verification officer |

### Access URLs
| Interface | URL | Description |
|-----------|-----|-------------|
| **Public Verification** | http://localhost:3000 | Verify certificates (no login required) |
| **Staff Login** | http://localhost:3000/login | Login for DOE staff |
| **Issuer Dashboard** | http://localhost:3000/issuer | Certificate issuing (after login) |
| **Backend API** | http://localhost:5000 | REST API endpoints |
| **Blockchain RPC** | http://localhost:8545 | Hardhat Ethereum node |

---

## 🗄️ Database Connection (PostgreSQL)

Connect using Navicat, pgAdmin, or any PostgreSQL client:

| Field | Value |
|-------|-------|
| **Host** | `localhost` |
| **Port** | `5432` |
| **Database** | `document_verification` |
| **Username** | `docverify` |
| **Password** | `docverify123` |

### Database Tables
- `students` - G.C.E exam candidates
- `exam_results` - O/L and A/L results with subjects
- `certificates` - Issued certificates with verification codes
- `users` - System users and authentication

---

## 🌱 Automatic Test Data Seeding

When the application starts with an **empty database**, it automatically seeds:

| Data Type | Count | Description |
|-----------|-------|-------------|
| **Students** | 100 | Sri Lankan students with realistic names, NICs, schools |
| **Exam Results** | 100 | O/L (60%) and A/L (40%) results with subjects |
| **Certificates** | ~15 | Sample issued certificates with verification codes |
| **Users** | 4 | System users (admin, issuer, data entry, verifier) |

### Seed Data Features
- **Realistic Sri Lankan Names**: Sinhala (80%) and Tamil (20%) names
- **Schools**: From all 9 provinces across Sri Lanka
- **Exam Types**: G.C.E O/L with 9 subjects, A/L with streams (Science, Commerce, Arts)
- **Grades**: Realistic grade distribution (A, B, C, S, W)
- **NIC Numbers**: Valid format based on date of birth
- **A/L Features**: Z-scores, district/island ranks

### Reset Database (Fresh Seed Data)
```bash
# Stop containers and remove database volume
docker-compose down -v

# Start again (fresh database with new seed data)
docker-compose up --build
```

---

## 🚀 Quick Start

### Run the Application

```bash
# Clone the repository
git clone <repo-url>
cd "Document Verification System"

# Start all services (blockchain + backend + frontend)
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d
```

### Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (clean slate)
docker-compose down -v
```

---

## 📋 Architecture & Components

### Blockchain Layer
- **Platform**: Ethereum with Hardhat development environment
- **Smart Contract Features**:
  - Document hash storage (SHA-256)
  - Timestamp and uploader address tracking
  - Document metadata management
  - Functions: `registerDocument()`, `verifyDocument()`, `getDocumentHistory()`
- **Privacy**: Only hashes stored on-chain (not full documents)

### AI/ML Layer

**OCR Component:**
- Tesseract OCR for text extraction from uploaded documents
- Support for multiple document formats

**NLP Analysis:**
- Detect inconsistencies (dates, formatting, language patterns)
- BERT-based semantic analysis
- Pattern comparison for alteration detection

**Forgery Detection:**
- Font and spacing analysis
- Metadata examination
- CNN-based image manipulation detection (cloning, splicing)
- Digital signature and watermark verification

### Frontend/Integration
- React-based web interface for document upload
- MetaMask integration for blockchain transactions
- Real-time verification results with confidence scores
- Document history and chain of custody display

---

## Project Structure

```
document-verification-system/
│
├── backend/                          # Python Flask Backend
│   ├── Dockerfile                    # Backend container setup
│   ├── .dockerignore                 # Docker ignore rules
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment variables
│   └── app/
│       ├── main.py                   # Flask application
│       ├── config.py                 # Configuration management
│       ├── api/                      # API endpoints
│       ├── models/                   # AI/ML Models
│       ├── schemas/                  # Data validation models
│       ├── services/                 # Business logic
│       └── utils/                    # Helper functions
│
├── blockchain/                       # Smart Contracts
│   ├── Dockerfile                    # Blockchain container setup
│   ├── .dockerignore                 # Docker ignore rules
│   ├── hardhat.config.js             # Hardhat configuration
│   ├── package.json                  # Node.js dependencies
│   ├── .env                          # Environment variables
│   ├── contracts/
│   │   └── DocumentVerification.sol  # Main smart contract
│   ├── scripts/
│   │   ├── deploy.js                 # Deployment script
│   │   └── verify.js                 # Verification script
│   └── test/
│       └── DocumentVerification.test.js
│
├── frontend/                         # React Application
│   ├── Dockerfile                    # Production build
│   ├── Dockerfile.dev                # Development build
│   ├── .dockerignore                 # Docker ignore rules
│   ├── nginx.conf                    # Nginx configuration
│   ├── package.json                  # Node.js dependencies
│   ├── .env                          # Environment variables
│   ├── public/
│   └── src/
│       ├── components/               # React components
│       ├── hooks/                    # Custom hooks
│       ├── contexts/                 # Context providers
│       ├── services/                 # API & blockchain services
│       ├── utils/                    # Utility functions
│       ├── pages/                    # Page components
│       ├── App.jsx
│       └── index.jsx
│
├── docker-compose.yml                # Docker orchestration
├── .gitignore
└── README.md
```

---

## Docker Setup Details

### Container Services

1. **Blockchain Container** (Port 8545)
   - Node.js 18 Alpine
   - Hardhat local Ethereum network
   - Automatic contract compilation
   - Hot-reload enabled

2. **Backend Container** (Port 5000)
   - Python 3.11
   - Flask web framework
   - Tesseract OCR
   - OpenCV for image processing
   - ML libraries (scikit-learn, numpy)
   - Web3 for blockchain interaction

3. **Frontend Container** (Port 3000)
   - Node.js 18 Alpine
   - React development server
   - Hot-reload enabled
   - Proxy to backend API

### Docker Commands Reference

```bash
# Build all containers
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build blockchain
docker-compose build frontend

# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f blockchain
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up --build

# Access container shell
docker exec -it doc-verify-backend bash
docker exec -it doc-verify-blockchain sh
docker exec -it doc-verify-frontend sh

# Check running containers
docker ps

# Check container resource usage
docker stats
```

---

## Development Workflow

### Making Code Changes

**Backend (Python):**
- Edit files in `backend/` folder
- Changes auto-reload (no restart needed)
- View logs: `docker-compose logs -f backend`

**Blockchain (Solidity):**
- Edit smart contracts in `blockchain/contracts/`
- Recompile: `docker exec -it doc-verify-blockchain npx hardhat compile`
- Deploy: `docker exec -it doc-verify-blockchain npx hardhat run scripts/deploy.js --network localhost`

**Frontend (React):**
- Edit files in `frontend/src/` folder
- Changes auto-reload (no restart needed)
- View logs: `docker-compose logs -f frontend`

### Testing

```bash
# Run backend tests
docker exec -it doc-verify-backend pytest

# Run blockchain tests
docker exec -it doc-verify-blockchain npx hardhat test

# Run frontend tests
docker exec -it doc-verify-frontend npm test
```

### Deploy Smart Contract

```bash
# Compile contracts
docker exec -it doc-verify-blockchain npx hardhat compile

# Deploy to local network
docker exec -it doc-verify-blockchain npx hardhat run scripts/deploy.js --network localhost

# Run Hardhat console
docker exec -it doc-verify-blockchain npx hardhat console --network localhost
```

---

## 🔧 Environment Configuration

### Backend (.env)
```env
FLASK_APP=app.main
FLASK_ENV=development
FLASK_DEBUG=1
BLOCKCHAIN_RPC_URL=http://blockchain:8545
CORS_ORIGINS=http://localhost:3000
```

### Blockchain (.env)
```env
NODE_ENV=development
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_BLOCKCHAIN_RPC=http://localhost:8545
```

---

## 📦 Technology Stack

### Backend
- **Framework**: Flask 3.0
- **OCR**: Tesseract, pytesseract
- **Image Processing**: OpenCV, Pillow
- **ML**: scikit-learn, numpy
- **Blockchain**: web3.py
- **Utilities**: python-dotenv, werkzeug

### Blockchain
- **Platform**: Ethereum
- **Development**: Hardhat 2.19
- **Contracts**: Solidity 0.8.20
- **Libraries**: OpenZeppelin Contracts

### Frontend
- **Framework**: React 18
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Blockchain**: ethers.js, web3.js
- **Build Tool**: React Scripts

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :5000
netstat -ano | findstr :3000
netstat -ano | findstr :8545

# Kill the process or change port in docker-compose.yml
ports:
  - "5001:5000"  # Use different host port
```

### Container Won't Start
```bash
# Check container logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache

# Remove all containers and start fresh
docker-compose down -v
docker-compose up --build
```

### Hot Reload Not Working (Windows)
Already configured in `docker-compose.yml`:
```yaml
environment:
  - CHOKIDAR_USEPOLLING=true
  - WATCHPACK_POLLING=true
```

### Connection Issues Between Services
- Use service names, not `localhost`
- Backend → Blockchain: `http://blockchain:8545`
- Frontend → Backend: `http://backend:5000` (inside container)
- Frontend → Backend: `http://localhost:5000` (from browser)

### Permission Errors
- **Windows**: Enable file sharing in Docker Desktop settings
- **Linux**: Add user to docker group: `sudo usermod -aG docker $USER`

---

## 📚 Additional Resources

### Hardhat Commands
```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Start local node
npx hardhat node

# Deploy contracts
npx hardhat run scripts/deploy.js --network localhost

# Clean artifacts
npx hardhat clean
```

### Flask Commands (inside container)
```bash
# Run development server
python -m flask run --host=0.0.0.0 --port=5000

# Run with auto-reload
python -m flask run --reload

# Access Flask shell
python -m flask shell
```
