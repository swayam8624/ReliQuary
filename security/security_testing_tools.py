"""
Security Testing Tools for ReliQuary Platform
Specialized security testing tools for multi-agent consensus systems
"""

import asyncio
import hashlib
import hmac
import json
import logging
import random
import secrets
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import socket
import ssl


class CryptographicSecurityTester:
    """Test cryptographic implementations for vulnerabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger("crypto_security_tester")
        self.vulnerabilities = []
    
    async def test_cryptographic_security(self, target_url: str) -> List[Dict[str, Any]]:
        """Test cryptographic security implementations"""
        self.logger.info("Testing cryptographic security")
        
        await self._test_random_number_generation(target_url)
        await self._test_key_management(target_url)
        await self._test_encryption_strength(target_url)
        await self._test_hash_functions(target_url)
        await self._test_signature_verification(target_url)
        
        return self.vulnerabilities
    
    async def _test_random_number_generation(self, target_url: str):
        """Test random number generation quality"""
        try:
            # Test entropy endpoint
            entropy_endpoint = f"{target_url.rstrip('/')}/api/crypto/entropy"
            
            random_values = []
            for _ in range(100):
                response = requests.get(entropy_endpoint, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'random_value' in data:
                        random_values.append(data['random_value'])
            
            if len(random_values) > 10:
                # Test for patterns in random values
                if self._detect_patterns(random_values):
                    self.vulnerabilities.append({
                        "type": "weak_random_generation",
                        "severity": "HIGH",
                        "description": "Weak random number generation detected",
                        "location": entropy_endpoint,
                        "recommendation": "Use cryptographically secure random number generator"
                    })
                    
        except Exception as e:
            self.logger.error(f"Random number generation test failed: {e}")
    
    async def _test_key_management(self, target_url: str):
        """Test key management practices"""
        try:
            # Test key rotation endpoint
            key_rotation_endpoint = f"{target_url.rstrip('/')}/api/crypto/rotate-keys"
            
            response = requests.post(key_rotation_endpoint, timeout=10)
            
            # Check if key rotation is properly implemented
            if response.status_code == 404:
                self.vulnerabilities.append({
                    "type": "missing_key_rotation",
                    "severity": "MEDIUM",
                    "description": "Key rotation functionality not implemented",
                    "location": key_rotation_endpoint,
                    "recommendation": "Implement automated key rotation"
                })
            elif response.status_code == 200:
                # Check if rotation happens too frequently (potential DoS)
                for _ in range(5):
                    rapid_response = requests.post(key_rotation_endpoint, timeout=5)
                    if rapid_response.status_code == 200:
                        time.sleep(0.1)
                    else:
                        break
                else:
                    self.vulnerabilities.append({
                        "type": "excessive_key_rotation",
                        "severity": "MEDIUM",
                        "description": "Key rotation lacks proper rate limiting",
                        "location": key_rotation_endpoint,
                        "recommendation": "Implement rate limiting for key rotation"
                    })
                    
        except Exception as e:
            self.logger.error(f"Key management test failed: {e}")
    
    async def _test_encryption_strength(self, target_url: str):
        """Test encryption algorithm strength"""
        try:
            encrypt_endpoint = f"{target_url.rstrip('/')}/api/crypto/encrypt"
            
            # Test with known plaintexts
            test_plaintexts = [
                "A" * 16,  # Block-aligned
                "A" * 15,  # Not block-aligned
                "",        # Empty
                "A" * 1000 # Large
            ]
            
            ciphertexts = []
            for plaintext in test_plaintexts:
                response = requests.post(encrypt_endpoint, 
                                       json={"data": plaintext}, 
                                       timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'encrypted_data' in data:
                        ciphertexts.append(data['encrypted_data'])
            
            # Check for ECB mode detection (identical blocks)
            if len(ciphertexts) >= 2:
                if self._detect_ecb_mode(ciphertexts):
                    self.vulnerabilities.append({
                        "type": "weak_encryption_mode",
                        "severity": "HIGH",
                        "description": "ECB encryption mode detected",
                        "location": encrypt_endpoint,
                        "recommendation": "Use CBC, GCM, or other secure encryption modes"
                    })
                    
        except Exception as e:
            self.logger.error(f"Encryption strength test failed: {e}")
    
    async def _test_hash_functions(self, target_url: str):
        """Test hash function security"""
        try:
            hash_endpoint = f"{target_url.rstrip('/')}/api/crypto/hash"
            
            # Test with collision-prone inputs
            test_inputs = [
                "hello",
                "hello ",  # Similar input
                "",
                "a" * 1000000  # Large input
            ]
            
            hashes = []
            for input_data in test_inputs:
                response = requests.post(hash_endpoint, 
                                       json={"data": input_data}, 
                                       timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if 'hash' in data:
                        hashes.append(data['hash'])
                elif response.status_code == 500:
                    # Large input caused server error
                    self.vulnerabilities.append({
                        "type": "hash_dos_vulnerability",
                        "severity": "MEDIUM",
                        "description": "Hash function vulnerable to DoS with large inputs",
                        "location": hash_endpoint,
                        "recommendation": "Implement input size limits for hash operations"
                    })
            
            # Check hash length (weak hash functions have shorter outputs)
            if hashes and len(hashes[0]) < 32:  # Less than 128 bits
                self.vulnerabilities.append({
                    "type": "weak_hash_function",
                    "severity": "MEDIUM",
                    "description": "Weak hash function with short output detected",
                    "location": hash_endpoint,
                    "recommendation": "Use SHA-256 or stronger hash functions"
                })
                
        except Exception as e:
            self.logger.error(f"Hash function test failed: {e}")
    
    async def _test_signature_verification(self, target_url: str):
        """Test digital signature verification"""
        try:
            verify_endpoint = f"{target_url.rstrip('/')}/api/crypto/verify"
            
            # Test signature bypass attempts
            bypass_attempts = [
                {"signature": "", "data": "test", "public_key": "fake_key"},
                {"signature": "fake_sig", "data": "", "public_key": "fake_key"},
                {"signature": None, "data": "test", "public_key": "fake_key"}
            ]
            
            for attempt in bypass_attempts:
                response = requests.post(verify_endpoint, json=attempt, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('verified') == True:
                        self.vulnerabilities.append({
                            "type": "signature_verification_bypass",
                            "severity": "CRITICAL",
                            "description": "Signature verification can be bypassed",
                            "location": verify_endpoint,
                            "recommendation": "Implement proper signature verification logic"
                        })
                        break
                        
        except Exception as e:
            self.logger.error(f"Signature verification test failed: {e}")
    
    def _detect_patterns(self, values: List[Any]) -> bool:
        """Detect patterns in random values"""
        if len(values) < 10:
            return False
        
        # Check for sequential patterns
        numeric_values = []
        for val in values:
            try:
                if isinstance(val, str):
                    numeric_values.append(int(val, 16) if len(val) <= 8 else hash(val))
                else:
                    numeric_values.append(int(val))
            except (ValueError, TypeError):
                continue
        
        if len(numeric_values) < 5:
            return False
        
        # Check for increasing/decreasing sequences
        increasing = all(numeric_values[i] <= numeric_values[i+1] for i in range(len(numeric_values)-1))
        decreasing = all(numeric_values[i] >= numeric_values[i+1] for i in range(len(numeric_values)-1))
        
        return increasing or decreasing
    
    def _detect_ecb_mode(self, ciphertexts: List[str]) -> bool:
        """Detect ECB encryption mode by looking for repeated blocks"""
        for ciphertext in ciphertexts:
            if len(ciphertext) >= 32:  # At least 2 blocks of 16 bytes (hex encoded)
                blocks = [ciphertext[i:i+32] for i in range(0, len(ciphertext), 32)]
                if len(blocks) > 1 and len(blocks) != len(set(blocks)):  # Duplicate blocks found
                    return True
        return False


class ConsensusSecurityTester:
    """Test consensus mechanism security"""
    
    def __init__(self):
        self.logger = logging.getLogger("consensus_security_tester")
        self.vulnerabilities = []
    
    async def test_consensus_security(self, target_url: str) -> List[Dict[str, Any]]:
        """Test consensus mechanism security"""
        self.logger.info("Testing consensus security")
        
        await self._test_byzantine_resistance(target_url)
        await self._test_agent_authentication(target_url)
        await self._test_consensus_manipulation(target_url)
        await self._test_decision_integrity(target_url)
        
        return self.vulnerabilities
    
    async def _test_byzantine_resistance(self, target_url: str):
        """Test Byzantine fault resistance"""
        try:
            consensus_endpoint = f"{target_url.rstrip('/')}/api/consensus/request"
            
            # Simulate Byzantine behavior
            byzantine_requests = []
            for i in range(10):
                malicious_request = {
                    "request_type": "access_grant",
                    "context_data": {
                        "location": f"fake_location_{i}",
                        "device_id": f"malicious_device_{i}",
                        "timestamp": int(time.time()) + random.randint(-3600, 3600)
                    },
                    "user_id": f"attacker_{i}",
                    "resource_path": "/admin/sensitive_data"
                }
                
                response = requests.post(consensus_endpoint, json=malicious_request, timeout=10)
                if response.status_code == 200:
                    byzantine_requests.append(response.json())
            
            # Check if Byzantine requests are being granted
            granted_count = sum(1 for req in byzantine_requests if req.get('decision') == 'GRANT')
            
            if granted_count > len(byzantine_requests) * 0.3:  # More than 30% granted
                self.vulnerabilities.append({
                    "type": "weak_byzantine_resistance",
                    "severity": "HIGH",
                    "description": f"Consensus system grants {granted_count}/{len(byzantine_requests)} malicious requests",
                    "location": consensus_endpoint,
                    "recommendation": "Strengthen Byzantine fault tolerance mechanisms"
                })
                
        except Exception as e:
            self.logger.error(f"Byzantine resistance test failed: {e}")
    
    async def _test_agent_authentication(self, target_url: str):
        """Test agent authentication mechanisms"""
        try:
            agent_endpoint = f"{target_url.rstrip('/')}/api/agents/register"
            
            # Try to register malicious agents
            malicious_agents = [
                {"agent_id": "admin_override", "agent_type": "system", "credentials": "fake"},
                {"agent_id": "../../etc/passwd", "agent_type": "neutral", "credentials": "test"},
                {"agent_id": "'; DROP TABLE agents; --", "agent_type": "strict", "credentials": "sql"}
            ]
            
            for agent in malicious_agents:
                response = requests.post(agent_endpoint, json=agent, timeout=10)
                if response.status_code == 200:
                    self.vulnerabilities.append({
                        "type": "agent_authentication_bypass",
                        "severity": "CRITICAL",
                        "description": f"Malicious agent registration accepted: {agent['agent_id']}",
                        "location": agent_endpoint,
                        "recommendation": "Implement strong agent authentication and validation"
                    })
                    
        except Exception as e:
            self.logger.error(f"Agent authentication test failed: {e}")
    
    async def _test_consensus_manipulation(self, target_url: str):
        """Test for consensus manipulation vulnerabilities"""
        try:
            consensus_endpoint = f"{target_url.rstrip('/')}/api/consensus/request"
            
            # Test double voting
            double_vote_request = {
                "request_type": "access_grant",
                "context_data": {"location": "office", "device_id": "trusted_device"},
                "user_id": "legitimate_user",
                "resource_path": "/documents/public"
            }
            
            # Send same request multiple times rapidly
            responses = []
            for _ in range(5):
                response = requests.post(consensus_endpoint, json=double_vote_request, timeout=5)
                if response.status_code == 200:
                    responses.append(response.json())
                time.sleep(0.1)
            
            # Check for inconsistent decisions
            decisions = [r.get('decision') for r in responses]
            if len(set(decisions)) > 1:
                self.vulnerabilities.append({
                    "type": "consensus_inconsistency",
                    "severity": "MEDIUM",
                    "description": "Consensus system produces inconsistent decisions for identical requests",
                    "location": consensus_endpoint,
                    "recommendation": "Implement request deduplication and consistent decision logic"
                })
                
        except Exception as e:
            self.logger.error(f"Consensus manipulation test failed: {e}")
    
    async def _test_decision_integrity(self, target_url: str):
        """Test decision integrity and tamper resistance"""
        try:
            consensus_endpoint = f"{target_url.rstrip('/')}/api/consensus/request"
            
            # Test decision tampering
            legitimate_request = {
                "request_type": "access_grant",
                "context_data": {"location": "office", "device_id": "trusted_device"},
                "user_id": "legitimate_user",
                "resource_path": "/documents/confidential"
            }
            
            response = requests.post(consensus_endpoint, json=legitimate_request, timeout=10)
            
            if response.status_code == 200:
                decision_data = response.json()
                
                # Check for decision signature/integrity protection
                if 'signature' not in decision_data and 'hash' not in decision_data and 'checksum' not in decision_data:
                    self.vulnerabilities.append({
                        "type": "unprotected_decision_integrity",
                        "severity": "MEDIUM",
                        "description": "Consensus decisions lack integrity protection",
                        "location": consensus_endpoint,
                        "recommendation": "Implement digital signatures or checksums for decision integrity"
                    })
                    
        except Exception as e:
            self.logger.error(f"Decision integrity test failed: {e}")


class NetworkSecurityTester:
    """Test network security configurations"""
    
    def __init__(self):
        self.logger = logging.getLogger("network_security_tester")
        self.vulnerabilities = []
    
    async def test_network_security(self, target_url: str) -> List[Dict[str, Any]]:
        """Test network security"""
        self.logger.info("Testing network security")
        
        await self._test_ssl_configuration(target_url)
        await self._test_network_exposure(target_url)
        await self._test_rate_limiting(target_url)
        
        return self.vulnerabilities
    
    async def _test_ssl_configuration(self, target_url: str):
        """Test SSL/TLS configuration"""
        try:
            if not target_url.startswith('https://'):
                self.vulnerabilities.append({
                    "type": "missing_ssl",
                    "severity": "HIGH",
                    "description": "Service not using HTTPS encryption",
                    "location": target_url,
                    "recommendation": "Implement SSL/TLS encryption"
                })
                return
            
            host = target_url.replace("https://", "").split("/")[0]
            port = 443
            
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Check certificate validity
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry < 30:
                        self.vulnerabilities.append({
                            "type": "ssl_certificate_expiring",
                            "severity": "MEDIUM" if days_until_expiry > 7 else "HIGH",
                            "description": f"SSL certificate expires in {days_until_expiry} days",
                            "location": target_url,
                            "recommendation": "Renew SSL certificate"
                        })
                    
                    # Check cipher strength
                    if cipher and 'RC4' in str(cipher) or 'DES' in str(cipher):
                        self.vulnerabilities.append({
                            "type": "weak_ssl_cipher",
                            "severity": "HIGH",
                            "description": f"Weak SSL cipher in use: {cipher}",
                            "location": target_url,
                            "recommendation": "Configure strong SSL ciphers only"
                        })
                        
        except Exception as e:
            self.logger.error(f"SSL configuration test failed: {e}")
    
    async def _test_network_exposure(self, target_url: str):
        """Test for exposed network services"""
        try:
            host = target_url.replace("https://", "").replace("http://", "").split("/")[0]
            
            # Check common ports that shouldn't be exposed
            risky_ports = [22, 3306, 5432, 6379, 27017, 9200]
            
            for port in risky_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:  # Port is open
                        service_names = {22: "SSH", 3306: "MySQL", 5432: "PostgreSQL", 
                                       6379: "Redis", 27017: "MongoDB", 9200: "Elasticsearch"}
                        service = service_names.get(port, f"Unknown service on port {port}")
                        
                        self.vulnerabilities.append({
                            "type": "exposed_network_service",
                            "severity": "MEDIUM",
                            "description": f"{service} exposed on port {port}",
                            "location": f"{host}:{port}",
                            "recommendation": "Restrict access to internal services using firewall rules"
                        })
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Network exposure test failed: {e}")
    
    async def _test_rate_limiting(self, target_url: str):
        """Test rate limiting implementation"""
        try:
            # Send rapid requests to test rate limiting
            start_time = time.time()
            success_count = 0
            
            for i in range(100):
                try:
                    response = requests.get(target_url, timeout=1)
                    if response.status_code == 200:
                        success_count += 1
                    elif response.status_code == 429:  # Rate limited
                        break
                except requests.exceptions.Timeout:
                    continue
                except requests.exceptions.RequestException:
                    break
            
            elapsed_time = time.time() - start_time
            requests_per_second = success_count / elapsed_time if elapsed_time > 0 else 0
            
            # If we can make more than 50 requests per second, rate limiting might be weak
            if requests_per_second > 50:
                self.vulnerabilities.append({
                    "type": "weak_rate_limiting",
                    "severity": "MEDIUM",
                    "description": f"Weak rate limiting: {requests_per_second:.1f} requests/second allowed",
                    "location": target_url,
                    "recommendation": "Implement stronger rate limiting to prevent abuse"
                })
                
        except Exception as e:
            self.logger.error(f"Rate limiting test failed: {e}")


# Main security test runner
class SecurityTestRunner:
    """Main security test runner that coordinates all tests"""
    
    def __init__(self):
        self.logger = logging.getLogger("security_test_runner")
        self.crypto_tester = CryptographicSecurityTester()
        self.consensus_tester = ConsensusSecurityTester()
        self.network_tester = NetworkSecurityTester()
    
    async def run_all_security_tests(self, target_url: str) -> Dict[str, Any]:
        """Run all security tests"""
        self.logger.info(f"Starting comprehensive security tests for {target_url}")
        
        start_time = datetime.now()
        
        # Run all test categories
        crypto_results = await self.crypto_tester.test_cryptographic_security(target_url)
        consensus_results = await self.consensus_tester.test_consensus_security(target_url)
        network_results = await self.network_tester.test_network_security(target_url)
        
        end_time = datetime.now()
        
        all_vulnerabilities = crypto_results + consensus_results + network_results
        
        # Generate comprehensive report
        report = {
            "test_id": f"security_test_{int(time.time())}",
            "target": target_url,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
            "total_vulnerabilities": len(all_vulnerabilities),
            "categories_tested": {
                "cryptographic": len(crypto_results),
                "consensus": len(consensus_results),
                "network": len(network_results)
            },
            "severity_breakdown": self._calculate_severity_breakdown(all_vulnerabilities),
            "vulnerabilities": all_vulnerabilities,
            "recommendations": self._generate_recommendations(all_vulnerabilities),
            "overall_risk_level": self._calculate_overall_risk(all_vulnerabilities)
        }
        
        self.logger.info(f"Security testing completed. Found {len(all_vulnerabilities)} vulnerabilities")
        
        return report
    
    def _calculate_severity_breakdown(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate severity breakdown"""
        breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW")
            breakdown[severity] = breakdown.get(severity, 0) + 1
        return breakdown
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        critical_count = len([v for v in vulnerabilities if v.get("severity") == "CRITICAL"])
        if critical_count > 0:
            recommendations.append(f"IMMEDIATE: Address {critical_count} critical vulnerabilities")
        
        high_count = len([v for v in vulnerabilities if v.get("severity") == "HIGH"])
        if high_count > 0:
            recommendations.append(f"HIGH PRIORITY: Fix {high_count} high-severity issues")
        
        # Category-specific recommendations
        crypto_issues = len([v for v in vulnerabilities if "crypto" in v.get("type", "")])
        if crypto_issues > 0:
            recommendations.append("Review and strengthen cryptographic implementations")
        
        consensus_issues = len([v for v in vulnerabilities if "consensus" in v.get("type", "")])
        if consensus_issues > 0:
            recommendations.append("Enhance consensus mechanism security")
        
        network_issues = len([v for v in vulnerabilities if "network" in v.get("type", "") or "ssl" in v.get("type", "")])
        if network_issues > 0:
            recommendations.append("Improve network security configurations")
        
        return recommendations
    
    def _calculate_overall_risk(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level"""
        if any(v.get("severity") == "CRITICAL" for v in vulnerabilities):
            return "CRITICAL"
        elif len([v for v in vulnerabilities if v.get("severity") == "HIGH"]) > 2:
            return "HIGH"
        elif len(vulnerabilities) > 5:
            return "MEDIUM"
        else:
            return "LOW"


if __name__ == "__main__":
    async def main():
        runner = SecurityTestRunner()
        report = await runner.run_all_security_tests("https://api.reliquary.io")
        print(json.dumps(report, indent=2))
    
    asyncio.run(main())