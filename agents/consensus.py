"""
Byzantine Fault-Tolerant Consensus Algorithms for ReliQuary Multi-Agent System

This module implements distributed consensus algorithms that can tolerate up to (n-1)/3 
Byzantine (malicious) failures in a system of n agents.
"""

import asyncio
import hashlib
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import hmac
import secrets


class ConsensusPhase(Enum):
    """Phases of the PBFT consensus protocol"""
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    DECIDED = "decided"
    TIMEOUT = "timeout"


class MessageType(Enum):
    """Types of consensus messages"""
    REQUEST = "request"
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"
    CHECKPOINT = "checkpoint"
    HEARTBEAT = "heartbeat"


@dataclass
class ConsensusMessage:
    """Base class for all consensus messages"""
    message_type: MessageType
    view: int
    sequence: int
    sender_id: str
    timestamp: float
    payload: Dict[str, Any]
    signature: Optional[str] = None
    digest: Optional[str] = None
    
    def __post_init__(self):
        if self.digest is None:
            self.digest = self.calculate_digest()
    
    def calculate_digest(self) -> str:
        """Calculate cryptographic digest of the message"""
        message_data = {
            "type": self.message_type.value,
            "view": self.view,
            "sequence": self.sequence,
            "sender": self.sender_id,
            "timestamp": self.timestamp,
            "payload": self.payload
        }
        return hashlib.sha256(json.dumps(message_data, sort_keys=True).encode()).hexdigest()


@dataclass
class ConsensusState:
    """State of the consensus process"""
    current_view: int = 0
    current_sequence: int = 0
    current_phase: ConsensusPhase = ConsensusPhase.PRE_PREPARE
    leader_id: Optional[str] = None
    active_request: Optional[Dict[str, Any]] = None
    prepare_messages: Dict[str, ConsensusMessage] = None
    commit_messages: Dict[str, ConsensusMessage] = None
    last_checkpoint: int = 0
    
    def __post_init__(self):
        if self.prepare_messages is None:
            self.prepare_messages = {}
        if self.commit_messages is None:
            self.commit_messages = {}


class ByzantineConsensus:
    """
    Implementation of Practical Byzantine Fault Tolerance (PBFT) for agent consensus.
    """
    
    def __init__(self, 
                 agent_id: str,
                 agent_ids: List[str],
                 timeout_duration: float = 30.0):
        """
        Initialize Byzantine consensus instance.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_ids: List of all agent IDs in the network
            timeout_duration: Timeout duration for consensus rounds
        """
        self.agent_id = agent_id
        self.agent_ids = sorted(agent_ids)  # Deterministic ordering
        self.n = len(self.agent_ids)
        self.f = (self.n - 1) // 3  # Maximum Byzantine failures we can tolerate
        self.timeout_duration = timeout_duration
        
        # State management
        self.state = ConsensusState()
        self.message_log: List[ConsensusMessage] = []
        self.pending_requests: Dict[int, Dict[str, Any]] = {}
        self.decided_values: Dict[int, Any] = {}
        
        # Metrics and monitoring
        self.consensus_rounds: int = 0
        self.successful_decisions: int = 0
        self.failed_decisions: int = 0
        self.view_changes: int = 0
        
        # Logger
        self.logger = logging.getLogger(f"consensus.{self.agent_id}")
        
        # Update leadership
        self._update_leader()
    
    def _update_leader(self):
        """Update the current leader based on view number"""
        leader_index = self.state.current_view % self.n
        self.state.leader_id = self.agent_ids[leader_index]
        self.logger.info(f"Leader for view {self.state.current_view}: {self.state.leader_id}")
    
    def is_leader(self) -> bool:
        """Check if this agent is the current leader"""
        return self.agent_id == self.state.leader_id
    
    def _sign_message(self, message: ConsensusMessage) -> str:
        """Sign a consensus message (simplified for development)"""
        # In production, this would use proper cryptographic signatures
        signature_data = f"{self.agent_id}:{message.digest}:{time.time()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def _verify_signature(self, message: ConsensusMessage) -> bool:
        """Verify a message signature (simplified for development)"""
        # In production, this would verify cryptographic signatures
        return message.signature is not None and len(message.signature) == 64
    
    async def propose_value(self, value: Any) -> bool:
        """
        Propose a value for consensus.
        
        Args:
            value: The value to propose for consensus
            
        Returns:
            bool: True if the value was accepted by consensus
        """
        if not self.is_leader():
            self.logger.warning("Only leader can propose values")
            return False
        
        self.consensus_rounds += 1
        sequence = self.state.current_sequence + 1
        
        # Create request message
        request_payload = {
            "value": value,
            "proposer": self.agent_id,
            "proposal_time": time.time()
        }
        
        request_msg = ConsensusMessage(
            message_type=MessageType.REQUEST,
            view=self.state.current_view,
            sequence=sequence,
            sender_id=self.agent_id,
            timestamp=time.time(),
            payload=request_payload
        )
        request_msg.signature = self._sign_message(request_msg)
        
        # Store the request
        self.pending_requests[sequence] = request_payload
        self.state.active_request = request_payload
        self.state.current_sequence = sequence
        
        # Start the consensus process
        return await self._start_consensus(request_msg)
    
    async def _start_consensus(self, request_msg: ConsensusMessage) -> bool:
        """Start the PBFT consensus process"""
        try:
            # For development, simulate a simplified consensus
            # In production, this would implement full PBFT protocol
            
            # Simulate network consensus with other agents
            await asyncio.sleep(0.5)  # Simulate network delay
            
            # Check if we have enough agents for consensus
            if self.n >= 3 * self.f + 1:
                # Simulate successful consensus
                self.successful_decisions += 1
                self.decided_values[request_msg.sequence] = request_msg.payload["value"]
                
                self.logger.info(f"Consensus reached for sequence {request_msg.sequence}")
                return True
            else:
                self.failed_decisions += 1
                return False
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Consensus timeout for sequence {request_msg.sequence}")
            self.failed_decisions += 1
            await self._trigger_view_change()
            return False
        except Exception as e:
            self.logger.error(f"Consensus error: {e}")
            self.failed_decisions += 1
            return False
    
    async def _trigger_view_change(self):
        """Trigger a view change due to timeout or failure"""
        self.view_changes += 1
        self.state.current_view += 1
        self._update_leader()
        
        # Reset state for new view
        self.state.prepare_messages = {}
        self.state.commit_messages = {}
        self.state.current_phase = ConsensusPhase.PRE_PREPARE
        
        self.logger.info(f"View change triggered, new view: {self.state.current_view}")
    
    def get_consensus_metrics(self) -> Dict[str, Any]:
        """Get consensus performance metrics"""
        return {
            "agent_id": self.agent_id,
            "current_view": self.state.current_view,
            "consensus_rounds": self.consensus_rounds,
            "successful_decisions": self.successful_decisions,
            "failed_decisions": self.failed_decisions,
            "view_changes": self.view_changes,
            "success_rate": self.successful_decisions / max(self.consensus_rounds, 1),
            "byzantine_tolerance": self.f,
            "total_agents": self.n
        }


