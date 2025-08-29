# auth/webauthn/verify.py
import os
import sqlite3
import json
import logging
import traceback
import webauthn
from webauthn.helpers import options_to_json
# --- FIX: Import the necessary class ---
from webauthn.helpers.structs import AuthenticationCredential, PublicKeyCredentialDescriptor
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class AuthenticationOptions:
    """Represents WebAuthn authentication options"""
    challenge: str
    rp_id: str
    allow_credentials: List[PublicKeyCredentialDescriptor]

class WebAuthnVerificationManager:
    """Manages WebAuthn verification process"""
    
    def __init__(self):
        self.challenge_store = {}
        self.db_path = "auth/webauthn/keys.db"
        self.rp_id = "webauthn.io"
        self.rp_name = "ReliQuary"
        self.rp_origin = f"https://{self.rp_id}"
        self.init_db()
    
    def init_db(self):
        """Ensures the database and table exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    username TEXT PRIMARY KEY,
                    credential_id BLOB NOT NULL,
                    public_key BLOB NOT NULL,
                    sign_count INTEGER NOT NULL,
                    transports TEXT
                )
            """)
            conn.commit()
    
    def get_user_credential_ids(self, username: str) -> list[bytes]:
        """Retrieves existing credential IDs for a user to generate a challenge."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT credential_id FROM credentials WHERE username=?", (username,))
            results = cursor.fetchall()
            if not results:
                raise ValueError(f"User '{username}' does not exist or has no credentials.")
            return [row[0] for row in results]
    
    def start_verification(self, username: str) -> AuthenticationOptions:
        """Generates authentication options for the browser."""
        credential_ids = self.get_user_credential_ids(username)

        options = webauthn.generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=[PublicKeyCredentialDescriptor(id=cred_id) for cred_id in credential_ids],
        )

        self.challenge_store[username] = options.challenge
        return AuthenticationOptions(
            challenge=options.challenge,
            rp_id=self.rp_id,
            allow_credentials=[PublicKeyCredentialDescriptor(id=cred_id) for cred_id in credential_ids]
        )
    
    def complete_verification(self, username: str, response_json: str) -> Dict[str, Any]:
        """Verifies the browser's authentication response."""
        try:
            # The library expects a dictionary, so json.loads is correct here.
            credential_to_verify = json.loads(response_json)

            expected_challenge = self.challenge_store.get(username)
            if not expected_challenge:
                raise ValueError("No challenge found for user. Verification timed out or invalid.")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT credential_id, public_key, sign_count FROM credentials WHERE username=?", (username,))
                db_row = cursor.fetchone()
                if not db_row:
                    raise ValueError(f"Could not find user '{username}' in database.")
                
                credential_id, public_key, sign_count = db_row

            verification = webauthn.verify_authentication_response(
                credential=credential_to_verify,
                expected_challenge=expected_challenge,
                expected_rp_id=self.rp_id,
                expected_origin=self.rp_origin,
                credential_public_key=public_key,
                credential_current_sign_count=sign_count,
                require_user_verification=False
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE credentials SET sign_count = ? WHERE credential_id = ?",
                    (verification.new_sign_count, credential_id)
                )
                conn.commit()

            logging.info(f"✅ Verification successful for '{username}'")
            del self.challenge_store[username]
            return {"status": "success"}

        except Exception as e:
            logging.error(f"❌ Verification failed for '{username}': {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
DB_PATH = "auth/webauthn/keys.db"
RELIQUARY_RP_ID = "webauthn.io"
RELIQUARY_RP_NAME = "ReliQuary"
RELIQUARY_RP_ORIGIN = f"https://{RELIQUARY_RP_ID}"

def init_db():
    """Ensures the database and table exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                username TEXT PRIMARY KEY,
                credential_id BLOB NOT NULL,
                public_key BLOB NOT NULL,
                sign_count INTEGER NOT NULL,
                transports TEXT
            )
        """)
        conn.commit()

# Initialize DB
init_db()

CHALLENGE_STORE = {}

