# core/crypto/key_sharding.py

import os
import requests
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import List

NODE_SSS_API_BASE_URL = "http://localhost:31415"

# --- Secure Shamir's Secret Sharing using NodeJS SSS Server ---

def generate_random_secret(length: int) -> bytes:
    return os.urandom(length)


@dataclass
class KeyShard:
    """Represents a key shard for secure key distribution"""
    id: str
    data: str
    index: int
    threshold: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


def split_key_into_shards(secret: bytes, num_shares: int, threshold: int) -> List[KeyShard]:
    """
    Split a secret key into shards using Shamir's Secret Sharing.
    
    Args:
        secret: The secret key to split
        num_shares: Number of shares to generate
        threshold: Minimum number of shares required to reconstruct the secret
        
    Returns:
        List of KeyShard objects
    """
    if not (2 <= threshold <= num_shares):
        raise ValueError("Threshold must be >= 2 and <= num_shares.")

    hex_secret = secret.hex()
    response = requests.post(f"{NODE_SSS_API_BASE_URL}/split", json={
        "secret": hex_secret,
        "shares": num_shares,
        "threshold": threshold
    })
    response.raise_for_status()
    
    shares = response.json()["shares"]
    shards = []
    
    for i, share in enumerate(shares):
        shard = KeyShard(
            id=f"shard_{i+1}",
            data=share,
            index=i+1,
            threshold=threshold
        )
        shards.append(shard)
    
    return shards


def reconstruct_key_from_shards(shards: List[KeyShard], threshold: int) -> bytes:
    """
    Reconstruct a secret key from shards using Shamir's Secret Sharing.
    
    Args:
        shards: List of KeyShard objects
        threshold: Minimum number of shares required to reconstruct the secret
        
    Returns:
        Reconstructed secret key
    """
    if len(shards) < threshold:
        raise ValueError(f"Not enough shards to reconstruct secret: {len(shards)} provided, need {threshold}.")

    shares = [shard.data for shard in shards]
    response = requests.post(f"{NODE_SSS_API_BASE_URL}/combine", json={"shares": shares})
    response.raise_for_status()
    
    hex_secret = response.json()["secret"]
    return bytes.fromhex(hex_secret)


# Aliases for backward compatibility
create_shares = split_key_into_shards
reconstruct_secret = reconstruct_key_from_shards


class KeyShardManager:
    """Pure-Python Shamir secret sharing manager over GF(257)."""

    prime = 257

    def shard_key(self, key: bytes, num_shards: int = 3, threshold: int = 2) -> List[bytes]:
        if not (2 <= threshold <= num_shards <= 255):
            raise ValueError("Require 2 <= threshold <= num_shards <= 255.")

        polynomials = []
        for byte in key:
            coefficients = [byte] + [secrets.randbelow(self.prime) for _ in range(threshold - 1)]
            polynomials.append(coefficients)

        shares = []
        for x in range(1, num_shards + 1):
            encoded_values = bytearray([x])
            for coefficients in polynomials:
                y = 0
                for power, coefficient in enumerate(coefficients):
                    y = (y + coefficient * pow(x, power, self.prime)) % self.prime
                encoded_values.extend(y.to_bytes(2, "big"))
            shares.append(bytes(encoded_values))
        return shares

    def reconstruct_key(self, shards: List[bytes], threshold: int = 2) -> bytes:
        if len(shards) < threshold:
            raise ValueError(f"Not enough shards to reconstruct secret: {len(shards)} provided, need {threshold}.")

        selected = shards[:threshold]
        value_count = (len(selected[0]) - 1) // 2
        if any(len(share) != 1 + value_count * 2 for share in selected):
            raise ValueError("All shards must have the same encoded length.")

        points = []
        for share in selected:
            x = share[0]
            values = [
                int.from_bytes(share[1 + i * 2: 3 + i * 2], "big")
                for i in range(value_count)
            ]
            points.append((x, values))

        secret = bytearray()
        for value_index in range(value_count):
            total = 0
            for i, (x_i, values_i) in enumerate(points):
                numerator = 1
                denominator = 1
                for j, (x_j, _) in enumerate(points):
                    if i == j:
                        continue
                    numerator = (numerator * (-x_j)) % self.prime
                    denominator = (denominator * (x_i - x_j)) % self.prime
                lagrange = numerator * pow(denominator, -1, self.prime)
                total = (total + values_i[value_index] * lagrange) % self.prime
            if total > 255:
                raise ValueError("Invalid shard set reconstructed an out-of-byte-range value.")
            secret.append(total)
        return bytes(secret)

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
