"""
Tests for Canonical JSON serialization, SHA-256 integrity hashing, and tampering detection.
"""
from app.services.reports.canonicalizer import canonical_json_bytes
from app.services.reports.hasher import compute_report_hash, verify_report_integrity


def test_canonical_json_key_order_invariance():
    # Two dictionaries with identical keys in different insertion orders
    dict_a = {
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "chain_id": 1,
        "findings": [{"severity": "HIGH", "title": "Test"}]
    }
    dict_b = {
        "chain_id": 1,
        "findings": [{"title": "Test", "severity": "HIGH"}],
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }

    bytes_a = canonical_json_bytes(dict_a)
    bytes_b = canonical_json_bytes(dict_b)
    assert bytes_a == bytes_b


def test_canonical_json_ignores_mutable_fields():
    base_dict = {
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "chain_id": 1
    }
    augmented_dict = {
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "chain_id": 1,
        "report_id": "rep-different-id",
        "is_anchored": True,
        "registry_tx_hash": "0x123456",
        "view_count": 42
    }

    bytes_base = canonical_json_bytes(base_dict)
    bytes_aug = canonical_json_bytes(augmented_dict)
    assert bytes_base == bytes_aug


def test_sha256_report_tamper_detection():
    clean_report = {
        "investigation_id": "inv-001",
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "observed_facts": ["Fund flow verified"],
        "findings": [{"title": "Mixer Deposit", "severity": "CRITICAL"}]
    }

    original_hash, _ = compute_report_hash(clean_report)
    assert len(original_hash) == 64

    # Verify untampered report succeeds
    is_valid, _ = verify_report_integrity(clean_report, original_hash)
    assert is_valid is True

    # Tamper with 1 word in the findings
    tampered_report = {
        "investigation_id": "inv-001",
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "observed_facts": ["Fund flow verified"],
        "findings": [{"title": "Mixer Deposit", "severity": "LOW"}]  # Altered severity
    }

    is_valid_tampered, computed_tampered_hash = verify_report_integrity(tampered_report, original_hash)
    assert is_valid_tampered is False
    assert computed_tampered_hash != original_hash
