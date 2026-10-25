"""
Tests for Address and Transaction Hash validation, plus SSRF protection.
"""
import pytest
from app.core.security import (
    validate_evm_address,
    validate_tx_hash,
    validate_target_identifier,
    validate_public_url
)
from app.core.exceptions import ValidationException, SecurityViolationException


def test_valid_evm_addresses():
    addr = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    assert validate_evm_address(addr) == addr

    clean, t_type = validate_target_identifier(addr)
    assert clean == addr
    assert t_type == "address"


def test_invalid_evm_addresses():
    with pytest.raises(ValidationException):
        validate_evm_address("0xInvalidTooShort")

    with pytest.raises(ValidationException):
        validate_evm_address("not_an_address")

    with pytest.raises(ValidationException):
        validate_evm_address("")


def test_valid_tx_hashes():
    h = "0x4a8f93e1b72c918c54129e0134bc571b0213aa4f73b610c1f6d90d8137f84210"
    assert validate_tx_hash(h) == h

    clean, t_type = validate_target_identifier(h)
    assert clean == h
    assert t_type == "transaction"


def test_invalid_tx_hashes():
    with pytest.raises(ValidationException):
        validate_tx_hash("0x1234")


def test_ssrf_protection_blocks_private_and_localhost():
    with pytest.raises(SecurityViolationException):
        validate_public_url("http://localhost:8000/api")

    with pytest.raises(SecurityViolationException):
        validate_public_url("http://127.0.0.1:5432")

    with pytest.raises(SecurityViolationException):
        validate_public_url("ftp://example.com/file")


def test_ssrf_allows_public_urls():
    url = "https://ethereum.org/en/developers/docs/"
    assert validate_public_url(url) == url
