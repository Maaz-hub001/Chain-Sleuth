const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("InvestigationRegistry Contract", function () {
  let registry;
  let owner;
  let addr1;
  const sampleReportHash = ethers.keccak256(ethers.toUtf8Bytes("canonical-report-test-content-v1"));
  const sampleReportId = "rep-test-001";
  const sampleTarget = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e";

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    const InvestigationRegistry = await ethers.getContractFactory("InvestigationRegistry");
    registry = await InvestigationRegistry.deploy();
    await registry.waitForDeployment();
  });

  it("should deploy with zero registered reports", async function () {
    expect(await registry.totalRegisteredReports()).to.equal(0);
  });

  it("should successfully register a report hash and emit ReportRegistered event", async function () {
    const tx = await registry.connect(owner).registerReport(sampleReportHash, sampleReportId, sampleTarget);
    await expect(tx)
      .to.emit(registry, "ReportRegistered")
      .withArgs(sampleReportHash, sampleReportId, sampleTarget, owner.address, (await ethers.provider.getBlock("latest")).timestamp);

    expect(await registry.totalRegisteredReports()).to.equal(1);
    expect(await registry.getReportHashAtIndex(0)).to.equal(sampleReportHash);
  });

  it("should correctly verify a registered report", async function () {
    await registry.connect(owner).registerReport(sampleReportHash, sampleReportId, sampleTarget);

    const [exists, timestamp, blockNumber, reporter, reportId, targetIdentifier] =
      await registry.verifyReport(sampleReportHash);

    expect(exists).to.be.true;
    expect(timestamp).to.be.greaterThan(0);
    expect(blockNumber).to.be.greaterThan(0);
    expect(reporter).to.equal(owner.address);
    expect(reportId).to.equal(sampleReportId);
    expect(targetIdentifier).to.equal(sampleTarget);
  });

  it("should return exists=false for an unregistered report hash", async function () {
    const randomHash = ethers.keccak256(ethers.toUtf8Bytes("non-existent-hash"));
    const [exists] = await registry.verifyReport(randomHash);
    expect(exists).to.be.false;
  });

  it("should reject duplicate report registrations", async function () {
    await registry.connect(owner).registerReport(sampleReportHash, sampleReportId, sampleTarget);

    await expect(
      registry.connect(addr1).registerReport(sampleReportHash, "rep-test-002", sampleTarget)
    ).to.be.revertedWithCustomError(registry, "ReportAlreadyRegistered");
  });

  it("should reject invalid zero hash or empty report ID", async function () {
    await expect(
      registry.registerReport(ethers.ZeroHash, sampleReportId, sampleTarget)
    ).to.be.revertedWithCustomError(registry, "InvalidReportHash");

    await expect(
      registry.registerReport(sampleReportHash, "", sampleTarget)
    ).to.be.revertedWithCustomError(registry, "InvalidReportId");
  });
});