def get_user_credential_ids(username: str) -> list[bytes]:
    """Retrieves existing credential IDs for a user to generate a challenge."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credential_id FROM credentials WHERE username=?", (username,))
        results = cursor.fetchall()
        if not results:
            raise ValueError(f"User '{username}' does not exist or has no credentials.")
        return [row[0] for row in results]

def start_verification(username: str) -> PublicKeyCredentialDescriptor:
    """Generates authentication options for the browser."""
    credential_ids = get_user_credential_ids(username)

    # --- FIX: Use the PublicKeyCredentialDescriptor class ---
    options = webauthn.generate_authentication_options(
        rp_id=RELIQUARY_RP_ID,
        allow_credentials=[PublicKeyCredentialDescriptor(id=cred_id) for cred_id in credential_ids],
    )
    # --- END FIX ---

    CHALLENGE_STORE[username] = options.challenge
    return options

def complete_verification(username: str, response_json: str):
    """Verifies the browser's authentication response."""
    try:
        # The library expects a dictionary, so json.loads is correct here.
        credential_to_verify = json.loads(response_json)

        expected_challenge = CHALLENGE_STORE.get(username)
        if not expected_challenge:
            raise ValueError("No challenge found for user. Verification timed out or invalid.")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT credential_id, public_key, sign_count FROM credentials WHERE username=?", (username,))
            db_row = cursor.fetchone()
            if not db_row:
                raise ValueError(f"Could not find user '{username}' in database.")
            
            credential_id, public_key, sign_count = db_row

        verification = webauthn.verify_authentication_response(
            credential=credential_to_verify,
            expected_challenge=expected_challenge,
            expected_rp_id=RELIQUARY_RP_ID,
            expected_origin=RELIQUARY_RP_ORIGIN,
            credential_public_key=public_key,
            credential_current_sign_count=sign_count,
            require_user_verification=False
        )

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE credentials SET sign_count = ? WHERE credential_id = ?",
                (verification.new_sign_count, credential_id)
            )
            conn.commit()

        logging.info(f"✅ Verification successful for '{username}'")
        del CHALLENGE_STORE[username]
        return {"status": "success"}

    except Exception as e:
        logging.error(f"❌ Verification failed for '{username}': {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("--- `py_webauthn` Verification Test ---")
    test_username = "testuser"
    
    try:
        auth_options = start_verification(test_username)
        print("\n--- STEP 1: Use the JSON and JavaScript Snippet below ---")
        print("\nCOPY THIS JSON:")
        print(options_to_json(auth_options))
        print("\nJAVASCRIPT SNIPPET FOR BROWSER CONSOLE (for Authentication):")
        print("""
// Helper function to convert base64url to ArrayBuffer
function bufferDecode(value) {
  const b64 = value.replace(/-/g, '+').replace(/_/g, '/');
  const str = atob(b64);
  const G = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) {
    G[i] = str.charCodeAt(i);
  }
  return G.buffer;
}

// 1. PASTE THE JSON FROM YOUR SCRIPT HERE:
const options = PASTE_JSON_HERE;

// 2. This code prepares the options for the browser API
options.challenge = bufferDecode(options.challenge);
if (options.allowCredentials) {
  for (let cred of options.allowCredentials) {
    cred.id = bufferDecode(cred.id);
  }
}

// 3. This code calls the WebAuthn API and prints the result
(async () => {
  try {
    const credential = await navigator.credentials.get({ publicKey: options });
    console.log("✅ SUCCESS! Copy the JSON below and paste it into your Python script:");
    console.log(JSON.stringify(credential, (key, value) => {
      if (value instanceof ArrayBuffer) {
        return btoa(String.fromCharCode.apply(null, new Uint8Array(value))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=/g, '');
      }
      return value;
    }, 2));
  } catch (err) {
    console.error("❌ ERROR:", err);
  }
})();
        """)
        print("-----------------------------------------------------------------------")

        print("\n--- STEP 2: The script is now waiting. ---")
        print("Follow the browser instructions, then paste the final JSON response from the console here and press Enter:")
        browser_response_json = input("> ")

        if browser_response_json:
            print("\nAttempting to complete verification...")
            complete_verification(
                username=test_username,
                response_json=browser_response_json
            )
        else:
            print("\n🛑 No data pasted. Exiting.")

    except ValueError as e:
        print(f"\n❌ ERROR: Could not start verification. Have you registered '{test_username}' first? ({e})")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        traceback.print_exc()