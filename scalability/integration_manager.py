"""
Scalability Integration Manager for ReliQuary Enterprise Scale

This module integrates all scalability components including performance monitoring,
distributed consensus, agent pool management, and provides unified scaling
coordination for enterprise deployments with 100+ agents.
"""

import asyncio
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from scalability.performance_monitor import PerformanceMonitor, SystemHealth, PerformanceLevel
from scalability.distributed_consensus import ScalableConsensusManager, ConsensusRequest, HierarchicalConsensusResult
from scalability.agent_pool import AgentPoolManager, AgentType, PoolStatus


class ScalingStrategy(Enum):
    """Scaling strategies for different scenarios"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class DeploymentMode(Enum):
    """Deployment modes"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_AVAILABILITY = "high_availability"


@dataclass
class ScalabilityConfiguration:
    """Scalability system configuration"""
    max_total_agents: int
    target_agents_per_cluster: int
    monitoring_interval: int
    scaling_strategy: ScalingStrategy
    deployment_mode: DeploymentMode
    enable_auto_scaling: bool
    enable_predictive_scaling: bool
    performance_thresholds: Dict[str, float]
    consensus_timeout: float
    partition_tolerance: bool


@dataclass
class ScalabilityMetrics:
    """Comprehensive scalability metrics"""
    total_agents: int
    active_clusters: int
    system_health: PerformanceLevel
    consensus_success_rate: float
    average_response_time: float
    throughput: float
    resource_utilization: Dict[str, float]
    scaling_events_last_hour: int
    partition_status: str
    efficiency_score: float
    timestamp: datetime


