"""
Custom exceptions for the ReliQuary SDK.
This module defines specific exception types for different error conditions.
"""

class ReliQuaryError(Exception):
    """Base exception for all ReliQuary SDK errors"""
    pass


class ReliQuaryAPIError(ReliQuaryError):
    """Exception raised for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ReliQuaryAuthError(ReliQuaryAPIError):
    """Exception raised for authentication-related errors"""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)


class ReliQuaryValidationError(ReliQuaryError):
    """Exception raised for data validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ReliQuaryConsensusError(ReliQuaryError):
    """Exception raised for consensus-related errors"""
    def __init__(self, message: str, request_id: Optional[str] = None):
        self.message = message
        self.request_id = request_id
        super().__init__(self.message)


class ReliQuaryZKError(ReliQuaryError):
    """Exception raised for zero-knowledge proof errors"""
    def __init__(self, message: str, proof_id: Optional[str] = None):
        self.message = message
        self.proof_id = proof_id
        super().__init__(self.message)


class ReliQuaryVaultError(ReliQuaryError):
    """Exception raised for vault-related errors"""
    def __init__(self, message: str, vault_id: Optional[str] = None):
        self.message = message
        self.vault_id = vault_id
        super().__init__(self.message)


class ReliQuaryNetworkError(ReliQuaryAPIError):
    """Exception raised for network connectivity errors"""
    def __init__(self, message: str):
        super().__init__(message)


class ReliQuaryTimeoutError(ReliQuaryAPIError):
    """Exception raised for request timeout errors"""
    def __init__(self, message: str):
        super().__init__(message, status_code=408)