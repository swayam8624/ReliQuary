#!/usr/bin/env python3
"""
Demo Access Script for ReliQuary

This script demonstrates the complete access flow for the ReliQuary system,
including authentication, context verification, trust evaluation, and 
agent consensus decision making.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
import argparse
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ReliQuary components
try:
    from auth.oauth import OAuthManager
    from core.trust.scorer import TrustScoringEngine
    from agents.decision_orchestrator import DecisionOrchestrator
    from core.utils.device_fingerprint import generate_device_fingerprint
    from zk.context_manager import ContextVerificationManager
except ImportError:
    # Mock implementations for demo purposes
    class OAuthManager:
        def __init__(self):
            pass
        
        def generate_client_token(self, client_id: str, client_secret: str) -> str:
            return f"demo_token_{uuid.uuid4().hex[:8]}"
    
    class TrustScoringEngine:
        def evaluate_trust(self, user_id: str, context: dict) -> dict:
            return {
                "overall_trust_score": 85.5,
                "risk_level": "low",
                "confidence_score": 0.92,
                "trust_factors": [
                    {"name": "context_verification", "weight": 0.3, "score": 90.0, "impact": 5.0},
                    {"name": "historical_behavior", "weight": 0.5, "score": 80.0, "impact": -3.0},
                    {"name": "device_trust", "weight": 0.2, "score": 95.0, "impact": 7.0}
                ]
            }
    
    class DecisionOrchestrator:
        async def make_decision(self, context: dict, user_id: str, resource_path: str) -> dict:
            return {
                "decision": "approved",
                "confidence": 0.95,
                "agents_consulted": ["neutral_agent", "permissive_agent", "strict_agent"],
                "reasoning": "Context verified with high confidence",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    class ContextVerificationManager:
        def verify_context(self, request) -> dict:
            return {
                "verified": True,
                "device_verified": True,
                "timestamp_verified": True,
                "location_verified": True,
                "pattern_verified": True,
                "trust_score": 95.0,
                "proof_hash": "demo_proof_hash"
            }
        
        def generate_device_fingerprint(self, browser_info: str = "") -> str:
            return f"demo_device_fingerprint_{uuid.uuid4().hex[:12]}"


def generate_demo_context(user_id: str = "demo_user") -> dict:
    """Generate demo context data for access request"""
    return {
        "user_id": user_id,
        "timestamp": int(datetime.now().timestamp()),
        "device_fingerprint": generate_device_fingerprint("Demo Browser 1.0"),
        "ip_address": "192.168.1.100",
        "user_agent": "Demo Browser 1.0",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "keystrokes_per_minute": 60,
        "access_frequency": 1,
        "session_duration": 300,
        "timezone_offset": -18000,  # EST
        "business_hours": True
    }


async def demo_authentication_flow():
    """Demonstrate the authentication flow"""
    print("=== ReliQuary Demo Access Flow ===")
    print("Step 1: Authentication")
    
    # Initialize OAuth manager
    oauth_manager = OAuthManager()
    
    # Generate demo client credentials
    client_id = "demo_client_123"
    client_secret = "demo_secret_456"
    
    # Generate access token
    token = oauth_manager.generate_client_token(client_id, client_secret)
    
    print(f"  Client ID: {client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Access Token: {token}")
    print("  ✓ Authentication successful")
    
    return token


async def demo_context_verification(context_data: dict):
    """Demonstrate context verification"""
    print("\nStep 2: Context Verification")
    
    # Initialize context verification manager
    context_manager = ContextVerificationManager()
    
    # Create mock verification request
    class MockRequest:
        def __init__(self, context):
            self.user_id = context["user_id"]
            self.device_context = type('obj', (object,), {
                'fingerprint': context["device_fingerprint"]
            })()
    
    request = MockRequest(context_data)
    
    # Verify context
    verification_result = context_manager.verify_context(request)
    
    print(f"  Device Verified: {verification_result['device_verified']}")
    print(f"  Timestamp Verified: {verification_result['timestamp_verified']}")
    print(f"  Location Verified: {verification_result['location_verified']}")
    print(f"  Pattern Verified: {verification_result['pattern_verified']}")
    print(f"  Context Trust Score: {verification_result['trust_score']}")
    print("  ✓ Context verification completed")
    
    return verification_result


async def demo_trust_evaluation(context_data: dict):
    """Demonstrate trust evaluation"""
    print("\nStep 3: Trust Evaluation")
    
    # Initialize trust scoring engine
    trust_engine = TrustScoringEngine()
    
    # Evaluate trust
    trust_result = trust_engine.evaluate_trust(context_data["user_id"], context_data)
    
    print(f"  Overall Trust Score: {trust_result['overall_trust_score']}")
    print(f"  Risk Level: {trust_result['risk_level']}")
    print(f"  Confidence Score: {trust_result['confidence_score']}")
    
    # Display trust factors
    print("  Trust Factors:")
    for factor in trust_result['trust_factors']:
        print(f"    - {factor['name']}: {factor['score']}")
    
    print("  ✓ Trust evaluation completed")
    
    return trust_result


async def demo_agent_consensus(context_data: dict, trust_score: float):
    """Demonstrate agent consensus decision making"""
    print("\nStep 4: Agent Consensus Decision")
    
    # Initialize decision orchestrator
    orchestrator = DecisionOrchestrator()
    
    # Prepare context for decision
    decision_context = {
        "decision_type": "access_request",
        "context_data": context_data,
        "trust_score": trust_score
    }
    
    # Make decision
    decision_result = await orchestrator.make_decision(
        context=decision_context,
        user_id=context_data["user_id"],
        resource_path="demo_resource"
    )
    
    print(f"  Decision: {decision_result['decision']}")
    print(f"  Confidence: {decision_result['confidence']}")
    print(f"  Agents Consulted: {', '.join(decision_result['agents_consulted'])}")
    print(f"  Reasoning: {decision_result['reasoning']}")
    print("  ✓ Agent consensus completed")
    
    return decision_result


async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="ReliQuary Demo Access Script")
    parser.add_argument("--user-id", default="demo_user", help="User ID for demo")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting ReliQuary Demo Access Flow")
        print(f"User ID: {args.user_id}")
        print(f"Time: {datetime.now().isoformat()}")
        
        # Step 1: Authentication
        token = await demo_authentication_flow()
        
        # Step 2: Generate context
        print("\nStep 2: Context Generation")
        context_data = generate_demo_context(args.user_id)
        print(f"  Context generated for user: {context_data['user_id']}")
        if args.verbose:
            print(f"  Full context: {json.dumps(context_data, indent=2)}")
        
        # Step 3: Context verification
        verification_result = await demo_context_verification(context_data)
        
        # Step 4: Trust evaluation
        trust_result = await demo_trust_evaluation(context_data)
        
        # Step 5: Agent consensus
        decision_result = await demo_agent_consensus(context_data, trust_result["overall_trust_score"])
        
        # Summary
        print("\n=== Demo Summary ===")
        print(f"User: {args.user_id}")
        print(f"Access Decision: {decision_result['decision'].upper()}")
        print(f"Trust Score: {trust_result['overall_trust_score']}")
        print(f"Context Verified: {verification_result['verified']}")
        print(f"Confidence: {decision_result['confidence']:.2f}")
        print(f"Completion Time: {datetime.now().isoformat()}")
        
        if decision_result['decision'] == 'approved':
            print("\n🎉 Access GRANTED - Demo completed successfully!")
            return 0
        else:
            print("\n❌ Access DENIED - Demo completed with restrictions")
            return 1
            
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)