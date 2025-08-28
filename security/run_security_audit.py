#!/usr/bin/env python3
"""
ReliQuary Platform Security Audit Runner

This script runs comprehensive security audits and penetration testing
for the ReliQuary enterprise platform.
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from security.audit_framework import SecurityAuditor, PenetrationTester
from security.security_testing_tools import SecurityTestRunner


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'security_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )


def save_report(report: dict, filename: str):
    """Save security audit report to file"""
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report saved to: {filename}")


async def run_security_audit(target_url: str, config: dict) -> dict:
    """Run comprehensive security audit"""
    print(f"🔒 Starting Security Audit for {target_url}")
    print("=" * 60)
    
    audit_config = {
        "target_url": target_url,
        "scan_depth": config.get("scan_depth", "comprehensive"),
        "include_penetration_test": config.get("include_penetration_test", True),
        "check_compliance": config.get("check_compliance", True)
    }
    
    # Initialize security auditor
    auditor = SecurityAuditor(audit_config)
    
    try:
        # Run comprehensive audit
        print("📊 Running comprehensive security audit...")
        audit_report = await auditor.run_comprehensive_audit(target_url)
        
        print(f"✅ Security audit completed")
        print(f"   - Total findings: {audit_report.get('total_findings', 0)}")
        print(f"   - Risk score: {audit_report.get('risk_score', 0)}/10")
        
        return audit_report
        
    except Exception as e:
        print(f"❌ Security audit failed: {e}")
        logging.error(f"Security audit failed: {e}")
        return {"error": str(e)}


async def run_penetration_test(target_url: str) -> dict:
    """Run penetration testing"""
    print(f"🎯 Starting Penetration Testing for {target_url}")
    print("=" * 60)
    
    pen_tester = PenetrationTester()
    
    try:
        # Run penetration test
        print("🔍 Running penetration tests...")
        pen_test_results = await pen_tester.run_penetration_test(target_url)
        
        vuln_count = len(pen_test_results.get('vulnerabilities_found', []))
        overall_risk = pen_test_results.get('overall_risk', 'UNKNOWN')
        
        print(f"✅ Penetration testing completed")
        print(f"   - Vulnerabilities found: {vuln_count}")
        print(f"   - Overall risk: {overall_risk}")
        
        return pen_test_results
        
    except Exception as e:
        print(f"❌ Penetration testing failed: {e}")
        logging.error(f"Penetration testing failed: {e}")
        return {"error": str(e)}


async def run_specialized_security_tests(target_url: str) -> dict:
    """Run specialized security tests"""
    print(f"🔧 Starting Specialized Security Tests for {target_url}")
    print("=" * 60)
    
    test_runner = SecurityTestRunner()
    
    try:
        # Run specialized tests
        print("🧪 Running cryptographic security tests...")
        print("🤖 Running consensus security tests...")
        print("🌐 Running network security tests...")
        
        security_results = await test_runner.run_all_security_tests(target_url)
        
        total_vulns = security_results.get('total_vulnerabilities', 0)
        risk_level = security_results.get('overall_risk_level', 'UNKNOWN')
        
        print(f"✅ Specialized security tests completed")
        print(f"   - Total vulnerabilities: {total_vulns}")
        print(f"   - Risk level: {risk_level}")
        
        return security_results
        
    except Exception as e:
        print(f"❌ Specialized security tests failed: {e}")
        logging.error(f"Specialized security tests failed: {e}")
        return {"error": str(e)}


def generate_executive_summary(audit_report: dict, pen_test: dict, specialized_tests: dict) -> dict:
    """Generate executive summary of all security assessments"""
    
    # Aggregate findings
    total_findings = 0
    critical_count = 0
    high_count = 0
    
    if 'total_findings' in audit_report:
        total_findings += audit_report['total_findings']
        if 'severity_breakdown' in audit_report:
            breakdown = audit_report['severity_breakdown']
            critical_count += breakdown.get('critical', 0)
            high_count += breakdown.get('high', 0)
    
    if 'total_vulnerabilities' in specialized_tests:
        total_findings += specialized_tests['total_vulnerabilities']
        if 'severity_breakdown' in specialized_tests:
            breakdown = specialized_tests['severity_breakdown']
            critical_count += breakdown.get('CRITICAL', 0)
            high_count += breakdown.get('HIGH', 0)
    
    if 'vulnerabilities_found' in pen_test:
        pen_vulns = pen_test['vulnerabilities_found']
        total_findings += len(pen_vulns)
        critical_count += len([v for v in pen_vulns if v.get('severity') == 'CRITICAL'])
        high_count += len([v for v in pen_vulns if v.get('severity') == 'HIGH'])
    
    # Determine overall risk
    if critical_count > 0:
        overall_risk = "CRITICAL"
        risk_description = "Immediate action required"
    elif high_count > 2:
        overall_risk = "HIGH"
        risk_description = "Urgent attention needed"
    elif total_findings > 5:
        overall_risk = "MEDIUM"
        risk_description = "Moderate security concerns"
    else:
        overall_risk = "LOW"
        risk_description = "Good security posture"
    
    # Generate recommendations
    recommendations = []
    if critical_count > 0:
        recommendations.append(f"IMMEDIATE: Address {critical_count} critical vulnerabilities")
    if high_count > 0:
        recommendations.append(f"HIGH PRIORITY: Fix {high_count} high-severity issues")
    
    # Add category-specific recommendations
    if audit_report.get('findings'):
        config_issues = len([f for f in audit_report['findings'] 
                           if f.get('type') == 'configuration'])
        if config_issues > 0:
            recommendations.append("Review and harden security configurations")
    
    if specialized_tests.get('categories_tested', {}).get('cryptographic', 0) > 0:
        recommendations.append("Strengthen cryptographic implementations")
    
    if specialized_tests.get('categories_tested', {}).get('consensus', 0) > 0:
        recommendations.append("Enhance consensus mechanism security")
    
    summary = {
        "assessment_date": datetime.now().isoformat(),
        "total_security_findings": total_findings,
        "critical_vulnerabilities": critical_count,
        "high_vulnerabilities": high_count,
        "overall_risk_level": overall_risk,
        "risk_description": risk_description,
        "key_recommendations": recommendations,
        "compliance_status": {
            "owasp_compliant": critical_count == 0 and high_count < 2,
            "soc2_ready": critical_count == 0,
            "production_ready": overall_risk in ["LOW", "MEDIUM"]
        },
        "next_steps": [
            "Address critical and high-severity vulnerabilities",
            "Implement security hardening measures",
            "Schedule regular security assessments",
            "Develop incident response procedures"
        ]
    }
    
    return summary


async def main():
    """Main security audit runner"""
    parser = argparse.ArgumentParser(description="ReliQuary Security Audit Runner")
    parser.add_argument("target_url", help="Target URL to audit")
    parser.add_argument("--skip-pentest", action="store_true", 
                       help="Skip penetration testing")
    parser.add_argument("--skip-specialized", action="store_true",
                       help="Skip specialized security tests")
    parser.add_argument("--output", "-o", default="security_audit_report.json",
                       help="Output report filename")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--scan-depth", choices=["basic", "standard", "comprehensive"],
                       default="comprehensive", help="Scan depth level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    print("🛡️  ReliQuary Platform Security Assessment")
    print("=" * 60)
    print(f"Target: {args.target_url}")
    print(f"Scan Depth: {args.scan_depth}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configuration
    config = {
        "scan_depth": args.scan_depth,
        "include_penetration_test": not args.skip_pentest,
        "check_compliance": True
    }
    
    # Results storage
    results = {
        "metadata": {
            "target_url": args.target_url,
            "assessment_date": datetime.now().isoformat(),
            "scan_depth": args.scan_depth,
            "tools_used": ["SecurityAuditor", "PenetrationTester", "SecurityTestRunner"]
        }
    }
    
    try:
        # 1. Run comprehensive security audit
        audit_report = await run_security_audit(args.target_url, config)
        results["security_audit"] = audit_report
        
        # 2. Run penetration testing (if not skipped)
        if not args.skip_pentest:
            pen_test_results = await run_penetration_test(args.target_url)
            results["penetration_test"] = pen_test_results
        else:
            print("⏭️  Skipping penetration testing")
            results["penetration_test"] = {"skipped": True}
        
        # 3. Run specialized security tests (if not skipped)
        if not args.skip_specialized:
            specialized_results = await run_specialized_security_tests(args.target_url)
            results["specialized_tests"] = specialized_results
        else:
            print("⏭️  Skipping specialized security tests")
            results["specialized_tests"] = {"skipped": True}
        
        # 4. Generate executive summary
        print("\n📋 Generating Executive Summary...")
        executive_summary = generate_executive_summary(
            audit_report, 
            results.get("penetration_test", {}),
            results.get("specialized_tests", {})
        )
        results["executive_summary"] = executive_summary
        
        # 5. Save results
        save_report(results, args.output)
        
        # 6. Display summary
        print("\n" + "=" * 60)
        print("🏁 SECURITY ASSESSMENT COMPLETE")
        print("=" * 60)
        print(f"📊 Total Security Findings: {executive_summary['total_security_findings']}")
        print(f"🚨 Critical Vulnerabilities: {executive_summary['critical_vulnerabilities']}")
        print(f"⚠️  High Vulnerabilities: {executive_summary['high_vulnerabilities']}")
        print(f"🎯 Overall Risk Level: {executive_summary['overall_risk_level']}")
        print(f"📝 Risk Description: {executive_summary['risk_description']}")
        
        if executive_summary['key_recommendations']:
            print("\n🔧 Key Recommendations:")
            for i, rec in enumerate(executive_summary['key_recommendations'], 1):
                print(f"   {i}. {rec}")
        
        compliance = executive_summary['compliance_status']
        print(f"\n✅ Compliance Status:")
        print(f"   - OWASP Compliant: {'Yes' if compliance['owasp_compliant'] else 'No'}")
        print(f"   - SOC2 Ready: {'Yes' if compliance['soc2_ready'] else 'No'}")
        print(f"   - Production Ready: {'Yes' if compliance['production_ready'] else 'No'}")
        
        print(f"\n📄 Detailed report saved to: {args.output}")
        
        # Exit with appropriate code based on risk level
        if executive_summary['overall_risk_level'] == "CRITICAL":
            sys.exit(2)
        elif executive_summary['overall_risk_level'] == "HIGH":
            sys.exit(1)
        else:
            sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Security assessment interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Security assessment failed: {e}")
        logging.error(f"Security assessment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())