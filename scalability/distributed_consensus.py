"""
Distributed Consensus Optimization for Large-Scale Agent Networks

This module implements advanced consensus algorithms optimized for networks
with 100+ agents, including hierarchical clustering, partition tolerance,
and dynamic leader election.
"""

import asyncio
import time
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import random
import weakref

# Import ReliQuary components
try:
    from agents.consensus import DistributedConsensusManager, ConsensusEvent
    from agents.orchestrator import DecisionOrchestrator
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logging.warning("Agent modules not available - using simulation mode")


class ClusterRole(Enum):
    """Roles within agent clusters"""
    CLUSTER_LEADER = "cluster_leader"
    CLUSTER_MEMBER = "cluster_member"
    INTER_CLUSTER_COORDINATOR = "inter_cluster_coordinator"
    BACKUP_LEADER = "backup_leader"


class ConsensusPhase(Enum):
    """Phases of hierarchical consensus"""
    INTRA_CLUSTER = "intra_cluster"
    INTER_CLUSTER = "inter_cluster"
    GLOBAL_CONSENSUS = "global_consensus"
    FINALIZATION = "finalization"


class PartitionStatus(Enum):
    """Network partition status"""
    CONNECTED = "connected"
    PARTITIONED = "partitioned"
    HEALING = "healing"
    ISOLATED = "isolated"


@dataclass
class AgentCluster:
    """Agent cluster information"""
    cluster_id: str
    leader_id: str
    backup_leader_id: Optional[str]
    member_agents: Set[str]
    cluster_size: int
    last_heartbeat: datetime
    cluster_health: float
    consensus_history: List[Dict[str, Any]]
    partition_status: PartitionStatus


@dataclass
class ConsensusRequest:
    """Large-scale consensus request"""
    request_id: str
    request_type: str
    payload: Dict[str, Any]
    priority: int
    timeout_seconds: float
    required_clusters: Optional[Set[str]]
    minimum_consensus: float
    created_at: datetime


@dataclass
class HierarchicalConsensusResult:
    """Result of hierarchical consensus"""
    request_id: str
    consensus_reached: bool
    final_decision: str
    participating_clusters: Dict[str, str]
    cluster_decisions: Dict[str, Dict[str, Any]]
    global_consensus_confidence: float
    consensus_phases: Dict[ConsensusPhase, Dict[str, Any]]
    processing_time: float
    partition_handling: Dict[str, Any]
    timestamp: datetime


