const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("DocumentVerification Contract - O/L & A/L Certificates", function () {
  let DocumentVerification;
  let contract;
  let owner;
  let issuer;
  let student1;
  let student2;

  beforeEach(async function () {
    // Get signers
    [owner, issuer, student1, student2] = await ethers.getSigners();

    // Deploy contract
    DocumentVerification = await ethers.getContractFactory("DocumentVerification");
    contract = await DocumentVerification.deploy();
    await contract.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await contract.owner()).to.equal(owner.address);
    });

    it("Should authorize owner as issuer by default", async function () {
      expect(await contract.isAuthorizedIssuer(owner.address)).to.be.true;
    });
  });

  describe("Issuer Management", function () {
    it("Should allow owner to authorize new issuer", async function () {
      await contract.authorizeIssuer(issuer.address);
      expect(await contract.isAuthorizedIssuer(issuer.address)).to.be.true;
    });

    it("Should emit IssuerAuthorized event", async function () {
      await expect(contract.authorizeIssuer(issuer.address))
        .to.emit(contract, "IssuerAuthorized")
        .withArgs(issuer.address, owner.address, await getLatestTimestamp());
    });

    it("Should not allow non-owner to authorize issuer", async function () {
      await expect(
        contract.connect(issuer).authorizeIssuer(student1.address)
      ).to.be.revertedWith("Only contract owner can perform this action");
    });

    it("Should allow owner to revoke issuer", async function () {
      await contract.authorizeIssuer(issuer.address);
      await contract.revokeIssuer(issuer.address);
      expect(await contract.isAuthorizedIssuer(issuer.address)).to.be.false;
    });

    it("Should not allow revoking owner", async function () {
      await expect(
        contract.revokeIssuer(owner.address)
      ).to.be.revertedWith("Cannot revoke owner");
    });
  });

  describe("Document Registration - O/L Certificates", function () {
    const docHash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef";
    const ipfsHash = "QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX";
    const studentIndex = "2023OL123456";
    const examYear = 2023;
    const examSubject = "General";

    it("Should register O/L certificate successfully", async function () {
      await contract.registerDocument(
        docHash,
        ipfsHash,
        student1.address,
        "O/L",
        studentIndex,
        examYear,
        examSubject
      );

      const result = await contract.verifyDocument(docHash);
      expect(result.exists).to.be.true;
      expect(result.isValid).to.be.true;
      expect(result.documentType).to.equal("O/L");
      expect(result.studentIndex).to.equal(studentIndex);
      expect(result.examYear).to.equal(examYear);
    });

    it("Should emit DocumentRegistered event", async function () {
      await expect(
        contract.registerDocument(
          docHash,
          ipfsHash,
          student1.address,
          "O/L",
          studentIndex,
          examYear,
          examSubject
        )
      ).to.emit(contract, "DocumentRegistered");
    });

    it("Should not allow duplicate registration", async function () {
      await contract.registerDocument(
        docHash,
        ipfsHash,
        student1.address,
        "O/L",
        studentIndex,
        examYear,
        examSubject
      );

      await expect(
        contract.registerDocument(
          docHash,
          ipfsHash,
          student1.address,
          "O/L",
          studentIndex,
          examYear,
          examSubject
        )
      ).to.be.revertedWith("Document already exists");
    });

    it("Should reject invalid document type", async function () {
      await expect(
        contract.registerDocument(
          docHash,
          ipfsHash,
          student1.address,
          "INVALID",
          studentIndex,
          examYear,
          examSubject
        )
      ).to.be.revertedWith("Document type must be O/L or A/L");
    });

    it("Should reject invalid exam year", async function () {
      await expect(
        contract.registerDocument(
          docHash,
          ipfsHash,
          student1.address,
          "O/L",
          studentIndex,
          1800,
          examSubject
        )
      ).to.be.revertedWith("Invalid exam year");
    });

    it("Should not allow unauthorized issuer to register", async function () {
      await expect(
        contract.connect(student1).registerDocument(
          docHash,
          ipfsHash,
          student1.address,
          "O/L",
          studentIndex,
          examYear,
          examSubject
        )
      ).to.be.revertedWith("Only authorized issuers can register documents");
    });
  });

  describe("Document Registration - A/L Certificates", function () {
    const docHash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890";
    const ipfsHash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG";
    const studentIndex = "2023AL789012";
    const examYear = 2023;
    const examSubject = "Physical Science";

    it("Should register A/L certificate successfully", async function () {
      await contract.registerDocument(
        docHash,
        ipfsHash,
        student2.address,
        "A/L",
        studentIndex,
        examYear,
        examSubject
      );

      const result = await contract.verifyDocument(docHash);
      expect(result.exists).to.be.true;
      expect(result.documentType).to.equal("A/L");
      expect(result.examSubject).to.equal(examSubject);
    });
  });

  describe("Document Verification", function () {
    const docHash = "0x1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff";
    const ipfsHash = "QmTest123456789";
    const studentIndex = "2023OL999999";

    beforeEach(async function () {
      await contract.registerDocument(
        docHash,
        ipfsHash,
        student1.address,
        "O/L",
        studentIndex,
        2023,
        "General"
      );
    });

    it("Should verify by document hash", async function () {
      const result = await contract.verifyDocument(docHash);
      expect(result.exists).to.be.true;
      expect(result.isValid).to.be.true;
      expect(result.owner).to.equal(student1.address);
    });

    it("Should verify by student index", async function () {
      const result = await contract.verifyByStudentIndex(studentIndex);
      expect(result.exists).to.be.true;
      expect(result.documentHash).to.equal(docHash);
    });

    it("Should return false for non-existent document", async function () {
      const result = await contract.verifyDocument("0xnonexistent");
      expect(result.exists).to.be.false;
    });
  });

  describe("Document Revocation", function () {
    const docHash = "0xrevoketest1234567890abcdef1234567890abcdef1234567890abcdef12345";
    const ipfsHash = "QmRevoke123";
    const studentIndex = "2023OL111111";

    beforeEach(async function () {
      await contract.registerDocument(
        docHash,
        ipfsHash,
        student1.address,
        "O/L",
        studentIndex,
        2023,
        "General"
      );
    });

    it("Should allow issuer to revoke document", async function () {
      await contract.revokeDocument(docHash);
      const result = await contract.verifyDocument(docHash);
      expect(result.isValid).to.be.false;
    });

    it("Should emit DocumentRevoked event", async function () {
      await expect(contract.revokeDocument(docHash))
        .to.emit(contract, "DocumentRevoked");
    });

    it("Should not allow non-issuer to revoke", async function () {
      await expect(
        contract.connect(student1).revokeDocument(docHash)
      ).to.be.revertedWith("Only issuer or owner can revoke");
    });

    it("Should not revoke already revoked document", async function () {
      await contract.revokeDocument(docHash);
      await expect(
        contract.revokeDocument(docHash)
      ).to.be.revertedWith("Document already revoked");
    });
  });

  describe("User Documents", function () {
    it("Should return all documents for a user", async function () {
      const hash1 = "0xuser1doc1";
      const hash2 = "0xuser1doc2";
      
      await contract.registerDocument(hash1, "ipfs1", student1.address, "O/L", "2023OL001", 2023, "General");
      await contract.registerDocument(hash2, "ipfs2", student1.address, "A/L", "2024AL001", 2024, "Science");

      const docs = await contract.getUserDocuments(student1.address);
      expect(docs.length).to.equal(2);
      expect(docs[0]).to.equal(hash1);
      expect(docs[1]).to.equal(hash2);
    });
  });

  // Helper function
  async function getLatestTimestamp() {
    const block = await ethers.provider.getBlock("latest");
    return block.timestamp;
  }
});
