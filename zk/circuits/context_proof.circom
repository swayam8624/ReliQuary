pragma circom 2.0.0;

// Include individual verification circuits
include "./device_proof.circom";
include "./timestamp_verifier.circom";
include "./location_chain.circom";
include "./pattern_match.circom";

// Include necessary libraries
include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * Comprehensive Context Verification Circuit
 * 
 * This is the main circuit that combines all context verification components:
 * - Device verification (hardware fingerprints, HSM signatures)
 * - Timestamp verification (time windows, rate limiting, TOTP)
 * - Location verification (geographic boundaries, travel patterns)
 * - Pattern matching (behavioral analysis, risk scoring)
 * 
 * The circuit produces a unified proof that all context requirements are met
 * without revealing any sensitive information about the user's actual context.
 * 
 * Privacy Properties:
 * - Complete context privacy preservation
 * - Unified proof of all verification requirements
 * - Configurable verification levels
 * - Audit trail without sensitive data exposure
 */

template ContextProof() {
    // === Device Verification Inputs ===
    signal private input device_fingerprint;
    signal private input device_salt;
    signal private input hsm_signature;
    signal private input hsm_private_key;
    signal input expected_device_hash;
    signal input hsm_public_key;
    signal input device_whitelist_root;
    signal input device_blacklist_root;
    
    // === Timestamp Verification Inputs ===
    signal private input current_timestamp;
    signal private input last_access_time;
    signal private input timezone_offset;
    signal private input totp_secret;
    signal input min_allowed_time;
    signal input max_allowed_time;
    signal input min_interval;
    signal input business_hours_start;
    signal input business_hours_end;
    signal input totp_window;
    signal input expected_totp_hash;
    signal input require_business_hours;
    signal input require_totp;
    
    // === Location Verification Inputs ===
    signal private input current_latitude;
    signal private input current_longitude;
    signal private input previous_latitude;
    signal private input previous_longitude;
    signal private input ip_location_lat;
    signal private input ip_location_lon;
    signal private input location_salt;
    signal private input travel_time_hours;
    signal input authorized_region_center_lat;
    signal input authorized_region_center_lon;
    signal input authorized_radius_squared;
    signal input blacklist_region_lat;
    signal input blacklist_region_lon;
    signal input blacklist_radius_squared;
    signal input max_travel_speed;
    signal input ip_tolerance_radius_squared;
    signal input require_ip_consistency;
    
    // === Pattern Matching Inputs ===
    signal private input action_sequence[10];
    signal private input timing_intervals[9];
    signal private input session_duration;
    signal private input keystrokes_per_minute;
    signal private input mouse_movements;
    signal private input access_frequency;
    signal private input pattern_salt;
    signal input expected_pattern_hash;
    signal input min_session_duration;
    signal input max_session_duration;
    signal input typing_speed_min;
    signal input typing_speed_max;
    signal input max_timing_variance;
    signal input risk_threshold;
    signal input pattern_confidence_level;
    
    // === Global Context Inputs ===
    signal input challenge_nonce;                // Global challenge nonce
    signal input verification_level;             // Required verification level (1-4)
    signal input context_requirements_mask;      // Bitmask: 1=device, 2=time, 4=location, 8=pattern
    
    // === Outputs ===
    signal output device_verification_result;
    signal output timestamp_verification_result;
    signal output location_verification_result;
    signal output pattern_verification_result;
    signal output overall_context_valid;
    signal output verification_level_met;
    signal output context_proof_hash;
    signal output trust_score;                   // Combined trust score (0-100)
    
    // === Component Instantiation ===
    component device_verifier = DeviceVerifier();
    component timestamp_verifier = TimestampVerifier();
    component location_verifier = LocationChainVerifier();
    component pattern_verifier = PatternMatcher();
    
    // === Device Verification Setup ===
    device_verifier.device_fingerprint <== device_fingerprint;
    device_verifier.device_salt <== device_salt;
    device_verifier.hsm_signature <== hsm_signature;
    device_verifier.hsm_private_key <== hsm_private_key;
    device_verifier.expected_device_hash <== expected_device_hash;
    device_verifier.hsm_public_key <== hsm_public_key;
    device_verifier.device_whitelist_root <== device_whitelist_root;
    device_verifier.blacklist_root <== device_blacklist_root;
    device_verifier.challenge_nonce <== challenge_nonce;
    
    // === Timestamp Verification Setup ===
    timestamp_verifier.current_timestamp <== current_timestamp;
    timestamp_verifier.last_access_time <== last_access_time;
    timestamp_verifier.timezone_offset <== timezone_offset;
    timestamp_verifier.totp_secret <== totp_secret;
    timestamp_verifier.min_allowed_time <== min_allowed_time;
    timestamp_verifier.max_allowed_time <== max_allowed_time;
    timestamp_verifier.min_interval <== min_interval;
    timestamp_verifier.business_hours_start <== business_hours_start;
    timestamp_verifier.business_hours_end <== business_hours_end;
    timestamp_verifier.totp_window <== totp_window;
    timestamp_verifier.expected_totp_hash <== expected_totp_hash;
    timestamp_verifier.require_business_hours <== require_business_hours;
    timestamp_verifier.require_totp <== require_totp;
    
    // === Location Verification Setup ===
    location_verifier.current_latitude <== current_latitude;
    location_verifier.current_longitude <== current_longitude;
    location_verifier.previous_latitude <== previous_latitude;
    location_verifier.previous_longitude <== previous_longitude;
    location_verifier.ip_location_lat <== ip_location_lat;
    location_verifier.ip_location_lon <== ip_location_lon;
    location_verifier.location_salt <== location_salt;
    location_verifier.travel_time_hours <== travel_time_hours;
    location_verifier.authorized_region_center_lat <== authorized_region_center_lat;
    location_verifier.authorized_region_center_lon <== authorized_region_center_lon;
    location_verifier.authorized_radius_squared <== authorized_radius_squared;
    location_verifier.blacklist_region_lat <== blacklist_region_lat;
    location_verifier.blacklist_region_lon <== blacklist_region_lon;
    location_verifier.blacklist_radius_squared <== blacklist_radius_squared;
    location_verifier.max_travel_speed <== max_travel_speed;
    location_verifier.ip_tolerance_radius_squared <== ip_tolerance_radius_squared;
    location_verifier.require_ip_consistency <== require_ip_consistency;
    
    // === Pattern Verification Setup ===
    for (var i = 0; i < 10; i++) {
        pattern_verifier.action_sequence[i] <== action_sequence[i];
    }
    for (var i = 0; i < 9; i++) {
        pattern_verifier.timing_intervals[i] <== timing_intervals[i];
    }
    pattern_verifier.session_duration <== session_duration;
    pattern_verifier.keystrokes_per_minute <== keystrokes_per_minute;
    pattern_verifier.mouse_movements <== mouse_movements;
    pattern_verifier.access_frequency <== access_frequency;
    pattern_verifier.pattern_salt <== pattern_salt;
    pattern_verifier.expected_pattern_hash <== expected_pattern_hash;
    pattern_verifier.min_session_duration <== min_session_duration;
    pattern_verifier.max_session_duration <== max_session_duration;
    pattern_verifier.typing_speed_min <== typing_speed_min;
    pattern_verifier.typing_speed_max <== typing_speed_max;
    pattern_verifier.max_timing_variance <== max_timing_variance;
    pattern_verifier.risk_threshold <== risk_threshold;
    pattern_verifier.pattern_confidence_level <== pattern_confidence_level;
    
    // === Extract Results ===
    device_verification_result <== device_verifier.device_verified;
    timestamp_verification_result <== timestamp_verifier.overall_valid;
    location_verification_result <== location_verifier.overall_valid;
    pattern_verification_result <== pattern_verifier.overall_pattern_valid;
    
    // === Apply Context Requirements Mask ===
    signal device_required;
    signal timestamp_required;
    signal location_required;
    signal pattern_required;
    
    // Extract requirement flags from bitmask
    device_required <== (context_requirements_mask \ 1) % 2;
    timestamp_required <== (context_requirements_mask \ 2) % 2;
    location_required <== (context_requirements_mask \ 4) % 2;
    pattern_required <== (context_requirements_mask \ 8) % 2;
    
    // Apply conditional verification based on requirements
    signal device_check_result;
    signal timestamp_check_result;
    signal location_check_result;
    signal pattern_check_result;
    
    device_check_result <== device_required * device_verification_result + (1 - device_required);
    timestamp_check_result <== timestamp_required * timestamp_verification_result + (1 - timestamp_required);
    location_check_result <== location_required * location_verification_result + (1 - location_required);
    pattern_check_result <== pattern_required * pattern_verification_result + (1 - pattern_required);
    
    // === Calculate Overall Context Validity ===
    component context_and1 = IsEqual();
    context_and1.in[0] <== device_check_result + timestamp_check_result;
    context_and1.in[1] <== 2;
    
    component context_and2 = IsEqual();
    context_and2.in[0] <== context_and1.out + location_check_result;
    context_and2.in[1] <== 2;
    
    component context_and3 = IsEqual();
    context_and3.in[0] <== context_and2.out + pattern_check_result;
    context_and3.in[1] <== 2;
    
    overall_context_valid <== context_and3.out;
    
    // === Calculate Trust Score ===
    // Weighted scoring: device=30%, timestamp=20%, location=25%, pattern=25%
    signal weighted_device_score = device_verification_result * 30;
    signal weighted_timestamp_score = timestamp_verification_result * 20;
    signal weighted_location_score = location_verification_result * 25;
    signal weighted_pattern_score = (100 - pattern_verifier.risk_score) * 25 / 100;
    
    trust_score <== weighted_device_score + weighted_timestamp_score + 
                   weighted_location_score + weighted_pattern_score;
    
    // === Verification Level Check ===
    component level_check = GreaterEqThan(8);
    level_check.in[0] <== trust_score;
    level_check.in[1] <== verification_level * 25; // Level 1=25, 2=50, 3=75, 4=100
    verification_level_met <== level_check.out;
    
    // === Generate Context Proof Hash ===
    component context_hasher = Poseidon(8);
    context_hasher.inputs[0] <== overall_context_valid;
    context_hasher.inputs[1] <== trust_score;
    context_hasher.inputs[2] <== verification_level;
    context_hasher.inputs[3] <== context_requirements_mask;
    context_hasher.inputs[4] <== challenge_nonce;
    context_hasher.inputs[5] <== device_verifier.proof_hash;
    context_hasher.inputs[6] <== location_verifier.location_proof_hash;
    context_hasher.inputs[7] <== pattern_verifier.pattern_proof_hash;
    context_proof_hash <== context_hasher.out;
    
    // === Final Constraints ===
    // Ensure trust score is in valid range (0-100)
    component trust_min_check = GreaterEqThan(8);
    component trust_max_check = LessEqThan(8);
    trust_min_check.in[0] <== trust_score;
    trust_min_check.in[1] <== 0;
    trust_max_check.in[0] <== trust_score;
    trust_max_check.in[1] <== 100;
    
    component trust_range_check = IsEqual();
    trust_range_check.in[0] <== trust_min_check.out + trust_max_check.out;
    trust_range_check.in[1] <== 2;
    trust_range_check.out === 1;
    
    // Ensure overall_context_valid is binary
    component context_binary_check = IsEqual();
    context_binary_check.in[0] <== overall_context_valid * (overall_context_valid - 1);
    context_binary_check.in[1] <== 0;
    context_binary_check.out === 1;
}

component main = ContextProof();