"""
Context Verification Service for ReliQuary API.
This service orchestrates the use of ZK circuits to verify context data provided by enterprise clients.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Import ZK verification components
try:
    from zk.verifier.zk_runner import ZKRunner
    from zk.verifier.zk_batch_verifier import ZKBatchVerifier
except ImportError:
    # Mock implementations for development
    class ZKRunner:
        def generate_proof(self, circuit_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "proof": {"pi_a": [1, 2], "pi_b": [[1, 2], [3, 4]], "pi_c": [5, 6]},
                "public_signals": ["signal1", "signal2"]
            }
        
        def verify_proof(self, circuit_name: str, proof: Dict[str, Any], public_signals: List[str]) -> bool:
            return True
    
    class ZKBatchVerifier:
        def verify_batch(self, proofs: List[Dict[str, Any]]) -> List[bool]:
            return [True] * len(proofs)


@dataclass
class ContextVerificationRequest:
    """Request for context verification"""
    user_id: str
    ip_address: str
    user_agent: str
    timestamp: str
    device_fingerprint: str
    location_data: Optional[Dict[str, Any]] = None
    access_patterns: Optional[List[str]] = None

@dataclass
class ContextVerificationResponse:
    """Response for context verification"""
    request_id: str
    verified: bool
    confidence_score: float
    verified_components: List[str]
    timestamp: datetime
    zk_proof_data: Optional[Dict[str, Any]] = None

@dataclass
class ContextData:
    """Context data for verification"""
    user_id: str
    ip_address: str
    user_agent: str
    timestamp: str
    device_fingerprint: str
    location_data: Optional[Dict[str, Any]] = None
    access_patterns: Optional[List[str]] = None


@dataclass
class VerificationResult:
    """Result of context verification"""
    request_id: str
    verified: bool
    confidence_score: float
    verified_components: List[str]
    timestamp: datetime
    zk_proof_data: Optional[Dict[str, Any]] = None


class ContextVerificationService:
    """Service for verifying context data using Zero-Knowledge proofs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.zk_runner = ZKRunner()
        self.zk_batch_verifier = ZKBatchVerifier()
    
    def verify_context(self, context_data: ContextData) -> VerificationResult:
        """
        Verify context data using ZK proofs.
        
        Args:
            context_data: Context data to verify
            
        Returns:
            Verification result with confidence score
        """
        request_id = f"ctx_{int(datetime.now().timestamp() * 1000000)}"
        
        try:
            # Prepare verification components
            verification_components = []
            zk_proofs = []
            
            # Device fingerprint verification
            device_proof = self._verify_device_fingerprint(context_data)
            if device_proof:
                verification_components.append("device_fingerprint")
                zk_proofs.append(device_proof)
            
            # Timestamp verification
            timestamp_proof = self._verify_timestamp(context_data)
            if timestamp_proof:
                verification_components.append("timestamp")
                zk_proofs.append(timestamp_proof)
            
            # Location verification (if provided)
            if context_data.location_data:
                location_proof = self._verify_location(context_data)
                if location_proof:
                    verification_components.append("location")
                    zk_proofs.append(location_proof)
            
            # Access pattern verification (if provided)
            if context_data.access_patterns:
                pattern_proof = self._verify_access_patterns(context_data)
                if pattern_proof:
                    verification_components.append("access_patterns")
                    zk_proofs.append(pattern_proof)
            
            # Batch verify all ZK proofs
            if zk_proofs:
                verification_results = self.zk_batch_verifier.verify_batch(zk_proofs)
                all_verified = all(verification_results)
                
                # Calculate confidence score based on number of verified components
                confidence_score = len(verification_components) / 5.0  # Max 5 components
                if not all_verified:
                    confidence_score *= 0.5  # Reduce confidence if any proof fails
            else:
                all_verified = True
                confidence_score = 0.2  # Minimal confidence if no ZK verification performed
            
            # Create verification result
            result = VerificationResult(
                request_id=request_id,
                verified=all_verified,
                confidence_score=confidence_score,
                verified_components=verification_components,
                timestamp=datetime.now(),
                zk_proof_data={
                    "proofs": zk_proofs,
                    "verification_results": verification_results if zk_proofs else []
                } if zk_proofs else None
            )
            
            self.logger.info(f"Context verification completed for request {request_id}: {result.verified}")
            return result
            
        except Exception as e:
            self.logger.error(f"Context verification failed for request {request_id}: {str(e)}")
            # Return a failed verification result
            return VerificationResult(
                request_id=request_id,
                verified=False,
                confidence_score=0.0,
                verified_components=[],
                timestamp=datetime.now()
            )
    
    def _verify_device_fingerprint(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for device fingerprint verification.
        
        Args:
            context_data: Context data containing device fingerprint
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "device_fingerprint": context_data.device_fingerprint,
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("device_proof", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Device fingerprint verification failed: {str(e)}")
            return None
    
    def _verify_timestamp(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for timestamp verification.
        
        Args:
            context_data: Context data containing timestamp
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "timestamp": context_data.timestamp,
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("timestamp_verifier", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Timestamp verification failed: {str(e)}")
            return None
    
    def _verify_location(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for location verification.
        
        Args:
            context_data: Context data containing location information
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "ip_address": context_data.ip_address,
                "location_data": context_data.location_data or {},
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("location_chain", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Location verification failed: {str(e)}")
            return None
    
    def _verify_access_patterns(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for access pattern verification.
        
        Args:
            context_data: Context data containing access patterns
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "access_patterns": context_data.access_patterns or [],
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("pattern_match", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Access pattern verification failed: {str(e)}")
            return None


class ContextVerifier:
    """Service for verifying context data using Zero-Knowledge proofs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.zk_runner = ZKRunner()
        self.zk_batch_verifier = ZKBatchVerifier()
    
    def verify_context(self, context_data: ContextData) -> VerificationResult:
        """
        Verify context data using ZK proofs.
        
        Args:
            context_data: Context data to verify
            
        Returns:
            Verification result with confidence score
        """
        request_id = f"ctx_{int(datetime.now().timestamp() * 1000000)}"
        
        try:
            # Prepare verification components
            verification_components = []
            zk_proofs = []
            
            # Device fingerprint verification
            device_proof = self._verify_device_fingerprint(context_data)
            if device_proof:
                verification_components.append("device_fingerprint")
                zk_proofs.append(device_proof)
            
            # Timestamp verification
            timestamp_proof = self._verify_timestamp(context_data)
            if timestamp_proof:
                verification_components.append("timestamp")
                zk_proofs.append(timestamp_proof)
            
            # Location verification (if provided)
            if context_data.location_data:
                location_proof = self._verify_location(context_data)
                if location_proof:
                    verification_components.append("location")
                    zk_proofs.append(location_proof)
            
            # Access pattern verification (if provided)
            if context_data.access_patterns:
                pattern_proof = self._verify_access_patterns(context_data)
                if pattern_proof:
                    verification_components.append("access_patterns")
                    zk_proofs.append(pattern_proof)
            
            # Batch verify all ZK proofs
            if zk_proofs:
                verification_results = self.zk_batch_verifier.verify_batch(zk_proofs)
                all_verified = all(verification_results)
                
                # Calculate confidence score based on number of verified components
                confidence_score = len(verification_components) / 5.0  # Max 5 components
                if not all_verified:
                    confidence_score *= 0.5  # Reduce confidence if any proof fails
            else:
                all_verified = True
                confidence_score = 0.2  # Minimal confidence if no ZK verification performed
            
            # Create verification result
            result = VerificationResult(
                request_id=request_id,
                verified=all_verified,
                confidence_score=confidence_score,
                verified_components=verification_components,
                timestamp=datetime.now(),
                zk_proof_data={
                    "proofs": zk_proofs,
                    "verification_results": verification_results if zk_proofs else []
                } if zk_proofs else None
            )
            
            self.logger.info(f"Context verification completed for request {request_id}: {result.verified}")
            return result
            
        except Exception as e:
            self.logger.error(f"Context verification failed for request {request_id}: {str(e)}")
            # Return a failed verification result
            return VerificationResult(
                request_id=request_id,
                verified=False,
                confidence_score=0.0,
                verified_components=[],
                timestamp=datetime.now()
            )
    
    def _verify_device_fingerprint(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for device fingerprint verification.
        
        Args:
            context_data: Context data containing device fingerprint
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "device_fingerprint": context_data.device_fingerprint,
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("device_proof", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Device fingerprint verification failed: {str(e)}")
            return None
    
    def _verify_timestamp(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for timestamp verification.
        
        Args:
            context_data: Context data containing timestamp
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "timestamp": context_data.timestamp,
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("timestamp_verifier", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Timestamp verification failed: {str(e)}")
            return None
    
    def _verify_location(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for location verification.
        
        Args:
            context_data: Context data containing location information
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "ip_address": context_data.ip_address,
                "location_data": context_data.location_data or {},
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("location_chain", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Location verification failed: {str(e)}")
            return None
    
    def _verify_access_patterns(self, context_data: ContextData) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof for access pattern verification.
        
        Args:
            context_data: Context data containing access patterns
            
        Returns:
            ZK proof data or None if generation failed
        """
        try:
            inputs = {
                "access_patterns": context_data.access_patterns or [],
                "user_id": context_data.user_id
            }
            
            proof = self.zk_runner.generate_proof("pattern_match", inputs)
            return proof
        except Exception as e:
            self.logger.warning(f"Access pattern verification failed: {str(e)}")
            return None


# Global context verifier instance
_context_verifier = None


def get_context_verifier() -> ContextVerifier:
    """Get the global context verifier instance"""
    global _context_verifier
    if _context_verifier is None:
        _context_verifier = ContextVerifier()
    return _context_verifier


def verify_context_data(context_data: ContextData) -> VerificationResult:
    """Convenience function to verify context data"""
    verifier = get_context_verifier()
    return verifier.verify_context(context_data)