class ScalableConsensusManager:
    """Advanced consensus manager for large-scale agent networks"""
    
    def __init__(self, manager_id: str = "scalable_consensus_v1", max_agents: int = 150):
        self.manager_id = manager_id
        self.max_agents = max_agents
        self.logger = logging.getLogger(f"scalable_consensus.{manager_id}")
        
        # Clustering configuration
        self.optimal_cluster_size = 12  # Optimal size for Byzantine consensus
        self.max_cluster_size = 20
        self.min_cluster_size = 7
        
        # Agent and cluster tracking
        self.agents = {}
        self.clusters = {}
        self.cluster_assignments = {}
        self.coordinator_agents = set()
        
        # Consensus tracking
        self.active_consensus = {}
        self.consensus_history = deque(maxlen=1000)
        
        # Performance metrics
        self.total_consensus_requests = 0
        self.successful_consensus = 0
        self.failed_consensus = 0
        self.average_consensus_time = 0.0
        
        # Partition tolerance
        self.partition_detector = NetworkPartitionDetector()
        self.partition_recovery = PartitionRecoveryManager()
        
        # Leader election
        self.leader_election = DynamicLeaderElection()
        
        self.logger.info(f"Scalable Consensus Manager initialized for up to {max_agents} agents")
    
    async def initialize_clustering(self, agent_list: List[str]) -> Dict[str, Any]:
        """Initialize hierarchical clustering for agents"""
        try:
            if len(agent_list) > self.max_agents:
                raise ValueError(f"Agent count {len(agent_list)} exceeds maximum {self.max_agents}")
            
            # Clear existing clusters
            self.clusters.clear()
            self.cluster_assignments.clear()
            
            # Create clusters using optimal algorithms
            cluster_assignments = self._create_optimal_clusters(agent_list)
            
            # Initialize each cluster
            for cluster_id, agent_ids in cluster_assignments.items():
                await self._initialize_cluster(cluster_id, agent_ids)
            
            # Select inter-cluster coordinators
            self._select_coordinators()
            
            # Validate clustering
            validation_result = self._validate_clustering()
            
            self.logger.info(f"Clustering initialized: {len(self.clusters)} clusters for {len(agent_list)} agents")
            
            return {
                "total_agents": len(agent_list),
                "total_clusters": len(self.clusters),
                "cluster_assignments": {cid: list(cluster.member_agents) for cid, cluster in self.clusters.items()},
                "coordinators": list(self.coordinator_agents),
                "validation": validation_result,
                "initialization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Clustering initialization failed: {e}")
            raise
    
    def _create_optimal_clusters(self, agent_list: List[str]) -> Dict[str, List[str]]:
        """Create optimal clusters for consensus"""
        clusters = {}
        remaining_agents = agent_list.copy()
        cluster_counter = 0
        
        while remaining_agents:
            cluster_size = min(self.optimal_cluster_size, len(remaining_agents))
            
            # Adjust cluster size to avoid very small clusters
            if len(remaining_agents) - cluster_size < self.min_cluster_size and len(remaining_agents) > cluster_size:
                cluster_size = len(remaining_agents) // 2
            
            cluster_id = f"cluster_{cluster_counter:03d}"
            cluster_agents = remaining_agents[:cluster_size]
            clusters[cluster_id] = cluster_agents
            
            remaining_agents = remaining_agents[cluster_size:]
            cluster_counter += 1
        
        return clusters
    
    async def _initialize_cluster(self, cluster_id: str, agent_ids: List[str]):
        """Initialize a single cluster"""
        # Select cluster leader using leader election
        leader_id = await self.leader_election.elect_leader(agent_ids, cluster_id)
        backup_leader_id = self._select_backup_leader(agent_ids, leader_id)
        
        cluster = AgentCluster(
            cluster_id=cluster_id,
            leader_id=leader_id,
            backup_leader_id=backup_leader_id,
            member_agents=set(agent_ids),
            cluster_size=len(agent_ids),
            last_heartbeat=datetime.now(),
            cluster_health=1.0,
            consensus_history=[],
            partition_status=PartitionStatus.CONNECTED
        )
        
        self.clusters[cluster_id] = cluster
        
        # Update cluster assignments
        for agent_id in agent_ids:
            self.cluster_assignments[agent_id] = cluster_id
        
        self.logger.info(f"Initialized cluster {cluster_id} with {len(agent_ids)} agents, leader: {leader_id}")
    
    def _select_backup_leader(self, agent_ids: List[str], current_leader: str) -> Optional[str]:
        """Select backup leader for cluster"""
        candidates = [aid for aid in agent_ids if aid != current_leader]
        return candidates[0] if candidates else None
    
    def _select_coordinators(self):
        """Select inter-cluster coordinators"""
        self.coordinator_agents.clear()
        
        # Select one coordinator per cluster (typically the leader)
        for cluster in self.clusters.values():
            self.coordinator_agents.add(cluster.leader_id)
        
        # Add additional coordinators for redundancy if needed
        if len(self.clusters) > 5:
            for cluster in list(self.clusters.values())[:3]:
                if cluster.backup_leader_id:
                    self.coordinator_agents.add(cluster.backup_leader_id)
    
    def _validate_clustering(self) -> Dict[str, Any]:
        """Validate clustering configuration"""
        total_agents = sum(len(cluster.member_agents) for cluster in self.clusters.values())
        
        validation = {
            "total_agents_clustered": total_agents,
            "cluster_count": len(self.clusters),
            "average_cluster_size": total_agents / len(self.clusters) if self.clusters else 0,
            "all_agents_assigned": total_agents == len(self.cluster_assignments),
            "coordinator_count": len(self.coordinator_agents),
            "clusters_in_range": all(
                self.min_cluster_size <= cluster.cluster_size <= self.max_cluster_size
                for cluster in self.clusters.values()
            ),
            "valid": True
        }
        
        # Validate cluster size distribution
        cluster_sizes = [cluster.cluster_size for cluster in self.clusters.values()]
        validation["min_cluster_size"] = min(cluster_sizes) if cluster_sizes else 0
        validation["max_cluster_size"] = max(cluster_sizes) if cluster_sizes else 0
        
        # Overall validation
        validation["valid"] = (
            validation["all_agents_assigned"] and
            validation["clusters_in_range"] and
            validation["coordinator_count"] > 0
        )
        
        return validation
    
    async def execute_hierarchical_consensus(self, request: ConsensusRequest) -> HierarchicalConsensusResult:
        """Execute hierarchical consensus across all clusters"""
        start_time = time.time()
        self.total_consensus_requests += 1
        
        try:
            request_id = request.request_id
            self.active_consensus[request_id] = {
                "request": request,
                "start_time": start_time,
                "phase": ConsensusPhase.INTRA_CLUSTER
            }
            
            # Phase 1: Intra-cluster consensus
            intra_cluster_results = await self._execute_intra_cluster_consensus(request)
            
            # Phase 2: Inter-cluster coordination
            inter_cluster_results = await self._execute_inter_cluster_consensus(
                request, intra_cluster_results
            )
            
            # Phase 3: Global consensus
            global_consensus_result = await self._execute_global_consensus(
                request, inter_cluster_results
            )
            
            # Phase 4: Finalization
            finalization_result = await self._finalize_consensus(
                request, global_consensus_result
            )
            
            processing_time = time.time() - start_time
            
            # Handle network partitions if detected
            partition_handling = await self.partition_detector.check_and_handle_partitions(
                self.clusters, global_consensus_result
            )
            
            result = HierarchicalConsensusResult(
                request_id=request_id,
                consensus_reached=finalization_result["consensus_reached"],
                final_decision=finalization_result["final_decision"],
                participating_clusters=finalization_result["participating_clusters"],
                cluster_decisions=intra_cluster_results,
                global_consensus_confidence=global_consensus_result["confidence"],
                consensus_phases={
                    ConsensusPhase.INTRA_CLUSTER: intra_cluster_results,
                    ConsensusPhase.INTER_CLUSTER: inter_cluster_results,
                    ConsensusPhase.GLOBAL_CONSENSUS: global_consensus_result,
                    ConsensusPhase.FINALIZATION: finalization_result
                },
                processing_time=processing_time,
                partition_handling=partition_handling,
                timestamp=datetime.now()
            )
            
            # Update metrics
            if result.consensus_reached:
                self.successful_consensus += 1
            else:
                self.failed_consensus += 1
            
            self._update_consensus_metrics(processing_time)
            
            # Clean up
            if request_id in self.active_consensus:
                del self.active_consensus[request_id]
            
            # Store in history
            self.consensus_history.append({
                "request_id": request_id,
                "success": result.consensus_reached,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.failed_consensus += 1
            self._update_consensus_metrics(processing_time)
            
            self.logger.error(f"Hierarchical consensus failed: {e}")
            
            return HierarchicalConsensusResult(
                request_id=request.request_id,
                consensus_reached=False,
                final_decision="CONSENSUS_FAILED",
                participating_clusters={},
                cluster_decisions={},
                global_consensus_confidence=0.0,
                consensus_phases={},
                processing_time=processing_time,
                partition_handling={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def _execute_intra_cluster_consensus(self, request: ConsensusRequest) -> Dict[str, Dict[str, Any]]:
        """Execute consensus within each cluster"""
        cluster_results = {}
        
        # Execute consensus in parallel across clusters
        tasks = []
        for cluster_id, cluster in self.clusters.items():
            # Skip if cluster is specified and this isn't one of them
            if request.required_clusters and cluster_id not in request.required_clusters:
                continue
            
            task = self._cluster_consensus(cluster_id, cluster, request)
            tasks.append(task)
        
        # Wait for all cluster consensus to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            cluster_id = list(self.clusters.keys())[i]
            if isinstance(result, Exception):
                self.logger.error(f"Cluster {cluster_id} consensus failed: {result}")
                cluster_results[cluster_id] = {
                    "success": False,
                    "decision": "ERROR",
                    "confidence": 0.0,
                    "error": str(result)
                }
            else:
                cluster_results[cluster_id] = result
        
        return cluster_results
    
    async def _cluster_consensus(self, cluster_id: str, cluster: AgentCluster, 
                               request: ConsensusRequest) -> Dict[str, Any]:
        """Execute consensus within a single cluster"""
        try:
            # Simulate cluster consensus (in real implementation, would use actual consensus)
            if AGENTS_AVAILABLE:
                # Would integrate with actual consensus manager
                consensus_manager = DistributedConsensusManager(
                    agent_id=cluster.leader_id,
                    agent_network=list(cluster.member_agents)
                )
                # Execute consensus...
                pass
            
            # Simulation mode - simple majority voting
            participating_agents = list(cluster.member_agents)
            votes = {}
            
            for agent_id in participating_agents:
                # Simulate agent vote based on request
                vote = self._simulate_agent_vote(agent_id, request)
                votes[agent_id] = vote
            
            # Count votes
            vote_counts = defaultdict(int)
            for vote in votes.values():
                vote_counts[vote] += 1
            
            # Determine majority decision
            if vote_counts:
                majority_decision = max(vote_counts.items(), key=lambda x: x[1])
                decision = majority_decision[0]
                confidence = majority_decision[1] / len(votes)
            else:
                decision = "NO_CONSENSUS"
                confidence = 0.0
            
            return {
                "cluster_id": cluster_id,
                "success": True,
                "decision": decision,
                "confidence": confidence,
                "participating_agents": participating_agents,
                "vote_distribution": dict(vote_counts),
                "leader": cluster.leader_id,
                "processing_time": random.uniform(0.1, 0.5)  # Simulate processing time
            }
            
        except Exception as e:
            return {
                "cluster_id": cluster_id,
                "success": False,
                "decision": "ERROR",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _simulate_agent_vote(self, agent_id: str, request: ConsensusRequest) -> str:
        """Simulate an agent's vote (for simulation mode)"""
        # Simple simulation based on agent type and request
        if "strict" in agent_id.lower():
            return "DENY" if request.priority < 8 else "ALLOW"
        elif "permissive" in agent_id.lower():
            return "ALLOW" if request.priority > 2 else "DENY"
        elif "watchdog" in agent_id.lower():
            return "ALLOW_WITH_MONITORING"
        else:  # neutral agent
            return "ALLOW" if request.priority > 5 else "DENY"
    
    async def _execute_inter_cluster_consensus(self, request: ConsensusRequest, 
                                             cluster_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Execute consensus between cluster coordinators"""
        try:
            # Get decisions from each cluster
            cluster_decisions = {}
            for cluster_id, result in cluster_results.items():
                if result["success"]:
                    cluster_decisions[cluster_id] = {
                        "decision": result["decision"],
                        "confidence": result["confidence"],
                        "weight": len(self.clusters[cluster_id].member_agents)
                    }
            
            # Weighted voting among clusters
            decision_weights = defaultdict(float)
            total_weight = 0
            
            for cluster_id, cluster_data in cluster_decisions.items():
                decision = cluster_data["decision"]
                confidence = cluster_data["confidence"]
                weight = cluster_data["weight"]
                
                weighted_confidence = confidence * weight
                decision_weights[decision] += weighted_confidence
                total_weight += weight
            
            # Determine inter-cluster consensus
            if decision_weights and total_weight > 0:
                final_decision = max(decision_weights.items(), key=lambda x: x[1])
                consensus_decision = final_decision[0]
                consensus_confidence = final_decision[1] / total_weight
            else:
                consensus_decision = "NO_INTER_CLUSTER_CONSENSUS"
                consensus_confidence = 0.0
            
            return {
                "success": True,
                "consensus_decision": consensus_decision,
                "consensus_confidence": consensus_confidence,
                "participating_clusters": list(cluster_decisions.keys()),
                "cluster_decisions": cluster_decisions,
                "decision_weights": dict(decision_weights),
                "total_weight": total_weight
            }
            
        except Exception as e:
            self.logger.error(f"Inter-cluster consensus failed: {e}")
            return {
                "success": False,
                "consensus_decision": "ERROR",
                "consensus_confidence": 0.0,
                "error": str(e)
            }
    
    async def _execute_global_consensus(self, request: ConsensusRequest, 
                                      inter_cluster_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute global consensus across the entire network"""
        try:
            if not inter_cluster_result["success"]:
                return {
                    "success": False,
                    "global_decision": "INTER_CLUSTER_FAILED",
                    "confidence": 0.0
                }
            
            # Check if minimum consensus threshold is met
            confidence = inter_cluster_result["consensus_confidence"]
            
            if confidence >= request.minimum_consensus:
                global_decision = inter_cluster_result["consensus_decision"]
                success = True
            else:
                global_decision = "INSUFFICIENT_CONSENSUS"
                success = False
            
            return {
                "success": success,
                "global_decision": global_decision,
                "confidence": confidence,
                "minimum_required": request.minimum_consensus,
                "participating_clusters": inter_cluster_result["participating_clusters"],
                "consensus_achieved": success
            }
            
        except Exception as e:
            self.logger.error(f"Global consensus failed: {e}")
            return {
                "success": False,
                "global_decision": "GLOBAL_CONSENSUS_ERROR",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _finalize_consensus(self, request: ConsensusRequest, 
                                global_result: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize consensus and prepare result"""
        try:
            consensus_reached = global_result["success"]
            final_decision = global_result["global_decision"]
            
            # Determine participating clusters
            participating_clusters = {}
            for cluster_id, cluster in self.clusters.items():
                participating_clusters[cluster_id] = cluster.leader_id
            
            # Update cluster health based on participation
            for cluster_id in global_result.get("participating_clusters", []):
                if cluster_id in self.clusters:
                    self.clusters[cluster_id].last_heartbeat = datetime.now()
                    # Update health score based on successful participation
                    current_health = self.clusters[cluster_id].cluster_health
                    self.clusters[cluster_id].cluster_health = min(1.0, current_health + 0.1)
            
            return {
                "consensus_reached": consensus_reached,
                "final_decision": final_decision,
                "participating_clusters": participating_clusters,
                "global_confidence": global_result["confidence"],
                "finalization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Consensus finalization failed: {e}")
            return {
                "consensus_reached": False,
                "final_decision": "FINALIZATION_ERROR",
                "participating_clusters": {},
                "global_confidence": 0.0,
                "error": str(e)
            }
    
    def _update_consensus_metrics(self, processing_time: float):
        """Update consensus performance metrics"""
        total_time = self.average_consensus_time * (self.total_consensus_requests - 1) + processing_time
        self.average_consensus_time = total_time / self.total_consensus_requests
    
    async def handle_agent_failure(self, failed_agent_id: str):
        """Handle agent failure and maintain consensus capability"""
        if failed_agent_id not in self.cluster_assignments:
            return
        
        cluster_id = self.cluster_assignments[failed_agent_id]
        cluster = self.clusters[cluster_id]
        
        # Remove failed agent from cluster
        cluster.member_agents.discard(failed_agent_id)
        cluster.cluster_size -= 1
        del self.cluster_assignments[failed_agent_id]
        
        # Handle leader failure
        if cluster.leader_id == failed_agent_id:
            if cluster.backup_leader_id and cluster.backup_leader_id in cluster.member_agents:
                # Promote backup leader
                cluster.leader_id = cluster.backup_leader_id
                cluster.backup_leader_id = self._select_backup_leader(
                    list(cluster.member_agents), cluster.leader_id
                )
            else:
                # Elect new leader
                if cluster.member_agents:
                    cluster.leader_id = await self.leader_election.elect_leader(
                        list(cluster.member_agents), cluster_id
                    )
                    cluster.backup_leader_id = self._select_backup_leader(
                        list(cluster.member_agents), cluster.leader_id
                    )
        
        # Update coordinator set
        self._select_coordinators()
        
        # Check if cluster needs rebalancing
        if cluster.cluster_size < self.min_cluster_size:
            await self._rebalance_clusters()
        
        self.logger.info(f"Handled failure of agent {failed_agent_id} in cluster {cluster_id}")
    
    async def _rebalance_clusters(self):
        """Rebalance clusters when they become too small or large"""
        # This would implement cluster rebalancing logic
        self.logger.info("Cluster rebalancing initiated")
        pass
    
    def get_consensus_metrics(self) -> Dict[str, Any]:
        """Get comprehensive consensus metrics"""
        return {
            "manager_id": self.manager_id,
            "max_agents": self.max_agents,
            "current_agents": len(self.cluster_assignments),
            "total_clusters": len(self.clusters),
            "cluster_info": {
                cid: {
                    "size": cluster.cluster_size,
                    "leader": cluster.leader_id,
                    "health": cluster.cluster_health,
                    "last_heartbeat": cluster.last_heartbeat.isoformat()
                }
                for cid, cluster in self.clusters.items()
            },
            "performance_metrics": {
                "total_consensus_requests": self.total_consensus_requests,
                "successful_consensus": self.successful_consensus,
                "failed_consensus": self.failed_consensus,
                "success_rate": self.successful_consensus / max(self.total_consensus_requests, 1) * 100,
                "average_consensus_time": self.average_consensus_time
            },
            "coordinator_agents": list(self.coordinator_agents),
            "active_consensus_count": len(self.active_consensus)
        }


class NetworkPartitionDetector:
    """Detects and handles network partitions"""
    
    def __init__(self):
        self.partition_history = deque(maxlen=100)
        self.logger = logging.getLogger("partition_detector")
    
    async def check_and_handle_partitions(self, clusters: Dict[str, AgentCluster], 
                                        consensus_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check for network partitions and handle them"""
        try:
            # Simple partition detection based on cluster participation
            total_clusters = len(clusters)
            participating_clusters = len(consensus_result.get("participating_clusters", []))
            
            partition_ratio = participating_clusters / total_clusters if total_clusters > 0 else 0
            
            if partition_ratio < 0.6:  # Less than 60% participation
                partition_status = PartitionStatus.PARTITIONED
                handling_strategy = "WAIT_FOR_HEALING"
            elif partition_ratio < 0.8:  # Less than 80% participation
                partition_status = PartitionStatus.HEALING
                handling_strategy = "CONTINUE_WITH_MAJORITY"
            else:
                partition_status = PartitionStatus.CONNECTED
                handling_strategy = "NORMAL_OPERATION"
            
            partition_info = {
                "status": partition_status.value,
                "participation_ratio": partition_ratio,
                "participating_clusters": participating_clusters,
                "total_clusters": total_clusters,
                "handling_strategy": handling_strategy,
                "timestamp": datetime.now().isoformat()
            }
            
            self.partition_history.append(partition_info)
            
            return partition_info
            
        except Exception as e:
            self.logger.error(f"Partition detection failed: {e}")
            return {"error": str(e)}


class PartitionRecoveryManager:
    """Manages partition recovery procedures"""
    
    def __init__(self):
        self.recovery_procedures = {}
        self.logger = logging.getLogger("partition_recovery")
    
    async def initiate_recovery(self, partition_info: Dict[str, Any]):
        """Initiate partition recovery procedures"""
        # This would implement partition recovery logic
        self.logger.info(f"Initiating partition recovery: {partition_info}")


class DynamicLeaderElection:
    """Dynamic leader election for clusters"""
    
    def __init__(self):
        self.election_history = {}
        self.logger = logging.getLogger("leader_election")
    
    async def elect_leader(self, agent_ids: List[str], cluster_id: str) -> str:
        """Elect a leader from available agents"""
        if not agent_ids:
            raise ValueError("No agents available for leader election")
        
        # Simple leader election - select based on lexicographic order
        # In production, would use more sophisticated algorithms
        leader = sorted(agent_ids)[0]
        
        self.election_history[cluster_id] = {
            "leader": leader,
            "candidates": agent_ids,
            "election_time": datetime.now().isoformat()
        }
        
        self.logger.info(f"Elected leader {leader} for cluster {cluster_id}")
        return leader