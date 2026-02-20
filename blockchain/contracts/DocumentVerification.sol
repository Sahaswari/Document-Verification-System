// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DocumentVerification
 * @dev Smart Contract for Sri Lankan G.C.E O/L and A/L Certificate Verification
 * @notice This contract implements industry best practices for educational certificate verification:
 *         - Minimal on-chain data storage (hashes instead of raw data for privacy/GDPR compliance)
 *         - Multiple verification pathways (certificate ID, student index, document hash)
 *         - Tamper detection through cryptographic hashes of results
 *         - Immutable audit trail with timestamps
 *         - Revocation capability for compromised certificates
 * 
 * @dev Best Practices Implemented:
 *      1. Privacy: Personal data stored as hashes, not plain text
 *      2. Gas Efficiency: Minimal storage, using hashes for large data
 *      3. Security: Only authorized issuers can register/revoke
 *      4. Verifiability: Multiple lookup methods for flexibility
 *      5. Integrity: Results hash ensures grade tampering detection
 */
contract DocumentVerification {
    
    // Certificate types enum for O/L and A/L
    enum CertificateType { OL, AL }
    
    /**
     * @dev Certificate structure following best practices:
     *      - documentHash: Hash of PDF for file integrity verification
     *      - resultsHash: Hash of JSON results for grade tampering detection
     *      - verificationCode: Human-readable verification code
     *      - Personal data stored as hash for GDPR/privacy compliance
     */
    struct Document {
        string documentHash;        // SHA-256 hash of the certificate PDF
        string resultsHash;         // SHA-256 hash of exam results JSON (for integrity)
        string verificationCode;    // Human-readable code (e.g., "DOE-OL2024-A1B2C3D4")
        string studentInfoHash;     // Hash of student personal info (privacy protection)
        address issuer;             // Department of Examinations wallet address
        address owner;              // Student's wallet address (or zero address if not linked)
        uint256 timestamp;          // Registration timestamp (immutable audit trail)
        bool isValid;               // Validity status (can be revoked)
        string documentType;        // "O/L" or "A/L"
        string studentIndex;        // Student index number (searchable)
        uint256 examYear;           // Year of examination
        string examSubject;         // Subject/Stream (for A/L: Science/Arts/Commerce)
    }
    
    // Mapping from document hash to document details
    mapping(string => Document) private documents;
    
    // Mapping from user address to their document hashes
    mapping(address => string[]) private userDocuments;
    
    // Mapping from student index to document hashes (supports multiple certificates per student)
    mapping(string => string[]) private indexToDocuments;
    
    // Mapping from verification code to document hash (for quick lookups)
    mapping(string => string) private codeToDocument;
    
    // Authorized issuers (e.g., Department of Examinations)
    mapping(address => bool) public authorizedIssuers;
    
    // Contract owner (for issuer management)
    address public owner;
    
    // Statistics for transparency
    uint256 public totalCertificates;
    uint256 public totalRevoked;
    
    // Events
    event DocumentRegistered(
        string indexed documentHash,
        string verificationCode,
        address indexed issuer,
        address indexed owner,
        string documentType,
        string studentIndex,
        uint256 examYear,
        uint256 timestamp
    );
    
    event DocumentRevoked(
        string indexed documentHash,
        string verificationCode,
        address indexed revokedBy,
        string reason,
        uint256 timestamp
    );
    
    event IssuerAuthorized(
        address indexed issuer,
        address indexed authorizedBy,
        uint256 timestamp
    );
    
    event IssuerRevoked(
        address indexed issuer,
        address indexed revokedBy,
        uint256 timestamp
    );
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender], "Only authorized issuers can register documents");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true; // Owner is an authorized issuer by default
    }
    
    /**
     * @dev Authorize a new issuer (e.g., Department of Examinations)
     * @param _issuer Address to be authorized
     */
    function authorizeIssuer(address _issuer) public onlyOwner {
        require(!authorizedIssuers[_issuer], "Issuer already authorized");
        authorizedIssuers[_issuer] = true;
        emit IssuerAuthorized(_issuer, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Revoke an issuer's authorization
     * @param _issuer Address to be revoked
     */
    function revokeIssuer(address _issuer) public onlyOwner {
        require(authorizedIssuers[_issuer], "Issuer not authorized");
        require(_issuer != owner, "Cannot revoke owner");
        authorizedIssuers[_issuer] = false;
        emit IssuerRevoked(_issuer, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Register a new O/L or A/L certificate on the blockchain
     * @param _documentHash SHA-256 hash of the certificate PDF
     * @param _resultsHash SHA-256 hash of the exam results JSON (for tamper detection)
     * @param _verificationCode Human-readable verification code
     * @param _studentInfoHash Hash of student personal information
     * @param _owner Student's wallet address (can be zero address)
     * @param _documentType "O/L" or "A/L"
     * @param _studentIndex Student's index number
     * @param _examYear Year of examination
     * @param _examSubject Subject or stream
     */
    function registerDocument(
        string memory _documentHash,
        string memory _resultsHash,
        string memory _verificationCode,
        string memory _studentInfoHash,
        address _owner,
        string memory _documentType,
        string memory _studentIndex,
        uint256 _examYear,
        string memory _examSubject
    ) public onlyAuthorizedIssuer {
        require(bytes(documents[_documentHash].documentHash).length == 0, "Document already exists");
        require(bytes(_documentHash).length > 0, "Document hash cannot be empty");
        require(bytes(_verificationCode).length > 0, "Verification code cannot be empty");
        require(bytes(codeToDocument[_verificationCode]).length == 0, "Verification code already used");
        require(bytes(_studentIndex).length > 0, "Student index cannot be empty");
        require(_examYear >= 1900 && _examYear <= 2100, "Invalid exam year");
        
        // Validate document type
        require(
            keccak256(bytes(_documentType)) == keccak256(bytes("O/L")) || 
            keccak256(bytes(_documentType)) == keccak256(bytes("A/L")),
            "Document type must be O/L or A/L"
        );
        
        // Create document record
        documents[_documentHash] = Document({
            documentHash: _documentHash,
            resultsHash: _resultsHash,
            verificationCode: _verificationCode,
            studentInfoHash: _studentInfoHash,
            issuer: msg.sender,
            owner: _owner,
            timestamp: block.timestamp,
            isValid: true,
            documentType: _documentType,
            studentIndex: _studentIndex,
            examYear: _examYear,
            examSubject: _examSubject
        });
        
        // Add to user's document list (if owner provided)
        if (_owner != address(0)) {
            userDocuments[_owner].push(_documentHash);
        }
        
        // Map student index to document (supports multiple certs per student)
        indexToDocuments[_studentIndex].push(_documentHash);
        
        // Map verification code to document
        codeToDocument[_verificationCode] = _documentHash;
        
        // Update statistics
        totalCertificates++;
        
        emit DocumentRegistered(
            _documentHash,
            _verificationCode,
            msg.sender, 
            _owner, 
            _documentType,
            _studentIndex,
            _examYear,
            block.timestamp
        );
    }
    
    /**
     * @dev Verify a certificate by its document hash (Method 3: File Upload)
     * @param _documentHash SHA-256 hash of the certificate
     * @return exists Whether the certificate exists
     * @return isValid Whether the certificate is valid
     * @return issuer Address of the issuer
     * @return documentOwner Address of the certificate owner
     * @return timestamp Registration timestamp
     * @return documentType Type of certificate (OL/AL)
     * @return verificationCode Human-readable verification code
     * @return resultsHash Hash of exam results for integrity check
     * @return studentIndex Student index number
     * @return examYear Examination year
     */
    function verifyDocument(string memory _documentHash) public view returns (
        bool exists,
        bool isValid,
        address issuer,
        address documentOwner,
        uint256 timestamp,
        string memory documentType,
        string memory verificationCode,
        string memory resultsHash,
        string memory studentIndex,
        uint256 examYear
    ) {
        Document memory doc = documents[_documentHash];
        
        if (bytes(doc.documentHash).length == 0) {
            return (false, false, address(0), address(0), 0, "", "", "", "", 0);
        }
        
        return (
            true,
            doc.isValid,
            doc.issuer,
            doc.owner,
            doc.timestamp,
            doc.documentType,
            doc.verificationCode,
            doc.resultsHash,
            doc.studentIndex,
            doc.examYear
        );
    }
    
    /**
     * @dev Verify a certificate by verification code (Method 1: Certificate ID)
     * @param _verificationCode Human-readable verification code
     * @return exists Whether the certificate exists
     * @return isValid Whether the certificate is valid
     * @return documentHash The document hash
     * @return resultsHash Hash of exam results
     * @return documentType Type of certificate (OL/AL)
     * @return studentIndex Student index number
     * @return examYear Examination year
     * @return examSubject Subject/Stream
     * @return timestamp Registration timestamp
     * @return issuer Address of the issuer
     */
    function verifyByCode(string memory _verificationCode) public view returns (
        bool exists,
        bool isValid,
        string memory documentHash,
        string memory resultsHash,
        string memory documentType,
        string memory studentIndex,
        uint256 examYear,
        string memory examSubject,
        uint256 timestamp,
        address issuer
    ) {
        string memory docHash = codeToDocument[_verificationCode];
        
        if (bytes(docHash).length == 0) {
            return (false, false, "", "", "", "", 0, "", 0, address(0));
        }
        
        Document memory doc = documents[docHash];
        
        return (
            true,
            doc.isValid,
            doc.documentHash,
            doc.resultsHash,
            doc.documentType,
            doc.studentIndex,
            doc.examYear,
            doc.examSubject,
            doc.timestamp,
            doc.issuer
        );
    }
    
    /**
     * @dev Verify certificate by student index number (Method 2: Student Index)
     *      Returns the most recent certificate for the student
     * @param _studentIndex Student's index number
     * @return exists Whether any certificate exists
     * @return isValid Whether the certificate is valid
     * @return documentHash The document hash
     * @return resultsHash Hash of exam results for integrity verification
     * @return verificationCode Human-readable code
     * @return documentType Type of certificate (OL/AL)
     * @return examYear Examination year
     * @return examSubject Subject/Stream
     * @return timestamp Registration timestamp
     * @return certificateCount Total certificates for this student
     */
    function verifyByStudentIndex(string memory _studentIndex) public view returns (
        bool exists,
        bool isValid,
        string memory documentHash,
        string memory resultsHash,
        string memory verificationCode,
        string memory documentType,
        uint256 examYear,
        string memory examSubject,
        uint256 timestamp,
        uint256 certificateCount
    ) {
        string[] memory docHashes = indexToDocuments[_studentIndex];
        
        if (docHashes.length == 0) {
            return (false, false, "", "", "", "", 0, "", 0, 0);
        }
        
        // Return the most recent certificate (last in array)
        string memory latestHash = docHashes[docHashes.length - 1];
        Document memory doc = documents[latestHash];
        
        return (
            true,
            doc.isValid,
            doc.documentHash,
            doc.resultsHash,
            doc.verificationCode,
            doc.documentType,
            doc.examYear,
            doc.examSubject,
            doc.timestamp,
            docHashes.length
        );
    }
    
    /**
     * @dev Get all certificates for a student index
     * @param _studentIndex Student's index number
     * @return Array of document hashes
     */
    function getStudentCertificates(string memory _studentIndex) public view returns (string[] memory) {
        return indexToDocuments[_studentIndex];
    }
    
    /**
     * @dev Verify results integrity by comparing stored hash
     * @param _documentHash Document hash
     * @param _providedResultsHash Hash to compare against stored hash
     * @return matches Whether the provided hash matches stored hash
     * @return storedHash The hash stored on blockchain
     */
    function verifyResultsIntegrity(
        string memory _documentHash, 
        string memory _providedResultsHash
    ) public view returns (bool matches, string memory storedHash) {
        Document memory doc = documents[_documentHash];
        
        if (bytes(doc.documentHash).length == 0) {
            return (false, "");
        }
        
        bool hashMatches = keccak256(bytes(doc.resultsHash)) == keccak256(bytes(_providedResultsHash));
        return (hashMatches, doc.resultsHash);
    }
    
    /**
     * @dev Revoke/invalidate a certificate (only by original issuer or contract owner)
     * @param _documentHash SHA-256 hash of the certificate to revoke
     * @param _reason Reason for revocation
     */
    function revokeDocument(string memory _documentHash, string memory _reason) public {
        require(bytes(documents[_documentHash].documentHash).length > 0, "Document does not exist");
        require(
            documents[_documentHash].issuer == msg.sender || msg.sender == owner, 
            "Only issuer or owner can revoke"
        );
        require(documents[_documentHash].isValid, "Document already revoked");
        
        documents[_documentHash].isValid = false;
        totalRevoked++;
        
        emit DocumentRevoked(
            _documentHash, 
            documents[_documentHash].verificationCode,
            msg.sender, 
            _reason,
            block.timestamp
        );
    }
    
    /**
     * @dev Get all certificates owned by a user
     * @param _user User's wallet address
     * @return Array of document hashes
     */
    function getUserDocuments(address _user) public view returns (string[] memory) {
        return userDocuments[_user];
    }
    
    /**
     * @dev Check if an address is an authorized issuer
     * @param _issuer Address to check
     * @return bool indicating if authorized
     */
    function isAuthorizedIssuer(address _issuer) public view returns (bool) {
        return authorizedIssuers[_issuer];
    }
    
    /**
     * @dev Get document hash by verification code
     * @param _verificationCode Verification code
     * @return Document hash
     */
    function getDocumentByCode(string memory _verificationCode) public view returns (string memory) {
        return codeToDocument[_verificationCode];
    }
    
    /**
     * @dev Get contract statistics
     * @return total Total certificates registered
     * @return revoked Total certificates revoked
     * @return active Total active certificates
     */
    function getStatistics() public view returns (uint256 total, uint256 revoked, uint256 active) {
        return (totalCertificates, totalRevoked, totalCertificates - totalRevoked);
    }
}