"""
Agent Pool Management System for Dynamic Scaling

This module implements dynamic agent pool management with auto-scaling,
load balancing, and resource optimization for large-scale deployments.
"""

import asyncio
import time
import threading
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import weakref
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import ReliQuary components
try:
    from agents.nodes.neutral_agent import NeutralAgent
    from agents.nodes.permissive_agent import PermissiveAgent
    from agents.nodes.strict_agent import StrictAgent
    from agents.nodes.watchdog_agent import WatchdogAgent
    from agents.memory.encrypted_memory import EncryptedMemoryDB
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logging.warning("Agent modules not available - using simulation mode")


class AgentType(Enum):
    """Types of agents in the pool"""
    NEUTRAL = "neutral"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    WATCHDOG = "watchdog"
    SPECIALIZED = "specialized"


class PoolStatus(Enum):
    """Agent pool status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AgentStatus(Enum):
    """Individual agent status"""
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    IDLE = "idle"
    DRAINING = "draining"
    STOPPING = "stopping"
    FAILED = "failed"


@dataclass
class AgentInstance:
    """Individual agent instance information"""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    created_at: datetime
    last_activity: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    current_load: float
    memory_usage: float
    cpu_usage: float
    average_response_time: float
    health_score: float
    metadata: Dict[str, Any]


@dataclass
class PoolConfiguration:
    """Agent pool configuration"""
    pool_name: str
    min_agents: Dict[AgentType, int]
    max_agents: Dict[AgentType, int]
    target_agents: Dict[AgentType, int]
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_cooldown: int  # seconds
    scale_down_cooldown: int  # seconds
    health_check_interval: int  # seconds
    max_idle_time: int  # seconds
    load_balancing_strategy: str
    auto_scaling_enabled: bool


@dataclass
class ScalingEvent:
    """Scaling event information"""
    event_id: str
    event_type: str  # scale_up, scale_down, health_check
    agent_type: AgentType
    old_count: int
    new_count: int
    trigger_reason: str
    timestamp: datetime
    duration: float
    success: bool


class AgentPoolManager:
    """Dynamic agent pool management system"""
    
    def __init__(self, pool_name: str = "reliquary_agent_pool"):
        self.pool_name = pool_name
        self.logger = logging.getLogger(f"agent_pool.{pool_name}")
        
        # Agent pool
        self.agents: Dict[str, AgentInstance] = {}
        self.agent_references: Dict[str, Any] = {}  # Weak references to actual agent objects
        
        # Pool configuration
        self.config = PoolConfiguration(
            pool_name=pool_name,
            min_agents={
                AgentType.NEUTRAL: 2,
                AgentType.PERMISSIVE: 1,
                AgentType.STRICT: 1,
                AgentType.WATCHDOG: 1
            },
            max_agents={
                AgentType.NEUTRAL: 20,
                AgentType.PERMISSIVE: 15,
                AgentType.STRICT: 15,
                AgentType.WATCHDOG: 10
            },
            target_agents={
                AgentType.NEUTRAL: 5,
                AgentType.PERMISSIVE: 3,
                AgentType.STRICT: 3,
                AgentType.WATCHDOG: 2
            },
            scale_up_threshold=0.7,  # 70% load
            scale_down_threshold=0.3,  # 30% load
            scale_up_cooldown=60,    # 1 minute
            scale_down_cooldown=300,  # 5 minutes
            health_check_interval=30,  # 30 seconds
            max_idle_time=600,       # 10 minutes
            load_balancing_strategy="round_robin",
            auto_scaling_enabled=True
        )
        
        # Pool state
        self.pool_status = PoolStatus.INITIALIZING
        self.last_scale_events: Dict[AgentType, datetime] = {}
        self.scaling_history = deque(maxlen=1000)
        
        # Load balancing
        self.load_balancer = LoadBalancer(self.config.load_balancing_strategy)
        self.request_queue = asyncio.Queue()
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        self.health_check_task = None
        
        # Performance metrics
        self.total_requests_processed = 0
        self.total_scaling_events = 0
        self.pool_efficiency = 0.0
        
        # Thread pool for agent operations
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        self.logger.info(f"Agent Pool Manager initialized: {pool_name}")
    
    async def initialize_pool(self) -> Dict[str, Any]:
        """Initialize the agent pool with target configuration"""
        try:
            self.pool_status = PoolStatus.INITIALIZING
            
            # Create initial agents
            initialization_results = {}
            for agent_type, target_count in self.config.target_agents.items():
                created_agents = await self._create_agents(agent_type, target_count)
                initialization_results[agent_type.value] = {
                    "target": target_count,
                    "created": len(created_agents),
                    "agent_ids": created_agents
                }
            
            # Start monitoring
            await self._start_monitoring()
            
            self.pool_status = PoolStatus.ACTIVE
            
            result = {
                "pool_name": self.pool_name,
                "status": self.pool_status.value,
                "total_agents": len(self.agents),
                "agents_by_type": {
                    atype.value: len([a for a in self.agents.values() if a.agent_type == atype])
                    for atype in AgentType
                },
                "initialization_results": initialization_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Agent pool initialized with {len(self.agents)} agents")
            return result
            
        except Exception as e:
            self.pool_status = PoolStatus.ERROR
            self.logger.error(f"Pool initialization failed: {e}")
            raise
    
    async def _create_agents(self, agent_type: AgentType, count: int) -> List[str]:
        """Create multiple agents of specified type"""
        created_agents = []
        
        for i in range(count):
            try:
                agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
                agent_instance = await self._create_single_agent(agent_id, agent_type)
                
                if agent_instance:
                    created_agents.append(agent_id)
                    
            except Exception as e:
                self.logger.error(f"Failed to create {agent_type.value} agent {i}: {e}")
        
        return created_agents
    
    async def _create_single_agent(self, agent_id: str, agent_type: AgentType) -> Optional[AgentInstance]:
        """Create a single agent instance"""
        try:
            # Create agent metadata
            agent_instance = AgentInstance(
                agent_id=agent_id,
                agent_type=agent_type,
                status=AgentStatus.STARTING,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                current_load=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                average_response_time=0.0,
                health_score=1.0,
                metadata={"version": "1.0", "pool": self.pool_name}
            )
            
            # Create actual agent object (if available)
            if AGENTS_AVAILABLE:
                agent_obj = await self._instantiate_agent(agent_id, agent_type)
                if agent_obj:
                    self.agent_references[agent_id] = weakref.ref(agent_obj)
            
            # Mark as ready
            agent_instance.status = AgentStatus.READY
            
            # Store in pool
            self.agents[agent_id] = agent_instance
            
            self.logger.info(f"Created agent {agent_id} of type {agent_type.value}")
            return agent_instance
            
        except Exception as e:
            self.logger.error(f"Agent creation failed for {agent_id}: {e}")
            return None
    
    async def _instantiate_agent(self, agent_id: str, agent_type: AgentType):
        """Instantiate actual agent object"""
        try:
            # Create shared memory database
            memory_db = EncryptedMemoryDB(f"agent_memory_{agent_id}")
            
            # Create agent based on type
            if agent_type == AgentType.NEUTRAL:
                return NeutralAgent(memory_db, agent_id=agent_id)
            elif agent_type == AgentType.PERMISSIVE:
                return PermissiveAgent(memory_db, agent_id=agent_id)
            elif agent_type == AgentType.STRICT:
                return StrictAgent(memory_db, agent_id=agent_id)
            elif agent_type == AgentType.WATCHDOG:
                return WatchdogAgent(memory_db, agent_id=agent_id)
            else:
                self.logger.warning(f"Unknown agent type: {agent_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Agent instantiation failed: {e}")
            return None
    
    async def _start_monitoring(self):
        """Start monitoring tasks"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start health check task
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Start auto-scaling task
        if self.config.auto_scaling_enabled:
            self.monitoring_task = asyncio.create_task(self._auto_scaling_loop())
        
        self.logger.info("Monitoring tasks started")
    
    async def _stop_monitoring(self):
        """Stop monitoring tasks"""
        self.monitoring_active = False
        
        if self.health_check_task:
            self.health_check_task.cancel()
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        self.logger.info("Monitoring tasks stopped")
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _auto_scaling_loop(self):
        """Background auto-scaling loop"""
        while self.monitoring_active:
            try:
                await self._evaluate_scaling_needs()
                await asyncio.sleep(30)  # Check scaling every 30 seconds
            except Exception as e:
                self.logger.error(f"Auto-scaling loop error: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents"""
        unhealthy_agents = []
        
        for agent_id, agent_instance in list(self.agents.items()):
            try:
                health_score = await self._check_agent_health(agent_id, agent_instance)
                agent_instance.health_score = health_score
                agent_instance.last_activity = datetime.now()
                
                # Mark unhealthy agents
                if health_score < 0.3:
                    unhealthy_agents.append(agent_id)
                    agent_instance.status = AgentStatus.FAILED
                    
            except Exception as e:
                self.logger.error(f"Health check failed for agent {agent_id}: {e}")
                unhealthy_agents.append(agent_id)
        
        # Remove unhealthy agents
        for agent_id in unhealthy_agents:
            await self._remove_agent(agent_id, reason="health_check_failure")
    
    async def _check_agent_health(self, agent_id: str, agent_instance: AgentInstance) -> float:
        """Check health of individual agent"""
        health_factors = []
        
        # Check if agent object still exists
        if agent_id in self.agent_references:
            agent_ref = self.agent_references[agent_id]
            if agent_ref() is None:
                return 0.0  # Agent object was garbage collected
        
        # Response time factor
        if agent_instance.average_response_time > 0:
            response_factor = max(0, 1 - (agent_instance.average_response_time / 5000))  # 5s max
            health_factors.append(response_factor)
        
        # Success rate factor
        if agent_instance.total_requests > 0:
            success_rate = agent_instance.successful_requests / agent_instance.total_requests
            health_factors.append(success_rate)
        
        # Load factor
        load_factor = max(0, 1 - agent_instance.current_load)
        health_factors.append(load_factor)
        
        # Idle time factor
        idle_time = (datetime.now() - agent_instance.last_activity).total_seconds()
        if idle_time > self.config.max_idle_time:
            health_factors.append(0.5)  # Penalize very idle agents
        else:
            health_factors.append(1.0)
        
        # Calculate overall health
        return sum(health_factors) / len(health_factors) if health_factors else 0.5
    
    async def _evaluate_scaling_needs(self):
        """Evaluate if scaling is needed"""
        for agent_type in AgentType:
            try:
                current_agents = [a for a in self.agents.values() if a.agent_type == agent_type]
                current_count = len(current_agents)
                
                if current_count == 0:
                    continue
                
                # Calculate average load
                total_load = sum(agent.current_load for agent in current_agents)
                average_load = total_load / current_count
                
                # Check scaling conditions
                should_scale_up = (
                    average_load > self.config.scale_up_threshold and
                    current_count < self.config.max_agents[agent_type] and
                    self._can_scale_up(agent_type)
                )
                
                should_scale_down = (
                    average_load < self.config.scale_down_threshold and
                    current_count > self.config.min_agents[agent_type] and
                    self._can_scale_down(agent_type)
                )
                
                if should_scale_up:
                    await self._scale_up(agent_type, reason="high_load")
                elif should_scale_down:
                    await self._scale_down(agent_type, reason="low_load")
                    
            except Exception as e:
                self.logger.error(f"Scaling evaluation failed for {agent_type}: {e}")
    
    def _can_scale_up(self, agent_type: AgentType) -> bool:
        """Check if scaling up is allowed"""
        last_scale = self.last_scale_events.get(agent_type)
        if last_scale:
            cooldown = datetime.now() - last_scale
            return cooldown.total_seconds() >= self.config.scale_up_cooldown
        return True
    
    def _can_scale_down(self, agent_type: AgentType) -> bool:
        """Check if scaling down is allowed"""
        last_scale = self.last_scale_events.get(agent_type)
        if last_scale:
            cooldown = datetime.now() - last_scale
            return cooldown.total_seconds() >= self.config.scale_down_cooldown
        return True
    
    async def _scale_up(self, agent_type: AgentType, reason: str = "demand"):
        """Scale up agents of specified type"""
        try:
            current_count = len([a for a in self.agents.values() if a.agent_type == agent_type])
            new_agents = await self._create_agents(agent_type, 1)
            new_count = len([a for a in self.agents.values() if a.agent_type == agent_type])
            
            # Record scaling event
            event = ScalingEvent(
                event_id=f"scale_up_{uuid.uuid4().hex[:8]}",
                event_type="scale_up",
                agent_type=agent_type,
                old_count=current_count,
                new_count=new_count,
                trigger_reason=reason,
                timestamp=datetime.now(),
                duration=0.0,
                success=len(new_agents) > 0
            )
            
            self.scaling_history.append(event)
            self.last_scale_events[agent_type] = datetime.now()
            self.total_scaling_events += 1
            
            self.logger.info(f"Scaled up {agent_type.value}: {current_count} -> {new_count}")
            
        except Exception as e:
            self.logger.error(f"Scale up failed for {agent_type}: {e}")
    
    async def _scale_down(self, agent_type: AgentType, reason: str = "low_demand"):
        """Scale down agents of specified type"""
        try:
            current_agents = [a for a in self.agents.values() 
                            if a.agent_type == agent_type and a.status == AgentStatus.IDLE]
            
            if not current_agents:
                return
            
            # Remove least utilized agent
            agent_to_remove = min(current_agents, key=lambda a: a.current_load)
            await self._remove_agent(agent_to_remove.agent_id, reason="scale_down")
            
            # Record scaling event
            current_count = len([a for a in self.agents.values() if a.agent_type == agent_type])
            
            event = ScalingEvent(
                event_id=f"scale_down_{uuid.uuid4().hex[:8]}",
                event_type="scale_down",
                agent_type=agent_type,
                old_count=current_count + 1,
                new_count=current_count,
                trigger_reason=reason,
                timestamp=datetime.now(),
                duration=0.0,
                success=True
            )
            
            self.scaling_history.append(event)
            self.last_scale_events[agent_type] = datetime.now()
            self.total_scaling_events += 1
            
            self.logger.info(f"Scaled down {agent_type.value}: {current_count + 1} -> {current_count}")
            
        except Exception as e:
            self.logger.error(f"Scale down failed for {agent_type}: {e}")
    
    async def _remove_agent(self, agent_id: str, reason: str = "removal"):
        """Remove agent from pool"""
        if agent_id not in self.agents:
            return
        
        try:
            # Mark agent as stopping
            self.agents[agent_id].status = AgentStatus.STOPPING
            
            # Remove from references
            if agent_id in self.agent_references:
                del self.agent_references[agent_id]
            
            # Remove from pool
            del self.agents[agent_id]
            
            self.logger.info(f"Removed agent {agent_id}: {reason}")
            
        except Exception as e:
            self.logger.error(f"Agent removal failed for {agent_id}: {e}")
    
    async def get_available_agent(self, agent_type: Optional[AgentType] = None, 
                                required_capabilities: Optional[List[str]] = None) -> Optional[str]:
        """Get an available agent for request processing"""
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.status in [AgentStatus.READY, AgentStatus.IDLE] and
                (agent_type is None or agent.agent_type == agent_type) and
                agent.health_score > 0.5)
        ]
        
        if not available_agents:
            return None
        
        # Use load balancer to select agent
        selected_agent = self.load_balancer.select_agent(available_agents)
        
        if selected_agent:
            # Mark agent as busy
            selected_agent.status = AgentStatus.BUSY
            selected_agent.last_activity = datetime.now()
            return selected_agent.agent_id
        
        return None
    
    async def release_agent(self, agent_id: str, processing_time: float, success: bool):
        """Release agent after request processing"""
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        
        # Update statistics
        agent.total_requests += 1
        if success:
            agent.successful_requests += 1
        else:
            agent.failed_requests += 1
        
        # Update response time
        total_time = agent.average_response_time * (agent.total_requests - 1) + processing_time
        agent.average_response_time = total_time / agent.total_requests
        
        # Update load (simplified)
        agent.current_load = max(0, agent.current_load - 0.1)
        
        # Mark as ready/idle
        agent.status = AgentStatus.IDLE if agent.current_load < 0.1 else AgentStatus.READY
        agent.last_activity = datetime.now()
        
        self.total_requests_processed += 1
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        agent_counts = defaultdict(int)
        agent_statuses = defaultdict(int)
        
        for agent in self.agents.values():
            agent_counts[agent.agent_type.value] += 1
            agent_statuses[agent.status.value] += 1
        
        # Calculate efficiency
        total_agents = len(self.agents)
        busy_agents = agent_statuses.get(AgentStatus.BUSY.value, 0)
        ready_agents = agent_statuses.get(AgentStatus.READY.value, 0)
        
        if total_agents > 0:
            efficiency = (busy_agents + ready_agents) / total_agents
        else:
            efficiency = 0.0
        
        return {
            "pool_name": self.pool_name,
            "status": self.pool_status.value,
            "total_agents": total_agents,
            "agents_by_type": dict(agent_counts),
            "agents_by_status": dict(agent_statuses),
            "efficiency": efficiency,
            "total_requests_processed": self.total_requests_processed,
            "total_scaling_events": self.total_scaling_events,
            "recent_scaling_events": [asdict(event) for event in list(self.scaling_history)[-10:]],
            "monitoring_active": self.monitoring_active,
            "auto_scaling_enabled": self.config.auto_scaling_enabled,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent pool"""
        self.logger.info("Shutting down agent pool...")
        
        self.pool_status = PoolStatus.DRAINING
        
        # Stop monitoring
        await self._stop_monitoring()
        
        # Mark all agents as draining
        for agent in self.agents.values():
            agent.status = AgentStatus.DRAINING
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)
        
        self.pool_status = PoolStatus.MAINTENANCE
        self.logger.info("Agent pool shutdown complete")


class LoadBalancer:
    """Load balancing strategies for agent selection"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.round_robin_index = 0
        
    def select_agent(self, available_agents: List[AgentInstance]) -> Optional[AgentInstance]:
        """Select agent based on load balancing strategy"""
        if not available_agents:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin_selection(available_agents)
        elif self.strategy == "least_loaded":
            return self._least_loaded_selection(available_agents)
        elif self.strategy == "weighted_random":
            return self._weighted_random_selection(available_agents)
        else:
            return available_agents[0]  # Default to first available
    
    def _round_robin_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Round robin selection"""
        selected = agents[self.round_robin_index % len(agents)]
        self.round_robin_index += 1
        return selected
    
    def _least_loaded_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Select least loaded agent"""
        return min(agents, key=lambda a: a.current_load)
    
    def _weighted_random_selection(self, agents: List[AgentInstance]) -> AgentInstance:
        """Weighted random selection based on inverse load"""
        import random
        
        # Calculate weights (inverse of load)
        weights = [max(0.1, 1.0 - agent.current_load) for agent in agents]
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return agents[0]
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return agents[i]
        
        return agents[-1]  # Fallback