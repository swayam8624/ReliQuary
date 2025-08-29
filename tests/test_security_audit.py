"""
Comprehensive Security Test Suite for ReliQuary Platform

This module provides comprehensive security tests covering all aspects
of the ReliQuary enterprise platform including authentication, consensus,
cryptography, and infrastructure security.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/Users/swayamsingal/Desktop/Programming/ReliQuary')

from security.audit_framework import SecurityAuditor, SecurityFinding, SeverityLevel, VulnerabilityType
from security.security_testing_tools import SecurityTestRunner, CryptographicSecurityTester, ConsensusSecurityTester


class TestSecurityAuditFramework:
    """Test suite for security audit framework"""
    
    @pytest.fixture
    def security_auditor(self):
        """Create security auditor for testing"""
        config = {
            "target_url": "https://test.reliquary.io",
            "scan_depth": "comprehensive"
        }
        return SecurityAuditor(config)
    
    @pytest.mark.asyncio
    async def test_security_audit_initialization(self, security_auditor):
        """Test security auditor initialization"""
        assert security_auditor.config["target_url"] == "https://test.reliquary.io"
        assert security_auditor.findings == []
        assert security_auditor.audit_id is None
    
    @pytest.mark.asyncio
    async def test_add_security_finding(self, security_auditor):
        """Test adding security findings"""
        # Add a test finding
        security_auditor._add_finding(
            title="Test Vulnerability",
            description="Test vulnerability description",
            severity=SeverityLevel.HIGH,
            vuln_type=VulnerabilityType.AUTHENTICATION,
            component="Test Component",
            location="https://test.reliquary.io/test",
            evidence={"test": "data"}
        )
        
        assert len(security_auditor.findings) == 1
        finding = security_auditor.findings[0]
        assert finding.title == "Test Vulnerability"
        assert finding.severity == SeverityLevel.HIGH
        assert finding.vulnerability_type == VulnerabilityType.AUTHENTICATION
    
    @pytest.mark.asyncio
    async def test_web_security_scan(self, security_auditor):
        """Test web security scanning"""
        with patch('requests.get') as mock_get:
            # Mock response with missing security headers
            mock_response = MagicMock()
            mock_response.headers = {
                'server': 'nginx/1.18.0',
                'x-powered-by': 'PHP/8.1.0'
            }
            mock_get.return_value = mock_response
            
            await security_auditor._web_security_scan("https://test.reliquary.io")
            
            # Should find missing security headers and information disclosure
            findings = security_auditor.findings
            assert len(findings) > 0
            
            # Check for missing security header findings
            missing_header_findings = [f for f in findings if "Missing Security Header" in f.title]
            assert len(missing_header_findings) > 0
            
            # Check for information disclosure findings
            disclosure_findings = [f for f in findings if "Information Disclosure" in f.title]
            assert len(disclosure_findings) > 0
    
    @pytest.mark.asyncio
    async def test_api_security_test(self, security_auditor):
        """Test API security testing"""
        with patch('requests.post') as mock_post:
            # Mock SQL injection response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "SQL syntax error near 'OR'"
            mock_post.return_value = mock_response
            
            await security_auditor._api_security_test("https://test.reliquary.io")
            
            # Should detect SQL injection vulnerability
            sql_findings = [f for f in security_auditor.findings 
                           if f.vulnerability_type == VulnerabilityType.INJECTION]
            assert len(sql_findings) > 0
            assert any("SQL Injection" in f.title for f in sql_findings)
    
    @pytest.mark.asyncio
    async def test_authentication_test(self, security_auditor):
        """Test authentication security testing"""
        with patch('requests.get') as mock_get:
            # Mock unprotected admin endpoint
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Admin Dashboard - Welcome"
            mock_get.return_value = mock_response
            
            await security_auditor._authentication_test("https://test.reliquary.io")
            
            # Should detect unprotected admin endpoints
            auth_findings = [f for f in security_auditor.findings 
                           if f.vulnerability_type == VulnerabilityType.AUTHORIZATION]
            assert len(auth_findings) > 0
            assert any("Unprotected Administrative Endpoint" in f.title for f in auth_findings)
    
    @pytest.mark.asyncio
    async def test_compliance_checking(self, security_auditor):
        """Test compliance checking functionality"""
        # Add some test findings to affect compliance
        security_auditor._add_finding(
            title="SQL Injection",
            description="SQL injection vulnerability",
            severity=SeverityLevel.CRITICAL,
            vuln_type=VulnerabilityType.INJECTION,
            component="API",
            location="test",
            evidence={}
        )
        
        await security_auditor._compliance_check()
        
        # Should detect compliance issues
        compliance_findings = [f for f in security_auditor.findings 
                             if f.vulnerability_type == VulnerabilityType.COMPLIANCE]
        assert len(compliance_findings) > 0
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, security_auditor):
        """Test risk score calculation"""
        # Add findings of different severities
        security_auditor._add_finding("Critical", "desc", SeverityLevel.CRITICAL, 
                                    VulnerabilityType.INJECTION, "comp", "loc", {})
        security_auditor._add_finding("High", "desc", SeverityLevel.HIGH, 
                                    VulnerabilityType.AUTHENTICATION, "comp", "loc", {})
        security_auditor._add_finding("Medium", "desc", SeverityLevel.MEDIUM, 
                                    VulnerabilityType.CONFIGURATION, "comp", "loc", {})
        
        risk_score = security_auditor._calculate_risk_score()
        
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 10.0
        assert risk_score > 5.0  # Should be high due to critical finding
    
    @pytest.mark.asyncio
    async def test_generate_report(self, security_auditor):
        """Test audit report generation"""
        # Add some test findings
        security_auditor._add_finding("Test Finding", "description", SeverityLevel.MEDIUM,
                                    VulnerabilityType.CONFIGURATION, "component", "location", {})
        
        report = security_auditor._generate_report("https://test.reliquary.io")
        
        assert "report_id" in report
        assert "target_system" in report
        assert "total_findings" in report
        assert "severity_breakdown" in report
        assert "findings" in report
        assert "recommendations" in report
        assert "compliance_status" in report
        
        assert report["total_findings"] == 1
        assert report["target_system"] == "https://test.reliquary.io"


class TestCryptographicSecurityTester:
    """Test suite for cryptographic security testing"""
    
    @pytest.fixture
    def crypto_tester(self):
        """Create cryptographic security tester"""
        return CryptographicSecurityTester()
    
    @pytest.mark.asyncio
    async def test_random_number_generation_test(self, crypto_tester):
        """Test random number generation testing"""
        print("Starting random number generation test")
        with patch('security.security_testing_tools.requests.get') as mock_get:
            # Mock predictable random values - provide enough for 100 requests
            mock_responses = []
            for i in range(100):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"random_value": str(i % 10)}  # Sequential values 0-9 repeating
                mock_responses.append(mock_response)
                print(f"Created mock response {i}: {mock_response.json.return_value}")
            
            mock_get.side_effect = mock_responses
            print(f"Set mock_get.side_effect with {len(mock_responses)} responses")
            
            await crypto_tester._test_random_number_generation("https://test.reliquary.io")
            print(f"Test completed, vulnerabilities: {crypto_tester.vulnerabilities}")
            
            # Should detect weak random number generation
            weak_random_findings = [v for v in crypto_tester.vulnerabilities 
                                  if v["type"] == "weak_random_generation"]
            print(f"Weak random findings: {weak_random_findings}")
            assert len(weak_random_findings) > 0
    
    @pytest.mark.asyncio
    async def test_encryption_strength_test(self, crypto_tester):
        """Test encryption strength testing"""
        with patch('requests.post') as mock_post:
            # Mock ECB mode detection (same plaintext -> same ciphertext)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "encrypted_data": "1234567890abcdef" * 4  # Repeated pattern
            }
            mock_post.return_value = mock_response
            
            await crypto_tester._test_encryption_strength("https://test.reliquary.io")
            
            # Should detect weak encryption mode
            weak_encryption_findings = [v for v in crypto_tester.vulnerabilities 
                                      if v["type"] == "weak_encryption_mode"]
            assert len(weak_encryption_findings) > 0
    
    @pytest.mark.asyncio
    async def test_signature_verification_test(self, crypto_tester):
        """Test signature verification testing"""
        with patch('requests.post') as mock_post:
            # Mock signature verification bypass
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"verified": True}
            mock_post.return_value = mock_response
            
            await crypto_tester._test_signature_verification("https://test.reliquary.io")
            
            # Should detect signature verification bypass
            bypass_findings = [v for v in crypto_tester.vulnerabilities 
                             if v["type"] == "signature_verification_bypass"]
            assert len(bypass_findings) > 0
    
    def test_pattern_detection(self, crypto_tester):
        """Test pattern detection in random values"""
        # Test sequential pattern
        sequential_values = [str(i) for i in range(10)]
        assert crypto_tester._detect_patterns(sequential_values) == True
        
        # Test random pattern
        random_values = ["abc", "xyz", "123", "def"]
        assert crypto_tester._detect_patterns(random_values) == False
    
    def test_ecb_mode_detection(self, crypto_tester):
        """Test ECB mode detection"""
        # Test with repeated blocks (ECB mode) - same 32-character block repeated
        ecb_ciphertext = ["abcd1234efgh5678ijkl9012mnop3456abcd1234efgh5678ijkl9012mnop3456"]
        assert crypto_tester._detect_ecb_mode(ecb_ciphertext) == True
        
        # Test with unique blocks (CBC/GCM mode)
        cbc_ciphertext = ["abcd1234efgh5678ijkl9012mnop3456"]
        assert crypto_tester._detect_ecb_mode(cbc_ciphertext) == False


class TestConsensusSecurityTester:
    """Test suite for consensus security testing"""
    
    @pytest.fixture
    def consensus_tester(self):
        """Create consensus security tester"""
        return ConsensusSecurityTester()
    
    @pytest.mark.asyncio
    async def test_byzantine_resistance_test(self, consensus_tester):
        """Test Byzantine resistance testing"""
        with patch('requests.post') as mock_post:
            # Mock weak Byzantine resistance (grants too many malicious requests)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"decision": "GRANT"}
            mock_post.return_value = mock_response
            
            await consensus_tester._test_byzantine_resistance("https://test.reliquary.io")
            
            # Should detect weak Byzantine resistance
            byzantine_findings = [v for v in consensus_tester.vulnerabilities 
                                if v["type"] == "weak_byzantine_resistance"]
            assert len(byzantine_findings) > 0
    
    @pytest.mark.asyncio
    async def test_agent_authentication_test(self, consensus_tester):
        """Test agent authentication testing"""
        with patch('requests.post') as mock_post:
            # Mock successful malicious agent registration
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            await consensus_tester._test_agent_authentication("https://test.reliquary.io")
            
            # Should detect agent authentication bypass
            auth_bypass_findings = [v for v in consensus_tester.vulnerabilities 
                                  if v["type"] == "agent_authentication_bypass"]
            assert len(auth_bypass_findings) > 0
    
    @pytest.mark.asyncio
    async def test_consensus_manipulation_test(self, consensus_tester):
        """Test consensus manipulation testing"""
        with patch('requests.post') as mock_post:
            # Mock inconsistent consensus decisions (5 responses to match implementation)
            responses = [
                MagicMock(status_code=200, json=lambda: {"decision": "GRANT"}),
                MagicMock(status_code=200, json=lambda: {"decision": "DENY"}),
                MagicMock(status_code=200, json=lambda: {"decision": "GRANT"}),
                MagicMock(status_code=200, json=lambda: {"decision": "DENY"}),
                MagicMock(status_code=200, json=lambda: {"decision": "GRANT"})
            ]
            mock_post.side_effect = responses
            
            await consensus_tester._test_consensus_manipulation("https://test.reliquary.io")
            
            # Should detect consensus inconsistency
            inconsistency_findings = [v for v in consensus_tester.vulnerabilities 
                                    if v["type"] == "consensus_inconsistency"]
            assert len(inconsistency_findings) > 0
    
    @pytest.mark.asyncio
    async def test_decision_integrity_test(self, consensus_tester):
        """Test decision integrity testing"""
        with patch('requests.post') as mock_post:
            # Mock decision without integrity protection
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "decision": "GRANT",
                "timestamp": int(time.time())
                # Missing signature/hash/checksum
            }
            mock_post.return_value = mock_response
            
            await consensus_tester._test_decision_integrity("https://test.reliquary.io")
            
            # Should detect unprotected decision integrity
            integrity_findings = [v for v in consensus_tester.vulnerabilities 
                                if v["type"] == "unprotected_decision_integrity"]
            assert len(integrity_findings) > 0


class TestSecurityTestRunner:
    """Test suite for security test runner"""
    
    @pytest.fixture
    def test_runner(self):
        """Create security test runner"""
        return SecurityTestRunner()
    
    @pytest.mark.asyncio
    async def test_comprehensive_security_test(self, test_runner):
        """Test comprehensive security testing"""
        with patch.multiple(
            'security.security_testing_tools',
            CryptographicSecurityTester=MagicMock(),
            ConsensusSecurityTester=MagicMock(),
            NetworkSecurityTester=MagicMock()
        ):
            # Mock individual tester results to return coroutines
            async def mock_crypto_test(*args, **kwargs):
                return [{"type": "weak_crypto", "severity": "HIGH"}]
            
            async def mock_consensus_test(*args, **kwargs):
                return [{"type": "consensus_bypass", "severity": "CRITICAL"}]
            
            async def mock_network_test(*args, **kwargs):
                return [{"type": "exposed_service", "severity": "MEDIUM"}]
            
            test_runner.crypto_tester.test_cryptographic_security = mock_crypto_test
            test_runner.consensus_tester.test_consensus_security = mock_consensus_test
            test_runner.network_tester.test_network_security = mock_network_test
            
            report = await test_runner.run_all_security_tests("https://test.reliquary.io")
            
            assert "test_id" in report
            assert "target" in report
            assert "total_vulnerabilities" in report
            assert "categories_tested" in report
            assert "severity_breakdown" in report
            assert "overall_risk_level" in report
            
            assert report["total_vulnerabilities"] == 3
            assert report["target"] == "https://test.reliquary.io"
    
    def test_severity_breakdown_calculation(self, test_runner):
        """Test severity breakdown calculation"""
        vulnerabilities = [
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"},
            {"severity": "LOW"}
        ]
        
        breakdown = test_runner._calculate_severity_breakdown(vulnerabilities)
        
        assert breakdown["CRITICAL"] == 1
        assert breakdown["HIGH"] == 2
        assert breakdown["MEDIUM"] == 1
        assert breakdown["LOW"] == 1
    
    def test_overall_risk_calculation(self, test_runner):
        """Test overall risk calculation"""
        # Test critical risk
        critical_vulns = [{"severity": "CRITICAL"}]
        assert test_runner._calculate_overall_risk(critical_vulns) == "CRITICAL"
        
        # Test high risk
        high_vulns = [{"severity": "HIGH"}] * 3
        assert test_runner._calculate_overall_risk(high_vulns) == "HIGH"
        
        # Test medium risk
        medium_vulns = [{"severity": "MEDIUM"}] * 6
        assert test_runner._calculate_overall_risk(medium_vulns) == "MEDIUM"
        
        # Test low risk
        low_vulns = [{"severity": "LOW"}] * 2
        assert test_runner._calculate_overall_risk(low_vulns) == "LOW"
    
    def test_recommendations_generation(self, test_runner):
        """Test recommendations generation"""
        vulnerabilities = [
            {"severity": "CRITICAL", "type": "crypto_weakness"},
            {"severity": "HIGH", "type": "consensus_bypass"},
            {"severity": "MEDIUM", "type": "network_exposure"}
        ]
        
        recommendations = test_runner._generate_recommendations(vulnerabilities)
        
        assert any("IMMEDIATE" in rec for rec in recommendations)
        assert any("HIGH PRIORITY" in rec for rec in recommendations)
        assert any("cryptographic" in rec for rec in recommendations)
        assert any("consensus" in rec for rec in recommendations)


class TestIntegrationSecurityTests:
    """Integration tests for security testing components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_security_audit(self):
        """Test end-to-end security audit workflow"""
        config = {
            "target_url": "https://test.reliquary.io",
            "scan_depth": "comprehensive"
        }
        
        auditor = SecurityAuditor(config)
        
        # Mock all external requests to avoid actual network calls
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post, \
             patch('socket.create_connection') as mock_socket:
            
            # Mock web response with security issues
            mock_response = MagicMock()
            mock_response.headers = {'server': 'nginx/1.18.0'}
            mock_response.status_code = 200
            mock_response.text = "Welcome to admin panel"
            mock_get.return_value = mock_response
            
            # Mock API response with vulnerabilities
            mock_api_response = MagicMock()
            mock_api_response.status_code = 500
            mock_api_response.text = "SQL syntax error"
            mock_post.return_value = mock_api_response
            
            # Mock SSL connection
            mock_ssl_sock = MagicMock()
            mock_ssl_sock.getpeercert.return_value = {
                'notAfter': 'Dec 31 23:59:59 2024 GMT'
            }
            mock_ssl_sock.cipher.return_value = ('AES256-GCM-SHA384', 'TLSv1.3', 256)
            mock_socket.return_value.__enter__.return_value = mock_ssl_sock
            
            # Run comprehensive audit
            report = await auditor.run_comprehensive_audit("https://test.reliquary.io")
            
            # Verify report structure
            assert isinstance(report, dict)
            assert "report_id" in report
            assert "total_findings" in report
            assert "findings" in report
            
            # Verify findings were detected
            assert report["total_findings"] > 0
    
    @pytest.mark.asyncio
    async def test_security_test_performance(self):
        """Test security test performance and timing"""
        runner = SecurityTestRunner()
        
        start_time = time.time()
        
        # Mock all external calls for performance testing
        with patch('requests.get'), \
             patch('requests.post'), \
             patch('socket.create_connection'):
            
            await runner.run_all_security_tests("https://test.reliquary.io")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Security tests should complete within reasonable time
        assert duration < 30.0  # Less than 30 seconds for mocked tests
    
    @pytest.mark.asyncio
    async def test_security_findings_aggregation(self):
        """Test security findings aggregation across multiple testers"""
        config = {"target_url": "https://test.reliquary.io"}
        auditor = SecurityAuditor(config)
        
        # Add findings from different categories
        auditor._add_finding("Crypto Issue", "desc", SeverityLevel.HIGH,
                           VulnerabilityType.CRYPTOGRAPHY, "crypto", "loc", {})
        auditor._add_finding("Auth Issue", "desc", SeverityLevel.CRITICAL,
                           VulnerabilityType.AUTHENTICATION, "auth", "loc", {})
        auditor._add_finding("Network Issue", "desc", SeverityLevel.MEDIUM,
                           VulnerabilityType.NETWORK, "network", "loc", {})
        
        report = auditor._generate_report("https://test.reliquary.io")
        
        # Verify aggregation
        assert report["total_findings"] == 3
        assert report["severity_breakdown"]["critical"] == 1
        assert report["severity_breakdown"]["high"] == 1
        assert report["severity_breakdown"]["medium"] == 1
        
        # Verify risk score reflects severity
        assert report["risk_score"] > 6.0  # Should be high due to critical finding


if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])