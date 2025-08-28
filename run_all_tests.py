#!/usr/bin/env python3
"""
Script to run all major tests for the ReliQuary project.
This provides a comprehensive validation of the system functionality.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test_script(script_name, description):
    """Run a test script and return the result."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            print(result.stdout[-1000:])  # Show last 1000 chars of output
            return True
        else:
            print("❌ FAILED")
            print(result.stderr[-1000:])  # Show last 1000 chars of error
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Test took too long to complete")
        return False
    except Exception as e:
        print(f"💥 ERROR - {e}")
        return False

def main():
    """Run all major tests and report results."""
    print("🚀 ReliQuary Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List of test scripts to run in order
    test_scripts = [
        ("test_agents.py", "Multi-Agent System Tests"),
        ("test_zk_comprehensive.py", "Zero-Knowledge Proof System Tests"),
        ("test_trust_engine.py", "Trust Scoring Engine Tests"),
        ("test_context_manager.py", "Context Verification Manager Tests"),
    ]
    
    results = []
    
    # Run each test script
    for script_name, description in test_scripts:
        success = run_test_script(script_name, description)
        results.append((description, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! The system is functioning correctly.")
        print("✅ ReliQuary is ready for production deployment.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()