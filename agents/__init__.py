# agents/__init__.py

"""
Multi-Agent System Foundation for ReliQuary

This package provides the foundation for distributed agents that will enable:
- Distributed context verification
- Consensus-based trust scoring
- Collaborative security monitoring
- Decentralized access control
- Multi-agent coordination and communication

This is the foundation for Phase 4 of the ReliQuary project.
"""

from .agent_foundation import (
    BaseAgent,
    AgentCoordinator,
    AgentRole,
    AgentStatus,
    MessageType,
    AgentMessage,
    AgentCapabilities,
    AgentMetrics,
    create_validator_agent,
    create_consensus_agent,
    create_monitor_agent,
    create_coordinator_agent
)

__version__ = "1.0.0"
__author__ = "ReliQuary Team"

__all__ = [
    "BaseAgent",
    "AgentCoordinator", 
    "AgentRole",
    "AgentStatus",
    "MessageType",
    "AgentMessage",
    "AgentCapabilities",
    "AgentMetrics",
    "create_validator_agent",
    "create_consensus_agent",
    "create_monitor_agent",
    "create_coordinator_agent"
]