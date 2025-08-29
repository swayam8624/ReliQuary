# auth/webauthn/register.py
import os
import sqlite3
import json
import logging
import traceback
import webauthn
from webauthn.helpers import options_to_json
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class RegistrationOptions:
    """Represents WebAuthn registration options"""
    challenge: str
    rp_id: str
    rp_name: str
    user_id: str
    user_name: str

class WebAuthnRegistrationManager:
    """Manages WebAuthn registration process"""
    
    def __init__(self):
        self.challenge_store = {}
        self.db_path = "auth/webauthn/keys.db"
        self.rp_id = "webauthn.io"
        self.rp_name = "ReliQuary"
        self.rp_origin = f"https://{self.rp_id}"
        self.init_db()
    
    def init_db(self):
        """Initializes the SQLite database."""
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
    
    def start_registration(self, username: str) -> RegistrationOptions:
        """Generates registration options for the browser."""
        user_id = username.encode()

        options = webauthn.generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id,
            user_name=username,
        )
        # Store the challenge to verify it in the completion step
        self.challenge_store[username] = options.challenge
        return RegistrationOptions(
            challenge=options.challenge,
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id.decode(),
            user_name=username
        )
    
    def complete_registration(self, username: str, response_json: str) -> Dict[str, Any]:
        """Verifies the browser's response and saves the new credential."""
        try:
            credential_to_verify = json.loads(response_json)

            expected_challenge = self.challenge_store.get(username)
            if not expected_challenge:
                raise ValueError("No challenge found for user.")

            verification = webauthn.verify_registration_response(
                credential=credential_to_verify,
                expected_challenge=expected_challenge,
                expected_origin=self.rp_origin,
                expected_rp_id=self.rp_id,
                require_user_verification=False
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM credentials WHERE username=?", (username,))
                cursor.execute(
                    "INSERT INTO credentials (username, credential_id, public_key, sign_count, transports) VALUES (?, ?, ?, ?, ?)",
                    (
                        username,
                        verification.credential_id,
                        verification.credential_public_key,
                        verification.sign_count,
                        json.dumps(credential_to_verify.get("response", {}).get("transports") or []),
                    )
                )
                conn.commit()

            logging.info(f"✅ Registration successful for '{username}'")
            del self.challenge_store[username]
            return {"status": "success"}

        except Exception as e:
            logging.error(f"❌ Registration failed for '{username}': {e}")
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
    """Initializes the SQLite database."""
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

# This is a temporary, in-memory store for the challenge.
# It will now persist for the entire run of the script.
CHALLENGE_STORE = {}

def start_registration(username: str):
    """Generates registration options for the browser."""
    user_id = username.encode()

    options = webauthn.generate_registration_options(
        rp_id=RELIQUARY_RP_ID,
        rp_name=RELIQUARY_RP_NAME,
        user_id=user_id,
        user_name=username,
    )
    # Store the challenge to verify it in the completion step
    CHALLENGE_STORE[username] = options.challenge
    return options

def complete_registration(username: str, response_json: str):
    """Verifies the browser's response and saves the new credential."""
    try:
        credential_to_verify = json.loads(response_json)

        expected_challenge = CHALLENGE_STORE.get(username)
        if not expected_challenge:
            raise ValueError("No challenge found for user.")

        verification = webauthn.verify_registration_response(
            credential=credential_to_verify,
            expected_challenge=expected_challenge,
            expected_origin=RELIQUARY_RP_ORIGIN,
            expected_rp_id=RELIQUARY_RP_ID,
            require_user_verification=False
        )

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credentials WHERE username=?", (username,))
            cursor.execute(
                "INSERT INTO credentials (username, credential_id, public_key, sign_count, transports) VALUES (?, ?, ?, ?, ?)",
                (
                    username,
                    verification.credential_id,
                    verification.credential_public_key,
                    verification.sign_count,
                    json.dumps(credential_to_verify.get("response", {}).get("transports") or []),
                )
            )
            conn.commit()

        logging.info(f"✅ Registration successful for '{username}'")
        del CHALLENGE_STORE[username]
        return {"status": "success"}

    except Exception as e:
        logging.error(f"❌ Registration failed for '{username}': {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("--- `py_webauthn` Registration Test ---")
    test_username = "testuser"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM credentials WHERE username=?", (test_username,))
        print(f"🧹 Cleared old credentials for '{test_username}'.")

    # STEP 1: Generate registration options
    registration_options = start_registration(test_username)
    print("\n--- STEP 1: Use the JSON and JavaScript Snippet below ---")
    print("\nCOPY THIS JSON:")
    print(options_to_json(registration_options))
    print("\nJAVASCRIPT SNIPPET FOR BROWSER CONSOLE:")
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
options.user.id = bufferDecode(options.user.id);
if (options.excludeCredentials) {
  for (let cred of options.excludeCredentials) {
    cred.id = bufferDecode(cred.id);
  }
}

// 3. This code calls the WebAuthn API and prints the result
(async () => {
  try {
    const credential = await navigator.credentials.create({ publicKey: options });
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

    # --- FIX: Use input() to pause the script and wait for the user ---
    print("\n--- STEP 2: The script is now waiting. ---")
    print("Follow the browser instructions, then paste the final JSON response from the console here and press Enter:")
    browser_response_json = input("> ")
    # --- END FIX ---

    if browser_response_json:
        print("\nAttempting to complete registration...")
        complete_registration(
            username=test_username,
            response_json=browser_response_json
        )
    else:
        print("\n🛑 No data pasted. Exiting.")