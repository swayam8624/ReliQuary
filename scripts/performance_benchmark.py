#!/usr/bin/env python3
"""
Performance Benchmarking Suite for ReliQuary Platform
Comprehensive performance testing for production readiness validation
"""

import asyncio
import json
import time
import statistics
import concurrent.futures
from typing import Dict, List, Any
import psutil
import requests
import logging
from dataclasses import dataclass
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crypto.rust_ffi_wrappers import encrypt_data_rust, decrypt_data_rust
from agents.orchestrator import DecisionOrchestrator, DecisionType
from core.merkle_logging.merkle import MerkleLogWriter


@dataclass
class BenchmarkResult:
    """Container for benchmark results"""
    test_name: str
    total_operations: int
    total_time: float
    ops_per_second: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    errors: List[str]


class PerformanceBenchmarker:
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.logger = logging.getLogger("benchmark")
        
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark suite"""
        self.logger.info("Starting ReliQuary performance benchmarks")
        
        # System benchmarks
        crypto_result = await self._benchmark_cryptographic_operations()
        consensus_result = await self._benchmark_consensus_system()
        merkle_result = await self._benchmark_merkle_operations()
        api_result = await self._benchmark_api_endpoints()
        concurrent_result = await self._benchmark_concurrent_load()
        
        self.results.extend([
            crypto_result,
            consensus_result, 
            merkle_result,
            api_result,
            concurrent_result
        ])
        
        return self._generate_benchmark_report()
    
    async def _benchmark_cryptographic_operations(self) -> BenchmarkResult:
        """Benchmark cryptographic operations performance"""
        self.logger.info("Benchmarking cryptographic operations")
        
        operations = 1000
        test_data = b"Performance test data for ReliQuary cryptographic benchmarking"
        test_key = os.urandom(32)
        
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()
        latencies = []
        errors = []
        
        for i in range(operations):
            op_start = time.time()
            try:
                # Encrypt
                ciphertext, nonce = encrypt_data_rust(test_data, test_key)
                
                # Decrypt
                decrypted = decrypt_data_rust(ciphertext, nonce, test_key)
                
                if decrypted != test_data:
                    errors.append(f"Decryption mismatch at operation {i}")
                    
                latencies.append((time.time() - op_start) * 1000)
                
            except Exception as e:
                errors.append(f"Crypto operation {i} failed: {str(e)}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_time = end_time - start_time
        success_rate = (operations - len(errors)) / operations * 100
        
        return BenchmarkResult(
            test_name="Cryptographic Operations",
            total_operations=operations,
            total_time=total_time,
            ops_per_second=operations / total_time,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if latencies else 0,
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if latencies else 0,
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            success_rate=success_rate,
            errors=errors[:10]  # First 10 errors only
        )
    
    async def _benchmark_consensus_system(self) -> BenchmarkResult:
        """Benchmark multi-agent consensus system performance"""
        self.logger.info("Benchmarking consensus system")
        
        operations = 100
        agent_network = ["neutral_agent", "permissive_agent", "strict_agent", "watchdog_agent"]
        
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()
        latencies = []
        errors = []
        
        orchestrator = DecisionOrchestrator("benchmark_orchestrator", agent_network)
        
        for i in range(operations):
            op_start = time.time()
            try:
                context_data = {
                    "user_id": f"benchmark_user_{i}",
                    "resource_id": f"resource_{i}",
                    "action": "read"
                }
                
                result = await orchestrator.orchestrate_decision(
                    decision_type=DecisionType.ACCESS_REQUEST,
                    requestor_id=f"benchmark_user_{i}",
                    context_data=context_data,
                    timeout_seconds=10.0
                )
                
                latencies.append((time.time() - op_start) * 1000)
                
            except Exception as e:
                errors.append(f"Consensus operation {i} failed: {str(e)}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_time = end_time - start_time
        success_rate = (operations - len(errors)) / operations * 100
        
        return BenchmarkResult(
            test_name="Consensus System",
            total_operations=operations,
            total_time=total_time,
            ops_per_second=operations / total_time,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if latencies else 0,
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if latencies else 0,
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            success_rate=success_rate,
            errors=errors[:10]
        )
    
    async def _benchmark_merkle_operations(self) -> BenchmarkResult:
        """Benchmark Merkle tree operations performance"""
        self.logger.info("Benchmarking Merkle operations")
        
        operations = 500
        merkle_writer = MerkleLogWriter("benchmark_merkle.log")
        
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()
        latencies = []
        errors = []
        
        for i in range(operations):
            op_start = time.time()
            try:
                log_entry = {
                    "timestamp": time.time(),
                    "action": "benchmark_operation",
                    "data": f"Benchmark entry {i}",
                    "user_id": f"benchmark_user_{i}"
                }
                
                merkle_writer.log_entry(log_entry)
                latencies.append((time.time() - op_start) * 1000)
                
            except Exception as e:
                errors.append(f"Merkle operation {i} failed: {str(e)}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_time = end_time - start_time
        success_rate = (operations - len(errors)) / operations * 100
        
        # Cleanup
        if os.path.exists("benchmark_merkle.log"):
            os.remove("benchmark_merkle.log")
        
        return BenchmarkResult(
            test_name="Merkle Operations",
            total_operations=operations,
            total_time=total_time,
            ops_per_second=operations / total_time,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if latencies else 0,
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if latencies else 0,
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            success_rate=success_rate,
            errors=errors[:10]
        )
    
    async def _benchmark_api_endpoints(self) -> BenchmarkResult:
        """Benchmark API endpoint performance"""
        self.logger.info("Benchmarking API endpoints")
        
        operations = 200
        endpoints = [
            "/health",
            "/status",
            "/version",
            "/observability/health"
        ]
        
        start_time = time.time()
        latencies = []
        errors = []
        
        for i in range(operations):
            endpoint = endpoints[i % len(endpoints)]
            op_start = time.time()
            
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    latencies.append((time.time() - op_start) * 1000)
                else:
                    errors.append(f"API call {i} returned {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                errors.append(f"API call {i} failed: {str(e)}")
        
        end_time = time.time()
        
        total_time = end_time - start_time
        success_rate = (operations - len(errors)) / operations * 100
        
        return BenchmarkResult(
            test_name="API Endpoints",
            total_operations=operations,
            total_time=total_time,
            ops_per_second=operations / total_time,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if latencies else 0,
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if latencies else 0,
            memory_usage_mb=0,  # Not measured for API calls
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            success_rate=success_rate,
            errors=errors[:10]
        )
    
    async def _benchmark_concurrent_load(self) -> BenchmarkResult:
        """Benchmark system under concurrent load"""
        self.logger.info("Benchmarking concurrent load")
        
        operations = 500
        concurrent_users = 50
        
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        async def concurrent_operation(user_id: int):
            """Single concurrent operation"""
            try:
                # Simulate mixed workload
                test_data = f"User {user_id} concurrent test data".encode()
                test_key = os.urandom(32)
                
                # Crypto operation
                ciphertext, nonce = encrypt_data_rust(test_data, test_key)
                decrypted = decrypt_data_rust(ciphertext, nonce, test_key)
                
                # API call
                response = requests.get(f"{self.base_url}/health", timeout=2)
                
                return response.status_code == 200 and decrypted == test_data
                
            except Exception:
                return False
        
        # Execute concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(asyncio.run, concurrent_operation(i))
                for i in range(operations)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_time = end_time - start_time
        successful_operations = sum(results)
        success_rate = successful_operations / operations * 100
        
        return BenchmarkResult(
            test_name="Concurrent Load",
            total_operations=operations,
            total_time=total_time,
            ops_per_second=operations / total_time,
            avg_latency_ms=(total_time / operations) * 1000,
            p95_latency_ms=0,  # Not measured in concurrent test
            p99_latency_ms=0,  # Not measured in concurrent test
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            success_rate=success_rate,
            errors=[]
        )
    
    def _generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        
        total_operations = sum(r.total_operations for r in self.results)
        avg_success_rate = statistics.mean([r.success_rate for r in self.results])
        
        report = {
            "benchmark_id": f"benchmark_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "platform": os.uname().sysname if hasattr(os, 'uname') else 'Unknown'
            },
            "summary": {
                "total_operations": total_operations,
                "overall_success_rate": avg_success_rate,
                "performance_grade": self._calculate_performance_grade(avg_success_rate),
                "production_ready": avg_success_rate >= 99.0
            },
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "ops_per_second": r.ops_per_second,
                    "avg_latency_ms": r.avg_latency_ms,
                    "p95_latency_ms": r.p95_latency_ms,
                    "success_rate": r.success_rate,
                    "memory_usage_mb": r.memory_usage_mb,
                    "errors": r.errors
                }
                for r in self.results
            ]
        }
        
        return report
    
    def _calculate_performance_grade(self, success_rate: float) -> str:
        """Calculate performance grade based on metrics"""
        if success_rate >= 99.5:
            return "A+"
        elif success_rate >= 99.0:
            return "A"
        elif success_rate >= 95.0:
            return "B"
        elif success_rate >= 90.0:
            return "C"
        else:
            return "F"


async def main():
    """Main benchmark execution"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create results directory
    os.makedirs("performance-results", exist_ok=True)
    
    # Run benchmarks
    benchmarker = PerformanceBenchmarker()
    report = await benchmarker.run_all_benchmarks()
    
    # Save results
    with open("performance-results/benchmark-report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("RELIQUARY PERFORMANCE BENCHMARK RESULTS")
    print("="*60)
    print(f"Total Operations: {report['summary']['total_operations']}")
    print(f"Overall Success Rate: {report['summary']['overall_success_rate']:.2f}%")
    print(f"Performance Grade: {report['summary']['performance_grade']}")
    print(f"Production Ready: {'✅ YES' if report['summary']['production_ready'] else '❌ NO'}")
    print("\nDetailed Results:")
    
    for result in report['detailed_results']:
        print(f"  {result['test_name']}:")
        print(f"    • {result['ops_per_second']:.1f} ops/sec")
        print(f"    • {result['avg_latency_ms']:.2f}ms avg latency")
        print(f"    • {result['success_rate']:.1f}% success rate")
    
    print("="*60)
    
    # Exit with appropriate code
    if report['summary']['production_ready']:
        print("🎉 System is PRODUCTION READY!")
        sys.exit(0)
    else:
        print("⚠️  System needs performance optimization before production")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())