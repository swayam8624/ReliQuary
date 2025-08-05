# config/api_config.py
import os
from pydantic_settings import BaseSettings

# --- FIX: Define project root to build absolute paths ---
# This ensures the database path is always correct.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class APISettings(BaseSettings):
    """
    Application settings for the FastAPI API.
    Reads from environment variables and provides defaults.
    """
    api_title: str = "RELIQUARY API"
    api_version: str = "v1"
    
    # WebAuthn and DID configuration
    rp_id: str = "localhost"  # Relying Party ID
    rp_name: str = "RELIQUARY" # Relying Party Name
    # --- FIX: Make origin a distinct, overridable setting ---
    rp_origin: str = "https://localhost:8000"

    # API key for OAuth authentication
    # In production, this should be read from a secrets manager.
    api_key_vault_admin: str = "supersecretclient1key"
    api_key_read_only: str = "anothersecretclient2key"
    
    # --- FIX: Use an absolute path for the database ---
    db_path: str = os.path.join(PROJECT_ROOT, 'auth', 'webauthn', 'keys.db')

# Instantiate the settings for use in the application
settings = APISettings()

if __name__ == "__main__":
    print("--- API Settings Test ---")
    print(f"API Title: {settings.api_title}")
    print(f"RP ID: {settings.rp_id}")
    print(f"RP Origin: {settings.rp_origin}")
    print(f"DB Path: {settings.db_path}") # Added for verification
    print("✅ API config loaded successfully.")