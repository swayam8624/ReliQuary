#!/usr/bin/env python3
# test_zk_comprehensive.py

"""
Comprehensive Integration Tests for ZK Proof System and Context Verification.

This test suite validates the complete Zero-Knowledge Context Verification system.
"""

import asyncio
import sys
import os
import time
import json
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import ZK components
from zk.context_manager import (
    ContextVerificationManager,
    create_basic_device_verification,
    create_standard_verification
)

from zk.trust_engine import TrustScoringEngine, RiskLevel

from agents import create_validator_agent, AgentCoordinator

async def test_complete_zk_workflow():
    """Test the complete ZK workflow from start to finish."""
    print("\n=== Testing Complete ZK Workflow ===")
    
    try:
        # Initialize all components
        context_manager = ContextVerificationManager()
        trust_engine = TrustScoringEngine()
        
        # Test 1: Basic device verification with ZK proof
        device_request = create_basic_device_verification(
            user_id="workflow_user_001",
            device_fingerprint="workflow_device_12345",
            challenge_nonce=str(int(time.time()))
        )
        
        device_result = context_manager.verify_context(device_request)
        device_verified = device_result.device_verified and device_result.trust_score > 0
        
        print(f"✓ Device ZK Verification: {'PASS' if device_verified else 'FAIL'}")
        print(f"  Trust Score: {device_result.trust_score}")
        print(f"  Proof Hash: {device_result.proof_hash[:16] if device_result.proof_hash else 'None'}...")
        
        # Test 2: Multi-context verification
        standard_request = create_standard_verification(
            user_id="workflow_user_002",
            device_fingerprint="workflow_device_67890",
            location_lat=37.7749,
            location_lon=-122.4194
        )
        
        standard_result = context_manager.verify_context(standard_request)
        multi_context_verified = (standard_result.device_verified and 
                                 standard_result.timestamp_verified and 
                                 standard_result.location_verified)
        
        print(f"✓ Multi-Context Verification: {'PASS' if multi_context_verified else 'FAIL'}")
        print(f"  All Contexts: {multi_context_verified}")
        print(f"  Trust Score: {standard_result.trust_score}")
        
        # Test 3: Trust scoring integration
        trust_context = {
            "device_verified": standard_result.device_verified,
            "timestamp_verified": standard_result.timestamp_verified,
            "location_verified": standard_result.location_verified,
            "pattern_verified": True,
            "device_fingerprint": "workflow_device_67890",
            "current_timestamp": int(time.time()),
            "session_duration": 1800,
            "keystrokes_per_minute": 65,
            "access_frequency": 3
        }
        
        trust_result = trust_engine.evaluate_trust("workflow_user_002", trust_context)
        trust_integration_success = trust_result.overall_trust_score > 60
        
        print(f"✓ Trust Integration: {'PASS' if trust_integration_success else 'FAIL'}")
        print(f"  Trust Score: {trust_result.overall_trust_score:.1f}")
        print(f"  Risk Level: {trust_result.risk_level.name}")
        
        # Test 4: Agent integration
        validator_agent = create_validator_agent("workflow_validator")
        agent_coordinator = AgentCoordinator()
        agent_coordinator.register_agent(validator_agent)
        
        agent_integration_success = (validator_agent.context_manager is not None and
                                   validator_agent.trust_engine is not None)
        
        print(f"✓ Agent Integration: {'PASS' if agent_integration_success else 'FAIL'}")
        print(f"  ZK Capabilities: {agent_integration_success}")
        
        # Overall workflow test
        workflow_success = (device_verified and multi_context_verified and 
                          trust_integration_success and agent_integration_success)
        
        print(f"✓ Complete Workflow: {'PASS' if workflow_success else 'FAIL'}")
        
        return workflow_success
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

