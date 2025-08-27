#!/usr/bin/env python3
# test_agents.py

"""
Test script for the Multi-Agent System Foundation.

This script tests the basic agent functionality including:
- Agent creation and initialization
- Inter-agent communication
- Agent coordination and discovery
- Health monitoring and metrics
- Message handling and routing
- Basic consensus participation
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from agents import (
    BaseAgent,
    AgentCoordinator,
    AgentRole,
    AgentStatus,
    MessageType,
    AgentMessage,
    AgentCapabilities,
    create_validator_agent,
    create_consensus_agent,
    create_monitor_agent,
    create_coordinator_agent
)

async def test_agent_creation():
    """Test creation of different agent types."""
    print("\n=== Testing Agent Creation ===")
    
    # Create different types of agents
    validator = create_validator_agent("validator_001")
    consensus = create_consensus_agent("consensus_001")
    monitor = create_monitor_agent("monitor_001")
    coordinator = create_coordinator_agent("coordinator_001")
    
    agents = [validator, consensus, monitor, coordinator]
    
    print(f"Created {len(agents)} agents:")
    for agent in agents:
        print(f"  ✓ {agent.agent_id}: {[r.value for r in agent.capabilities.roles]}")
        print(f"    Status: {agent.status.value}")
        print(f"    Max Tasks: {agent.capabilities.max_concurrent_tasks}")
        print(f"    Trust Scoring: {agent.capabilities.trust_scoring_enabled}")
        print(f"    Consensus: {agent.capabilities.consensus_participation}")
    
    return len(agents) == 4, agents

async def test_agent_coordinator():
    """Test agent coordinator functionality."""
    print("\n=== Testing Agent Coordinator ===")
    
    # Create coordinator
    coordinator = AgentCoordinator()
    
    # Create and register agents
    agents = [
        create_validator_agent("val_001"),
        create_validator_agent("val_002"),
        create_consensus_agent("con_001"),
        create_monitor_agent("mon_001")
    ]
    
    print(f"Registering {len(agents)} agents with coordinator...")
    for agent in agents:
        coordinator.register_agent(agent)
    
    # Test role-based queries
    validators = coordinator.get_agents_by_role(AgentRole.VALIDATOR)
    consensus_agents = coordinator.get_agents_by_role(AgentRole.CONSENSUS)
    monitors = coordinator.get_agents_by_role(AgentRole.MONITOR)
    
    print(f"✓ Validators: {len(validators)} ({[a.agent_id for a in validators]})")
    print(f"✓ Consensus: {len(consensus_agents)} ({[a.agent_id for a in consensus_agents]})")
    print(f"✓ Monitors: {len(monitors)} ({[a.agent_id for a in monitors]})")
    
    # Test system status
    system_status = coordinator.get_system_status()
    print(f"✓ System Status:")
    print(f"  Total Agents: {system_status['total_agents']}")
    print(f"  Average Load: {system_status['average_system_load']:.2f}")
    print(f"  System Health: {system_status['system_health']}")
    
    return (len(validators) == 2 and len(consensus_agents) == 1 and 
            len(monitors) == 1 and system_status['total_agents'] == 4), agents

async def test_agent_communication():
    """Test inter-agent communication."""
    print("\n=== Testing Agent Communication ===")
    
    # Create agents
    sender = create_validator_agent("sender_001")
    receiver = create_validator_agent("receiver_001")
    
    # Test message creation and signing
    test_message = AgentMessage(
        message_id="test_msg_001",
        sender_id=sender.agent_id,
        recipient_id=receiver.agent_id,
        message_type=MessageType.VERIFICATION_REQUEST,
        payload={
            "verification_request": {
                "user_id": "test_user",
                "device_fingerprint": "test_device"
            }
        },
        timestamp=int(time.time())
    )
    
    print(f"✓ Created message: {test_message.message_type.value}")
    print(f"  From: {test_message.sender_id}")
    print(f"  To: {test_message.recipient_id}")
    print(f"  ID: {test_message.message_id}")
    
    # Test message signing and verification
    signature = sender._sign_message(test_message)
    test_message.signature = signature
    
    is_valid = receiver._verify_message_signature(test_message)
    print(f"✓ Message signature valid: {is_valid}")
    
    # Test message handling
    verification_result = await receiver.handle_verification_request(test_message)
    print(f"✓ Verification result: {verification_result.get('verified', False)}")
    print(f"  Trust Score: {verification_result.get('trust_score', 0)}")
    print(f"  Processing Agent: {verification_result.get('agent_id')}")
    
    return is_valid and verification_result.get('verified', False), [sender, receiver]

async def test_health_monitoring():
    """Test agent health monitoring."""
    print("\n=== Testing Health Monitoring ===")
    
    # Create agents
    agents = [
        create_validator_agent("health_val_001"),
        create_monitor_agent("health_mon_001")
    ]
    
    # Test individual health checks
    for agent in agents:
        health_data = await agent.perform_health_check()
        print(f"✓ Agent {agent.agent_id} health:")
        print(f"  Status: {health_data['status']}")
        print(f"  Uptime: {health_data['uptime']}s")
        print(f"  Current Load: {health_data['current_load']:.2f}")
        print(f"  Total Tasks: {health_data['total_tasks']}")
        print(f"  Success Rate: {health_data['success_rate']:.2f}")
    
    # Test network status
    for agent in agents:
        # Simulate agent discovery
        for other_agent in agents:
            if other_agent.agent_id != agent.agent_id:
                agent.register_agent(other_agent.agent_id, {
                    "roles": [r.value for r in other_agent.capabilities.roles],
                    "status": other_agent.status.value
                })
        
        network_status = agent.get_network_status()
        print(f"✓ Agent {agent.agent_id} network view:")
        print(f"  Total Agents: {network_status['total_agents']}")
        print(f"  Known Agents: {network_status['known_agents']}")
        print(f"  Network Health: {network_status['network_health']}")
    
    return True, agents

async def test_consensus_basics():
    """Test basic consensus functionality."""
    print("\n=== Testing Basic Consensus ===")
    
    # Create consensus-capable agents
    proposer = create_coordinator_agent("proposer_001")
    voters = [
        create_validator_agent("voter_001"),
        create_validator_agent("voter_002"),
        create_consensus_agent("voter_003")
    ]
    
    all_agents = [proposer] + voters
    
    print(f"Created consensus network with {len(all_agents)} agents")
    print(f"  Proposer: {proposer.agent_id}")
    print(f"  Voters: {[v.agent_id for v in voters]}")
    
    # Create a consensus proposal
    proposal = {
        "proposal_id": "test_proposal_001",
        "proposal_type": "trust_threshold_update",
        "proposed_value": 85,
        "reasoning": "Increase trust threshold for enhanced security",
        "timestamp": int(time.time())
    }
    
    print(f"✓ Created proposal: {proposal['proposal_type']}")
    print(f"  Value: {proposal['proposed_value']}")
    print(f"  Reasoning: {proposal['reasoning']}")
    
    # Test proposal handling by voters
    votes = []
    for voter in voters:
        if voter.capabilities.consensus_participation:
            proposal_message = AgentMessage(
                message_id=f"proposal_{voter.agent_id}",
                sender_id=proposer.agent_id,
                recipient_id=voter.agent_id,
                message_type=MessageType.CONSENSUS_PROPOSAL,
                payload={"proposal": proposal},
                timestamp=int(time.time())
            )
            
            vote_result = await voter.handle_consensus_proposal(proposal_message)
            votes.append(vote_result)
            
            print(f"  ✓ {voter.agent_id}: {vote_result.get('vote', 'no_vote')}")
    
    # Analyze votes
    approve_count = sum(1 for vote in votes if vote.get('vote') == 'approve')
    total_votes = len(votes)
    
    print(f"✓ Consensus results:")
    print(f"  Total Votes: {total_votes}")
    print(f"  Approvals: {approve_count}")
    print(f"  Approval Rate: {approve_count/total_votes:.1%}")
    
    return approve_count > 0 and total_votes > 0, all_agents

async def test_system_integration():
    """Test integrated system functionality."""
    print("\n=== Testing System Integration ===")
    
    # Create a complete agent ecosystem
    coordinator = AgentCoordinator()
    
    agents = [
        create_coordinator_agent("sys_coordinator_001"),
        create_validator_agent("sys_validator_001"),
        create_validator_agent("sys_validator_002"), 
        create_consensus_agent("sys_consensus_001"),
        create_monitor_agent("sys_monitor_001")
    ]
    
    # Register all agents
    for agent in agents:
        coordinator.register_agent(agent)
    
    print(f"✓ Created integrated system with {len(agents)} agents")
    
    # Test system status
    system_status = coordinator.get_system_status()
    print(f"✓ System Overview:")
    print(f"  Total Agents: {system_status['total_agents']}")
    print(f"  Tasks Processed: {system_status['total_tasks_processed']}")
    print(f"  Average Load: {system_status['average_system_load']:.2f}")
    print(f"  Health: {system_status['system_health']}")
    
    # Test role distribution
    role_distribution = {}
    for agent in agents:
        for role in agent.capabilities.roles:
            role_distribution[role.value] = role_distribution.get(role.value, 0) + 1
    
    print(f"✓ Role Distribution:")
    for role, count in role_distribution.items():
        print(f"  {role}: {count} agents")
    
    # Test capability coverage
    capabilities = {
        "context_verification": sum(1 for a in agents if a.context_manager is not None),
        "trust_scoring": sum(1 for a in agents if a.trust_engine is not None),
        "consensus_participation": sum(1 for a in agents if a.capabilities.consensus_participation),
    }
    
    print(f"✓ Capability Coverage:")
    for capability, count in capabilities.items():
        print(f"  {capability}: {count} agents")
    
    return (len(agents) == 5 and system_status['total_agents'] == 5 and
            capabilities['context_verification'] > 0 and 
            capabilities['trust_scoring'] > 0), agents

async def main():
    """Run all agent foundation tests."""
    print("🚀 Starting Multi-Agent System Foundation Tests")
    print("=" * 60)
    
    try:
        # Test agent creation
        test1_passed, agents1 = await test_agent_creation()
        
        # Test agent coordinator
        test2_passed, agents2 = await test_agent_coordinator()
        
        # Test inter-agent communication
        test3_passed, agents3 = await test_agent_communication()
        
        # Test health monitoring
        test4_passed, agents4 = await test_health_monitoring()
        
        # Test consensus basics
        test5_passed, agents5 = await test_consensus_basics()
        
        # Test system integration
        test6_passed, agents6 = await test_system_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Multi-Agent System Test Summary:")
        print(f"✓ Agent Creation: {'PASS' if test1_passed else 'FAIL'}")
        print(f"✓ Agent Coordinator: {'PASS' if test2_passed else 'FAIL'}")
        print(f"✓ Inter-Agent Communication: {'PASS' if test3_passed else 'FAIL'}")
        print(f"✓ Health Monitoring: {'PASS' if test4_passed else 'FAIL'}")
        print(f"✓ Consensus Basics: {'PASS' if test5_passed else 'FAIL'}")
        print(f"✓ System Integration: {'PASS' if test6_passed else 'FAIL'}")
        
        all_passed = all([test1_passed, test2_passed, test3_passed, 
                         test4_passed, test5_passed, test6_passed])
        
        if all_passed:
            print("\n🎉 All Multi-Agent System Foundation Tests PASSED!")
            print("✅ Agent creation and initialization working correctly")
            print("✅ Inter-agent communication and coordination functional")
            print("✅ Health monitoring and metrics collection operational")
            print("✅ Basic consensus mechanisms in place")
            print("✅ System integration and scalability foundation ready")
            print("✅ Multi-agent system foundation prepared for Phase 4")
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