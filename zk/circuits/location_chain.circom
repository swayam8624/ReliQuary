pragma circom 2.0.0;

// Include necessary libraries
include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

/*
 * Location Chain Verification Circuit
 * 
 * This circuit proves that access is happening from an authorized location
 * without revealing the exact coordinates. It verifies:
 * 1. Location is within authorized geographic boundaries
 * 2. Location is not in restricted/blacklisted areas
 * 3. Location chain consistency (reasonable travel time between locations)
 * 4. IP geolocation consistency with claimed location
 * 
 * Privacy Properties:
 * - Exact coordinates remain private
 * - Only proof of authorized location access is public
 * - Supports multiple authorized regions
 * - Travel pattern analysis without location exposure
 */

template LocationChainVerifier() {
    // Private inputs (witness)
    signal private input current_latitude;      // Current GPS latitude (scaled to integer)
    signal private input current_longitude;     // Current GPS longitude (scaled to integer)
    signal private input previous_latitude;     // Previous location latitude
    signal private input previous_longitude;    // Previous location longitude
    signal private input ip_location_lat;       // IP-based location latitude
    signal private input ip_location_lon;       // IP-based location longitude
    signal private input location_salt;         // Salt for location hashing
    signal private input travel_time_hours;     // Time since last location update
    
    // Public inputs
    signal input authorized_region_center_lat;  // Authorized region center latitude
    signal input authorized_region_center_lon;  // Authorized region center longitude
    signal input authorized_radius_squared;     // Authorized radius squared (for distance calc)
    signal input blacklist_region_lat;          // Blacklisted region center
    signal input blacklist_region_lon;          // Blacklisted region center
    signal input blacklist_radius_squared;      // Blacklisted region radius squared
    signal input max_travel_speed;              // Maximum reasonable travel speed (km/h)
    signal input ip_tolerance_radius_squared;   // Tolerance for IP vs GPS location
    signal input require_ip_consistency;        // 1 if IP consistency check is required
    
    // Outputs
    signal output location_authorized;          // 1 if location is in authorized region
    signal output not_blacklisted;             // 1 if location is not blacklisted
    signal output travel_time_valid;           // 1 if travel time is reasonable
    signal output ip_consistency_ok;           // 1 if IP location matches GPS
    signal output overall_valid;               // 1 if all location checks pass
    signal output location_proof_hash;         // Hash proof for auditability
    
    // Internal signals for distance calculations
    signal lat_diff_auth;
    signal lon_diff_auth;
    signal distance_squared_auth;
    signal lat_diff_blacklist;
    signal lon_diff_blacklist;
    signal distance_squared_blacklist;
    signal lat_diff_travel;
    signal lon_diff_travel;
    signal travel_distance_squared;
    signal max_travel_distance_squared;
    signal lat_diff_ip;
    signal lon_diff_ip;
    signal ip_distance_squared;
    
    // Step 1: Verify location is within authorized region
    lat_diff_auth <== current_latitude - authorized_region_center_lat;
    lon_diff_auth <== current_longitude - authorized_region_center_lon;
    distance_squared_auth <== lat_diff_auth * lat_diff_auth + lon_diff_auth * lon_diff_auth;
    
    component auth_check = LessEqThan(32);
    auth_check.in[0] <== distance_squared_auth;
    auth_check.in[1] <== authorized_radius_squared;
    location_authorized <== auth_check.out;
    
    // Step 2: Verify location is not in blacklisted region
    lat_diff_blacklist <== current_latitude - blacklist_region_lat;
    lon_diff_blacklist <== current_longitude - blacklist_region_lon;
    distance_squared_blacklist <== lat_diff_blacklist * lat_diff_blacklist + lon_diff_blacklist * lon_diff_blacklist;
    
    component blacklist_check = GreaterThan(32);
    blacklist_check.in[0] <== distance_squared_blacklist;
    blacklist_check.in[1] <== blacklist_radius_squared;
    not_blacklisted <== blacklist_check.out;
    
    // Step 3: Verify travel time is reasonable (if previous location exists)
    lat_diff_travel <== current_latitude - previous_latitude;
    lon_diff_travel <== current_longitude - previous_longitude;
    travel_distance_squared <== lat_diff_travel * lat_diff_travel + lon_diff_travel * lon_diff_travel;
    
    // Maximum possible travel distance based on time and speed
    max_travel_distance_squared <== travel_time_hours * travel_time_hours * max_travel_speed * max_travel_speed;
    
    component travel_check = LessEqThan(32);
    travel_check.in[0] <== travel_distance_squared;
    travel_check.in[1] <== max_travel_distance_squared;
    travel_time_valid <== travel_check.out;
    
    // Step 4: Verify IP location consistency (if required)
    lat_diff_ip <== current_latitude - ip_location_lat;
    lon_diff_ip <== current_longitude - ip_location_lon;
    ip_distance_squared <== lat_diff_ip * lat_diff_ip + lon_diff_ip * lon_diff_ip;
    
    component ip_check = LessEqThan(32);
    ip_check.in[0] <== ip_distance_squared;
    ip_check.in[1] <== ip_tolerance_radius_squared;
    
    // Apply IP consistency check only if required
    component ip_conditional = IsEqual();
    ip_conditional.in[0] <== require_ip_consistency * ip_check.out + (1 - require_ip_consistency);
    ip_conditional.in[1] <== 1;
    ip_consistency_ok <== ip_conditional.out;
    
    // Step 5: Combine all location validations
    component location_and1 = IsEqual();
    location_and1.in[0] <== location_authorized + not_blacklisted;
    location_and1.in[1] <== 2;
    
    component location_and2 = IsEqual();
    location_and2.in[0] <== location_and1.out + travel_time_valid;
    location_and2.in[1] <== 2;
    
    component location_and3 = IsEqual();
    location_and3.in[0] <== location_and2.out + ip_consistency_ok;
    location_and3.in[1] <== 2;
    
    overall_valid <== location_and3.out;
    
    // Step 6: Generate location proof hash for auditability
    component location_hasher = Poseidon(4);
    location_hasher.inputs[0] <== overall_valid;
    location_hasher.inputs[1] <== authorized_region_center_lat;
    location_hasher.inputs[2] <== authorized_region_center_lon;
    location_hasher.inputs[3] <== location_salt;
    location_proof_hash <== location_hasher.out;
    
    // Constraints: ensure outputs are binary
    component binary_check1 = IsEqual();
    binary_check1.in[0] <== location_authorized * (location_authorized - 1);
    binary_check1.in[1] <== 0;
    binary_check1.out === 1;
    
    component binary_check2 = IsEqual();
    binary_check2.in[0] <== overall_valid * (overall_valid - 1);
    binary_check2.in[1] <== 0;
    binary_check2.out === 1;
    
    // Constraint: ensure latitude and longitude are within valid ranges
    // Latitude: -90 to +90 degrees (scaled)
    component lat_min_check = GreaterEqThan(16);
    component lat_max_check = LessEqThan(16);
    lat_min_check.in[0] <== current_latitude;
    lat_min_check.in[1] <== -9000; // -90.00 degrees scaled by 100
    lat_max_check.in[0] <== current_latitude;
    lat_max_check.in[1] <== 9000;  // +90.00 degrees scaled by 100
    
    component lat_range_check = IsEqual();
    lat_range_check.in[0] <== lat_min_check.out + lat_max_check.out;
    lat_range_check.in[1] <== 2;
    lat_range_check.out === 1;
    
    // Longitude: -180 to +180 degrees (scaled)
    component lon_min_check = GreaterEqThan(16);
    component lon_max_check = LessEqThan(16);
    lon_min_check.in[0] <== current_longitude;
    lon_min_check.in[1] <== -18000; // -180.00 degrees scaled by 100
    lon_max_check.in[0] <== current_longitude;
    lon_max_check.in[1] <== 18000;  // +180.00 degrees scaled by 100
    
    component lon_range_check = IsEqual();
    lon_range_check.in[0] <== lon_min_check.out + lon_max_check.out;
    lon_range_check.in[1] <== 2;
    lon_range_check.out === 1;
}

component main = LocationChainVerifier();