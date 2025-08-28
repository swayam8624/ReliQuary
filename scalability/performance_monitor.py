"""
Advanced Performance Monitoring System for ReliQuary Scalability

This module implements comprehensive performance monitoring, metrics collection,
and scalability optimization for large-scale multi-agent networks (100+ agents).
"""

import asyncio
import time
import psutil
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref

# System monitoring imports
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available - using basic metrics")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available - using memory-based metrics")


class MetricType(Enum):
    """Types of performance metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class PerformanceLevel(Enum):
    """Performance levels for system health"""
    EXCELLENT = "excellent"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"


class ScalabilityStatus(Enum):
    """Scalability status indicators"""
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"
    STABLE = "stable"
    AT_CAPACITY = "at_capacity"
    OVERLOADED = "overloaded"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    help_text: str


@dataclass
class SystemHealth:
    """System health assessment"""
    overall_health: PerformanceLevel
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_agents: int
    pending_decisions: int
    average_response_time: float
    error_rate: float
    scalability_status: ScalabilityStatus
    bottlenecks: List[str]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class AgentPerformanceStats:
    """Performance statistics for individual agents"""
    agent_id: str
    agent_type: str
    total_decisions: int
    successful_decisions: int
    failed_decisions: int
    average_processing_time: float
    current_load: float
    memory_usage: float
    cpu_usage: float
    last_activity: datetime
    health_status: PerformanceLevel
    error_messages: List[str]


class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, monitor_name: str = "performance_monitor_v1"):
        self.monitor_name = monitor_name
        self.logger = logging.getLogger(f"performance_monitor.{monitor_name}")
        
        # Metrics storage
        self.metrics_registry = {}
        self.metric_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Redis connection (if available)
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                self.redis_client.ping()
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        
        # Performance thresholds
        self.thresholds = {
            "cpu_usage_warning": 70.0,
            "cpu_usage_critical": 90.0,
            "memory_usage_warning": 80.0,
            "memory_usage_critical": 95.0,
            "response_time_warning": 1000,  # ms
            "response_time_critical": 5000,  # ms
            "error_rate_warning": 5.0,  # %
            "error_rate_critical": 15.0,  # %
            "max_agents_optimal": 50,
            "max_agents_capacity": 100,
            "max_agents_overload": 150
        }
        
        # Agent tracking
        self.active_agents = {}
        self.agent_stats = {}
        self.agent_load_balancer = AgentLoadBalancer()
        
        # System metrics
        self.system_start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_interval = 10  # seconds
        self.monitoring_thread = None
        
        self.logger.info(f"Performance Monitor {monitor_name} initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collectors"""
        try:
            self.prometheus_metrics = {
                'decision_requests_total': Counter(
                    'reliquary_decision_requests_total',
                    'Total number of decision requests',
                    ['agent_type', 'status']
                ),
                'decision_duration_seconds': Histogram(
                    'reliquary_decision_duration_seconds',
                    'Decision processing duration in seconds',
                    ['agent_type']
                ),
                'active_agents': Gauge(
                    'reliquary_active_agents',
                    'Number of active agents',
                    ['agent_type']
                ),
                'system_cpu_usage': Gauge(
                    'reliquary_system_cpu_usage_percent',
                    'System CPU usage percentage'
                ),
                'system_memory_usage': Gauge(
                    'reliquary_system_memory_usage_percent',
                    'System memory usage percentage'
                ),
                'queue_size': Gauge(
                    'reliquary_queue_size',
                    'Size of decision processing queue'
                )
            }
            self.logger.info("Prometheus metrics initialized")
        except Exception as e:
            self.logger.error(f"Prometheus metrics setup failed: {e}")
    
    def start_monitoring(self):
        """Start background performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect agent metrics
                self._collect_agent_metrics()
                
                # Update health assessment
                health = self.assess_system_health()
                
                # Check for scaling needs
                self._check_scaling_requirements(health)
                
                # Store metrics
                if self.redis_client:
                    self._store_metrics_redis(health)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system_cpu_usage", cpu_percent, MetricType.GAUGE)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric("system_memory_usage", memory.percent, MetricType.GAUGE)
            self.record_metric("system_memory_available", memory.available, MetricType.GAUGE)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("system_disk_usage", disk_percent, MetricType.GAUGE)
            
            # Network metrics
            network = psutil.net_io_counters()
            self.record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER)
            self.record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER)
            
            # Process metrics
            process = psutil.Process()
            self.record_metric("process_cpu_usage", process.cpu_percent(), MetricType.GAUGE)
            self.record_metric("process_memory_usage", process.memory_percent(), MetricType.GAUGE)
            
        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
    
    def _collect_agent_metrics(self):
        """Collect agent-specific performance metrics"""
        for agent_id, agent_ref in list(self.active_agents.items()):
            try:
                agent = agent_ref()  # Weak reference
                if agent is None:
                    # Agent was garbage collected
                    del self.active_agents[agent_id]
                    continue
                
                # Get agent statistics
                if hasattr(agent, 'get_performance_stats'):
                    stats = agent.get_performance_stats()
                    self.agent_stats[agent_id] = AgentPerformanceStats(
                        agent_id=agent_id,
                        agent_type=getattr(agent, 'agent_type', 'unknown'),
                        total_decisions=stats.get('total_decisions', 0),
                        successful_decisions=stats.get('successful_decisions', 0),
                        failed_decisions=stats.get('failed_decisions', 0),
                        average_processing_time=stats.get('average_processing_time', 0),
                        current_load=stats.get('current_load', 0),
                        memory_usage=stats.get('memory_usage', 0),
                        cpu_usage=stats.get('cpu_usage', 0),
                        last_activity=datetime.now(),
                        health_status=self._assess_agent_health(stats),
                        error_messages=stats.get('recent_errors', [])
                    )
                
            except Exception as e:
                self.logger.error(f"Agent metrics collection failed for {agent_id}: {e}")
    
    def _assess_agent_health(self, stats: Dict[str, Any]) -> PerformanceLevel:
        """Assess individual agent health"""
        cpu_usage = stats.get('cpu_usage', 0)
        memory_usage = stats.get('memory_usage', 0)
        error_rate = stats.get('error_rate', 0)
        response_time = stats.get('average_processing_time', 0)
        
        if (cpu_usage > 90 or memory_usage > 95 or 
            error_rate > 20 or response_time > 10000):
            return PerformanceLevel.CRITICAL
        elif (cpu_usage > 70 or memory_usage > 80 or 
              error_rate > 10 or response_time > 5000):
            return PerformanceLevel.DEGRADED
        elif (cpu_usage > 50 or memory_usage > 60 or 
              error_rate > 5 or response_time > 2000):
            return PerformanceLevel.GOOD
        else:
            return PerformanceLevel.EXCELLENT
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     labels: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        labels = labels or {}
        timestamp = datetime.now()
        
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            labels=labels,
            help_text=f"Performance metric: {name}"
        )
        
        # Store in registry
        metric_key = f"{name}_{hash(str(sorted(labels.items())))}"
        self.metrics_registry[metric_key] = metric
        
        # Add to history
        self.metric_history[name].append((timestamp, value))
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and hasattr(self, 'prometheus_metrics'):
            self._update_prometheus_metric(name, value, metric_type, labels)
    
    def _update_prometheus_metric(self, name: str, value: float, 
                                 metric_type: MetricType, labels: Dict[str, str]):
        """Update Prometheus metrics"""
        try:
            prometheus_name = name.replace('_', '_')
            
            if prometheus_name in self.prometheus_metrics:
                prom_metric = self.prometheus_metrics[prometheus_name]
                
                if metric_type == MetricType.COUNTER:
                    if labels:
                        prom_metric.labels(**labels).inc(value)
                    else:
                        prom_metric.inc(value)
                elif metric_type == MetricType.GAUGE:
                    if labels:
                        prom_metric.labels(**labels).set(value)
                    else:
                        prom_metric.set(value)
                elif metric_type == MetricType.HISTOGRAM:
                    if labels:
                        prom_metric.labels(**labels).observe(value)
                    else:
                        prom_metric.observe(value)
                        
        except Exception as e:
            self.logger.error(f"Prometheus metric update failed: {e}")
    
    def assess_system_health(self) -> SystemHealth:
        """Assess overall system health"""
        try:
            # Get latest system metrics
            cpu_usage = self._get_latest_metric("system_cpu_usage", 0)
            memory_usage = self._get_latest_metric("system_memory_usage", 0)
            disk_usage = self._get_latest_metric("system_disk_usage", 0)
            
            # Network I/O
            network_io = {
                "bytes_sent": self._get_latest_metric("network_bytes_sent", 0),
                "bytes_recv": self._get_latest_metric("network_bytes_recv", 0)
            }
            
            # Agent metrics
            active_agents = len(self.active_agents)
            pending_decisions = 0  # Would be tracked separately
            
            # Calculate averages
            response_times = []
            error_rates = []
            
            for stats in self.agent_stats.values():
                response_times.append(stats.average_processing_time)
                if stats.total_decisions > 0:
                    error_rate = (stats.failed_decisions / stats.total_decisions) * 100
                    error_rates.append(error_rate)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0
            
            # Determine overall health
            overall_health = self._determine_overall_health(
                cpu_usage, memory_usage, avg_response_time, avg_error_rate, active_agents
            )
            
            # Determine scalability status
            scalability_status = self._determine_scalability_status(
                active_agents, cpu_usage, memory_usage, avg_response_time
            )
            
            # Identify bottlenecks
            bottlenecks = self._identify_bottlenecks(
                cpu_usage, memory_usage, avg_response_time, avg_error_rate
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                overall_health, scalability_status, bottlenecks
            )
            
            return SystemHealth(
                overall_health=overall_health,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_agents=active_agents,
                pending_decisions=pending_decisions,
                average_response_time=avg_response_time,
                error_rate=avg_error_rate,
                scalability_status=scalability_status,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Health assessment failed: {e}")
            return SystemHealth(
                overall_health=PerformanceLevel.FAILED,
                cpu_usage=0, memory_usage=0, disk_usage=0,
                network_io={}, active_agents=0, pending_decisions=0,
                average_response_time=0, error_rate=100,
                scalability_status=ScalabilityStatus.OVERLOADED,
                bottlenecks=["Health assessment failure"],
                recommendations=["Investigate system health monitoring"],
                timestamp=datetime.now()
            )
    
    def _get_latest_metric(self, name: str, default: float = 0.0) -> float:
        """Get the latest value for a metric"""
        if name in self.metric_history and self.metric_history[name]:
            return self.metric_history[name][-1][1]
        return default
    
    def _determine_overall_health(self, cpu: float, memory: float, 
                                 response_time: float, error_rate: float, 
                                 agents: int) -> PerformanceLevel:
        """Determine overall system health level"""
        critical_conditions = [
            cpu > self.thresholds["cpu_usage_critical"],
            memory > self.thresholds["memory_usage_critical"],
            response_time > self.thresholds["response_time_critical"],
            error_rate > self.thresholds["error_rate_critical"],
            agents > self.thresholds["max_agents_overload"]
        ]
        
        warning_conditions = [
            cpu > self.thresholds["cpu_usage_warning"],
            memory > self.thresholds["memory_usage_warning"],
            response_time > self.thresholds["response_time_warning"],
            error_rate > self.thresholds["error_rate_warning"],
            agents > self.thresholds["max_agents_capacity"]
        ]
        
        if any(critical_conditions):
            return PerformanceLevel.CRITICAL
        elif any(warning_conditions):
            return PerformanceLevel.DEGRADED
        elif agents > self.thresholds["max_agents_optimal"]:
            return PerformanceLevel.GOOD
        else:
            return PerformanceLevel.EXCELLENT
    
    def _determine_scalability_status(self, agents: int, cpu: float, 
                                    memory: float, response_time: float) -> ScalabilityStatus:
        """Determine scalability status"""
        if agents > self.thresholds["max_agents_overload"]:
            return ScalabilityStatus.OVERLOADED
        elif agents >= self.thresholds["max_agents_capacity"]:
            return ScalabilityStatus.AT_CAPACITY
        elif (cpu > 80 or memory > 85 or response_time > 3000):
            return ScalabilityStatus.SCALING_UP
        elif (cpu < 30 and memory < 40 and agents > 10):
            return ScalabilityStatus.SCALING_DOWN
        else:
            return ScalabilityStatus.STABLE
    
    def _identify_bottlenecks(self, cpu: float, memory: float, 
                            response_time: float, error_rate: float) -> List[str]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        if cpu > self.thresholds["cpu_usage_warning"]:
            bottlenecks.append(f"High CPU usage: {cpu:.1f}%")
        
        if memory > self.thresholds["memory_usage_warning"]:
            bottlenecks.append(f"High memory usage: {memory:.1f}%")
        
        if response_time > self.thresholds["response_time_warning"]:
            bottlenecks.append(f"High response time: {response_time:.1f}ms")
        
        if error_rate > self.thresholds["error_rate_warning"]:
            bottlenecks.append(f"High error rate: {error_rate:.1f}%")
        
        return bottlenecks
    
    def _generate_recommendations(self, health: PerformanceLevel, 
                                scalability: ScalabilityStatus, 
                                bottlenecks: List[str]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if health == PerformanceLevel.CRITICAL:
            recommendations.append("Immediate intervention required - system in critical state")
            recommendations.append("Consider emergency scaling or load shedding")
        
        if scalability == ScalabilityStatus.OVERLOADED:
            recommendations.append("Scale up infrastructure immediately")
            recommendations.append("Implement load balancing across more nodes")
        
        if scalability == ScalabilityStatus.SCALING_UP:
            recommendations.append("Consider adding more agent instances")
            recommendations.append("Monitor resource allocation")
        
        if "High CPU usage" in str(bottlenecks):
            recommendations.append("Optimize CPU-intensive operations")
            recommendations.append("Consider CPU scaling or optimization")
        
        if "High memory usage" in str(bottlenecks):
            recommendations.append("Optimize memory usage and implement garbage collection")
            recommendations.append("Consider memory scaling")
        
        if not recommendations:
            recommendations.append("System performing well - maintain current configuration")
        
        return recommendations
    
    def _check_scaling_requirements(self, health: SystemHealth):
        """Check if scaling actions are required"""
        if health.scalability_status == ScalabilityStatus.OVERLOADED:
            self.logger.warning("System overloaded - scaling up required")
            # Trigger scaling up logic
            
        elif health.scalability_status == ScalabilityStatus.SCALING_DOWN:
            self.logger.info("System underutilized - consider scaling down")
            # Trigger scaling down logic
    
    def _store_metrics_redis(self, health: SystemHealth):
        """Store metrics in Redis for distributed access"""
        if not self.redis_client:
            return
        
        try:
            # Store current health status
            health_key = f"reliquary:health:{int(time.time())}"
            self.redis_client.setex(health_key, 3600, json.dumps(asdict(health), default=str))
            
            # Store agent statistics
            for agent_id, stats in self.agent_stats.items():
                stats_key = f"reliquary:agent:{agent_id}"
                self.redis_client.setex(stats_key, 300, json.dumps(asdict(stats), default=str))
                
        except Exception as e:
            self.logger.error(f"Redis storage failed: {e}")
    
    def register_agent(self, agent_id: str, agent_instance):
        """Register an agent for monitoring"""
        self.active_agents[agent_id] = weakref.ref(agent_instance)
        self.logger.info(f"Registered agent {agent_id} for monitoring")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from monitoring"""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        if agent_id in self.agent_stats:
            del self.agent_stats[agent_id]
        self.logger.info(f"Unregistered agent {agent_id} from monitoring")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        health = self.assess_system_health()
        
        return {
            "monitor_name": self.monitor_name,
            "system_health": asdict(health),
            "agent_count": len(self.active_agents),
            "agent_stats": {aid: asdict(stats) for aid, stats in self.agent_stats.items()},
            "uptime_seconds": time.time() - self.system_start_time,
            "total_requests": self.total_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1) * 100,
            "monitoring_active": self.monitoring_active,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "redis_available": self.redis_client is not None,
            "timestamp": datetime.now().isoformat()
        }


