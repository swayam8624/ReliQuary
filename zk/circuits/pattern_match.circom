pragma circom 2.0.0;

// Include necessary libraries
include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * Pattern Matching Circuit
 * 
 * This circuit proves that user behavior matches expected patterns without
 * revealing specific actions or timing details. It verifies:
 * 1. Access frequency patterns (daily/weekly patterns)
 * 2. Behavioral consistency (typing patterns, click patterns)
 * 3. Session duration patterns
 * 4. Risk scoring based on deviation from normal patterns
 * 
 * Privacy Properties:
 * - Specific actions and timings remain private
 * - Only proof of pattern compliance is public
 * - Supports adaptive pattern learning
 * - Risk assessment without behavior exposure
 */

template PatternMatcher() {
    // Private inputs (witness) - behavioral data
    signal private input action_sequence[10];    // Sequence of recent actions (encoded)
    signal private input timing_intervals[9];    // Time intervals between actions
    signal private input session_duration;       // Current session duration
    signal private input keystrokes_per_minute;  // Typing speed
    signal private input mouse_movements;        // Mouse movement patterns
    signal private input access_frequency;       // Recent access frequency
    signal private input pattern_salt;           // Salt for pattern hashing
    
    // Public inputs - expected patterns and thresholds
    signal input expected_pattern_hash;         // Hash of expected behavior pattern
    signal input min_session_duration;          // Minimum expected session duration
    signal input max_session_duration;          // Maximum expected session duration
    signal input typing_speed_min;              // Minimum expected typing speed
    signal input typing_speed_max;              // Maximum expected typing speed
    signal input max_timing_variance;           // Maximum allowed timing variance
    signal input risk_threshold;                // Risk score threshold
    signal input pattern_confidence_level;      // Required confidence level (0-100)
    
    // Outputs
    signal output pattern_matches;              // 1 if behavior pattern matches
    signal output session_duration_ok;          // 1 if session duration is normal
    signal output typing_pattern_ok;            // 1 if typing pattern is normal
    signal output timing_consistency_ok;        // 1 if timing is consistent
    signal output risk_score;                   // Calculated risk score (0-100)
    signal output overall_pattern_valid;        // 1 if all pattern checks pass
    signal output pattern_proof_hash;           // Hash proof for auditability
    
    // Internal signals for pattern analysis
    signal computed_pattern_hash;
    signal timing_variance;
    signal risk_components[4];
    signal weighted_risk_score;
    
    // Step 1: Compute behavior pattern hash
    component pattern_hasher = Poseidon(8);
    pattern_hasher.inputs[0] <== action_sequence[0] + action_sequence[1] + action_sequence[2];
    pattern_hasher.inputs[1] <== action_sequence[3] + action_sequence[4] + action_sequence[5];
    pattern_hasher.inputs[2] <== action_sequence[6] + action_sequence[7] + action_sequence[8] + action_sequence[9];
    pattern_hasher.inputs[3] <== keystrokes_per_minute;
    pattern_hasher.inputs[4] <== mouse_movements;
    pattern_hasher.inputs[5] <== access_frequency;
    pattern_hasher.inputs[6] <== pattern_salt;
    pattern_hasher.inputs[7] <== session_duration;
    computed_pattern_hash <== pattern_hasher.out;
    
    // Step 2: Verify pattern matches expected pattern
    component pattern_verifier = IsEqual();
    pattern_verifier.in[0] <== computed_pattern_hash;
    pattern_verifier.in[1] <== expected_pattern_hash;
    pattern_matches <== pattern_verifier.out;
    
    // Step 3: Validate session duration
    component session_min_check = GreaterEqThan(32);
    component session_max_check = LessEqThan(32);
    session_min_check.in[0] <== session_duration;
    session_min_check.in[1] <== min_session_duration;
    session_max_check.in[0] <== session_duration;
    session_max_check.in[1] <== max_session_duration;
    
    component session_and = IsEqual();
    session_and.in[0] <== session_min_check.out + session_max_check.out;
    session_and.in[1] <== 2;
    session_duration_ok <== session_and.out;
    
    // Step 4: Validate typing pattern
    component typing_min_check = GreaterEqThan(16);
    component typing_max_check = LessEqThan(16);
    typing_min_check.in[0] <== keystrokes_per_minute;
    typing_min_check.in[1] <== typing_speed_min;
    typing_max_check.in[0] <== keystrokes_per_minute;
    typing_max_check.in[1] <== typing_speed_max;
    
    component typing_and = IsEqual();
    typing_and.in[0] <== typing_min_check.out + typing_max_check.out;
    typing_and.in[1] <== 2;
    typing_pattern_ok <== typing_and.out;
    
    // Step 5: Calculate timing consistency
    // Compute variance in timing intervals
    signal mean_interval = (timing_intervals[0] + timing_intervals[1] + timing_intervals[2] + 
                           timing_intervals[3] + timing_intervals[4] + timing_intervals[5] + 
                           timing_intervals[6] + timing_intervals[7] + timing_intervals[8]) / 9;
    
    // Simplified variance calculation (absolute deviations)
    signal deviations[9];
    component abs_calc[9];
    
    for (var i = 0; i < 9; i++) {
        abs_calc[i] = LessEqThan(16);
        abs_calc[i].in[0] <== timing_intervals[i];
        abs_calc[i].in[1] <== mean_interval;
        deviations[i] <== abs_calc[i].out * (mean_interval - timing_intervals[i]) + 
                         (1 - abs_calc[i].out) * (timing_intervals[i] - mean_interval);
    }
    
    timing_variance <== (deviations[0] + deviations[1] + deviations[2] + deviations[3] + 
                        deviations[4] + deviations[5] + deviations[6] + deviations[7] + 
                        deviations[8]) / 9;
    
    component variance_check = LessEqThan(16);
    variance_check.in[0] <== timing_variance;
    variance_check.in[1] <== max_timing_variance;
    timing_consistency_ok <== variance_check.out;
    
    // Step 6: Calculate risk score (0-100)
    // Risk components: pattern mismatch, session anomaly, typing anomaly, timing inconsistency
    risk_components[0] <== (1 - pattern_matches) * 25;          // 25 points for pattern mismatch
    risk_components[1] <== (1 - session_duration_ok) * 20;      // 20 points for session anomaly
    risk_components[2] <== (1 - typing_pattern_ok) * 15;        // 15 points for typing anomaly
    risk_components[3] <== (1 - timing_consistency_ok) * 10;    // 10 points for timing inconsistency
    
    weighted_risk_score <== risk_components[0] + risk_components[1] + 
                           risk_components[2] + risk_components[3];
    
    // Add variance-based risk (remaining 30 points)
    signal variance_risk = (timing_variance * 30) / max_timing_variance;
    risk_score <== weighted_risk_score + variance_risk;
    
    // Step 7: Overall pattern validation
    component risk_check = LessEqThan(8);
    risk_check.in[0] <== risk_score;
    risk_check.in[1] <== risk_threshold;
    
    component pattern_final_and1 = IsEqual();
    pattern_final_and1.in[0] <== pattern_matches + session_duration_ok;
    pattern_final_and1.in[1] <== 2;
    
    component pattern_final_and2 = IsEqual();
    pattern_final_and2.in[0] <== pattern_final_and1.out + typing_pattern_ok;
    pattern_final_and2.in[1] <== 2;
    
    component pattern_final_and3 = IsEqual();
    pattern_final_and3.in[0] <== pattern_final_and2.out + timing_consistency_ok;
    pattern_final_and3.in[1] <== 2;
    
    component pattern_final_and4 = IsEqual();
    pattern_final_and4.in[0] <== pattern_final_and3.out + risk_check.out;
    pattern_final_and4.in[1] <== 2;
    
    overall_pattern_valid <== pattern_final_and4.out;
    
    // Step 8: Generate pattern proof hash for auditability
    component proof_hasher = Poseidon(5);
    proof_hasher.inputs[0] <== overall_pattern_valid;
    proof_hasher.inputs[1] <== risk_score;
    proof_hasher.inputs[2] <== pattern_confidence_level;
    proof_hasher.inputs[3] <== expected_pattern_hash;
    proof_hasher.inputs[4] <== pattern_salt;
    pattern_proof_hash <== proof_hasher.out;
    
    // Constraints: ensure outputs are in valid ranges
    component binary_check1 = IsEqual();
    binary_check1.in[0] <== overall_pattern_valid * (overall_pattern_valid - 1);
    binary_check1.in[1] <== 0;
    binary_check1.out === 1;
    
    // Risk score should be between 0 and 100
    component risk_min_check = GreaterEqThan(8);
    component risk_max_check = LessEqThan(8);
    risk_min_check.in[0] <== risk_score;
    risk_min_check.in[1] <== 0;
    risk_max_check.in[0] <== risk_score;
    risk_max_check.in[1] <== 100;
    
    component risk_range_check = IsEqual();
    risk_range_check.in[0] <== risk_min_check.out + risk_max_check.out;
    risk_range_check.in[1] <== 2;
    risk_range_check.out === 1;
    
    // Session duration should be positive
    component session_positive = GreaterThan(32);
    session_positive.in[0] <== session_duration;
    session_positive.in[1] <== 0;
    session_positive.out === 1;
}

component main = PatternMatcher();