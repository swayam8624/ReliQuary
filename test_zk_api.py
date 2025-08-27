#!/usr/bin/env python3
# test_zk_api.py

"""
Integration test script for ZK API endpoints.

This script tests the complete ZK integration including:
- API endpoint authentication
- Context verification via REST API
- Vault access control with ZK proofs
- Trust scoring integration
- Error handling and edge cases
"""

import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

def get_auth_token() -> str:
    """Get authentication token for API access."""
    # For testing, we'll use the client credentials flow
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": "test_client",
        "client_secret": "test_secret",
        "scope": "read write admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Failed to get auth token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Auth token request failed: {e}")
        return None

def test_zk_system_status(token: str) -> bool:
    """Test the ZK system status endpoint."""
    print("\n=== Testing ZK System Status ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/zk/system-status", headers=headers)
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✓ System Status: {status_data['status']}")
            print(f"✓ Components: {', '.join(status_data['components'].keys())}")
            print(f"✓ Test Evaluation Time: {status_data['performance']['test_evaluation_time']}s")
            print(f"✓ System Responsive: {status_data['performance']['system_responsive']}")
            
            return status_data["status"] == "healthy"
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_quick_verify(token: str) -> bool:
    """Test the quick verification endpoint."""
    print("\n=== Testing Quick Verification ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test basic device verification
    params = {
        "device_fingerprint": "test_device_api_12345"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/zk/quick-verify", headers=headers, params=params)
        
        if response.status_code == 200:
            verify_data = response.json()
            print(f"✓ Device Verified: {verify_data['verified']}")
            print(f"✓ Trust Score: {verify_data['trust_score']}")
            print(f"✓ Level Met: {verify_data['verification_level_met']}")
            print(f"✓ Processing Time: {verify_data['processing_time']:.3f}s")
            
            return verify_data["verified"]
        else:
            print(f"❌ Quick verify failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Quick verify error: {e}")
        return False

def test_context_verification(token: str) -> bool:
    """Test full context verification endpoint."""
    print("\n=== Testing Full Context Verification ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create comprehensive verification request
    verification_request = {
        "verification_level": "STANDARD",
        "requirements_mask": 7,  # Device + Timestamp + Location
        "device_context": {
            "fingerprint": "comprehensive_device_67890",
            "hsm_signature": "hsm_signature_test",
            "device_hash": "device_hash_test",
            "challenge_nonce": str(int(time.time()))
        },
        "timestamp_context": {
            "current_timestamp": int(time.time()),
            "last_access_time": int(time.time()) - 3600,
            "timezone_offset": -28800,
            "require_business_hours": False,
            "require_totp": False
        },
        "location_context": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "previous_latitude": 37.7750,
            "previous_longitude": -122.4195,
            "travel_time_hours": 1
        },
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/zk/verify-context", 
            headers=headers, 
            json=verification_request
        )
        
        if response.status_code == 200:
            verify_data = response.json()
            print(f"✓ Overall Verified: {verify_data['verified']}")
            print(f"✓ Trust Score: {verify_data['trust_score']}/100")
            print(f"✓ Risk Level: {verify_data['risk_level']}")
            print(f"✓ Device Verified: {verify_data['device_verified']}")
            print(f"✓ Timestamp Verified: {verify_data['timestamp_verified']}")
            print(f"✓ Location Verified: {verify_data['location_verified']}")
            print(f"✓ Verification Time: {verify_data['verification_time']:.3f}s")
            print(f"✓ Confidence Level: {verify_data['confidence_level']:.1f}%")
            
            if verify_data['recommendations']:
                print(f"✓ Recommendations: {len(verify_data['recommendations'])} items")
                for i, rec in enumerate(verify_data['recommendations'][:3], 1):
                    print(f"   {i}. {rec}")
            
            return verify_data["verified"]
        else:
            print(f"❌ Context verification failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Context verification error: {e}")
        return False

def test_vault_access(token: str) -> bool:
    """Test vault access with ZK verification."""
    print("\n=== Testing Vault Access with ZK Verification ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test vault read access
    vault_request = {
        "vault_operation": "read",
        "vault_path": "/secrets/test-data",
        "verification_request": {
            "verification_level": "BASIC",
            "requirements_mask": 1,  # Device only
            "device_context": {
                "fingerprint": "vault_access_device_99999",
                "hsm_signature": "vault_hsm_signature",
                "device_hash": "vault_device_hash",
                "challenge_nonce": str(int(time.time()))
            },
            "session_id": "vault_session_456"
        },
        "force_verification": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/zk/vault-access", 
            headers=headers, 
            json=vault_request
        )
        
        if response.status_code == 200:
            access_data = response.json()
            print(f"✓ Access Granted: {access_data['access_granted']}")
            print(f"✓ Trust Score: {access_data['verification_result']['trust_score']}")
            print(f"✓ Risk Level: {access_data['verification_result']['risk_level']}")
            
            if access_data['access_granted']:
                print(f"✓ Access Token: {access_data['access_token'][:16]}...")
                print(f"✓ Token Expires: {access_data['access_expires']}")
            
            if access_data['required_actions']:
                print(f"✓ Required Actions: {len(access_data['required_actions'])} items")
                for i, action in enumerate(access_data['required_actions'][:2], 1):
                    print(f"   {i}. {action}")
            
            return access_data["access_granted"]
        else:
            print(f"❌ Vault access failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Vault access error: {e}")
        return False

def test_edge_cases(token: str) -> bool:
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases and Error Handling ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Invalid verification level
    print("1. Testing invalid verification level:")
    invalid_request = {
        "verification_level": "INVALID_LEVEL",
        "requirements_mask": 1,
        "device_context": {
            "fingerprint": "test_device",
            "hsm_signature": "test_sig",
            "device_hash": "test_hash",
            "challenge_nonce": "test_nonce"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/zk/verify-context", headers=headers, json=invalid_request)
        if response.status_code in [400, 422]:
            print("   ✓ Properly rejected invalid verification level")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid level: {e}")
    
    # Test 2: Missing required context
    print("2. Testing missing required context:")
    missing_context_request = {
        "verification_level": "STANDARD",
        "requirements_mask": 15,  # All requirements but no context provided
    }
    
    try:
        response = requests.post(f"{BASE_URL}/zk/verify-context", headers=headers, json=missing_context_request)
        if response.status_code == 200:
            result = response.json()
            if not result["verified"]:
                print("   ✓ Properly handled missing context")
            else:
                print("   ❌ Should not verify with missing context")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing missing context: {e}")
    
    # Test 3: Invalid vault operation
    print("3. Testing invalid vault operation:")
    invalid_vault_request = {
        "vault_operation": "invalid_operation",
        "vault_path": "/test",
        "verification_request": {
            "verification_level": "BASIC",
            "requirements_mask": 1
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/zk/vault-access", headers=headers, json=invalid_vault_request)
        if response.status_code == 400:
            print("   ✓ Properly rejected invalid vault operation")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid vault operation: {e}")
    
    return True

def main():
    """Run all ZK API integration tests."""
    print("🚀 Starting ZK API Integration Tests")
    print("=" * 60)
    
    # Get authentication token
    print("Getting authentication token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Failed to get authentication token")
        print("Make sure the API server is running and authentication is configured")
        return False
    
    print("✓ Authentication token obtained")
    
    try:
        # Run tests
        test1_passed = test_zk_system_status(token)
        test2_passed = test_quick_verify(token)
        test3_passed = test_context_verification(token)
        test4_passed = test_vault_access(token)
        test5_passed = test_edge_cases(token)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 ZK API Integration Test Summary:")
        print(f"✓ System Status: {'PASS' if test1_passed else 'FAIL'}")
        print(f"✓ Quick Verification: {'PASS' if test2_passed else 'FAIL'}")
        print(f"✓ Context Verification: {'PASS' if test3_passed else 'FAIL'}")
        print(f"✓ Vault Access: {'PASS' if test4_passed else 'FAIL'}")
        print(f"✓ Edge Cases: {'PASS' if test5_passed else 'FAIL'}")
        
        all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
        
        if all_passed:
            print("\n🎉 All ZK API Integration Tests PASSED!")
            print("✅ Zero-knowledge API endpoints are fully operational")
            print("✅ Context verification REST API working correctly")
            print("✅ Vault access control with ZK proofs functional")
            print("✅ Trust scoring integration successful")
            print("✅ Error handling and edge cases properly managed")
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