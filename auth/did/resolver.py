# auth/did/resolver.py

import sqlite3
import json
import os
import sys
import cbor2
import traceback
from webauthn.helpers import bytes_to_base64url
from typing import Optional, Dict, Any

class DIDDocument:
    """Represents a DID Document"""
    def __init__(self, did: str, verification_methods: list, authentication: list):
        self.id = did
        self.verificationMethod = verification_methods
        self.authentication = authentication
        self.context = "https://www.w3.org/ns/did/v1"

class DIDResolutionResult:
    """Represents the result of a DID resolution"""
    def __init__(self, did_document: Optional[DIDDocument] = None, error: Optional[str] = None):
        self.did_document = did_document
        self.error = error
        self.status = "error" if error else "success"

class DIDResolver:
    """Resolves DIDs to DID Documents"""
    
    def __init__(self):
        pass
    
    def resolve(self, did: str) -> DIDResolutionResult:
        """
        Resolves a DID to its DID Document.
        """
        if not did.startswith("did:reliquary:"):
            return DIDResolutionResult(error="Invalid DID format.")

        username = did.split(":")[-1]

        try:
            public_key_blob = get_public_key_from_db(username)
            if not public_key_blob:
                return DIDResolutionResult(error=f"No public key found for user '{username}'.")

            # Use cbor2 to parse the COSE key, same as get_jwk.py
            cose_key = cbor2.loads(public_key_blob)
            
            # Verify key type and curve
            if not isinstance(cose_key, dict) or cose_key.get(1) != 2:  # kty == EC2
                return DIDResolutionResult(error="Public key is not an Elliptic Curve key.")
            if cose_key.get(-1) != 1:  # crv == P-256
                return DIDResolutionResult(error="Public key is not a P-256 curve key.")

            # Extract coordinates
            x_bytes = cose_key.get(-2)
            y_bytes = cose_key.get(-3)

            if not isinstance(x_bytes, bytes) or not isinstance(y_bytes, bytes):
                return DIDResolutionResult(error="Missing x or y coordinates in COSE key.")
            
            x_base64url = bytes_to_base64url(x_bytes)
            y_base64url = bytes_to_base64url(y_bytes)

            # Create verification method
            verification_method = {
                "id": f"{did}#key-1",
                "type": "JsonWebKey2020",
                "controller": did,
                "publicKeyJwk": {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": x_base64url,
                    "y": y_base64url
                }
            }
            
            # Create DID Document
            did_doc = DIDDocument(
                did=did,
                verification_methods=[verification_method],
                authentication=[f"{did}#key-1"]
            )
            
            return DIDResolutionResult(did_document=did_doc)
        except Exception as e:
            print(f"Error resolving DID: {e}", file=sys.stderr)
            traceback.print_exc()
            return DIDResolutionResult(error=str(e))

def get_absolute_db_path():
    """Calculates the absolute path to the database to ensure it's always found."""
    try:
        # This works when running as a .py file from the 'scripts' directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    except NameError:
        # This is a fallback for interactive environments like Jupyter.
        # It assumes the notebook is running from the project's root directory.
        project_root = os.getcwd()
    
    return os.path.join(project_root, 'auth', 'webauthn', 'keys.db')

# --- Configuration ---
DB_PATH = get_absolute_db_path()

def get_public_key_from_db(username: str) -> bytes:
    """Helper to retrieve the public key blob from the database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at the expected path: {DB_PATH}")

    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT public_key FROM credentials WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
    return None

def resolve_did(did: str) -> dict:
    """
    Resolves a DID to its DID Document using the corrected key parsing logic.
    """
    resolver = DIDResolver()
    result = resolver.resolve(did)
    
    if result.status == "success":
        did_doc_dict = {
            "@context": result.did_document.context,
            "id": result.did_document.id,
            "verificationMethod": result.did_document.verificationMethod,
            "authentication": result.did_document.authentication
        }
        return {"status": "success", "did_doc": did_doc_dict}
    else:
        return {"status": "error", "message": result.error}

def main(username: str):
    """Main function to resolve a DID for a given username."""
    test_did = f"did:reliquary:{username}"
    print(f"Resolving DID: {test_did}")
    
    result = resolve_did(test_did)
    
    if result.get("status") == "success":
        print("\n✅ DID resolved successfully. Here is the DID Document:")
        print(json.dumps(result["did_doc"], indent=2))
    else:
        print(f"\n❌ Failed to resolve DID: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    print("--- Running local DID Resolver Test ---")
    
    # Explicitly set the user for testing to avoid argument parsing issues
    test_username = "testuser"
    main(test_username)