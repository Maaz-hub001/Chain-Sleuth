const hre = require("hardhat");

async function main() {
  console.log("Deploying InvestigationRegistry contract...");

  const InvestigationRegistry = await hre.ethers.getContractFactory("InvestigationRegistry");
  const registry = await InvestigationRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log(`InvestigationRegistry successfully deployed to: ${contractAddress}`);
  console.log(`Update REPORT_REGISTRY_ADDRESS in your .env with: ${contractAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
