"""
Cross-Chain Consensus Coordinator for ReliQuary

This module coordinates consensus decisions across blockchain networks,
integrating the multi-agent system with cross-chain governance protocols
for decentralized decision-making and validation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Import ReliQuary components
from agents.orchestrator import DecisionOrchestrator, DecisionType, OrchestrationResult
from agents.consensus import DistributedConsensusManager
from agents.workflow import AgentWorkflowCoordinator
from crosschain.protocols import (
    CrossChainGovernance,
    BlockchainNetwork,
    ConsensusEvent,
    ChainConfig,
    create_default_chain_configs
)


class CrossChainDecisionType(Enum):
    """Types of cross-chain consensus decisions"""
    MULTI_CHAIN_ACCESS = "multi_chain_access"
    CROSS_CHAIN_TRANSFER = "cross_chain_transfer"
    GOVERNANCE_DECISION = "governance_decision"
    EMERGENCY_COORDINATION = "emergency_coordination"
    TRUST_SYNCHRONIZATION = "trust_synchronization"
    SYSTEM_COORDINATION = "system_coordination"


class ConsensusScope(Enum):
    """Scope of consensus operation"""
    LOCAL_AGENTS = "local_agents"
    SINGLE_CHAIN = "single_chain"
    MULTI_CHAIN = "multi_chain"
    GLOBAL_NETWORK = "global_network"


@dataclass
class CrossChainConsensusRequest:
    """Request for cross-chain consensus decision"""
    request_id: str
    decision_type: CrossChainDecisionType
    scope: ConsensusScope
    initiator: str
    target_chains: List[BlockchainNetwork]
    context_data: Dict[str, Any]
    priority: int
    timeout_seconds: float
    requires_governance: bool
    min_confirmations: int


@dataclass
class CrossChainConsensusResult:
    """Result of cross-chain consensus operation"""
    request_id: str
    final_decision: str
    consensus_scope: ConsensusScope
    participating_chains: List[BlockchainNetwork]
    agent_consensus: Dict[str, Any]
    blockchain_confirmations: Dict[str, int]
    governance_status: Optional[Dict[str, Any]]
    execution_time: float
    cross_chain_proofs: List[str]
    timestamp: datetime


class CrossChainConsensusCoordinator:
    """
    Coordinates consensus decisions across multiple blockchain networks
    and integrates with the ReliQuary multi-agent system.
    """
    
    def __init__(self, 
                 agent_orchestrator: DecisionOrchestrator,
                 workflow_coordinator: AgentWorkflowCoordinator,
                 chain_configs: List[ChainConfig] = None):
        """
        Initialize cross-chain consensus coordinator.
        
        Args:
            agent_orchestrator: ReliQuary decision orchestrator
            workflow_coordinator: Agent workflow coordinator
            chain_configs: Blockchain network configurations
        """
        self.agent_orchestrator = agent_orchestrator
        self.workflow_coordinator = workflow_coordinator
        
        # Initialize cross-chain governance
        self.chain_configs = chain_configs or create_default_chain_configs()
        self.governance = CrossChainGovernance(self.chain_configs)
        
        # Cross-chain state management
        self.active_requests: Dict[str, CrossChainConsensusRequest] = {}
        self.pending_confirmations: Dict[str, Dict[str, int]] = {}
        self.consensus_history: Dict[str, CrossChainConsensusResult] = {}
        
        # Performance metrics
        self.total_cross_chain_decisions = 0
        self.successful_cross_chain_decisions = 0
        self.failed_cross_chain_decisions = 0
        self.average_cross_chain_time = 0.0
        
        # Configuration
        self.min_chain_confirmations = 2
        self.max_consensus_timeout = 300.0  # 5 minutes
        self.governance_voting_period = 24  # hours
        
        self.logger = logging.getLogger("crosschain_coordinator")
        self.logger.info("Cross-chain consensus coordinator initialized")
    
    async def coordinate_cross_chain_consensus(self, 
                                             request: CrossChainConsensusRequest) -> CrossChainConsensusResult:
        """
        Coordinate consensus across multiple blockchain networks.
        
        Args:
            request: Cross-chain consensus request
            
        Returns:
            CrossChainConsensusResult with decision and proofs
        """
        start_time = time.time()
        self.total_cross_chain_decisions += 1
        
        try:
            # Store active request
            self.active_requests[request.request_id] = request
            
            self.logger.info(f"Starting cross-chain consensus for {request.request_id}")
            
            # Phase 1: Local agent consensus
            agent_result = await self._conduct_agent_consensus(request)
            
            # Phase 2: Blockchain validation
            blockchain_confirmations = await self._validate_on_blockchains(request, agent_result)
            
            # Phase 3: Governance coordination (if required)
            governance_result = None
            if request.requires_governance:
                governance_result = await self._coordinate_governance(request, agent_result)
            
            # Phase 4: Generate cross-chain proofs
            cross_chain_proofs = await self._generate_cross_chain_proofs(
                request, agent_result, blockchain_confirmations
            )
            
            # Phase 5: Finalize consensus
            final_result = await self._finalize_cross_chain_consensus(
                request, agent_result, blockchain_confirmations, 
                governance_result, cross_chain_proofs, start_time
            )
            
            self.successful_cross_chain_decisions += 1
            self.consensus_history[request.request_id] = final_result
            
            self.logger.info(f"Cross-chain consensus completed for {request.request_id}: {final_result.final_decision}")
            return final_result
            
        except Exception as e:
            self.failed_cross_chain_decisions += 1
            self.logger.error(f"Cross-chain consensus failed for {request.request_id}: {e}")
            
            # Create error result
            error_result = CrossChainConsensusResult(
                request_id=request.request_id,
                final_decision="denied",
                consensus_scope=request.scope,
                participating_chains=request.target_chains,
                agent_consensus={"error": str(e)},
                blockchain_confirmations={},
                governance_status=None,
                execution_time=time.time() - start_time,
                cross_chain_proofs=[],
                timestamp=datetime.now()
            )
            
            self.consensus_history[request.request_id] = error_result
            return error_result
            
        finally:
            # Cleanup
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
    
    async def _conduct_agent_consensus(self, request: CrossChainConsensusRequest) -> OrchestrationResult:
        """Conduct consensus using the multi-agent system"""
        try:
            # Map cross-chain decision type to agent decision type
            agent_decision_type = self._map_to_agent_decision_type(request.decision_type)
            
            # Enhance context with cross-chain information
            enhanced_context = request.context_data.copy()
            enhanced_context.update({
                "cross_chain_request": True,
                "target_chains": [chain.value for chain in request.target_chains],
                "consensus_scope": request.scope.value,
                "requires_governance": request.requires_governance
            })
            
            # Orchestrate agent decision
            result = await self.agent_orchestrator.orchestrate_decision(
                decision_type=agent_decision_type,
                requestor_id=request.initiator,
                context_data=enhanced_context,
                priority=request.priority,
                timeout_seconds=min(request.timeout_seconds, 120.0)  # Limit agent timeout
            )
            
            self.logger.info(f"Agent consensus for {request.request_id}: {result.final_decision}")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent consensus failed for {request.request_id}: {e}")
            raise
    
    def _map_to_agent_decision_type(self, cross_chain_type: CrossChainDecisionType) -> DecisionType:
        """Map cross-chain decision type to agent decision type"""
        mapping = {
            CrossChainDecisionType.MULTI_CHAIN_ACCESS: DecisionType.ACCESS_REQUEST,
            CrossChainDecisionType.CROSS_CHAIN_TRANSFER: DecisionType.ACCESS_REQUEST,
            CrossChainDecisionType.GOVERNANCE_DECISION: DecisionType.POLICY_UPDATE,
            CrossChainDecisionType.EMERGENCY_COORDINATION: DecisionType.EMERGENCY_OVERRIDE,
            CrossChainDecisionType.TRUST_SYNCHRONIZATION: DecisionType.TRUST_CALIBRATION,
            CrossChainDecisionType.SYSTEM_COORDINATION: DecisionType.SYSTEM_MAINTENANCE
        }
        return mapping.get(cross_chain_type, DecisionType.ACCESS_REQUEST)
    
    async def _validate_on_blockchains(self, 
                                     request: CrossChainConsensusRequest,
                                     agent_result: OrchestrationResult) -> Dict[str, int]:
        """Validate consensus decision on target blockchains"""
        confirmations = {}
        
        if request.scope in [ConsensusScope.LOCAL_AGENTS]:
            # No blockchain validation needed for local consensus
            return confirmations
        
        validation_tasks = []
        for chain in request.target_chains:
            if chain in [config.network for config in self.chain_configs if config.enabled]:
                task = self._validate_on_single_chain(request, agent_result, chain)
                validation_tasks.append(task)
        
        if validation_tasks:
            results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                chain = request.target_chains[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Blockchain validation failed for {chain.value}: {result}")
                    confirmations[chain.value] = 0
                else:
                    confirmations[chain.value] = result
        
        return confirmations
    
    async def _validate_on_single_chain(self, 
                                      request: CrossChainConsensusRequest,
                                      agent_result: OrchestrationResult,
                                      chain: BlockchainNetwork) -> int:
        """Validate decision on a single blockchain"""
        try:
            # Find appropriate bridge for this chain
            bridge = None
            for bridge_key, bridge_obj in self.governance.bridges.items():
                if bridge_key[1] == chain:
                    bridge = bridge_obj
                    break
            
            if not bridge:
                self.logger.warning(f"No bridge found for {chain.value}")
                return 0
            
            # Create validation transaction
            validation_data = {
                "request_id": request.request_id,
                "agent_decision": agent_result.final_decision,
                "consensus_confidence": agent_result.consensus_confidence,
                "participating_agents": agent_result.participating_agents,
                "timestamp": time.time()
            }
            
            # Submit validation transaction
            tx_id = await bridge.submit_transaction(
                self._create_validation_transaction(request, validation_data, chain)
            )
            
            # Wait for confirmations
            confirmations = await self._wait_for_confirmations(bridge, tx_id, chain)
            
            self.logger.info(f"Blockchain validation for {chain.value}: {confirmations} confirmations")
            return confirmations
            
        except Exception as e:
            self.logger.error(f"Validation failed for {chain.value}: {e}")
            return 0
    
    def _create_validation_transaction(self, 
                                     request: CrossChainConsensusRequest,
                                     validation_data: Dict[str, Any],
                                     chain: BlockchainNetwork):
        """Create validation transaction for blockchain"""
        from crosschain.protocols import CrossChainTransaction
        
        return CrossChainTransaction(
            tx_id=f"validation_{request.request_id}_{chain.value}",
            source_chain=BlockchainNetwork.LOCAL_TESTNET,
            target_chain=chain,
            event_type=ConsensusEvent.AGENT_DECISION,
            payload=validation_data,
            signatures=[],
            timestamp=time.time()
        )
    
    async def _wait_for_confirmations(self, 
                                    bridge,
                                    tx_id: str,
                                    chain: BlockchainNetwork,
                                    max_wait: int = 60) -> int:
        """Wait for blockchain confirmations"""
        confirmations = 0
        waited = 0
        
        while waited < max_wait:
            try:
                status = await bridge.get_transaction_status(tx_id)
                confirmations = status.get("confirmations", 0)
                
                if confirmations >= self.min_chain_confirmations:
                    break
                
                await asyncio.sleep(2)
                waited += 2
                
            except Exception as e:
                self.logger.error(f"Error checking confirmations for {tx_id}: {e}")
                break
        
        return confirmations
    
    async def _coordinate_governance(self, 
                                   request: CrossChainConsensusRequest,
                                   agent_result: OrchestrationResult) -> Dict[str, Any]:
        """Coordinate governance voting if required"""
        try:
            # Create governance proposal
            proposal_content = {
                "request_id": request.request_id,
                "decision_type": request.decision_type.value,
                "agent_decision": agent_result.final_decision,
                "context_summary": self._summarize_context(request.context_data),
                "consensus_confidence": agent_result.consensus_confidence
            }
            
            # Submit proposal to governance
            proposal_id = await self.governance.submit_proposal(
                proposer=request.initiator,
                proposal_type=ConsensusEvent.GOVERNANCE_DECISION,
                content=proposal_content,
                target_chain=request.target_chains[0] if request.target_chains else BlockchainNetwork.LOCAL_TESTNET,
                voting_period_hours=self.governance_voting_period
            )
            
            # For demonstration, simulate automatic approval for high-confidence decisions
            if agent_result.consensus_confidence > 0.8:
                await self.governance.vote_on_proposal(proposal_id, "system_auto", True, 1.0)
                await self.governance.vote_on_proposal(proposal_id, "admin_auto", True, 2.0)
                await self.governance.vote_on_proposal(proposal_id, "validator_auto", True, 1.5)
            
            # Get proposal status
            governance_status = self.governance.get_proposal_status(proposal_id)
            governance_status["proposal_id"] = proposal_id
            
            self.logger.info(f"Governance coordination for {request.request_id}: {governance_status['status']}")
            return governance_status
            
        except Exception as e:
            self.logger.error(f"Governance coordination failed for {request.request_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    def _summarize_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of context data for governance"""
        summary = {}
        
        # Include key context elements
        key_fields = ["user_id", "resource_id", "action", "risk_level", "trust_score"]
        for field in key_fields:
            if field in context_data:
                summary[field] = context_data[field]
        
        # Add metadata
        summary["context_size"] = len(context_data)
        summary["has_sensitive_data"] = any(
            key in context_data for key in ["password", "private_key", "secret"]
        )
        
        return summary
    
    async def _generate_cross_chain_proofs(self, 
                                         request: CrossChainConsensusRequest,
                                         agent_result: OrchestrationResult,
                                         blockchain_confirmations: Dict[str, int]) -> List[str]:
        """Generate cross-chain consensus proofs"""
        proofs = []
        
        try:
            # Agent consensus proof
            agent_proof = self._generate_agent_proof(request, agent_result)
            proofs.append(agent_proof)
            
            # Blockchain confirmation proofs
            for chain, confirmations in blockchain_confirmations.items():
                if confirmations > 0:
                    blockchain_proof = self._generate_blockchain_proof(request, chain, confirmations)
                    proofs.append(blockchain_proof)
            
            # Merkle proof of consensus history
            if len(proofs) > 1:
                merkle_proof = self._generate_merkle_proof(proofs)
                proofs.append(merkle_proof)
            
            self.logger.info(f"Generated {len(proofs)} cross-chain proofs for {request.request_id}")
            return proofs
            
        except Exception as e:
            self.logger.error(f"Proof generation failed for {request.request_id}: {e}")
            return []
    
    def _generate_agent_proof(self, 
                            request: CrossChainConsensusRequest,
                            agent_result: OrchestrationResult) -> str:
        """Generate proof of agent consensus"""
        import hashlib
        
        proof_data = {
            "type": "agent_consensus",
            "request_id": request.request_id,
            "decision": agent_result.final_decision,
            "confidence": agent_result.consensus_confidence,
            "agents": agent_result.participating_agents,
            "timestamp": agent_result.timestamp.isoformat()
        }
        
        proof_json = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return f"agent_proof:{proof_hash}"
    
    def _generate_blockchain_proof(self, 
                                 request: CrossChainConsensusRequest,
                                 chain: str,
                                 confirmations: int) -> str:
        """Generate proof of blockchain validation"""
        import hashlib
        
        proof_data = {
            "type": "blockchain_validation",
            "request_id": request.request_id,
            "chain": chain,
            "confirmations": confirmations,
            "timestamp": time.time()
        }
        
        proof_json = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return f"blockchain_proof:{chain}:{proof_hash}"
    
    def _generate_merkle_proof(self, proofs: List[str]) -> str:
        """Generate Merkle proof of all consensus proofs"""
        import hashlib
        
        # Create Merkle tree of proofs
        proof_hashes = [hashlib.sha256(proof.encode()).hexdigest() for proof in proofs]
        
        # Simple Merkle root calculation (in production, use proper Merkle tree)
        merkle_data = "".join(sorted(proof_hashes))
        merkle_root = hashlib.sha256(merkle_data.encode()).hexdigest()
        
        return f"merkle_proof:{merkle_root}"
    
    async def _finalize_cross_chain_consensus(self, 
                                            request: CrossChainConsensusRequest,
                                            agent_result: OrchestrationResult,
                                            blockchain_confirmations: Dict[str, int],
                                            governance_result: Optional[Dict[str, Any]],
                                            cross_chain_proofs: List[str],
                                            start_time: float) -> CrossChainConsensusResult:
        """Finalize cross-chain consensus decision"""
        
        # Determine final decision based on all factors
        final_decision = self._determine_final_decision(
            request, agent_result, blockchain_confirmations, governance_result
        )
        
        execution_time = time.time() - start_time
        
        result = CrossChainConsensusResult(
            request_id=request.request_id,
            final_decision=final_decision,
            consensus_scope=request.scope,
            participating_chains=request.target_chains,
            agent_consensus={
                "decision": agent_result.final_decision,
                "confidence": agent_result.consensus_confidence,
                "agents": agent_result.participating_agents
            },
            blockchain_confirmations=blockchain_confirmations,
            governance_status=governance_result,
            execution_time=execution_time,
            cross_chain_proofs=cross_chain_proofs,
            timestamp=datetime.now()
        )
        
        return result
    
    def _determine_final_decision(self, 
                                request: CrossChainConsensusRequest,
                                agent_result: OrchestrationResult,
                                blockchain_confirmations: Dict[str, int],
                                governance_result: Optional[Dict[str, Any]]) -> str:
        """Determine final consensus decision based on all factors"""
        
        # Start with agent decision
        decision = agent_result.final_decision
        
        # Check blockchain confirmations if required
        if request.scope in [ConsensusScope.SINGLE_CHAIN, ConsensusScope.MULTI_CHAIN]:
            sufficient_confirmations = sum(
                1 for confirmations in blockchain_confirmations.values() 
                if confirmations >= request.min_confirmations
            )
            
            if sufficient_confirmations < len(request.target_chains) / 2:
                decision = "denied"  # Insufficient blockchain validation
        
        # Check governance result if required
        if request.requires_governance and governance_result:
            if governance_result.get("status") not in ["passed", "active"]:
                decision = "denied"  # Governance rejection
        
        return decision
    
    def _update_metrics(self, execution_time: float):
        """Update performance metrics"""
        total_time = (self.average_cross_chain_time * (self.total_cross_chain_decisions - 1) + 
                     execution_time)
        self.average_cross_chain_time = total_time / self.total_cross_chain_decisions
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get cross-chain coordinator status"""
        return {
            "total_cross_chain_decisions": self.total_cross_chain_decisions,
            "successful_decisions": self.successful_cross_chain_decisions,
            "failed_decisions": self.failed_cross_chain_decisions,
            "success_rate": (self.successful_cross_chain_decisions / 
                           max(self.total_cross_chain_decisions, 1)),
            "average_execution_time": self.average_cross_chain_time,
            "active_requests": len(self.active_requests),
            "supported_chains": len([c for c in self.chain_configs if c.enabled]),
            "governance_metrics": self.governance.get_governance_metrics()
        }
    
    async def emergency_cross_chain_coordination(self, 
                                               emergency_type: str,
                                               affected_chains: List[BlockchainNetwork],
                                               coordination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate emergency response across chains"""
        emergency_request = CrossChainConsensusRequest(
            request_id=f"emergency_{int(time.time())}",
            decision_type=CrossChainDecisionType.EMERGENCY_COORDINATION,
            scope=ConsensusScope.MULTI_CHAIN,
            initiator="system_emergency",
            target_chains=affected_chains,
            context_data={
                "emergency_type": emergency_type,
                "coordination_data": coordination_data,
                "severity": "high"
            },
            priority=1,  # Highest priority
            timeout_seconds=60.0,  # Fast response
            requires_governance=False,  # Skip governance for emergencies
            min_confirmations=1
        )
        
        result = await self.coordinate_cross_chain_consensus(emergency_request)
        
        self.logger.warning(f"Emergency coordination completed: {result.final_decision}")
        return {
            "emergency_type": emergency_type,
            "coordination_result": result.final_decision,
            "affected_chains": [chain.value for chain in affected_chains],
            "response_time": result.execution_time,
            "proofs": result.cross_chain_proofs
        }