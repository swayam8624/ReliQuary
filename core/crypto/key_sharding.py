# core/crypto/key_sharding.py

import os
import requests

NODE_SSS_API_BASE_URL = "http://localhost:31415"

# --- Secure Shamir's Secret Sharing using NodeJS SSS Server ---

def create_shares(secret: bytes, num_shares: int, threshold: int) -> list[str]:
    if not (2 <= threshold <= num_shares):
        raise ValueError("Threshold must be >= 2 and <= num_shares.")

    hex_secret = secret.hex()
    response = requests.post(f"{NODE_SSS_API_BASE_URL}/split", json={
        "secret": hex_secret,
        "shares": num_shares,
        "threshold": threshold
    })
    response.raise_for_status()
    return response.json()["shares"]

def reconstruct_secret(shares: list[str], threshold: int) -> bytes:
    if len(shares) < threshold:
        raise ValueError(f"Not enough shares to reconstruct secret: {len(shares)} provided, need {threshold}.")

    response = requests.post(f"{NODE_SSS_API_BASE_URL}/combine", json={"shares": shares})
    response.raise_for_status()
    hex_secret = response.json()["secret"]
    return bytes.fromhex(hex_secret)

def generate_random_secret(length: int) -> bytes:
    return os.urandom(length)

# --- Optional local test ---

if __name__ == "__main__":
    print("\n-- Running local SSS service test (requires Node.js server to be running) ---")
    test_secret = generate_random_secret(32)
    print("Original secret:", test_secret.hex())

    test_shares = create_shares(test_secret, num_shares=5, threshold=3)
    print("Generated 5 shares:")
    for i, s in enumerate(test_shares):
        print(f"  Share {i+1}: {s}")

    recovered = reconstruct_secret(test_shares[:3], threshold=3)
    print("Recovered secret (exact threshold):", recovered.hex())
    assert recovered == test_secret
    print("✅ Secret reconstruction with exact threshold succeeded.")

    recovered_more = reconstruct_secret(test_shares[1:4], threshold=3)
    print("Recovered secret (more than threshold):", recovered_more.hex())
    assert recovered_more == test_secret
    print("✅ Secret reconstruction with more than threshold succeeded.")

    print("Attempting reconstruction with insufficient shares...")
    try:
        reconstruct_secret(test_shares[:2], threshold=3)
        print("❌ ERROR: Reconstruction succeeded with insufficient shares (this should fail!).")
    except ValueError as e:
        print(f"✅ Correctly failed to reconstruct with insufficient shares: {e}")

    print("Attempting to create shares with invalid parameters (num_shares=1, threshold=2)...")
    try:
        create_shares(test_secret, num_shares=1, threshold=2)
        print("❌ ERROR: create_shares succeeded with invalid parameters (this should fail!).")
    except ValueError as e:
        print(f"✅ Correctly failed to create shares with invalid parameters: {e}")
