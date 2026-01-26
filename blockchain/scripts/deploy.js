/**
 * Deployment Script for DocumentVerification Smart Contract
 * This script deploys the contract to the local Hardhat network
 */

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Starting deployment process...\n");

  // Get the contract factory
  const DocumentVerification = await hre.ethers.getContractFactory("DocumentVerification");
  
  console.log("Deploying DocumentVerification contract...");
  
  // Deploy the contract
  const documentVerification = await DocumentVerification.deploy();
  await documentVerification.waitForDeployment();

  const contractAddress = await documentVerification.getAddress();
  
  console.log("✅ DocumentVerification contract deployed successfully!");
  console.log("📍 Contract Address:", contractAddress);
  console.log("🌐 Network:", hre.network.name);
  console.log("⛽ Gas Used: Estimated during deployment\n");

  // Get deployer information
  const [deployer] = await hre.ethers.getSigners();
  console.log("👤 Deployed by:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("💰 Deployer Balance:", hre.ethers.formatEther(balance), "ETH\n");

  // Save contract address and ABI to a JSON file for backend integration
  const contractData = {
    address: contractAddress,
    network: hre.network.name,
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
    abi: JSON.parse(documentVerification.interface.formatJson())
  };

  // Save to blockchain/deployed directory
  const deployedDir = path.join(__dirname, "..", "deployed");
  if (!fs.existsSync(deployedDir)) {
    fs.mkdirSync(deployedDir, { recursive: true });
  }

  const contractDataPath = path.join(deployedDir, "DocumentVerification.json");
  fs.writeFileSync(contractDataPath, JSON.stringify(contractData, null, 2));
  console.log("📄 Contract data saved to:", contractDataPath);

  // Also save to backend directory for easy access
  const backendContractDir = path.join(__dirname, "..", "..", "backend", "app", "contracts");
  if (!fs.existsSync(backendContractDir)) {
    fs.mkdirSync(backendContractDir, { recursive: true });
  }

  const backendContractPath = path.join(backendContractDir, "DocumentVerification.json");
  fs.writeFileSync(backendContractPath, JSON.stringify(contractData, null, 2));
  console.log("📄 Contract data copied to backend:", backendContractPath);

  console.log("\n🎉 Deployment completed successfully!");
  console.log("\n📝 Next Steps:");
  console.log("1. The contract is now live on the blockchain");
  console.log("2. Use the contract address in your backend/frontend");
  console.log("3. Contract ABI is saved for interaction");
  console.log("4. Test the contract using: npm run test");
}

// Execute deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
