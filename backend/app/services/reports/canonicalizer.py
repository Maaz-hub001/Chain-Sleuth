"""
Canonical JSON Serializer for Tamper-Evident Report Verification.
Ensures deterministic, reproducible byte representations across platforms.
"""
import json
from typing import Any, Dict


# Excluded mutable fields that must not alter report cryptographic integrity
EXCLUDED_HASH_FIELDS = {
    "report_id",
    "is_anchored",
    "registry_chain_id",
    "registry_contract_address",
    "registry_tx_hash",
    "anchored_timestamp",
    "verification_details",
    "view_count",
    "last_viewed_at"
}


def _canonicalize_obj(obj: Any) -> Any:
    """Recursively formats and strips non-canonical mutable fields."""
    if isinstance(obj, dict):
        clean_dict = {}
        for k in sorted(obj.keys()):
            if k in EXCLUDED_HASH_FIELDS:
                continue
            clean_dict[k] = _canonicalize_obj(obj[k])
        return clean_dict
    elif isinstance(obj, list):
        return [_canonicalize_obj(item) for item in obj]
    elif isinstance(obj, float):
        # Prevent floating-point decimal representation quirks
        return round(obj, 6)
    else:
        return obj


def canonical_json_bytes(report_dict: Dict[str, Any]) -> bytes:
    """
    Serializes report into deterministic canonical UTF-8 bytes:
    - Excludes mutable tracking keys
    - Sorted keys recursively
    - Compact separators (',', ':')
    - No trailing whitespace
    """
    cleaned = _canonicalize_obj(report_dict)
    json_str = json.dumps(
        cleaned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True
    )
    return json_str.encode("utf-8")
