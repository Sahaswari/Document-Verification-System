// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DocumentVerification
 * @dev Smart Contract for Sri Lankan O/L and A/L Certificate Verification
 * @notice This contract stores certificate hashes and metadata on the blockchain
 */
contract DocumentVerification {
    
    // Certificate types enum for O/L and A/L
    enum CertificateType { OL, AL }
    
    struct Document {
        string documentHash;        // SHA-256 hash of the certificate
        string ipfsHash;           // IPFS hash for metadata storage
        address issuer;            // Department of Examinations wallet address
        address owner;             // Student's wallet address
        uint256 timestamp;         // Registration timestamp
        bool isValid;             // Validity status
        string documentType;      // "O/L" or "A/L"
        string studentIndex;      // Student index number
        uint256 examYear;         // Year of examination
        string examSubject;       // Subject/Stream (for A/L: Science/Arts/Commerce)
    }
    
    // Mapping from document hash to document details
    mapping(string => Document) private documents;
    
    // Mapping from user address to their document hashes
    mapping(address => string[]) private userDocuments;
    
    // Mapping from student index to document hash (for quick lookups)
    mapping(string => string) private indexToDocument;
    
    // Authorized issuers (e.g., Department of Examinations)
    mapping(address => bool) public authorizedIssuers;
    
    // Contract owner (for issuer management)
    address public owner;
    
    // Events
    event DocumentRegistered(
        string indexed documentHash,
        address indexed issuer,
        address indexed owner,
        string documentType,
        string studentIndex,
        uint256 examYear,
        uint256 timestamp
    );
    
    event DocumentRevoked(
        string indexed documentHash,
        address indexed revokedBy,
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
     * @param _documentHash SHA-256 hash of the certificate
     * @param _ipfsHash IPFS hash for metadata storage
     * @param _owner Student's wallet address
     * @param _documentType "O/L" or "A/L"
     * @param _studentIndex Student's index number
     * @param _examYear Year of examination
     * @param _examSubject Subject or stream
     */
    function registerDocument(
        string memory _documentHash,
        string memory _ipfsHash,
        address _owner,
        string memory _documentType,
        string memory _studentIndex,
        uint256 _examYear,
        string memory _examSubject
    ) public onlyAuthorizedIssuer {
        require(bytes(documents[_documentHash].documentHash).length == 0, "Document already exists");
        require(bytes(_documentHash).length > 0, "Document hash cannot be empty");
        require(_owner != address(0), "Invalid owner address");
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
            ipfsHash: _ipfsHash,
            issuer: msg.sender,
            owner: _owner,
            timestamp: block.timestamp,
            isValid: true,
            documentType: _documentType,
            studentIndex: _studentIndex,
            examYear: _examYear,
            examSubject: _examSubject
        });
        
        // Add to user's document list
        userDocuments[_owner].push(_documentHash);
        
        // Map student index to document
        indexToDocument[_studentIndex] = _documentHash;
        
        emit DocumentRegistered(
            _documentHash, 
            msg.sender, 
            _owner, 
            _documentType,
            _studentIndex,
            _examYear,
            block.timestamp
        );
    }
    
    /**
     * @dev Verify a certificate by its hash
     * @param _documentHash SHA-256 hash of the certificate
     * @return exists Whether the certificate exists
     * @return isValid Whether the certificate is valid
     * @return issuer Address of the issuer
     * @return documentOwner Address of the certificate owner
     * @return timestamp Registration timestamp
     * @return documentType Type of certificate (OL/AL)
     * @return ipfsHash IPFS hash
     * @return studentIndex Student index number
     * @return examYear Examination year
     * @return examSubject Exam subject/stream
     */
    function verifyDocument(string memory _documentHash) public view returns (
        bool exists,
        bool isValid,
        address issuer,
        address documentOwner,
        uint256 timestamp,
        string memory documentType,
        string memory ipfsHash,
        string memory studentIndex,
        uint256 examYear,
        string memory examSubject
    ) {
        Document memory doc = documents[_documentHash];
        
        if (bytes(doc.documentHash).length == 0) {
            return (false, false, address(0), address(0), 0, "", "", "", 0, "");
        }
        
        return (
            true,
            doc.isValid,
            doc.issuer,
            doc.owner,
            doc.timestamp,
            doc.documentType,
            doc.ipfsHash,
            doc.studentIndex,
            doc.examYear,
            doc.examSubject
        );
    }
    
    /**
     * @dev Verify certificate by student index number
     * @param _studentIndex Student's index number
     * @return exists Whether the certificate exists
     * @return isValid Whether the certificate is valid
     * @return issuer Address of the issuer
     * @return documentOwner Address of the certificate owner
     * @return timestamp Registration timestamp
     * @return documentType Type of certificate (OL/AL)
     * @return ipfsHash IPFS hash
     * @return documentHash Document hash
     * @return examYear Examination year
     * @return examSubject Exam subject/stream
     */
    function verifyByStudentIndex(string memory _studentIndex) public view returns (
        bool exists,
        bool isValid,
        address issuer,
        address documentOwner,
        uint256 timestamp,
        string memory documentType,
        string memory ipfsHash,
        string memory documentHash,
        uint256 examYear,
        string memory examSubject
    ) {
        string memory docHash = indexToDocument[_studentIndex];
        
        if (bytes(docHash).length == 0) {
            return (false, false, address(0), address(0), 0, "", "", "", 0, "");
        }
        
        Document memory doc = documents[docHash];
        
        return (
            true,
            doc.isValid,
            doc.issuer,
            doc.owner,
            doc.timestamp,
            doc.documentType,
            doc.ipfsHash,
            doc.documentHash,
            doc.examYear,
            doc.examSubject
        );
    }
    
    /**
     * @dev Revoke/invalidate a certificate (only by original issuer or contract owner)
     * @param _documentHash SHA-256 hash of the certificate to revoke
     */
    function revokeDocument(string memory _documentHash) public {
        require(bytes(documents[_documentHash].documentHash).length > 0, "Document does not exist");
        require(
            documents[_documentHash].issuer == msg.sender || msg.sender == owner, 
            "Only issuer or owner can revoke"
        );
        require(documents[_documentHash].isValid, "Document already revoked");
        
        documents[_documentHash].isValid = false;
        
        emit DocumentRevoked(_documentHash, msg.sender, block.timestamp);
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
     * @dev Get document hash by student index
     * @param _studentIndex Student's index number
     * @return Document hash
     */
    function getDocumentByIndex(string memory _studentIndex) public view returns (string memory) {
        return indexToDocument[_studentIndex];
    }
}