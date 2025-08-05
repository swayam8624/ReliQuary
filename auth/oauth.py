# auth/oauth.py

import hmac
import hashlib
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from config_package import API_KEYS

# Use a custom API key header
# The client will send the API key in the 'X-API-Key' header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def hash_api_key(api_key: str) -> str:
    """Hashes the API key using a secure, constant-time algorithm for comparison."""
    # In a real-world app, use a proper hashing function with a salt and a secret key.
    # For now, a simple SHA-256 hash is used for demonstration.
    # NOTE: This is for demonstration. A proper implementation would use bcrypt or Argon2
    # and a secret salt stored in a secrets manager.
    return hashlib.sha256(api_key.encode()).hexdigest()

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validates the API key provided in the header.
    Returns the client's name if valid, raises HTTPException otherwise.
    """
    api_key_hash = hash_api_key(api_key)
    if api_key_hash in API_KEYS:
        return API_KEYS[api_key_hash]["client_name"]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key"
    )

def get_api_client_roles(api_key: str = Security(api_key_header)) -> list[str]:
    """
    Validates the API key and returns the roles associated with the client.
    """
    api_key_hash = hash_api_key(api_key)
    if api_key_hash in API_KEYS:
        return API_KEYS[api_key_hash]["roles"]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key"
    )