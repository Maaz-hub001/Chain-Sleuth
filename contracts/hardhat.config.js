require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: "./src",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  networks: {
    hardhat: {},
    sepolia: {
      url: process.env.REPORT_ANCHOR_RPC_URL || "https://rpc.ankr.com/eth_sepolia",
      accounts: process.env.REPORT_ANCHOR_PRIVATE_KEY ? [process.env.REPORT_ANCHOR_PRIVATE_KEY] : [],
    },
  },
};
