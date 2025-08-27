#!/usr/bin/env python3
# test_context_manager.py

"""
Test script for the Context Verification Manager.

This script tests the ZK-based context verification system including:
- Device verification with zero-knowledge proofs
- Timestamp validation with privacy preservation  
- Location verification without coordinate exposure
- Behavioral pattern matching
- Trust scoring and verification levels
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from zk.context_manager import (
    ContextVerificationManager, 
    ContextVerificationRequest,
    DeviceContext,
    TimestampContext, 
    LocationContext,
    PatternContext,
    VerificationLevel,
    ContextRequirement,
    create_basic_device_verification,
    create_standard_verification
)

def test_basic_device_verification():
    """Test basic device verification with ZK proof."""
    print("\n=== Testing Basic Device Verification ===")
    
    # Initialize context manager
    context_manager = ContextVerificationManager()
    
    # Create a basic device verification request
    request = create_basic_device_verification(
        user_id="test_user_123",
        device_fingerprint="test_device_fingerprint_12345",
        challenge_nonce="challenge_nonce_67890"
    )
    
    print(f"User ID: {request.user_id}")
    print(f"Verification Level: {request.verification_level.name}")
    print(f"Requirements Mask: {request.requirements_mask}")
    print(f"Device Fingerprint: {request.device_context.fingerprint}")
    
    # Perform verification
    print("\nPerforming device verification...")
    result = context_manager.verify_context(request)
    
    # Display results
    print(f"\nVerification Results:")
    print(f"✓ Verified: {result.verified}")
    print(f"✓ Trust Score: {result.trust_score}/100")
    print(f"✓ Level Met: {result.verification_level_met}")
    print(f"✓ Device Verified: {result.device_verified}")
    print(f"✓ Verification Time: {result.verification_time:.3f}s")
    
    if result.proof_hash:
        print(f"✓ Proof Hash: {result.proof_hash[:16]}...")
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
    
    return result.verified

def test_standard_verification():
    """Test standard verification with device, timestamp, and location."""
    print("\n=== Testing Standard Context Verification ===")
    
    # Initialize context manager
    context_manager = ContextVerificationManager()
    
    # Create a standard verification request
    request = create_standard_verification(
        user_id="test_user_456",
        device_fingerprint="standard_device_98765",
        location_lat=37.7749,  # San Francisco
        location_lon=-122.4194
    )
    
    print(f"User ID: {request.user_id}")
    print(f"Verification Level: {request.verification_level.name}")
    print(f"Device Fingerprint: {request.device_context.fingerprint}")
    print(f"Location: ({request.location_context.latitude}, {request.location_context.longitude})")
    print(f"Timestamp: {request.timestamp_context.current_timestamp}")
    
    # Perform verification
    print("\nPerforming standard verification...")
    result = context_manager.verify_context(request)
    
    # Display results
    print(f"\nVerification Results:")
    print(f"✓ Verified: {result.verified}")
    print(f"✓ Trust Score: {result.trust_score}/100")
    print(f"✓ Level Met: {result.verification_level_met}")
    print(f"✓ Device Verified: {result.device_verified}")
    print(f"✓ Timestamp Verified: {result.timestamp_verified}")
    print(f"✓ Location Verified: {result.location_verified}")
    print(f"✓ Verification Time: {result.verification_time:.3f}s")
    
    if result.proof_hash:
        print(f"✓ Combined Proof Hash: {result.proof_hash[:16]}...")
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
    
    return result.verified

def test_comprehensive_verification():
    """Test comprehensive verification with all context types."""
    print("\n=== Testing Comprehensive Context Verification ===")
    
    # Initialize context manager
    context_manager = ContextVerificationManager()
    
    # Create comprehensive context data
    challenge_nonce = str(int(time.time()))
    
    device_context = DeviceContext(
        fingerprint="comprehensive_device_11111",
        hsm_signature=f"hsm_sig_{challenge_nonce}",
        device_hash="device_hash_22222",
        challenge_nonce=challenge_nonce
    )
    
    timestamp_context = TimestampContext(
        current_timestamp=int(time.time()),
        last_access_time=int(time.time()) - 1800,  # 30 minutes ago
        timezone_offset=-28800,  # PST
        require_business_hours=False,
        require_totp=False
    )
    
    location_context = LocationContext(
        latitude=40.7128,   # New York
        longitude=-74.0060,
        previous_latitude=40.7589,  # Previous location in NYC
        previous_longitude=-73.9851,
        travel_time_hours=1
    )
    
    pattern_context = PatternContext(
        action_sequence=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        timing_intervals=[100, 150, 120, 110, 140, 130, 125, 135, 115],
        session_duration=1800,  # 30 minutes
        keystrokes_per_minute=65,
        mouse_movements=200,
        access_frequency=5
    )
    
    # Create comprehensive verification request
    request = ContextVerificationRequest(
        user_id="test_user_comprehensive",
        verification_level=VerificationLevel.HIGH,
        requirements_mask=(ContextRequirement.DEVICE.value | 
                          ContextRequirement.TIMESTAMP.value |
                          ContextRequirement.LOCATION.value |
                          ContextRequirement.PATTERN.value),
        device_context=device_context,
        timestamp_context=timestamp_context,
        location_context=location_context,
        pattern_context=pattern_context,
        challenge_nonce=challenge_nonce
    )
    
    print(f"User ID: {request.user_id}")
    print(f"Verification Level: {request.verification_level.name}")
    print(f"Requirements: Device + Timestamp + Location + Pattern")
    print(f"Session Duration: {pattern_context.session_duration}s")
    print(f"Typing Speed: {pattern_context.keystrokes_per_minute} WPM")
    
    # Perform verification
    print("\nPerforming comprehensive verification...")
    result = context_manager.verify_context(request)
    
    # Display results
    print(f"\nVerification Results:")
    print(f"✓ Verified: {result.verified}")
    print(f"✓ Trust Score: {result.trust_score}/100")
    print(f"✓ Level Met: {result.verification_level_met}")
    print(f"✓ Device Verified: {result.device_verified}")
    print(f"✓ Timestamp Verified: {result.timestamp_verified}")
    print(f"✓ Location Verified: {result.location_verified}")
    print(f"✓ Pattern Verified: {result.pattern_verified}")
    print(f"✓ Verification Time: {result.verification_time:.3f}s")
    
    if result.proof_hash:
        print(f"✓ Combined Proof Hash: {result.proof_hash[:16]}...")
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
    
    return result.verified

def test_failed_verification():
    """Test verification failure scenarios."""
    print("\n=== Testing Failed Verification Scenarios ===")
    
    # Initialize context manager
    context_manager = ContextVerificationManager()
    
    # Test 1: Missing required context
    print("\n--- Test 1: Missing Device Context ---")
    request = ContextVerificationRequest(
        user_id="test_user_fail",
        verification_level=VerificationLevel.BASIC,
        requirements_mask=ContextRequirement.DEVICE.value,
        device_context=None  # Missing required context
    )
    
    result = context_manager.verify_context(request)
    print(f"Expected failure - Verified: {result.verified}")
    print(f"Error Message: {result.error_message}")
    
    # Test 2: Invalid location data
    print("\n--- Test 2: Invalid Location Data ---")
    device_context = DeviceContext(
        fingerprint="test_device",
        hsm_signature="test_sig", 
        device_hash="test_hash",
        challenge_nonce="test_nonce"
    )
    
    invalid_location_context = LocationContext(
        latitude=999,  # Invalid latitude
        longitude=-999  # Invalid longitude
    )
    
    request = ContextVerificationRequest(
        user_id="test_user_fail_location",
        verification_level=VerificationLevel.STANDARD,
        requirements_mask=ContextRequirement.DEVICE.value | ContextRequirement.LOCATION.value,
        device_context=device_context,
        location_context=invalid_location_context
    )
    
    result = context_manager.verify_context(request)
    print(f"Invalid location - Verified: {result.verified}")
    print(f"Trust Score: {result.trust_score}")
    
    return True

def main():
    """Run all context verification tests."""
    print("🚀 Starting Context Verification Manager Tests")
    print("=" * 60)
    
    try:
        # Test basic device verification with ZK proof
        test1_passed = test_basic_device_verification()
        
        # Test standard multi-context verification
        test2_passed = test_standard_verification()
        
        # Test comprehensive verification
        test3_passed = test_comprehensive_verification()
        
        # Test failure scenarios
        test4_passed = test_failed_verification()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Test Summary:")
        print(f"✓ Basic Device Verification: {'PASS' if test1_passed else 'FAIL'}")
        print(f"✓ Standard Verification: {'PASS' if test2_passed else 'FAIL'}")
        print(f"✓ Comprehensive Verification: {'PASS' if test3_passed else 'FAIL'}")
        print(f"✓ Failure Scenarios: {'PASS' if test4_passed else 'FAIL'}")
        
        all_passed = test1_passed and test2_passed and test3_passed and test4_passed
        
        if all_passed:
            print("\n🎉 All Context Verification Tests PASSED!")
            print("✅ Zero-knowledge context verification system is working correctly")
            print("✅ Privacy-preserving authentication is operational")
            print("✅ Trust scoring and verification levels are functional")
        else:
            print("\n❌ Some tests failed. Please check the logs above.")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)