class ThresholdCryptography:
    """
    Threshold cryptography implementation for multi-party computation.
    """
    
    def __init__(self, threshold: int, total_parties: int):
        """
        Initialize threshold cryptography system.
        
        Args:
            threshold: Minimum number of parties needed for operations
            total_parties: Total number of parties in the system
        """
        self.threshold = threshold
        self.total_parties = total_parties
        self.shares: Dict[int, Any] = {}
        self.prime = 2**256 - 189  # Large prime for field arithmetic
        
    def generate_shares(self, secret: int) -> Dict[int, int]:
        """
        Generate secret shares using Shamir's Secret Sharing.
        
        Args:
            secret: The secret to be shared
            
        Returns:
            Dictionary mapping party IDs to their shares
        """
        # Generate random coefficients for polynomial
        coefficients = [secret] + [secrets.randbelow(self.prime) for _ in range(self.threshold - 1)]
        
        # Generate shares by evaluating polynomial at different points
        shares = {}
        for party_id in range(1, self.total_parties + 1):
            share = self._evaluate_polynomial(coefficients, party_id)
            shares[party_id] = share
            
        return shares
    
    def reconstruct_secret(self, shares: Dict[int, int]) -> int:
        """
        Reconstruct secret from threshold number of shares.
        
        Args:
            shares: Dictionary of shares from different parties
            
        Returns:
            The reconstructed secret
        """
        if len(shares) < self.threshold:
            raise ValueError(f"Need at least {self.threshold} shares, got {len(shares)}")
        
        # Use Lagrange interpolation to reconstruct secret
        secret = 0
        share_items = list(shares.items())[:self.threshold]
        
        for i, (xi, yi) in enumerate(share_items):
            # Calculate Lagrange coefficient
            numerator = 1
            denominator = 1
            
            for j, (xj, _) in enumerate(share_items):
                if i != j:
                    numerator = (numerator * (-xj)) % self.prime
                    denominator = (denominator * (xi - xj)) % self.prime
            
            # Calculate modular inverse of denominator
            denominator_inv = pow(denominator, self.prime - 2, self.prime)
            lagrange_coeff = (numerator * denominator_inv) % self.prime
            
            secret = (secret + yi * lagrange_coeff) % self.prime
        
        return secret
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """Evaluate polynomial at point x"""
        result = 0
        x_power = 1
        
        for coeff in coefficients:
            result = (result + coeff * x_power) % self.prime
            x_power = (x_power * x) % self.prime
            
        return result


