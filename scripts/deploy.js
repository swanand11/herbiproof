import hre from "hardhat";
import "@nomicfoundation/hardhat-ethers";

async function main() {
  try {
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contract with:", deployer.address);
    console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

    const CropToken = await hre.ethers.getContractFactory("CropToken");
    const cropToken = await CropToken.deploy();

    await cropToken.waitForDeployment();
    const contractAddress = await cropToken.getAddress();
    
    console.log("CropToken deployed at:", contractAddress);
    
    // Save deployment info
    console.log("\n=== Deployment Summary ===");
    console.log("Contract Name: CropToken");
    console.log("Contract Address:", contractAddress);
    console.log("Deployer Address:", deployer.address);
    console.log("Network:", hre.network.name);
    
  } catch (error) {
    console.error("Deployment failed:", error);
    throw error;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});