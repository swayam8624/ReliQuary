# scripts/get_jwk.py
import sqlite3
import sys
import json
import cbor2
import os
from webauthn.helpers import bytes_to_base64url

# --- FIX: Use os.getcwd() for interactive environments ---
# This gets the directory where you started your notebook or script.
# Assumes you are running from the project's root directory (e.g., 'ReliQuary').
try:
    # This works when running as a .py file
    SCRIPT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
except NameError:
    # This works in a Jupyter Notebook or interactive console
    PROJECT_ROOT = os.getcwd()

DB_PATH = os.path.join(PROJECT_ROOT, 'auth', 'webauthn', 'keys.db')
# --- END FIX ---


def get_public_key_blob(username: str) -> bytes:
    """Retrieves the public key blob for a given username."""
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found at the expected path: {DB_PATH}")

        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT public_key FROM credentials WHERE username=?", (username,))
            result = cursor.fetchone()
            if result is None:
                raise ValueError(f"No public key found for user '{username}' in the database.")
            return result[0]
    except sqlite3.OperationalError as e:
        print(f"❌ DB error: {e}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def parse_cose_ec_key(cose_blob: bytes) -> tuple[str, str]:
    """Parses a COSE key blob and returns base64url-encoded x and y coordinates."""
    try:
        cose_key = cbor2.loads(cose_blob)

        if not isinstance(cose_key, dict) or cose_key.get(1) != 2:  # kty == EC2
            raise ValueError("Key is not an EC2 key")
        if cose_key.get(-1) != 1:  # crv == P-256
            raise ValueError("Not P-256 curve")

        x = cose_key.get(-2)
        y = cose_key.get(-3)

        if not isinstance(x, bytes) or not isinstance(y, bytes):
            raise ValueError("Missing x or y coordinates in COSE key")

        return bytes_to_base64url(x), bytes_to_base64url(y)

    except Exception as e:
        print(f"❌ Error parsing COSE key: {e}", file=sys.stderr)
        sys.exit(1)

def main(username: str):
    """Fetches a user's public key and prints it as a JWK."""
    print(f"--- Attempting to read from database: {DB_PATH} ---")
    pubkey_blob = get_public_key_blob(username)
    x_b64url, y_b64url = parse_cose_ec_key(pubkey_blob)

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": x_b64url,
        "y": y_b64url
    }

    print(f"\n✅ JWK for DID 'did:reliquary:{username}#key-1':\n")
    print(json.dumps(jwk, indent=2))

# To run this in an interactive cell, you would call:
# main("testuser")