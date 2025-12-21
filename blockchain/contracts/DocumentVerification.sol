// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerification {
    struct Document {
        string documentHash;
        string ipfsHash;
        address issuer;
        address owner;
        uint256 timestamp;
        bool isValid;
        string documentType;
    }
    
    mapping(string => Document) private documents;
    mapping(address => string[]) private userDocuments;
    
    event DocumentRegistered(
        string indexed documentHash,
        address indexed issuer,
        address indexed owner,
        uint256 timestamp
    );
    
    event DocumentRevoked(
        string indexed documentHash,
        uint256 timestamp
    );
    
    function registerDocument(
        string memory _documentHash,
        string memory _ipfsHash,
        address _owner,
        string memory _documentType
    ) public {
        require(bytes(documents[_documentHash].documentHash).length == 0, "Document already exists");
        
        documents[_documentHash] = Document({
            documentHash: _documentHash,
            ipfsHash: _ipfsHash,
            issuer: msg.sender,
            owner: _owner,
            timestamp: block.timestamp,
            isValid: true,
            documentType: _documentType
        });
        
        userDocuments[_owner].push(_documentHash);
        
        emit DocumentRegistered(_documentHash, msg.sender, _owner, block.timestamp);
    }
    
    function verifyDocument(string memory _documentHash) public view returns (
        bool exists,
        bool isValid,
        address issuer,
        address owner,
        uint256 timestamp,
        string memory documentType,
        string memory ipfsHash
    ) {
        Document memory doc = documents[_documentHash];
        
        if (bytes(doc.documentHash).length == 0) {
            return (false, false, address(0), address(0), 0, "", "");
        }
        
        return (
            true,
            doc.isValid,
            doc.issuer,
            doc.owner,
            doc.timestamp,
            doc.documentType,
            doc.ipfsHash
        );
    }
    
    function revokeDocument(string memory _documentHash) public {
        require(bytes(documents[_documentHash].documentHash).length > 0, "Document does not exist");
        require(documents[_documentHash].issuer == msg.sender, "Only issuer can revoke");
        
        documents[_documentHash].isValid = false;
        
        emit DocumentRevoked(_documentHash, block.timestamp);
    }
    
    function getUserDocuments(address _user) public view returns (string[] memory) {
        return userDocuments[_user];
    }
}