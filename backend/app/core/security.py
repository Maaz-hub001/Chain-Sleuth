"""
Security utilities: address validation, hash validation, SSRF protection, and sanitization.
"""
import re
import socket
import ipaddress
from urllib.parse import urlparse
from typing import Optional
from app.core.exceptions import ValidationException, SecurityViolationException

# Ethereum address: 0x followed by 40 hex characters
ETH_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")

# Transaction hash: 0x followed by 64 hex characters
TX_HASH_REGEX = re.compile(r"^0x[a-fA-F0-9]{64}$")

# Blocked IP networks for SSRF protection
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local & cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def validate_evm_address(address: str) -> str:
    """
    Validates and normalizes an EVM address.
    Returns normalized address with proper checksum or lowercase.
    """
    if not address or not isinstance(address, str):
        raise ValidationException("Address must be a non-empty string.")

    cleaned = address.strip()
    if not ETH_ADDRESS_REGEX.match(cleaned):
        raise ValidationException(
            f"Invalid EVM address '{address}'. Must be a 0x-prefixed 40-character hexadecimal string."
        )
    return cleaned


def validate_tx_hash(tx_hash: str) -> str:
    """
    Validates an EVM transaction hash.
    """
    if not tx_hash or not isinstance(tx_hash, str):
        raise ValidationException("Transaction hash must be a non-empty string.")

    cleaned = tx_hash.strip().lower()
    if not TX_HASH_REGEX.match(cleaned):
        raise ValidationException(
            f"Invalid transaction hash '{tx_hash}'. Must be a 0x-prefixed 64-character hexadecimal string."
        )
    return cleaned


def validate_target_identifier(target: str) -> tuple[str, str]:
    """
    Identifies if target is an address or a transaction hash.
    Returns (normalized_identifier, 'address' | 'transaction').
    """
    cleaned = target.strip()
    if ETH_ADDRESS_REGEX.match(cleaned):
        return cleaned, "address"
    elif TX_HASH_REGEX.match(cleaned.lower()):
        return cleaned.lower(), "transaction"
    else:
        raise ValidationException(
            f"Target '{target}' is neither a valid EVM address (0x + 40 hex) nor a transaction hash (0x + 64 hex)."
        )


def validate_public_url(url: str) -> str:
    """
    Strict SSRF validation: ensures URL is public, using http/https,
    and does not resolve to private/local/cloud-metadata networks.
    """
    if not url:
        raise ValidationException("URL cannot be empty.")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SecurityViolationException(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SecurityViolationException("URL does not contain a valid hostname.")

    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        raise SecurityViolationException(f"Access to private/local hostname '{hostname}' is blocked.")

    # Resolve IP address to check CIDRs
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
        for item in resolved_ips:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_NETWORKS:
                if ip_obj in blocked_net:
                    raise SecurityViolationException(
                        f"Resolved IP {ip_str} for host '{hostname}' resides in private/reserved network {blocked_net}."
                    )
    except socket.gaierror:
        # If DNS fails, reject
        raise ValidationException(f"Could not resolve host '{hostname}'.")

    return url
