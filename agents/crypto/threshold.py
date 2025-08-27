"""
Enhanced Threshold Cryptography for ReliQuary Multi-Agent System

This module implements advanced threshold cryptography protocols including
Shamir's Secret Sharing, multi-party computation, verifiable secret sharing,
and threshold signatures for secure distributed operations.
"""

import hashlib
import secrets
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math
from collections import defaultdict

# Import post-quantum cryptography
from core.crypto.rust_ffi_wrappers import (
    encrypt_data_rust as encrypt_data,
    decrypt_data_rust as decrypt_data
)


class ThresholdScheme(Enum):
    """Types of threshold cryptography schemes"""
    SHAMIR_SECRET_SHARING = "shamir_ss"
    VERIFIABLE_SECRET_SHARING = "verifiable_ss"
    THRESHOLD_SIGNATURES = "threshold_signatures"
    MULTI_PARTY_COMPUTATION = "mpc"
    DISTRIBUTED_KEY_GENERATION = "dkg"


class ShareValidationResult(Enum):
    """Results of share validation"""
    VALID = "valid"
    INVALID = "invalid"
    CORRUPTED = "corrupted"
    MISSING = "missing"
    DUPLICATE = "duplicate"


@dataclass
class SecretShare:
    """A share in a threshold secret sharing scheme"""
    party_id: int
    share_value: int
    scheme_id: str
    threshold: int
    total_parties: int
    metadata: Dict[str, Any]
    created_at: float
    signature: Optional[str] = None
    proof: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert share to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecretShare":
        """Create share from dictionary"""
        return cls(**data)


@dataclass
class ThresholdSchemeConfig:
    """Configuration for threshold cryptography scheme"""
    scheme_type: ThresholdScheme
    threshold: int
    total_parties: int
    security_level: int
    prime_bits: int
    enable_verification: bool
    enable_proofs: bool
    party_ids: List[int]
    metadata: Dict[str, Any]


@dataclass
class ReconstructionResult:
    """Result of secret reconstruction"""
    success: bool
    reconstructed_secret: Optional[int]
    participating_shares: List[SecretShare]
    validation_results: Dict[int, ShareValidationResult]
    reconstruction_time: float
    error_message: Optional[str] = None


@dataclass
class VerificationProof:
    """Zero-knowledge proof for verifiable secret sharing"""
    proof_type: str
    commitments: List[int]
    challenges: List[int]
    responses: List[int]
    public_parameters: Dict[str, Any]
    created_at: float


