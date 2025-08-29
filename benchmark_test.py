import requests
import time
import json
import statistics
import concurrent.futures
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np

# Configuration
BASE_URL = "http://localhost"
NUM_REQUESTS = 100
CONCURRENT_USERS = 10

def measure_response_time(url: str) -> Dict:
    """Measure response time for a single request"""
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        end_time = time.time()
        return {
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,  # Convert to milliseconds
            "success": response.status_code == 200
        }
    except Exception as e:
        end_time = time.time()
        return {
            "status_code": None,
            "response_time": (end_time - start_time) * 1000,
            "success": False,
            "error": str(e)
        }

def run_sequential_tests(endpoints: List[str]) -> Dict:
    """Run sequential tests on endpoints"""
    results = {}
    
    for endpoint in endpoints:
        print(f"Testing {endpoint}...")
        url = f"{BASE_URL}{endpoint}"
        endpoint_times = []
        successes = 0
        
        for i in range(NUM_REQUESTS):
            result = measure_response_time(url)
            endpoint_times.append(result["response_time"])
            if result["success"]:
                successes += 1
        
        results[endpoint] = {
            "times": endpoint_times,
            "avg_response_time": statistics.mean(endpoint_times),
            "min_response_time": min(endpoint_times),
            "max_response_time": max(endpoint_times),
            "success_rate": successes / NUM_REQUESTS * 100,
            "median_response_time": statistics.median(endpoint_times)
        }
    
    return results

def run_concurrent_tests(endpoints: List[str]) -> Dict:
    """Run concurrent tests on endpoints"""
    results = {}
    
    for endpoint in endpoints:
        print(f"Concurrent testing {endpoint}...")
        url = f"{BASE_URL}{endpoint}"
        endpoint_times = []
        successes = 0
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [executor.submit(measure_response_time, url) for _ in range(NUM_REQUESTS)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                endpoint_times.append(result["response_time"])
                if result["success"]:
                    successes += 1
        
        results[endpoint] = {
            "times": endpoint_times,
            "avg_response_time": statistics.mean(endpoint_times),
            "min_response_time": min(endpoint_times),
            "max_response_time": max(endpoint_times),
            "success_rate": successes / NUM_REQUESTS * 100,
            "median_response_time": statistics.median(endpoint_times)
        }
    
    return results

def create_performance_graphs(results: Dict, test_type: str):
    """Create performance graphs"""
    endpoints = list(results.keys())
    
    # Response time comparison
    avg_times = [results[ep]["avg_response_time"] for ep in endpoints]
    min_times = [results[ep]["min_response_time"] for ep in endpoints]
    max_times = [results[ep]["max_response_time"] for ep in endpoints]
    
    x = np.arange(len(endpoints))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, min_times, width, label='Min Time', alpha=0.7)
    ax.bar(x, avg_times, width, label='Avg Time', alpha=0.7)
    ax.bar(x + width, max_times, width, label='Max Time', alpha=0.7)
    
    ax.set_xlabel('Endpoints')
    ax.set_ylabel('Response Time (ms)')
    ax.set_title(f'{test_type} Response Times by Endpoint')
    ax.set_xticks(x)
    ax.set_xticklabels(endpoints, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f'{test_type.lower()}_response_times.png')
    plt.close()
    
    # Success rate comparison
    success_rates = [results[ep]["success_rate"] for ep in endpoints]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(endpoints, success_rates, color='green', alpha=0.7)
    
    ax.set_xlabel('Endpoints')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title(f'{test_type} Success Rates by Endpoint')
    ax.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%', ha='center', va='bottom')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{test_type.lower()}_success_rates.png')
    plt.close()

def create_comparison_graphs(sequential_results: Dict, concurrent_results: Dict):
    """Create comparison graphs between sequential and concurrent tests"""
    endpoints = list(sequential_results.keys())
    
    # Response time comparison
    seq_avg_times = [sequential_results[ep]["avg_response_time"] for ep in endpoints]
    conc_avg_times = [concurrent_results[ep]["avg_response_time"] for ep in endpoints]
    
    x = np.arange(len(endpoints))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, seq_avg_times, width, label='Sequential', alpha=0.7)
    ax.bar(x + width/2, conc_avg_times, width, label='Concurrent', alpha=0.7)
    
    ax.set_xlabel('Endpoints')
    ax.set_ylabel('Average Response Time (ms)')
    ax.set_title('Sequential vs Concurrent Response Times')
    ax.set_xticks(x)
    ax.set_xticklabels(endpoints, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('sequential_vs_concurrent_comparison.png')
    plt.close()

def save_results_to_json(results: Dict, filename: str):
    """Save results to JSON file"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    # Endpoints to test
    endpoints = [
        "/health",
        "/auth/health",
        "/zk/system-status",
        "/version"
    ]
    
    print("Running sequential tests...")
    sequential_results = run_sequential_tests(endpoints)
    
    print("Running concurrent tests...")
    concurrent_results = run_concurrent_tests(endpoints)
    
    # Save results
    save_results_to_json(sequential_results, "sequential_benchmark_results.json")
    save_results_to_json(concurrent_results, "concurrent_benchmark_results.json")
    
    # Create graphs
    create_performance_graphs(sequential_results, "Sequential")
    create_performance_graphs(concurrent_results, "Concurrent")
    create_comparison_graphs(sequential_results, concurrent_results)
    
    # Print summary
    print("\n=== BENCHMARK RESULTS SUMMARY ===")
    print("\nSequential Tests:")
    for endpoint, data in sequential_results.items():
        print(f"  {endpoint}:")
        print(f"    Avg Response Time: {data['avg_response_time']:.2f} ms")
        print(f"    Success Rate: {data['success_rate']:.1f}%")
    
    print("\nConcurrent Tests:")
    for endpoint, data in concurrent_results.items():
        print(f"  {endpoint}:")
        print(f"    Avg Response Time: {data['avg_response_time']:.2f} ms")
        print(f"    Success Rate: {data['success_rate']:.1f}%")

if __name__ == "__main__":
    main()