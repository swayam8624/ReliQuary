pragma circom 2.0.0;

// Include necessary libraries
include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * Timestamp Verification Circuit
 * 
 * This circuit proves that an access request occurred within valid time windows
 * without revealing the exact timestamp. It verifies:
 * 1. Current timestamp is within allowed time range
 * 2. Access follows rate limiting rules (time between requests)
 * 3. Access is within business hours/allowed time windows
 * 4. Time-based OTP (TOTP) validation if required
 * 
 * Privacy Properties:
 * - Exact timestamp remains private
 * - Only proof of valid timing is public
 * - Supports multiple time zone verification
 * - Rate limiting without timestamp exposure
 */

template TimestampVerifier() {
    // Private inputs (witness)
    signal private input current_timestamp;     // Current Unix timestamp
    signal private input last_access_time;      // Previous access timestamp
    signal private input timezone_offset;       // User's timezone offset
    signal private input totp_secret;           // TOTP secret key (if TOTP is enabled)
    
    // Public inputs
    signal input min_allowed_time;             // Minimum allowed timestamp
    signal input max_allowed_time;             // Maximum allowed timestamp
    signal input min_interval;                 // Minimum time between accesses (rate limiting)
    signal input business_hours_start;         // Start of business hours (in seconds from midnight)
    signal input business_hours_end;           // End of business hours (in seconds from midnight)
    signal input totp_window;                  // TOTP time window (typically 30 seconds)
    signal input expected_totp_hash;           // Expected TOTP value hash
    signal input require_business_hours;       // 1 if business hours check is required
    signal input require_totp;                 // 1 if TOTP validation is required
    
    // Outputs
    signal output timestamp_valid;             // 1 if timestamp verification passes
    signal output rate_limit_ok;               // 1 if rate limiting check passes
    signal output business_hours_ok;           // 1 if business hours check passes
    signal output totp_valid;                  // 1 if TOTP validation passes
    signal output overall_valid;               // 1 if all checks pass
    
    // Internal signals
    signal local_hour;
    signal totp_computed;
    signal time_diff;
    
    // Components for timestamp range validation
    component min_check = GreaterEqThan(64);
    component max_check = LessEqThan(64);
    
    // Step 1: Verify timestamp is within allowed range
    min_check.in[0] <== current_timestamp;
    min_check.in[1] <== min_allowed_time;
    
    max_check.in[0] <== current_timestamp;
    max_check.in[1] <== max_allowed_time;
    
    component range_and = IsEqual();
    range_and.in[0] <== min_check.out + max_check.out;
    range_and.in[1] <== 2;
    timestamp_valid <== range_and.out;
    
    // Step 2: Rate limiting check
    component rate_limit_check = GreaterEqThan(64);
    time_diff <== current_timestamp - last_access_time;
    rate_limit_check.in[0] <== time_diff;
    rate_limit_check.in[1] <== min_interval;
    rate_limit_ok <== rate_limit_check.out;
    
    // Step 3: Business hours validation
    // Convert timestamp to local hour of day
    component hour_extractor = Num2Bits(32);
    hour_extractor.in <== (current_timestamp + timezone_offset) % 86400; // Seconds in a day
    
    // Extract hour from seconds (divide by 3600)
    // Simplified: assume we have the hour directly for this example
    local_hour <== ((current_timestamp + timezone_offset) % 86400) \ 3600;
    
    component business_start_check = GreaterEqThan(8);
    component business_end_check = LessEqThan(8);
    
    business_start_check.in[0] <== local_hour * 3600; // Convert back to seconds
    business_start_check.in[1] <== business_hours_start;
    
    business_end_check.in[0] <== local_hour * 3600;
    business_end_check.in[1] <== business_hours_end;
    
    component business_hours_and = IsEqual();
    business_hours_and.in[0] <== business_start_check.out + business_end_check.out;
    business_hours_and.in[1] <== 2;
    
    // Apply business hours check only if required
    component business_hours_conditional = IsEqual();
    business_hours_conditional.in[0] <== require_business_hours * business_hours_and.out + (1 - require_business_hours);
    business_hours_conditional.in[1] <== 1;
    business_hours_ok <== business_hours_conditional.out;
    
    // Step 4: TOTP validation
    component totp_hasher = Poseidon(3);
    totp_hasher.inputs[0] <== totp_secret;
    totp_hasher.inputs[1] <== current_timestamp \ totp_window; // Time step
    totp_hasher.inputs[2] <== totp_window;
    totp_computed <== totp_hasher.out;
    
    component totp_verifier = IsEqual();
    totp_verifier.in[0] <== totp_computed;
    totp_verifier.in[1] <== expected_totp_hash;
    
    // Apply TOTP check only if required
    component totp_conditional = IsEqual();
    totp_conditional.in[0] <== require_totp * totp_verifier.out + (1 - require_totp);
    totp_conditional.in[1] <== 1;
    totp_valid <== totp_conditional.out;
    
    // Step 5: Combine all validations
    component final_and1 = IsEqual();
    final_and1.in[0] <== timestamp_valid + rate_limit_ok;
    final_and1.in[1] <== 2;
    
    component final_and2 = IsEqual();
    final_and2.in[0] <== final_and1.out + business_hours_ok;
    final_and2.in[1] <== 2;
    
    component final_and3 = IsEqual();
    final_and3.in[0] <== final_and2.out + totp_valid;
    final_and3.in[1] <== 2;
    
    overall_valid <== final_and3.out;
    
    // Constraints: all outputs must be binary
    component binary_check1 = IsEqual();
    binary_check1.in[0] <== timestamp_valid * (timestamp_valid - 1);
    binary_check1.in[1] <== 0;
    binary_check1.out === 1;
    
    component binary_check2 = IsEqual();
    binary_check2.in[0] <== overall_valid * (overall_valid - 1);
    binary_check2.in[1] <== 0;
    binary_check2.out === 1;
}

component main = TimestampVerifier();