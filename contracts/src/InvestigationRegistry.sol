// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title InvestigationRegistry
 * @dev Anchors canonical SHA-256 / keccak256 hashes of ChainSleuth investigation reports.
 * Provides public, tamper-evident verification that a report existed in a specific state
 * at a specific timestamp without storing private data, full reports, or personal identifiers on-chain.
 */
contract InvestigationRegistry {
    struct ReportRecord {
        bytes32 reportHash;
        string reportId;
        string targetIdentifier;
        address reporter;
        uint256 registeredTimestamp;
        uint256 blockNumber;
        bool exists;
    }

    // Mapping from reportHash to ReportRecord
    mapping(bytes32 => ReportRecord) private _reports;

    // List of registered report hashes for discovery
    bytes32[] private _registeredHashes;

    // Events
    event ReportRegistered(
        bytes32 indexed reportHash,
        string reportId,
        string targetIdentifier,
        address indexed reporter,
        uint256 timestamp
    );

    // Custom errors for gas efficiency
    error ReportAlreadyRegistered(bytes32 reportHash, uint256 existingTimestamp);
    error InvalidReportHash();
    error InvalidReportId();

    /**
     * @notice Registers a new investigation report hash
     * @param reportHash The 32-byte cryptographic hash of the canonical report
     * @param reportId The internal identifier of the report
     * @param targetIdentifier The blockchain address or tx hash investigated
     */
    function registerReport(
        bytes32 reportHash,
        string calldata reportId,
        string calldata targetIdentifier
    ) external returns (bool) {
        if (reportHash == bytes32(0)) revert InvalidReportHash();
        if (bytes(reportId).length == 0) revert InvalidReportId();
        if (_reports[reportHash].exists) {
            revert ReportAlreadyRegistered(reportHash, _reports[reportHash].registeredTimestamp);
        }

        ReportRecord memory record = ReportRecord({
            reportHash: reportHash,
            reportId: reportId,
            targetIdentifier: targetIdentifier,
            reporter: msg.sender,
            registeredTimestamp: block.timestamp,
            blockNumber: block.number,
            exists: true
        });

        _reports[reportHash] = record;
        _registeredHashes.push(reportHash);

        emit ReportRegistered(
            reportHash,
            reportId,
            targetIdentifier,
            msg.sender,
            block.timestamp
        );

        return true;
    }

    /**
     * @notice Verifies if a report hash is registered
     * @param reportHash The 32-byte hash to verify
     * @return exists Whether the report hash is registered
     * @return timestamp The block timestamp when registered
     * @return blockNumber The block number when registered
     * @return reporter The address of the reporter
     * @return reportId The report ID
     * @return targetIdentifier The investigated target
     */
    function verifyReport(bytes32 reportHash)
        external
        view
        returns (
            bool exists,
            uint256 timestamp,
            uint256 blockNumber,
            address reporter,
            string memory reportId,
            string memory targetIdentifier
        )
    {
        ReportRecord memory record = _reports[reportHash];
        return (
            record.exists,
            record.registeredTimestamp,
            record.blockNumber,
            record.reporter,
            record.reportId,
            record.targetIdentifier
        );
    }

    /**
     * @notice Returns total number of registered reports
     */
    function totalRegisteredReports() external view returns (uint256) {
        return _registeredHashes.length;
    }

    /**
     * @notice Returns registered hash by index
     */
    function getReportHashAtIndex(uint256 index) external view returns (bytes32) {
        require(index < _registeredHashes.length, "Index out of bounds");
        return _registeredHashes[index];
    }
}
