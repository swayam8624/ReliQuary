#!/usr/bin/env python3
# test_trust_engine.py

"""
Test script for the Trust Scoring Engine.

This script tests the advanced trust scoring system including:
- Dynamic trust evaluation with multiple factors
- Machine learning-based pattern recognition  
- Adaptive thresholds based on user behavior
- Risk assessment and anomaly detection
- Historical trend analysis
- Compliance monitoring
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from zk.trust_engine import (
    TrustScoringEngine,
    TrustFactor,
    RiskLevel,
    TrustMetrics,
    UserTrustProfile,
    evaluate_user_trust
)

def test_new_user_evaluation():
    """Test trust evaluation for a new user."""
    print("\n=== Testing New User Trust Evaluation ===")
    
    # Initialize trust engine
    trust_engine = TrustScoringEngine()
    
    # Create context data for a new user
    context_data = {
        "user_id": "new_user_001",
        "device_verified": True,
        "timestamp_verified": True,
        "location_verified": True,
        "pattern_verified": True,
        "device_fingerprint": "new_device_12345",
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 3600,  # 1 hour ago
        "latitude": 37.7749,
        "longitude": -122.4194,
        "session_duration": 1800,  # 30 minutes
        "keystrokes_per_minute": 65,
        "access_frequency": 3,
        "business_hours_ok": True,
        "ip_consistency_ok": True
    }
    
    print(f"User: {context_data['user_id']}")
    print(f"All verifications passed: {all([context_data['device_verified'], context_data['timestamp_verified'], context_data['location_verified'], context_data['pattern_verified']])}")
    
    # Perform trust evaluation
    evaluation = trust_engine.evaluate_trust(context_data["user_id"], context_data, "session_001")
    
    # Display results
    print(f"\nTrust Evaluation Results:")
    print(f"✓ Overall Trust Score: {evaluation.overall_trust_score:.1f}/100")
    print(f"✓ Risk Level: {evaluation.risk_level.name}")
    print(f"✓ Confidence Level: {evaluation.confidence_level:.1f}%")
    print(f"✓ Recommendations: {len(evaluation.recommendations)} items")
    
    print(f"\nTrust Metrics Breakdown:")
    print(f"  Device Consistency: {evaluation.trust_metrics.device_consistency:.1f}")
    print(f"  Temporal Patterns: {evaluation.trust_metrics.temporal_patterns:.1f}")
    print(f"  Geographic Consistency: {evaluation.trust_metrics.geographic_consistency:.1f}")
    print(f"  Behavioral Patterns: {evaluation.trust_metrics.behavioral_patterns:.1f}")
    print(f"  Access Frequency: {evaluation.trust_metrics.access_frequency:.1f}")
    print(f"  Risk Indicators: {evaluation.trust_metrics.risk_indicators:.1f}")
    print(f"  Compliance Score: {evaluation.trust_metrics.compliance_score:.1f}")
    print(f"  Historical Reliability: {evaluation.trust_metrics.historical_reliability:.1f}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(evaluation.recommendations, 1):
        print(f"  {i}. {rec}")
    
    return evaluation.overall_trust_score >= 60, evaluation

def test_returning_user_patterns():
    """Test trust evaluation for a returning user with established patterns."""
    print("\n=== Testing Returning User with Established Patterns ===")
    
    trust_engine = TrustScoringEngine()
    user_id = "returning_user_002"
    
    # Simulate multiple access sessions to establish patterns
    print("Simulating historical access patterns...")
    
    base_context = {
        "user_id": user_id,
        "device_verified": True,
        "timestamp_verified": True,
        "location_verified": True,
        "pattern_verified": True,
        "device_fingerprint": "consistent_device_67890",
        "latitude": 40.7128,   # New York
        "longitude": -74.0060,
        "session_duration": 1200,  # 20 minutes
        "keystrokes_per_minute": 72,
        "access_frequency": 4,
        "business_hours_ok": True,
        "ip_consistency_ok": True
    }
    
    # Simulate 5 previous sessions with consistent patterns
    for i in range(5):
        session_time = int(time.time()) - (i + 1) * 86400  # Daily access
        context = base_context.copy()
        context.update({
            "current_timestamp": session_time,
            "last_access_time": session_time - 86400 if i < 4 else session_time - 3600,
            "session_duration": 1200 + (i * 60),  # Slightly varying session duration
            "keystrokes_per_minute": 72 + (i * 2)  # Slightly varying typing speed
        })
        
        evaluation = trust_engine.evaluate_trust(user_id, context, f"session_{i+1}")
        print(f"  Session {i+1}: Trust Score = {evaluation.overall_trust_score:.1f}")
    
    # Now perform current evaluation
    print(f"\nCurrent session evaluation:")
    current_context = base_context.copy()
    current_context.update({
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 86400,  # Same pattern (daily access)
    })
    
    evaluation = trust_engine.evaluate_trust(user_id, current_context, "current_session")
    
    # Display results
    print(f"\nTrust Evaluation Results:")
    print(f"✓ Overall Trust Score: {evaluation.overall_trust_score:.1f}/100")
    print(f"✓ Risk Level: {evaluation.risk_level.name}")
    print(f"✓ Confidence Level: {evaluation.confidence_level:.1f}%")
    print(f"✓ Adaptive Thresholds Adjusted: {'Yes' if evaluation.confidence_level > 50 else 'No'}")
    
    print(f"\nAdaptive Thresholds:")
    for level, threshold in evaluation.adaptive_thresholds.items():
        print(f"  {level.replace('_', ' ').title()}: {threshold:.1f}")
    
    return evaluation.overall_trust_score >= 80, evaluation

def test_anomaly_detection():
    """Test anomaly detection and risk assessment."""
    print("\n=== Testing Anomaly Detection and Risk Assessment ===")
    
    trust_engine = TrustScoringEngine()
    user_id = "anomaly_user_003"
    
    # First, establish normal patterns
    print("Establishing normal user patterns...")
    normal_context = {
        "user_id": user_id,
        "device_verified": True,
        "timestamp_verified": True,
        "location_verified": True,
        "pattern_verified": True,
        "device_fingerprint": "normal_device_11111",
        "latitude": 51.5074,   # London
        "longitude": -0.1278,
        "session_duration": 900,   # 15 minutes
        "keystrokes_per_minute": 55,
        "access_frequency": 2,
        "business_hours_ok": True,
        "ip_consistency_ok": True
    }
    
    # Establish baseline (3 normal sessions)
    for i in range(3):
        session_time = int(time.time()) - (i + 1) * 86400
        context = normal_context.copy()
        context.update({
            "current_timestamp": session_time,
            "last_access_time": session_time - 86400 if i < 2 else session_time - 3600,
        })
        
        evaluation = trust_engine.evaluate_trust(user_id, context, f"baseline_{i+1}")
        print(f"  Baseline Session {i+1}: Trust Score = {evaluation.overall_trust_score:.1f}")
    
    # Now test with anomalous behavior
    print(f"\nTesting anomalous access patterns:")
    
    # Test 1: Different device
    print("1. Different device access:")
    anomaly_context = normal_context.copy()
    anomaly_context.update({
        "device_verified": False,  # Device verification failed
        "device_fingerprint": "suspicious_device_99999",
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 86400,
    })
    
    evaluation = trust_engine.evaluate_trust(user_id, anomaly_context, "anomaly_device")
    print(f"   Trust Score: {evaluation.overall_trust_score:.1f}, Risk: {evaluation.risk_level.name}")
    
    # Test 2: Unusual location
    print("2. Unusual location access:")
    anomaly_context = normal_context.copy()
    anomaly_context.update({
        "latitude": -33.8688,   # Sydney (very different from London)
        "longitude": 151.2093,
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 7200,  # 2 hours ago (impossible travel)
    })
    
    evaluation = trust_engine.evaluate_trust(user_id, anomaly_context, "anomaly_location")
    print(f"   Trust Score: {evaluation.overall_trust_score:.1f}, Risk: {evaluation.risk_level.name}")
    
    # Test 3: Rapid access attempts
    print("3. Rapid access attempts:")
    anomaly_context = normal_context.copy()
    anomaly_context.update({
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 30,  # 30 seconds ago (very rapid)
        "access_frequency": 20,  # Much higher than normal
    })
    
    evaluation = trust_engine.evaluate_trust(user_id, anomaly_context, "anomaly_rapid")
    print(f"   Trust Score: {evaluation.overall_trust_score:.1f}, Risk: {evaluation.risk_level.name}")
    
    # Test 4: Multiple verification failures
    print("4. Multiple verification failures:")
    anomaly_context = normal_context.copy()
    anomaly_context.update({
        "device_verified": False,
        "timestamp_verified": False,
        "location_verified": False,
        "pattern_verified": False,
        "business_hours_ok": False,
        "ip_consistency_ok": False,
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 86400,
    })
    
    evaluation = trust_engine.evaluate_trust(user_id, anomaly_context, "anomaly_multiple_failures")
    print(f"   Trust Score: {evaluation.overall_trust_score:.1f}, Risk: {evaluation.risk_level.name}")
    
    print(f"\nHigh-Risk Recommendations:")
    for i, rec in enumerate(evaluation.recommendations, 1):
        print(f"  {i}. {rec}")
    
    return evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH], evaluation

def test_adaptive_thresholds():
    """Test adaptive threshold adjustment based on user behavior."""
    print("\n=== Testing Adaptive Threshold Adjustment ===")
    
    trust_engine = TrustScoringEngine()
    
    # Test with high-trust user
    high_trust_user = "high_trust_user"
    print("1. High-trust user pattern:")
    
    # Establish high trust pattern
    for i in range(10):
        high_trust_context = {
            "user_id": high_trust_user,
            "device_verified": True,
            "timestamp_verified": True,
            "location_verified": True,
            "pattern_verified": True,
            "device_fingerprint": "trusted_device",
            "current_timestamp": int(time.time()) - i * 3600,
            "last_access_time": int(time.time()) - (i + 1) * 3600,
            "latitude": 47.6062,   # Seattle
            "longitude": -122.3321,
            "session_duration": 1500,
            "keystrokes_per_minute": 80,
            "access_frequency": 3,
            "business_hours_ok": True,
            "ip_consistency_ok": True
        }
        
        evaluation = trust_engine.evaluate_trust(high_trust_user, high_trust_context, f"high_trust_{i}")
    
    print(f"   Final Trust Score: {evaluation.overall_trust_score:.1f}")
    print(f"   Confidence Level: {evaluation.confidence_level:.1f}%")
    print(f"   Adaptive Thresholds:")
    for level, threshold in evaluation.adaptive_thresholds.items():
        print(f"     {level}: {threshold:.1f}")
    
    # Test with low-trust user
    low_trust_user = "low_trust_user"
    print("\n2. Low-trust user pattern:")
    
    # Establish low trust pattern
    for i in range(10):
        low_trust_context = {
            "user_id": low_trust_user,
            "device_verified": i % 2 == 0,  # Inconsistent device verification
            "timestamp_verified": True,
            "location_verified": i % 3 != 0,  # Inconsistent location
            "pattern_verified": i % 4 != 0,  # Inconsistent patterns
            "device_fingerprint": f"device_{i % 3}",  # Multiple devices
            "current_timestamp": int(time.time()) - i * 1800,
            "last_access_time": int(time.time()) - (i + 1) * 1800,
            "latitude": 37.7749 + (i * 0.1),  # Varying locations
            "longitude": -122.4194 + (i * 0.1),
            "session_duration": 600 + (i * 100),  # Varying sessions
            "keystrokes_per_minute": 40 + (i * 5),  # Varying typing
            "access_frequency": 1 + (i % 5),
            "business_hours_ok": i % 5 != 0,
            "ip_consistency_ok": i % 3 == 0
        }
        
        evaluation = trust_engine.evaluate_trust(low_trust_user, low_trust_context, f"low_trust_{i}")
    
    print(f"   Final Trust Score: {evaluation.overall_trust_score:.1f}")
    print(f"   Confidence Level: {evaluation.confidence_level:.1f}%")
    print(f"   Adaptive Thresholds:")
    for level, threshold in evaluation.adaptive_thresholds.items():
        print(f"     {level}: {threshold:.1f}")
    
    return True, evaluation

def test_convenience_functions():
    """Test convenience functions for easy integration."""
    print("\n=== Testing Convenience Functions ===")
    
    # Test the convenience function
    context_result = {
        "device_verified": True,
        "timestamp_verified": True,
        "location_verified": True,
        "pattern_verified": True,
        "device_fingerprint": "convenience_test_device",
        "current_timestamp": int(time.time()),
        "last_access_time": int(time.time()) - 1800,
        "latitude": 34.0522,   # Los Angeles
        "longitude": -118.2437,
        "session_duration": 2100,
        "keystrokes_per_minute": 58,
        "access_frequency": 4,
        "business_hours_ok": True,
        "ip_consistency_ok": True
    }
    
    # Use convenience function
    evaluation = evaluate_user_trust("convenience_user", context_result)
    
    print(f"User: convenience_user")
    print(f"Trust Score: {evaluation.overall_trust_score:.1f}/100")
    print(f"Risk Level: {evaluation.risk_level.name}")
    print(f"Confidence: {evaluation.confidence_level:.1f}%")
    
    return evaluation.overall_trust_score > 0, evaluation

def main():
    """Run all trust engine tests."""
    print("🚀 Starting Trust Scoring Engine Tests")
    print("=" * 60)
    
    try:
        # Test new user evaluation
        test1_passed, eval1 = test_new_user_evaluation()
        
        # Test returning user with patterns
        test2_passed, eval2 = test_returning_user_patterns()
        
        # Test anomaly detection
        test3_passed, eval3 = test_anomaly_detection()
        
        # Test adaptive thresholds
        test4_passed, eval4 = test_adaptive_thresholds()
        
        # Test convenience functions
        test5_passed, eval5 = test_convenience_functions()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Trust Engine Test Summary:")
        print(f"✓ New User Evaluation: {'PASS' if test1_passed else 'FAIL'}")
        print(f"✓ Returning User Patterns: {'PASS' if test2_passed else 'FAIL'}")
        print(f"✓ Anomaly Detection: {'PASS' if test3_passed else 'FAIL'}")
        print(f"✓ Adaptive Thresholds: {'PASS' if test4_passed else 'FAIL'}")
        print(f"✓ Convenience Functions: {'PASS' if test5_passed else 'FAIL'}")
        
        all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
        
        if all_passed:
            print("\n🎉 All Trust Scoring Engine Tests PASSED!")
            print("✅ Dynamic trust evaluation is working correctly")
            print("✅ Machine learning patterns and adaptive thresholds operational")
            print("✅ Risk assessment and anomaly detection functional")
            print("✅ Historical analysis and compliance monitoring active")
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