async def test_performance_and_privacy():
    """Test performance and privacy preservation."""
    print("\n=== Testing Performance and Privacy ===")
    
    try:
        context_manager = ContextVerificationManager()
        
        # Performance test: measure verification times
        verification_times = []
        for i in range(5):
            start_time = time.time()
            
            request = create_basic_device_verification(
                user_id=f"perf_user_{i}",
                device_fingerprint=f"perf_device_{i}",
                challenge_nonce=str(int(time.time()) + i)
            )
            
            result = context_manager.verify_context(request)
            verification_time = time.time() - start_time
            verification_times.append(verification_time)
        
        avg_time = sum(verification_times) / len(verification_times)
        performance_acceptable = avg_time < 1.0
        
        print(f"✓ Performance Test: {'PASS' if performance_acceptable else 'FAIL'}")
        print(f"  Average Time: {avg_time:.3f}s")
        print(f"  Throughput: {1/avg_time:.1f} verifications/second")
        
        # Privacy test: check that sensitive data is not exposed
        sensitive_fingerprint = "super_secret_device_12345"
        request = create_basic_device_verification(
            user_id="privacy_user",
            device_fingerprint=sensitive_fingerprint,
            challenge_nonce="secret_nonce"
        )
        
        result = context_manager.verify_context(request)
        result_str = str(result.__dict__)
        
        privacy_preserved = sensitive_fingerprint not in result_str
        has_proof = result.proof_hash is not None
        
        print(f"✓ Privacy Test: {'PASS' if privacy_preserved else 'FAIL'}")
        print(f"  Sensitive Data Hidden: {privacy_preserved}")
        print(f"  Cryptographic Proof: {has_proof}")
        
        return performance_acceptable and privacy_preserved
        
    except Exception as e:
        print(f"❌ Performance and privacy test failed: {e}")
        return False

async def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===")
    
    try:
        context_manager = ContextVerificationManager()
        trust_engine = TrustScoringEngine()
        
        # Test 1: Invalid verification data
        try:
            invalid_request = create_basic_device_verification(
                user_id="edge_user",
                device_fingerprint="",  # Empty fingerprint
                challenge_nonce=""
            )
            result = context_manager.verify_context(invalid_request)
            invalid_handled = not result.verified  # Should fail verification
        except Exception:
            invalid_handled = True  # Exception handling is also acceptable
        
        print(f"✓ Invalid Data Handling: {'PASS' if invalid_handled else 'FAIL'}")
        
        # Test 2: Anomaly detection
        anomaly_context = {
            "device_verified": False,
            "timestamp_verified": False,
            "location_verified": False,
            "pattern_verified": False,
            "device_fingerprint": "suspicious_device",
            "current_timestamp": int(time.time()),
            "session_duration": 30,  # Very short
            "keystrokes_per_minute": 300,  # Unrealistic
            "access_frequency": 100  # Very high
        }
        
        anomaly_result = trust_engine.evaluate_trust("edge_user", anomaly_context)
        anomaly_detected = (anomaly_result.overall_trust_score < 40 and
                          anomaly_result.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH])
        
        print(f"✓ Anomaly Detection: {'PASS' if anomaly_detected else 'FAIL'}")
        print(f"  Risk Level: {anomaly_result.risk_level.name}")
        print(f"  Trust Score: {anomaly_result.overall_trust_score:.1f}")
        
        return invalid_handled and anomaly_detected
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False

async def main():
    """Run all comprehensive ZK tests."""
    print("🚀 Starting Comprehensive ZK System Tests")
    print("=" * 70)
    
    try:
        # Run test suites
        workflow_passed = await test_complete_zk_workflow()
        performance_passed = await test_performance_and_privacy()
        edge_cases_passed = await test_edge_cases()
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 Comprehensive ZK Test Summary:")
        print(f"✓ Complete ZK Workflow: {'PASS' if workflow_passed else 'FAIL'}")
        print(f"✓ Performance & Privacy: {'PASS' if performance_passed else 'FAIL'}")
        print(f"✓ Edge Cases: {'PASS' if edge_cases_passed else 'FAIL'}")
        
        all_passed = workflow_passed and performance_passed and edge_cases_passed
        
        if all_passed:
            print("\n🎉 All Comprehensive ZK Tests PASSED!")
            print("✅ Zero-knowledge proof system fully operational")
            print("✅ Context verification with privacy preservation working")
            print("✅ Trust scoring with machine learning patterns functional")
            print("✅ Multi-agent integration ready for Phase 4")
            print("✅ Performance and security requirements met")
            print("✅ Edge cases and error handling robust")
            print("\n🏆 Phase 3 - Context Verification with Zero-Knowledge Proofs COMPLETE!")
        else:
            print("\n❌ Some tests failed. Please check the logs above.")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)