class ScalabilityManager:
    """Enterprise scalability management system"""
    
    def __init__(self, deployment_name: str = "reliquary_enterprise"):
        self.deployment_name = deployment_name
        self.logger = logging.getLogger(f"scalability.{deployment_name}")
        
        # Configuration
        self.config = ScalabilityConfiguration(
            max_total_agents=150,
            target_agents_per_cluster=12,
            monitoring_interval=30,
            scaling_strategy=ScalingStrategy.HYBRID,
            deployment_mode=DeploymentMode.PRODUCTION,
            enable_auto_scaling=True,
            enable_predictive_scaling=True,
            performance_thresholds={
                "cpu_warning": 70.0,
                "cpu_critical": 90.0,
                "memory_warning": 80.0,
                "memory_critical": 95.0,
                "response_time_warning": 1000.0,
                "response_time_critical": 5000.0,
                "throughput_minimum": 100.0
            },
            consensus_timeout=30.0,
            partition_tolerance=True
        )
        
        # Core components
        self.performance_monitor = PerformanceMonitor(f"{deployment_name}_monitor")
        self.consensus_manager = ScalableConsensusManager(f"{deployment_name}_consensus")
        self.agent_pool = AgentPoolManager(f"{deployment_name}_pool")
        
        # System state
        self.system_initialized = False
        self.monitoring_active = False
        self.scaling_coordinator_task = None
        
        # Metrics and history
        self.scaling_history = []
        self.performance_history = []
        self.system_alerts = []
        
        # Predictive scaling
        self.load_predictor = LoadPredictor() if self.config.enable_predictive_scaling else None
        
        self.logger.info(f"Scalability Manager initialized for {deployment_name}")
    
    async def initialize_system(self, initial_agent_config: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Initialize the complete scalability system"""
        try:
            self.logger.info("Initializing enterprise scalability system...")
            start_time = time.time()
            
            # Set default configuration if not provided
            if initial_agent_config is None:
                initial_agent_config = {
                    AgentType.NEUTRAL.value: 8,
                    AgentType.PERMISSIVE.value: 4,
                    AgentType.STRICT.value: 4,
                    AgentType.WATCHDOG.value: 4
                }
            
            # Initialize components in order
            initialization_results = {}
            
            # 1. Initialize performance monitoring
            self.performance_monitor.start_monitoring()
            initialization_results["performance_monitor"] = {
                "status": "active",
                "monitoring_interval": self.config.monitoring_interval
            }
            
            # 2. Initialize agent pool
            pool_result = await self.agent_pool.initialize_pool()
            initialization_results["agent_pool"] = pool_result
            
            # 3. Create agent list for consensus manager
            agent_list = []
            for agent_id in self.agent_pool.agents.keys():
                agent_list.append(agent_id)
                # Register with performance monitor
                if agent_id in self.agent_pool.agent_references:
                    agent_ref = self.agent_pool.agent_references[agent_id]
                    if agent_ref():
                        self.performance_monitor.register_agent(agent_id, agent_ref())
            
            # 4. Initialize consensus clustering
            if agent_list:
                clustering_result = await self.consensus_manager.initialize_clustering(agent_list)
                initialization_results["consensus_clustering"] = clustering_result
            
            # 5. Start scaling coordinator
            await self._start_scaling_coordinator()
            initialization_results["scaling_coordinator"] = {"status": "active"}
            
            initialization_time = time.time() - start_time
            
            self.system_initialized = True
            self.monitoring_active = True
            
            result = {
                "deployment_name": self.deployment_name,
                "system_initialized": True,
                "initialization_time": initialization_time,
                "total_agents": len(agent_list),
                "configuration": asdict(self.config),
                "components": initialization_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Scalability system initialized in {initialization_time:.2f}s with {len(agent_list)} agents")
            return result
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.system_initialized = False
            raise
    
    async def _start_scaling_coordinator(self):
        """Start the scaling coordination task"""
        if self.scaling_coordinator_task:
            return
        
        self.scaling_coordinator_task = asyncio.create_task(self._scaling_coordination_loop())
        self.logger.info("Scaling coordinator started")
    
    async def _scaling_coordination_loop(self):
        """Main scaling coordination loop"""
        while self.monitoring_active:
            try:
                # Get current system health
                system_health = self.performance_monitor.assess_system_health()
                
                # Store performance history
                self.performance_history.append({
                    "timestamp": system_health.timestamp.isoformat(),
                    "health": system_health.overall_health.value,
                    "cpu_usage": system_health.cpu_usage,
                    "memory_usage": system_health.memory_usage,
                    "response_time": system_health.average_response_time,
                    "active_agents": system_health.active_agents
                })
                
                # Keep only last 1000 entries
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
                
                # Evaluate scaling needs
                await self._evaluate_and_execute_scaling(system_health)
                
                # Handle system alerts
                await self._process_system_alerts(system_health)
                
                # Predictive scaling
                if self.load_predictor:
                    await self._execute_predictive_scaling()
                
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Scaling coordination error: {e}")
                await asyncio.sleep(self.config.monitoring_interval)
    
    async def _evaluate_and_execute_scaling(self, system_health: SystemHealth):
        """Evaluate system health and execute scaling decisions"""
        try:
            # Determine if scaling action is needed
            scaling_decision = self._analyze_scaling_needs(system_health)
            
            if scaling_decision["action"] != "none":
                await self._execute_scaling_action(scaling_decision, system_health)
                
        except Exception as e:
            self.logger.error(f"Scaling evaluation failed: {e}")
    
    def _analyze_scaling_needs(self, system_health: SystemHealth) -> Dict[str, Any]:
        """Analyze system health and determine scaling needs"""
        decision = {
            "action": "none",
            "reason": "",
            "agent_type": None,
            "scale_amount": 0,
            "priority": "normal"
        }
        
        # Critical conditions - immediate scaling up
        if (system_health.overall_health == PerformanceLevel.CRITICAL or
            system_health.cpu_usage > self.config.performance_thresholds["cpu_critical"] or
            system_health.memory_usage > self.config.performance_thresholds["memory_critical"]):
            
            decision.update({
                "action": "scale_up",
                "reason": "critical_system_health",
                "agent_type": AgentType.NEUTRAL,  # Scale neutral agents first
                "scale_amount": 3,
                "priority": "critical"
            })
            
        # High load conditions - scale up
        elif (system_health.overall_health == PerformanceLevel.DEGRADED or
              system_health.average_response_time > self.config.performance_thresholds["response_time_warning"]):
            
            decision.update({
                "action": "scale_up",
                "reason": "high_load",
                "agent_type": AgentType.NEUTRAL,
                "scale_amount": 2,
                "priority": "high"
            })
            
        # Low utilization - consider scaling down
        elif (system_health.overall_health == PerformanceLevel.EXCELLENT and
              system_health.cpu_usage < 30 and
              system_health.memory_usage < 40 and
              system_health.active_agents > 20):  # Only if we have enough agents
            
            decision.update({
                "action": "scale_down",
                "reason": "low_utilization",
                "agent_type": AgentType.NEUTRAL,
                "scale_amount": 1,
                "priority": "low"
            })
        
        return decision
    
    async def _execute_scaling_action(self, decision: Dict[str, Any], system_health: SystemHealth):
        """Execute the scaling action"""
        try:
            action = decision["action"]
            agent_type = decision["agent_type"]
            scale_amount = decision["scale_amount"]
            reason = decision["reason"]
            
            if action == "scale_up":
                await self._scale_up_system(agent_type, scale_amount, reason)
            elif action == "scale_down":
                await self._scale_down_system(agent_type, scale_amount, reason)
            
            # Record scaling event
            scaling_event = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "agent_type": agent_type.value if agent_type else None,
                "scale_amount": scale_amount,
                "reason": reason,
                "system_health_before": system_health.overall_health.value,
                "total_agents_before": system_health.active_agents
            }
            
            self.scaling_history.append(scaling_event)
            
            # Keep only last 100 scaling events
            if len(self.scaling_history) > 100:
                self.scaling_history = self.scaling_history[-100:]
                
        except Exception as e:
            self.logger.error(f"Scaling action execution failed: {e}")
    
    async def _scale_up_system(self, agent_type: AgentType, scale_amount: int, reason: str):
        """Scale up the system by adding agents"""
        try:
            # Get current agent count
            current_agents = list(self.agent_pool.agents.keys())
            current_count = len(current_agents)
            
            if current_count >= self.config.max_total_agents:
                self.logger.warning(f"Cannot scale up: at maximum agent limit ({self.config.max_total_agents})")
                return
            
            # Create new agents
            new_agent_ids = await self.agent_pool._create_agents(agent_type, scale_amount)
            
            if new_agent_ids:
                # Register new agents with performance monitor
                for agent_id in new_agent_ids:
                    if agent_id in self.agent_pool.agent_references:
                        agent_ref = self.agent_pool.agent_references[agent_id]
                        if agent_ref():
                            self.performance_monitor.register_agent(agent_id, agent_ref())
                
                # Update consensus clustering
                all_agents = list(self.agent_pool.agents.keys())
                await self.consensus_manager.initialize_clustering(all_agents)
                
                self.logger.info(f"Scaled up: added {len(new_agent_ids)} {agent_type.value} agents (reason: {reason})")
            
        except Exception as e:
            self.logger.error(f"Scale up failed: {e}")
    
    async def _scale_down_system(self, agent_type: AgentType, scale_amount: int, reason: str):
        """Scale down the system by removing agents"""
        try:
            # Get agents of specified type that can be removed
            removable_agents = [
                agent for agent in self.agent_pool.agents.values()
                if (agent.agent_type == agent_type and 
                    agent.status.value in ["idle", "ready"] and
                    agent.current_load < 0.3)
            ]
            
            # Don't remove too many agents
            min_agents = self.agent_pool.config.min_agents.get(agent_type, 1)
            current_count = len([a for a in self.agent_pool.agents.values() if a.agent_type == agent_type])
            max_removable = max(0, current_count - min_agents)
            
            agents_to_remove = min(scale_amount, len(removable_agents), max_removable)
            
            if agents_to_remove > 0:
                # Remove least utilized agents
                sorted_agents = sorted(removable_agents, key=lambda a: a.current_load)
                removed_agents = []
                
                for i in range(agents_to_remove):
                    agent = sorted_agents[i]
                    await self.agent_pool._remove_agent(agent.agent_id, f"scale_down_{reason}")
                    self.performance_monitor.unregister_agent(agent.agent_id)
                    removed_agents.append(agent.agent_id)
                
                # Update consensus clustering
                remaining_agents = list(self.agent_pool.agents.keys())
                if remaining_agents:
                    await self.consensus_manager.initialize_clustering(remaining_agents)
                
                self.logger.info(f"Scaled down: removed {len(removed_agents)} {agent_type.value} agents (reason: {reason})")
            
        except Exception as e:
            self.logger.error(f"Scale down failed: {e}")
    
    async def _process_system_alerts(self, system_health: SystemHealth):
        """Process and handle system alerts"""
        alerts = []
        
        # Generate alerts based on system health
        if system_health.overall_health == PerformanceLevel.CRITICAL:
            alerts.append({
                "level": "critical",
                "message": "System in critical state - immediate attention required",
                "recommendations": system_health.recommendations
            })
        
        if system_health.bottlenecks:
            alerts.append({
                "level": "warning",
                "message": f"Performance bottlenecks detected: {', '.join(system_health.bottlenecks)}",
                "recommendations": ["Investigate bottleneck causes"]
            })
        
        # Store alerts
        for alert in alerts:
            alert["timestamp"] = datetime.now().isoformat()
            self.system_alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.system_alerts) > 50:
            self.system_alerts = self.system_alerts[-50:]
    
    async def _execute_predictive_scaling(self):
        """Execute predictive scaling based on load predictions"""
        if not self.load_predictor:
            return
        
        try:
            # Get load prediction
            predicted_load = await self.load_predictor.predict_load(
                self.performance_history[-10:] if self.performance_history else []
            )
            
            # Make scaling decisions based on predictions
            if predicted_load > 0.8:  # High load predicted
                current_agents = len(self.agent_pool.agents)
                if current_agents < self.config.max_total_agents * 0.8:
                    await self._scale_up_system(AgentType.NEUTRAL, 1, "predictive_high_load")
            
        except Exception as e:
            self.logger.error(f"Predictive scaling failed: {e}")
    
    async def process_consensus_request(self, request_data: Dict[str, Any]) -> HierarchicalConsensusResult:
        """Process a consensus request through the scalable system"""
        try:
            # Create consensus request
            consensus_request = ConsensusRequest(
                request_id=request_data.get("request_id", f"req_{int(time.time())}"),
                request_type=request_data.get("request_type", "access_request"),
                payload=request_data.get("payload", {}),
                priority=request_data.get("priority", 5),
                timeout_seconds=request_data.get("timeout_seconds", self.config.consensus_timeout),
                required_clusters=request_data.get("required_clusters"),
                minimum_consensus=request_data.get("minimum_consensus", 0.6),
                created_at=datetime.now()
            )
            
            # Execute hierarchical consensus
            result = await self.consensus_manager.execute_hierarchical_consensus(consensus_request)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Consensus request processing failed: {e}")
            raise
    
    def get_scalability_metrics(self) -> ScalabilityMetrics:
        """Get comprehensive scalability metrics"""
        try:
            # Get current system health
            system_health = self.performance_monitor.assess_system_health()
            
            # Get pool status
            pool_status = self.agent_pool.get_pool_status()
            
            # Get consensus metrics
            consensus_metrics = self.consensus_manager.get_consensus_metrics()
            
            # Calculate scaling events in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_scaling = [
                event for event in self.scaling_history
                if datetime.fromisoformat(event["timestamp"]) > one_hour_ago
            ]
            
            # Calculate efficiency score
            efficiency_factors = []
            if system_health.active_agents > 0:
                efficiency_factors.append(pool_status["efficiency"])
            if consensus_metrics["total_consensus_requests"] > 0:
                efficiency_factors.append(consensus_metrics["performance_metrics"]["success_rate"] / 100)
            if system_health.average_response_time > 0:
                efficiency_factors.append(max(0, 1 - (system_health.average_response_time / 5000)))
            
            efficiency_score = sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0
            
            return ScalabilityMetrics(
                total_agents=system_health.active_agents,
                active_clusters=consensus_metrics["total_clusters"],
                system_health=system_health.overall_health,
                consensus_success_rate=consensus_metrics["performance_metrics"]["success_rate"],
                average_response_time=system_health.average_response_time,
                throughput=pool_status["total_requests_processed"] / max(1, time.time() - self.performance_monitor.system_start_time),
                resource_utilization={
                    "cpu": system_health.cpu_usage,
                    "memory": system_health.memory_usage,
                    "agents": (system_health.active_agents / self.config.max_total_agents) * 100
                },
                scaling_events_last_hour=len(recent_scaling),
                partition_status=system_health.scalability_status.value,
                efficiency_score=efficiency_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return ScalabilityMetrics(
                total_agents=0, active_clusters=0, system_health=PerformanceLevel.FAILED,
                consensus_success_rate=0, average_response_time=0, throughput=0,
                resource_utilization={}, scaling_events_last_hour=0,
                partition_status="unknown", efficiency_score=0, timestamp=datetime.now()
            )
    
    async def shutdown(self):
        """Gracefully shutdown the scalability system"""
        self.logger.info("Shutting down scalability system...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        if self.scaling_coordinator_task:
            self.scaling_coordinator_task.cancel()
        
        # Shutdown components
        self.performance_monitor.stop_monitoring()
        await self.agent_pool.shutdown()
        
        self.logger.info("Scalability system shutdown complete")


class LoadPredictor:
    """Simple load prediction for predictive scaling"""
    
    def __init__(self):
        self.logger = logging.getLogger("load_predictor")
    
    async def predict_load(self, performance_history: List[Dict[str, Any]]) -> float:
        """Predict future load based on historical data"""
        try:
            if len(performance_history) < 3:
                return 0.5  # Default prediction
            
            # Simple trend analysis
            recent_cpu = [entry["cpu_usage"] for entry in performance_history[-3:]]
            recent_response_times = [entry["response_time"] for entry in performance_history[-3:]]
            
            # Calculate trends
            cpu_trend = (recent_cpu[-1] - recent_cpu[0]) / len(recent_cpu)
            response_trend = (recent_response_times[-1] - recent_response_times[0]) / len(recent_response_times)
            
            # Predict load (0-1 scale)
            predicted_load = 0.5  # Base load
            
            if cpu_trend > 5:  # CPU increasing
                predicted_load += 0.2
            if response_trend > 100:  # Response time increasing
                predicted_load += 0.2
            
            return min(1.0, max(0.0, predicted_load))
            
        except Exception as e:
            self.logger.error(f"Load prediction failed: {e}")
            return 0.5  # Default prediction