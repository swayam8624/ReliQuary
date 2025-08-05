import sqlite3
import os
import json  # Needed for JSON serialization of transports

DB_PATH = "auth/webauthn/keys.db"

# Dummy/fake values (won't work for real verification)
username = "testuser"
credential_id = b"fake_cred_id_123456"
public_key = b"fake_public_key_abcdef"
attestation_type = "none"
transports = []  # Empty list for simplicity
aaguid = b"fake_aaguid_000000"
sign_count = 0

# Ensure parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Insert dummy credential into DB
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO credentials (
            credential_id, username, public_key,
            attestation_type, transports, aaguid, sign_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        credential_id,
        username,
        public_key,
        attestation_type,
        json.dumps(transports),  # Convert list to JSON string
        aaguid,
        sign_count
    ))
    conn.commit()

print("✅ Dummy credential inserted for testuser.")
