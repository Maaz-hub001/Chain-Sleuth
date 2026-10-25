"""
Domain exceptions and error handling for ChainSleuth.
"""
from typing import Optional, Any, Dict


class ChainSleuthException(Exception):
    """Base exception for all ChainSleuth domain errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationException(ChainSleuthException):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundException(ChainSleuthException):
    """Raised when an investigation, report, or entity is not found."""
    pass


class BlockchainProviderException(ChainSleuthException):
    """Raised when an external blockchain provider fails or returns malformed data."""
    pass


class RateLimitExceededException(ChainSleuthException):
    """Raised when provider or local rate limits are exceeded."""
    pass


class SecurityViolationException(ChainSleuthException):
    """Raised on security rule violations (e.g., SSRF, illegal URL)."""
    pass


class ReportTamperingException(ChainSleuthException):
    """Raised when a report's cryptographic signature or hash fails verification."""
    pass
