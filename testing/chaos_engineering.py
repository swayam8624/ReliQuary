#!/usr/bin/env python3
"""
Chaos Engineering Framework for ReliQuary Production
Resilience testing and failure simulation for production reliability
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import kubernetes
import requests
from kubernetes import client, config


class ChaosType(Enum):
    """Types of chaos experiments"""
    POD_FAILURE = "pod_failure"
    NETWORK_LATENCY = "network_latency"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FAILURE = "disk_failure"
    DATABASE_SLOWDOWN = "database_slowdown"
    CONSENSUS_DISRUPTION = "consensus_disruption"


@dataclass
class ChaosExperiment:
    """Chaos experiment configuration"""
    name: str
    chaos_type: ChaosType
    target_namespace: str
    target_selector: Dict[str, str]
    duration_seconds: int
    severity: str  # low, medium, high
    expected_recovery_time: int
    success_criteria: Dict[str, Any]


class ChaosEngineeringFramework:
    """Production chaos engineering system"""
    
    def __init__(self):
        config.load_incluster_config()
        self.k8s_client = client.AppsV1Api()
        self.core_client = client.CoreV1Api()
        self.logger = logging.getLogger("chaos_engineering")
        
        # Define experiments
        self.experiments = self._load_experiments()
        
    def _load_experiments(self) -> List[ChaosExperiment]:
        """Load chaos experiment configurations"""
        
        return [
            ChaosExperiment(
                name="platform_pod_failure",
                chaos_type=ChaosType.POD_FAILURE,
                target_namespace="reliquary",
                target_selector={"app": "reliquary-platform"},
                duration_seconds=300,
                severity="medium",
                expected_recovery_time=60,
                success_criteria={
                    "api_availability": 0.99,
                    "max_response_time_ms": 2000,
                    "error_rate_threshold": 0.05
                }
            ),
            ChaosExperiment(
                name="database_connection_failure",
                chaos_type=ChaosType.POD_FAILURE,
                target_namespace="reliquary",
                target_selector={"app": "postgresql"},
                duration_seconds=180,
                severity="high",
                expected_recovery_time=120,
                success_criteria={
                    "graceful_degradation": True,
                    "data_consistency": True,
                    "recovery_time_seconds": 120
                }
            ),
            ChaosExperiment(
                name="consensus_agent_failure",
                chaos_type=ChaosType.POD_FAILURE,
                target_namespace="reliquary",
                target_selector={"app": "reliquary-agent-orchestrator"},
                duration_seconds=240,
                severity="medium",
                expected_recovery_time=90,
                success_criteria={
                    "consensus_maintained": True,
                    "decision_latency_ms": 5000,
                    "agent_recovery": True
                }
            ),
            ChaosExperiment(
                name="network_partition",
                chaos_type=ChaosType.NETWORK_LATENCY,
                target_namespace="reliquary",
                target_selector={"app": "reliquary-platform"},
                duration_seconds=600,
                severity="high",
                expected_recovery_time=30,
                success_criteria={
                    "partition_tolerance": True,
                    "eventual_consistency": True,
                    "no_data_loss": True
                }
            )
        ]
    
    async def run_experiment(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Execute chaos experiment"""
        
        self.logger.info(f"Starting chaos experiment: {experiment.name}")
        
        start_time = time.time()
        experiment_result = {
            "experiment_name": experiment.name,
            "chaos_type": experiment.chaos_type.value,
            "start_time": datetime.now().isoformat(),
            "duration_seconds": experiment.duration_seconds,
            "success": False,
            "metrics": {},
            "observations": []
        }
        
        try:
            # Pre-experiment baseline
            baseline_metrics = await self._collect_baseline_metrics(experiment)
            experiment_result["baseline_metrics"] = baseline_metrics
            
            # Execute chaos action
            if experiment.chaos_type == ChaosType.POD_FAILURE:
                await self._execute_pod_failure(experiment)
            elif experiment.chaos_type == ChaosType.NETWORK_LATENCY:
                await self._execute_network_chaos(experiment)
            elif experiment.chaos_type == ChaosType.CPU_STRESS:
                await self._execute_cpu_stress(experiment)
            
            # Monitor during chaos
            await self._monitor_during_chaos(experiment, experiment_result)
            
            # Wait for recovery
            recovery_metrics = await self._wait_for_recovery(experiment)
            experiment_result["recovery_metrics"] = recovery_metrics
            
            # Validate success criteria
            success = await self._validate_success_criteria(experiment, experiment_result)
            experiment_result["success"] = success
            
            end_time = time.time()
            experiment_result["total_duration_seconds"] = end_time - start_time
            experiment_result["end_time"] = datetime.now().isoformat()
            
            status = "PASSED" if success else "FAILED"
            self.logger.info(f"Chaos experiment {experiment.name} {status}")
            
            return experiment_result
            
        except Exception as e:
            self.logger.error(f"Chaos experiment {experiment.name} failed: {e}")
            experiment_result["error"] = str(e)
            experiment_result["success"] = False
            return experiment_result
    
    async def _execute_pod_failure(self, experiment: ChaosExperiment):
        """Simulate pod failure by deleting pods"""
        
        # Get target pods
        pods = self.core_client.list_namespaced_pod(
            namespace=experiment.target_namespace,
            label_selector=",".join([f"{k}={v}" for k, v in experiment.target_selector.items()])
        )
        
        if not pods.items:
            raise ValueError(f"No pods found for selector {experiment.target_selector}")
        
        # Delete random pod based on severity
        pods_to_delete = 1
        if experiment.severity == "high":
            pods_to_delete = min(2, len(pods.items) // 2)
        
        selected_pods = random.sample(pods.items, pods_to_delete)
        
        for pod in selected_pods:
            self.logger.info(f"Deleting pod: {pod.metadata.name}")
            self.core_client.delete_namespaced_pod(
                name=pod.metadata.name,
                namespace=experiment.target_namespace
            )
    
    async def _execute_network_chaos(self, experiment: ChaosExperiment):
        """Simulate network issues using NetworkPolicy"""
        
        # Create restrictive network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"chaos-network-{int(time.time())}",
                "namespace": experiment.target_namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": experiment.target_selector
                },
                "policyTypes": ["Egress"],
                "egress": []
            }
        }
        
        # Apply network policy
        networking_client = client.NetworkingV1Api()
        networking_client.create_namespaced_network_policy(
            namespace=experiment.target_namespace,
            body=network_policy
        )
        
        # Wait for experiment duration
        await asyncio.sleep(experiment.duration_seconds)
        
        # Remove network policy
        networking_client.delete_namespaced_network_policy(
            name=network_policy["metadata"]["name"],
            namespace=experiment.target_namespace
        )
    
    async def _collect_baseline_metrics(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Collect baseline system metrics before chaos"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "pod_count": len(self._get_target_pods(experiment)),
            "api_response_time": await self._measure_api_response_time(),
            "consensus_latency": await self._measure_consensus_latency(),
            "error_rate": await self._get_current_error_rate()
        }
    
    async def _monitor_during_chaos(self, experiment: ChaosExperiment, result: Dict[str, Any]):
        """Monitor system behavior during chaos"""
        
        monitoring_interval = 30
        monitoring_duration = min(experiment.duration_seconds, 300)
        
        observations = []
        
        for i in range(0, monitoring_duration, monitoring_interval):
            await asyncio.sleep(monitoring_interval)
            
            observation = {
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": i + monitoring_interval,
                "pod_count": len(self._get_target_pods(experiment)),
                "api_available": await self._check_api_availability(),
                "response_time_ms": await self._measure_api_response_time()
            }
            
            observations.append(observation)
            
        result["observations"] = observations
    
    async def _wait_for_recovery(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Wait for system recovery and measure metrics"""
        
        max_wait_time = experiment.expected_recovery_time * 3
        check_interval = 15
        
        recovery_start = time.time()
        
        for elapsed in range(0, max_wait_time, check_interval):
            await asyncio.sleep(check_interval)
            
            if await self._is_system_recovered(experiment):
                recovery_time = time.time() - recovery_start
                return {
                    "recovered": True,
                    "recovery_time_seconds": recovery_time,
                    "within_expected_time": recovery_time <= experiment.expected_recovery_time
                }
        
        return {
            "recovered": False,
            "recovery_time_seconds": max_wait_time,
            "within_expected_time": False
        }
    
    async def _validate_success_criteria(self, experiment: ChaosExperiment, result: Dict[str, Any]) -> bool:
        """Validate experiment success criteria"""
        
        criteria = experiment.success_criteria
        
        # Check API availability
        if "api_availability" in criteria:
            actual_availability = await self._calculate_availability(result)
            if actual_availability < criteria["api_availability"]:
                return False
        
        # Check response time
        if "max_response_time_ms" in criteria:
            max_response_time = max(
                obs.get("response_time_ms", 0) for obs in result.get("observations", [])
            )
            if max_response_time > criteria["max_response_time_ms"]:
                return False
        
        # Check recovery
        if "recovery_time_seconds" in criteria:
            recovery_metrics = result.get("recovery_metrics", {})
            if not recovery_metrics.get("within_expected_time", False):
                return False
        
        return True
    
    def _get_target_pods(self, experiment: ChaosExperiment) -> List[Any]:
        """Get pods matching experiment target selector"""
        
        pods = self.core_client.list_namespaced_pod(
            namespace=experiment.target_namespace,
            label_selector=",".join([f"{k}={v}" for k, v in experiment.target_selector.items()])
        )
        return pods.items
    
    async def _measure_api_response_time(self) -> float:
        """Measure API response time"""
        
        try:
            start_time = time.time()
            response = requests.get("http://reliquary-platform-service/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            return response_time if response.status_code == 200 else 9999
        except Exception:
            return 9999
    
    async def _check_api_availability(self) -> bool:
        """Check if API is available"""
        
        try:
            response = requests.get("http://reliquary-platform-service/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    async def _measure_consensus_latency(self) -> float:
        """Measure consensus operation latency"""
        # Simplified - would measure actual consensus operations
        return random.uniform(100, 500)
    
    async def _get_current_error_rate(self) -> float:
        """Get current system error rate"""
        # Simplified - would query actual metrics
        return random.uniform(0.001, 0.01)
    
    async def _is_system_recovered(self, experiment: ChaosExperiment) -> bool:
        """Check if system has recovered from chaos"""
        
        # Check pod count
        target_pods = self._get_target_pods(experiment)
        if len(target_pods) == 0:
            return False
        
        # Check API availability
        if not await self._check_api_availability():
            return False
        
        # Check response time
        response_time = await self._measure_api_response_time()
        if response_time > 2000:  # 2 seconds threshold
            return False
        
        return True
    
    async def _calculate_availability(self, result: Dict[str, Any]) -> float:
        """Calculate system availability during experiment"""
        
        observations = result.get("observations", [])
        if not observations:
            return 0.0
        
        available_count = sum(1 for obs in observations if obs.get("api_available", False))
        return available_count / len(observations)
    
    async def run_chaos_campaign(self, experiments: List[str] = None) -> Dict[str, Any]:
        """Run a campaign of chaos experiments"""
        
        target_experiments = experiments or [exp.name for exp in self.experiments]
        
        campaign_results = {
            "campaign_id": f"chaos_campaign_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "experiments": [],
            "summary": {}
        }
        
        for exp_name in target_experiments:
            experiment = next((exp for exp in self.experiments if exp.name == exp_name), None)
            if not experiment:
                continue
            
            result = await self.run_experiment(experiment)
            campaign_results["experiments"].append(result)
            
            # Wait between experiments
            await asyncio.sleep(60)
        
        # Generate summary
        total_experiments = len(campaign_results["experiments"])
        successful_experiments = sum(1 for exp in campaign_results["experiments"] if exp["success"])
        
        campaign_results["summary"] = {
            "total_experiments": total_experiments,
            "successful_experiments": successful_experiments,
            "success_rate": successful_experiments / total_experiments if total_experiments > 0 else 0,
            "overall_resilience_score": self._calculate_resilience_score(campaign_results["experiments"])
        }
        
        campaign_results["end_time"] = datetime.now().isoformat()
        
        return campaign_results
    
    def _calculate_resilience_score(self, experiments: List[Dict[str, Any]]) -> float:
        """Calculate overall system resilience score"""
        
        if not experiments:
            return 0.0
        
        scores = []
        for exp in experiments:
            if exp["success"]:
                recovery_metrics = exp.get("recovery_metrics", {})
                recovery_score = 1.0 if recovery_metrics.get("within_expected_time", False) else 0.5
                scores.append(recovery_score)
            else:
                scores.append(0.0)
        
        return sum(scores) / len(scores)


async def main():
    """Run chaos engineering campaign"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    chaos_framework = ChaosEngineeringFramework()
    
    # Run chaos campaign
    results = await chaos_framework.run_chaos_campaign([
        "platform_pod_failure",
        "consensus_agent_failure"
    ])
    
    print("🔥 Chaos Engineering Campaign Results:")
    print(f"📊 Success Rate: {results['summary']['success_rate']:.2%}")
    print(f"🛡️ Resilience Score: {results['summary']['overall_resilience_score']:.2f}")
    print(f"✅ Production Ready: {'YES' if results['summary']['success_rate'] > 0.8 else 'NO'}")


if __name__ == "__main__":
    asyncio.run(main())