class AgentLoadBalancer:
    """Load balancing for agent distribution"""
    
    def __init__(self):
        self.agent_loads = defaultdict(float)
        self.agent_queues = defaultdict(int)
        self.load_history = defaultdict(lambda: deque(maxlen=100))
        
    def update_agent_load(self, agent_id: str, load: float):
        """Update agent load information"""
        self.agent_loads[agent_id] = load
        self.load_history[agent_id].append((time.time(), load))
    
    def get_least_loaded_agent(self, agent_type: Optional[str] = None) -> Optional[str]:
        """Get the least loaded agent of specified type"""
        if not self.agent_loads:
            return None
        
        # Simple load balancing - return agent with lowest load
        return min(self.agent_loads.items(), key=lambda x: x[1])[0]
    
    def distribute_load(self, total_requests: int) -> Dict[str, int]:
        """Distribute load across available agents"""
        if not self.agent_loads:
            return {}
        
        # Distribute based on inverse of current load
        total_capacity = sum(1.0 / max(load, 0.1) for load in self.agent_loads.values())
        
        distribution = {}
        for agent_id, load in self.agent_loads.items():
            capacity_ratio = (1.0 / max(load, 0.1)) / total_capacity
            distribution[agent_id] = int(total_requests * capacity_ratio)
        
        return distribution