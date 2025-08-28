#!/usr/bin/env python3
"""
Basic health check script for API endpoint.
This script performs a basic health check of the ReliQuary API endpoint.
"""

import argparse
import requests
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime


def check_api_health(base_url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check the health of the API endpoint.
    
    Args:
        base_url: Base URL of the API
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing health check results
    """
    health_url = f"{base_url.rstrip('/')}/health"
    
    start_time = time.time()
    
    try:
        response = requests.get(health_url, timeout=timeout)
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "details": response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        }
    except requests.exceptions.RequestException as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy",
            "status_code": None,
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


def check_service_status(base_url: str, service: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check the status of a specific service.
    
    Args:
        base_url: Base URL of the API
        service: Service to check (e.g., 'database', 'cache', 'storage')
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing service status
    """
    status_url = f"{base_url.rstrip('/')}/status/{service}"
    
    try:
        response = requests.get(status_url, timeout=timeout)
        return {
            "service": service,
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "status_code": response.status_code,
            "details": response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        }
    except requests.exceptions.RequestException as e:
        return {
            "service": service,
            "status": "unhealthy",
            "status_code": None,
            "error": str(e)
        }


def format_health_report(health_result: Dict[str, Any]) -> str:
    """
    Format the health check result as a human-readable report.
    
    Args:
        health_result: Health check result dictionary
        
    Returns:
        Formatted health report string
    """
    report = []
    report.append("=" * 50)
    report.append("RELIQUARY API HEALTH CHECK REPORT")
    report.append("=" * 50)
    report.append(f"Timestamp: {health_result['timestamp']}")
    report.append(f"Status: {health_result['status'].upper()}")
    report.append(f"Response Time: {health_result['response_time_ms']} ms")
    
    if health_result['status_code']:
        report.append(f"Status Code: {health_result['status_code']}")
    
    if 'error' in health_result:
        report.append(f"Error: {health_result['error']}")
    
    if 'details' in health_result and health_result['details']:
        report.append("\nDetails:")
        for key, value in health_result['details'].items():
            report.append(f"  {key}: {value}")
    
    report.append("=" * 50)
    return "\n".join(report)


def main():
    """Main function for the health check script"""
    parser = argparse.ArgumentParser(description="Perform health check of ReliQuary API")
    parser.add_argument("-u", "--url", default="http://localhost:8000", help="Base URL of the API (default: http://localhost:8000)")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("-s", "--service", help="Check specific service status")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Output file for results")
    
    args = parser.parse_args()
    
    if args.service:
        # Check specific service
        result = check_service_status(args.url, args.service, args.timeout)
        print(f"Service '{args.service}' is {result['status']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        elif args.verbose and 'details' in result:
            print("Details:")
            for key, value in result['details'].items():
                print(f"  {key}: {value}")
    else:
        # Perform general health check
        result = check_api_health(args.url, args.timeout)
        
        if args.verbose:
            print(format_health_report(result))
        else:
            status = result['status'].upper()
            response_time = result['response_time_ms']
            print(f"API Status: {status} ({response_time} ms)")
        
        # Save to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
        
        # Exit with error code if unhealthy
        if result['status'] != 'healthy':
            sys.exit(1)


if __name__ == "__main__":
    main()