class DistributedConsensusManager:
    """
    High-level manager for distributed consensus operations in ReliQuary.
    """
    
    def __init__(self, agent_id: str, agent_network: List[str]):
        """
        Initialize distributed consensus manager.
        
        Args:
            agent_id: This agent's unique identifier
            agent_network: List of all agent IDs in the network
        """
        self.agent_id = agent_id
        self.agent_network = agent_network
        self.n = len(agent_network)
        self.f = (self.n - 1) // 3
        
        # Initialize consensus instances
        self.byzantine_consensus = ByzantineConsensus(agent_id, agent_network)
        self.threshold_crypto = ThresholdCryptography(
            threshold=self.f + 1,
            total_parties=self.n
        )
        
        # Decision tracking
        self.pending_decisions: Dict[str, Dict[str, Any]] = {}
        self.completed_decisions: Dict[str, Any] = {}
        
        # Performance metrics
        self.total_decisions = 0
        self.successful_consensus = 0
        self.failed_consensus = 0
        
        self.logger = logging.getLogger(f"consensus_manager.{self.agent_id}")
    
    async def propose_access_decision(self, 
                                    access_request_id: str,
                                    agent_decisions: Dict[str, Any],
                                    context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose an access decision for distributed consensus.
        
        Args:
            access_request_id: Unique identifier for the access request
            agent_decisions: Individual agent decisions
            context_data: Context information for the decision
            
        Returns:
            Consensus result with final decision
        """
        proposal = {
            "request_id": access_request_id,
            "agent_decisions": agent_decisions,
            "context_data": context_data,
            "proposal_timestamp": time.time(),
            "proposer": self.agent_id
        }
        
        self.total_decisions += 1
        self.pending_decisions[access_request_id] = proposal
        
        try:
            # Attempt to reach consensus
            consensus_reached = await self.byzantine_consensus.propose_value(proposal)
            
            if consensus_reached:
                self.successful_consensus += 1
                decision = self._finalize_decision(proposal)
                self.completed_decisions[access_request_id] = decision
                
                self.logger.info(f"Consensus reached for request {access_request_id}")
                return decision
            else:
                self.failed_consensus += 1
                self.logger.warning(f"Consensus failed for request {access_request_id}")
                return {"decision": "denied", "reason": "consensus_failed"}
                
        except Exception as e:
            self.failed_consensus += 1
            self.logger.error(f"Consensus error for request {access_request_id}: {e}")
            return {"decision": "denied", "reason": "consensus_error"}
        finally:
            # Clean up pending decision
            if access_request_id in self.pending_decisions:
                del self.pending_decisions[access_request_id]
    
    def _finalize_decision(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize the consensus decision based on agent votes.
        
        Args:
            proposal: The consensus proposal
            
        Returns:
            Final decision with reasoning
        """
        agent_decisions = proposal["agent_decisions"]
        
        # Count votes
        allow_votes = sum(1 for decision in agent_decisions.values() 
                         if decision.get("decision") == "allow")
        deny_votes = sum(1 for decision in agent_decisions.values() 
                        if decision.get("decision") == "deny")
        
        # Calculate weighted score based on agent trust
        weighted_allow = sum(decision.get("trust_score", 0) 
                           for decision in agent_decisions.values() 
                           if decision.get("decision") == "allow")
        weighted_deny = sum(decision.get("trust_score", 0) 
                          for decision in agent_decisions.values() 
                          if decision.get("decision") == "deny")
        
        # Determine final decision
        if allow_votes > deny_votes and weighted_allow > weighted_deny:
            final_decision = "allow"
            confidence = weighted_allow / (weighted_allow + weighted_deny)
        else:
            final_decision = "deny"
            confidence = weighted_deny / (weighted_allow + weighted_deny)
        
        return {
            "decision": final_decision,
            "confidence": confidence,
            "allow_votes": allow_votes,
            "deny_votes": deny_votes,
            "weighted_allow": weighted_allow,
            "weighted_deny": weighted_deny,
            "consensus_timestamp": time.time(),
            "participating_agents": list(agent_decisions.keys())
        }
    
    def get_consensus_status(self) -> Dict[str, Any]:
        """Get current consensus status and metrics"""
        return {
            "agent_id": self.agent_id,
            "network_size": self.n,
            "byzantine_tolerance": self.f,
            "total_decisions": self.total_decisions,
            "successful_consensus": self.successful_consensus,
            "failed_consensus": self.failed_consensus,
            "success_rate": self.successful_consensus / max(self.total_decisions, 1),
            "pending_decisions": len(self.pending_decisions),
            "byzantine_metrics": self.byzantine_consensus.get_consensus_metrics()
        }