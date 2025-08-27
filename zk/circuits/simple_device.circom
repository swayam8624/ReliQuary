pragma circom 2.0.0;

/*
 * Simplified Device Verification Circuit (for testing)
 * 
 * This circuit proves basic device authenticity without external dependencies.
 * It verifies:
 * 1. Device fingerprint hash matches expected value
 * 2. Device signature is valid (simplified version)
 * 
 * This is a testing version - the full circuit uses Poseidon hashing.
 */

template SimpleDeviceVerifier() {
    // Private inputs (witness) - marked as private by being inputs without public designation
    signal input device_fingerprint;    // Unique device hardware fingerprint
    signal input device_signature;      // Device signature
    
    // Public inputs
    signal input expected_fingerprint;          // Expected device fingerprint
    signal input challenge_nonce;               // Challenge nonce to prevent replay
    
    // Outputs
    signal output device_verified;              // 1 if device is verified, 0 otherwise
    signal output proof_value;                  // Simple proof value
    
    // Internal computation
    signal fingerprint_diff;
    signal fingerprint_match;
    signal expected_signature;
    signal signature_diff;
    signal signature_match;
    
    // Step 1: Check if fingerprint matches (simplified)
    fingerprint_diff <== device_fingerprint - expected_fingerprint;
    
    // If fingerprints match, diff should be 0, so match should be 1
    // This is a simplified check - in production use proper equality circuits
    fingerprint_match <== 1 - fingerprint_diff * fingerprint_diff;
    
    // Step 2: Simple signature verification
    expected_signature <== device_fingerprint + challenge_nonce;
    signature_diff <== device_signature - expected_signature;
    signature_match <== 1 - signature_diff * signature_diff;
    
    // Step 3: Device is verified if both checks pass
    device_verified <== fingerprint_match * signature_match;
    
    // Step 4: Generate proof value
    proof_value <== device_verified * (device_fingerprint + challenge_nonce);
}

component main = SimpleDeviceVerifier();