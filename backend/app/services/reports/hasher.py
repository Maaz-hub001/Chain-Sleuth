"""
Report Hasher: computes SHA-256 cryptographic digests of canonical reports.
"""
import hashlib
from typing import Dict, Any, Tuple
from app.services.reports.canonicalizer import canonical_json_bytes


def compute_report_hash(report_dict: Dict[str, Any]) -> Tuple[str, bytes]:
    """
    Computes standard SHA-256 hex digest of the canonical report bytes.
    Returns (hex_digest, canonical_bytes).
    """
    canon_bytes = canonical_json_bytes(report_dict)
    hex_digest = hashlib.sha256(canon_bytes).hexdigest()
    return hex_digest, canon_bytes


def verify_report_integrity(report_dict: Dict[str, Any], claimed_hash: str) -> Tuple[bool, str]:
    """
    Verifies if a report matches its claimed SHA-256 hash.
    Returns (is_valid, computed_hash).
    """
    computed_hash, _ = compute_report_hash(report_dict)
    is_valid = (computed_hash.lower() == claimed_hash.lower())
    return is_valid, computed_hash
