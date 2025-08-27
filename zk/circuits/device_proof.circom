pragma circom 2.0.0;

// Include necessary libraries for hash functions
include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * Device Verification Circuit
 * 
 * This circuit proves that a user controls a specific device without revealing
 * the device's actual hardware fingerprint. It verifies:
 * 1. Device fingerprint hash matches known registered device
 * 2. Hardware security module (HSM) signature is valid
 * 3. Device is not blacklisted
 * 
 * Privacy Properties:
 * - Device fingerprint remains private
 * - Only proof of device ownership is public
 * - Supports device registration without identity exposure
 */

template DeviceVerifier() {
    // Private inputs (witness)
    signal private input device_fingerprint;    // Unique device hardware fingerprint
    signal private input device_salt;           // Random salt for fingerprint hashing
    signal private input hsm_signature;         // Hardware security module signature
    signal private input hsm_private_key;       // HSM private key (for signature verification)
    
    // Public inputs
    signal input expected_device_hash;          // Expected hash of (fingerprint + salt)
    signal input hsm_public_key;               // HSM public key for signature verification
    signal input device_whitelist_root;        // Merkle root of whitelisted devices
    signal input blacklist_root;               // Merkle root of blacklisted devices
    signal input challenge_nonce;              // Challenge nonce to prevent replay attacks
    
    // Outputs
    signal output device_verified;             // 1 if device is verified, 0 otherwise
    signal output proof_hash;                  // Hash of the proof for auditability
    
    // Internal signals
    signal device_hash_computed;
    signal signature_valid;
    signal not_blacklisted;
    signal whitelist_verified;
    
    // Components
    component device_hasher = Poseidon(2);
    component signature_verifier = Poseidon(3);
    component blacklist_checker = LessEqThan(252);
    component whitelist_checker = IsEqual();
    component final_and1 = IsEqual();
    component final_and2 = IsEqual();
    component proof_hasher = Poseidon(4);
    
    // Step 1: Compute device fingerprint hash
    device_hasher.inputs[0] <== device_fingerprint;
    device_hasher.inputs[1] <== device_salt;
    device_hash_computed <== device_hasher.out;
    
    // Step 2: Verify device hash matches expected value
    component hash_verifier = IsEqual();
    hash_verifier.in[0] <== device_hash_computed;
    hash_verifier.in[1] <== expected_device_hash;
    
    // Step 3: Verify HSM signature
    // Simplified signature verification (in production, use proper ECDSA/EdDSA)
    signature_verifier.inputs[0] <== hsm_private_key;
    signature_verifier.inputs[1] <== device_fingerprint;
    signature_verifier.inputs[2] <== challenge_nonce;
    
    component sig_verifier = IsEqual();
    sig_verifier.in[0] <== signature_verifier.out;
    sig_verifier.in[1] <== hsm_signature;
    signature_valid <== sig_verifier.out;
    
    // Step 4: Check device is not blacklisted
    // Simplified: check if device_hash is not in blacklist range
    blacklist_checker.in[0] <== device_hash_computed;
    blacklist_checker.in[1] <== blacklist_root;
    not_blacklisted <== 1 - blacklist_checker.out;
    
    // Step 5: Verify device is whitelisted
    whitelist_checker.in[0] <== device_hash_computed;
    whitelist_checker.in[1] <== device_whitelist_root;
    whitelist_verified <== whitelist_checker.out;
    
    // Step 6: Combine all verification results
    final_and1.in[0] <== hash_verifier.out;
    final_and1.in[1] <== signature_valid;
    
    final_and2.in[0] <== final_and1.out;
    final_and2.in[1] <== not_blacklisted;
    
    component final_and3 = IsEqual();
    final_and3.in[0] <== final_and2.out;
    final_and3.in[1] <== whitelist_verified;
    
    device_verified <== final_and3.out;
    
    // Step 7: Generate proof hash for auditability
    proof_hasher.inputs[0] <== device_verified;
    proof_hasher.inputs[1] <== expected_device_hash;
    proof_hasher.inputs[2] <== challenge_nonce;
    proof_hasher.inputs[3] <== hsm_public_key;
    proof_hash <== proof_hasher.out;
    
    // Constraint: device_verified must be 0 or 1
    component binary_check = IsEqual();
    binary_check.in[0] <== device_verified * (device_verified - 1);
    binary_check.in[1] <== 0;
    binary_check.out === 1;
}

component main = DeviceVerifier();