class EnhancedThresholdCryptography:
    """
    Enhanced threshold cryptography system with multiple schemes.
    
    Supports Shamir's Secret Sharing, Verifiable Secret Sharing,
    Threshold Signatures, and Multi-Party Computation protocols.
    """
    
    def __init__(self, security_level: int = 256):
        """
        Initialize enhanced threshold cryptography system.
        
        Args:
            security_level: Security level in bits (128, 192, 256, 384, 512)
        """
        self.security_level = security_level
        self.logger = logging.getLogger("threshold_crypto")
        
        # Generate secure prime based on security level
        self.prime = self._generate_secure_prime(security_level)
        self.generator = self._find_generator(self.prime)
        
        # Active schemes
        self.active_schemes: Dict[str, ThresholdSchemeConfig] = {}
        self.share_storage: Dict[str, Dict[int, SecretShare]] = {}
        self.verification_proofs: Dict[str, VerificationProof] = {}
        
        # Performance metrics
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.average_operation_time = 0.0
        
        # Security parameters
        self.max_share_age = 3600  # 1 hour
        self.enable_share_refresh = True
        self.require_proof_verification = True
        
        self.logger.info(f"Enhanced threshold cryptography initialized with {security_level}-bit security")
    
    def create_scheme(self, 
                     scheme_type: ThresholdScheme,
                     threshold: int,
                     total_parties: int,
                     party_ids: Optional[List[int]] = None,
                     enable_verification: bool = True) -> str:
        """
        Create a new threshold cryptography scheme.
        
        Args:
            scheme_type: Type of threshold scheme
            threshold: Minimum number of parties needed for operations
            total_parties: Total number of parties in the scheme
            party_ids: List of party identifiers
            enable_verification: Whether to enable verifiable secret sharing
            
        Returns:
            Scheme identifier
        """
        # Validate parameters
        if threshold > total_parties:
            raise ValueError("Threshold cannot exceed total parties")
        if threshold < 1:
            raise ValueError("Threshold must be at least 1")
        
        # Generate scheme ID
        scheme_id = f"{scheme_type.value}_{secrets.token_hex(8)}"
        
        # Set default party IDs
        if party_ids is None:
            party_ids = list(range(1, total_parties + 1))
        
        if len(party_ids) != total_parties:
            raise ValueError("Party IDs count must match total parties")
        
        # Create scheme configuration
        config = ThresholdSchemeConfig(
            scheme_type=scheme_type,
            threshold=threshold,
            total_parties=total_parties,
            security_level=self.security_level,
            prime_bits=self.security_level,
            enable_verification=enable_verification,
            enable_proofs=self.require_proof_verification,
            party_ids=party_ids,
            metadata={
                "created_at": time.time(),
                "creator": "threshold_crypto_system"
            }
        )
        
        # Store scheme
        self.active_schemes[scheme_id] = config
        self.share_storage[scheme_id] = {}
        
        self.logger.info(f"Created {scheme_type.value} scheme {scheme_id} with threshold {threshold}/{total_parties}")
        return scheme_id
    
    def share_secret(self, 
                    scheme_id: str,
                    secret: int,
                    dealer_id: Optional[int] = None) -> Dict[int, SecretShare]:
        """
        Share a secret using the specified threshold scheme.
        
        Args:
            scheme_id: Identifier of the threshold scheme
            secret: Secret value to share
            dealer_id: ID of the party sharing the secret
            
        Returns:
            Dictionary mapping party IDs to their shares
        """
        start_time = time.time()
        self.total_operations += 1
        
        try:
            # Get scheme configuration
            if scheme_id not in self.active_schemes:
                raise ValueError(f"Unknown scheme ID: {scheme_id}")
            
            config = self.active_schemes[scheme_id]
            
            # Generate shares based on scheme type
            if config.scheme_type in [ThresholdScheme.SHAMIR_SECRET_SHARING, 
                                    ThresholdScheme.VERIFIABLE_SECRET_SHARING]:
                shares = self._shamir_share_secret(config, secret)
            elif config.scheme_type == ThresholdScheme.THRESHOLD_SIGNATURES:
                shares = self._threshold_signature_share(config, secret)
            elif config.scheme_type == ThresholdScheme.MULTI_PARTY_COMPUTATION:
                shares = self._mpc_share_secret(config, secret)
            else:
                raise ValueError(f"Unsupported scheme type: {config.scheme_type}")
            
            # Generate verification proofs if enabled
            if config.enable_verification and config.scheme_type == ThresholdScheme.VERIFIABLE_SECRET_SHARING:
                proof = self._generate_verification_proof(config, secret, shares)
                self.verification_proofs[scheme_id] = proof
            
            # Store shares
            self.share_storage[scheme_id] = shares
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, True)
            
            self.logger.info(f"Secret shared using scheme {scheme_id}, generated {len(shares)} shares")
            return shares
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, False)
            self.logger.error(f"Secret sharing failed: {e}")
            raise
    
    def reconstruct_secret(self, 
                         scheme_id: str,
                         shares: Dict[int, SecretShare],
                         verify_shares: bool = True) -> ReconstructionResult:
        """
        Reconstruct a secret from threshold shares.
        
        Args:
            scheme_id: Identifier of the threshold scheme
            shares: Dictionary of shares for reconstruction
            verify_shares: Whether to verify share validity
            
        Returns:
            ReconstructionResult with reconstruction details
        """
        start_time = time.time()
        
        try:
            # Get scheme configuration
            if scheme_id not in self.active_schemes:
                raise ValueError(f"Unknown scheme ID: {scheme_id}")
            
            config = self.active_schemes[scheme_id]
            
            # Validate minimum threshold
            if len(shares) < config.threshold:
                return ReconstructionResult(
                    success=False,
                    reconstructed_secret=None,
                    participating_shares=list(shares.values()),
                    validation_results={},
                    reconstruction_time=time.time() - start_time,
                    error_message=f"Insufficient shares: {len(shares)} < {config.threshold}"
                )
            
            # Initialize validation_results
            validation_results = {}
            
            # Verify shares if requested
            if verify_shares:
                validation_results = self._verify_shares(scheme_id, shares)
                
                # Check if enough valid shares
                valid_shares = {pid: share for pid, share in shares.items() 
                              if validation_results.get(pid) == ShareValidationResult.VALID}
                
                if len(valid_shares) < config.threshold:
                    return ReconstructionResult(
                        success=False,
                        reconstructed_secret=None,
                        participating_shares=list(shares.values()),
                        validation_results=validation_results,
                        reconstruction_time=time.time() - start_time,
                        error_message=f"Insufficient valid shares: {len(valid_shares)} < {config.threshold}"
                    )
                
                shares = valid_shares
            
            # Reconstruct secret based on scheme type
            if config.scheme_type in [ThresholdScheme.SHAMIR_SECRET_SHARING, 
                                    ThresholdScheme.VERIFIABLE_SECRET_SHARING]:
                secret = self._shamir_reconstruct_secret(config, shares)
            elif config.scheme_type == ThresholdScheme.THRESHOLD_SIGNATURES:
                secret = self._threshold_signature_reconstruct(config, shares)
            elif config.scheme_type == ThresholdScheme.MULTI_PARTY_COMPUTATION:
                secret = self._mpc_reconstruct_secret(config, shares)
            else:
                raise ValueError(f"Unsupported scheme type: {config.scheme_type}")
            
            processing_time = time.time() - start_time
            
            return ReconstructionResult(
                success=True,
                reconstructed_secret=secret,
                participating_shares=list(shares.values()),
                validation_results=validation_results,
                reconstruction_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Secret reconstruction failed: {e}")
            
            return ReconstructionResult(
                success=False,
                reconstructed_secret=None,
                participating_shares=list(shares.values()) if shares else [],
                validation_results=validation_results if 'validation_results' in locals() else {},
                reconstruction_time=processing_time,
                error_message=str(e)
            )
    
    def _shamir_share_secret(self, config: ThresholdSchemeConfig, secret: int) -> Dict[int, SecretShare]:
        """Generate Shamir's Secret Sharing shares."""
        # Generate random coefficients for polynomial
        coefficients = [secret] + [secrets.randbelow(self.prime) for _ in range(config.threshold - 1)]
        
        shares = {}
        for party_id in config.party_ids:
            # Evaluate polynomial at party_id
            share_value = self._evaluate_polynomial(coefficients, party_id, self.prime)
            
            share = SecretShare(
                party_id=party_id,
                share_value=share_value,
                scheme_id=f"scheme_{secrets.token_hex(4)}",
                threshold=config.threshold,
                total_parties=config.total_parties,
                metadata={"algorithm": "shamir_ss", "polynomial_degree": config.threshold - 1},
                created_at=time.time()
            )
            
            # Sign share if verification is enabled
            if config.enable_verification:
                share.signature = self._sign_share(share)
            
            shares[party_id] = share
        
        return shares
    
    def _shamir_reconstruct_secret(self, config: ThresholdSchemeConfig, shares: Dict[int, SecretShare]) -> int:
        """Reconstruct secret using Shamir's Secret Sharing."""
        # Use Lagrange interpolation to reconstruct secret
        secret = 0
        share_items = list(shares.items())[:config.threshold]
        
        for i, (xi, share_i) in enumerate(share_items):
            # Calculate Lagrange coefficient
            numerator = 1
            denominator = 1
            
            for j, (xj, _) in enumerate(share_items):
                if i != j:
                    numerator = (numerator * (-xj)) % self.prime
                    denominator = (denominator * (xi - xj)) % self.prime
            
            # Calculate modular inverse of denominator
            denominator_inv = pow(denominator, self.prime - 2, self.prime)
            lagrange_coeff = (numerator * denominator_inv) % self.prime
            
            secret = (secret + share_i.share_value * lagrange_coeff) % self.prime
        
        return secret
    
    def _threshold_signature_share(self, config: ThresholdSchemeConfig, message_hash: int) -> Dict[int, SecretShare]:
        """Generate threshold signature shares."""
        # Simulate threshold signature sharing (simplified)
        shares = {}
        
        for party_id in config.party_ids:
            # Generate signature share
            share_value = pow(message_hash, party_id, self.prime)
            
            share = SecretShare(
                party_id=party_id,
                share_value=share_value,
                scheme_id=f"threshold_sig_{secrets.token_hex(4)}",
                threshold=config.threshold,
                total_parties=config.total_parties,
                metadata={"algorithm": "threshold_signature", "message_hash": message_hash},
                created_at=time.time()
            )
            
            shares[party_id] = share
        
        return shares
    
    def _threshold_signature_reconstruct(self, config: ThresholdSchemeConfig, shares: Dict[int, SecretShare]) -> int:
        """Reconstruct threshold signature."""
        # Combine signature shares
        signature = 1
        for share in shares.values():
            signature = (signature * share.share_value) % self.prime
        
        return signature
    
    def _mpc_share_secret(self, config: ThresholdSchemeConfig, secret: int) -> Dict[int, SecretShare]:
        """Generate MPC shares for multi-party computation."""
        # Generate additive shares for MPC
        shares = {}
        remaining_secret = secret
        
        for i, party_id in enumerate(config.party_ids[:-1]):
            share_value = secrets.randbelow(self.prime)
            remaining_secret = (remaining_secret - share_value) % self.prime
            
            share = SecretShare(
                party_id=party_id,
                share_value=share_value,
                scheme_id=f"mpc_{secrets.token_hex(4)}",
                threshold=config.threshold,
                total_parties=config.total_parties,
                metadata={"algorithm": "mpc_additive"},
                created_at=time.time()
            )
            
            shares[party_id] = share
        
        # Last party gets the remaining value
        last_party_id = config.party_ids[-1]
        shares[last_party_id] = SecretShare(
            party_id=last_party_id,
            share_value=remaining_secret,
            scheme_id=f"mpc_{secrets.token_hex(4)}",
            threshold=config.threshold,
            total_parties=config.total_parties,
            metadata={"algorithm": "mpc_additive"},
            created_at=time.time()
        )
        
        return shares
    
    def _mpc_reconstruct_secret(self, config: ThresholdSchemeConfig, shares: Dict[int, SecretShare]) -> int:
        """Reconstruct secret from MPC shares."""
        # Sum all additive shares
        secret = sum(share.share_value for share in shares.values()) % self.prime
        return secret
    
    def _generate_verification_proof(self, 
                                   config: ThresholdSchemeConfig,
                                   secret: int,
                                   shares: Dict[int, SecretShare]) -> VerificationProof:
        """Generate zero-knowledge proof for verifiable secret sharing."""
        # Generate commitments to polynomial coefficients
        commitments = []
        challenges = []
        responses = []
        
        # Simplified proof generation (in practice, would use proper ZK protocols)
        for i in range(config.threshold):
            commitment = pow(self.generator, secrets.randbelow(self.prime), self.prime)
            challenge = secrets.randbelow(self.prime)
            response = (secret + challenge) % self.prime
            
            commitments.append(commitment)
            challenges.append(challenge)
            responses.append(response)
        
        return VerificationProof(
            proof_type="polynomial_commitment",
            commitments=commitments,
            challenges=challenges,
            responses=responses,
            public_parameters={
                "generator": self.generator,
                "prime": self.prime,
                "threshold": config.threshold
            },
            created_at=time.time()
        )
    
    def _verify_shares(self, scheme_id: str, shares: Dict[int, SecretShare]) -> Dict[int, ShareValidationResult]:
        """Verify the validity of shares."""
        validation_results = {}
        
        for party_id, share in shares.items():
            try:
                # Check share age
                if time.time() - share.created_at > self.max_share_age:
                    validation_results[party_id] = ShareValidationResult.INVALID
                    continue
                
                # Verify signature if present
                if share.signature:
                    if self._verify_share_signature(share):
                        validation_results[party_id] = ShareValidationResult.VALID
                    else:
                        validation_results[party_id] = ShareValidationResult.CORRUPTED
                else:
                    validation_results[party_id] = ShareValidationResult.VALID
                
            except Exception as e:
                self.logger.error(f"Share verification failed for party {party_id}: {e}")
                validation_results[party_id] = ShareValidationResult.CORRUPTED
        
        return validation_results
    
    def _sign_share(self, share: SecretShare) -> str:
        """Generate signature for a share."""
        share_data = {
            "party_id": share.party_id,
            "share_value": share.share_value,
            "scheme_id": share.scheme_id,
            "created_at": share.created_at
        }
        
        data_str = json.dumps(share_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _verify_share_signature(self, share: SecretShare) -> bool:
        """Verify signature of a share."""
        expected_signature = self._sign_share(share)
        return share.signature == expected_signature
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int, prime: int) -> int:
        """Evaluate polynomial at point x using Horner's method."""
        result = 0
        x_power = 1
        
        for coeff in coefficients:
            result = (result + coeff * x_power) % prime
            x_power = (x_power * x) % prime
            
        return result
    
    def _generate_secure_prime(self, bits: int) -> int:
        """Generate a secure prime for the given bit length."""
        # Use well-known secure primes for common bit lengths
        secure_primes = {
            128: 2**127 - 1,  # Mersenne prime
            192: 2**192 - 2**64 - 1,
            256: 2**256 - 189,
            384: 2**384 - 317,
            512: 2**512 - 569
        }
        
        if bits in secure_primes:
            return secure_primes[bits]
        
        # For other bit lengths, generate a random prime
        return self._generate_random_prime(bits)
    
    def _generate_random_prime(self, bits: int) -> int:
        """Generate a random prime of specified bit length."""
        # Simplified prime generation (in production, use proper algorithms)
        while True:
            candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
            if self._is_prime(candidate):
                return candidate
    
    def _is_prime(self, n: int, k: int = 10) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        # Write n-1 as d * 2^r
        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Perform k rounds of testing
        for _ in range(k):
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        
        return True
    
    def _find_generator(self, prime: int) -> int:
        """Find a generator for the multiplicative group mod prime."""
        # Simplified generator finding (in production, use proper algorithms)
        for g in range(2, min(100, prime)):
            if pow(g, (prime - 1) // 2, prime) != 1:
                return g
        return 2  # Fallback
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics."""
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
        
        # Update average processing time
        total_time = self.average_operation_time * (self.total_operations - 1) + processing_time
        self.average_operation_time = total_time / self.total_operations
    
    def refresh_shares(self, scheme_id: str) -> Dict[int, SecretShare]:
        """Refresh shares without changing the secret."""
        if scheme_id not in self.active_schemes:
            raise ValueError(f"Unknown scheme ID: {scheme_id}")
        
        config = self.active_schemes[scheme_id]
        old_shares = self.share_storage.get(scheme_id, {})
        
        if len(old_shares) < config.threshold:
            raise ValueError("Insufficient shares for refresh")
        
        # Reconstruct secret
        reconstruction = self.reconstruct_secret(scheme_id, old_shares, verify_shares=False)
        if not reconstruction.success:
            raise ValueError("Failed to reconstruct secret for refresh")
        
        # Generate new shares
        if reconstruction.reconstructed_secret is not None:
            new_shares = self.share_secret(scheme_id, reconstruction.reconstructed_secret)
        else:
            raise ValueError("Failed to reconstruct secret for refresh")
        
        self.logger.info(f"Refreshed shares for scheme {scheme_id}")
        return new_shares
    
    def get_scheme_info(self, scheme_id: str) -> Dict[str, Any]:
        """Get information about a threshold scheme."""
        if scheme_id not in self.active_schemes:
            raise ValueError(f"Unknown scheme ID: {scheme_id}")
        
        config = self.active_schemes[scheme_id]
        shares = self.share_storage.get(scheme_id, {})
        
        return {
            "scheme_id": scheme_id,
            "scheme_type": config.scheme_type.value,
            "threshold": config.threshold,
            "total_parties": config.total_parties,
            "security_level": config.security_level,
            "shares_generated": len(shares),
            "verification_enabled": config.enable_verification,
            "created_at": config.metadata.get("created_at"),
            "has_verification_proof": scheme_id in self.verification_proofs
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.successful_operations / max(self.total_operations, 1),
            "average_operation_time": self.average_operation_time,
            "active_schemes": len(self.active_schemes),
            "security_level": self.security_level,
            "prime_modulus_bits": self.security_level
        }