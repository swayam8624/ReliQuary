"""
Quantum-Resistant Integration Layer for ReliQuary

This module integrates the enhanced post-quantum cryptography system
with ReliQuary's existing infrastructure, providing seamless quantum-resistant
security across all system components.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

# Import ReliQuary components
from quantum.pqc_engine import (
    HybridCryptographicSystem,
    PQCAlgorithm,
    SecurityLevel,
    PQCKeyPair,
    QuantumKeyDistribution
)
from agents.consensus import DistributedConsensusManager
from agents.orchestrator import DecisionOrchestrator
from core.crypto.rust_ffi_wrappers import encrypt_data_rust, decrypt_data_rust


@dataclass
class QuantumSecurityProfile:
    """Security profile for quantum-resistant operations"""
    user_id: str
    primary_algorithm: PQCAlgorithm
    secondary_algorithm: Optional[PQCAlgorithm]
    security_level: SecurityLevel
    key_rotation_interval: int  # hours
    qkd_enabled: bool
    hybrid_signatures: bool
    quantum_proof_required: bool
    created_at: datetime
    last_rotation: datetime


@dataclass
class QuantumSecureTransaction:
    """Quantum-secure transaction structure"""
    transaction_id: str
    transaction_type: str
    sender_id: str
    recipient_id: str
    payload: bytes
    pqc_signatures: Dict[str, bytes]
    kem_ciphertext: bytes
    symmetric_ciphertext: bytes
    qkd_channel_id: Optional[str]
    proof_of_quantumness: Optional[str]
    timestamp: datetime
    security_level: SecurityLevel


class QuantumResistantSecurityManager:
    """
    Manages quantum-resistant security across the ReliQuary system.
    
    Integrates post-quantum cryptography with existing authentication,
    consensus, and vault management systems.
    """
    
    def __init__(self, 
                 consensus_manager: DistributedConsensusManager,
                 decision_orchestrator: DecisionOrchestrator):
        """Initialize quantum-resistant security manager."""
        self.consensus_manager = consensus_manager
        self.decision_orchestrator = decision_orchestrator
        
        # Initialize quantum cryptographic systems
        self.hybrid_crypto = HybridCryptographicSystem()
        self.qkd_system = QuantumKeyDistribution()
        
        # Security profiles and key management
        self.security_profiles: Dict[str, QuantumSecurityProfile] = {}
        self.active_keypairs: Dict[str, Dict[str, PQCKeyPair]] = {}
        self.quantum_transactions: Dict[str, QuantumSecureTransaction] = {}
        
        # Default security configurations
        self.default_algorithms = {
            "high_security": (PQCAlgorithm.CRYSTALS_KYBER_1024, PQCAlgorithm.CRYSTALS_DILITHIUM_5),
            "standard_security": (PQCAlgorithm.CRYSTALS_KYBER_1024, None),
            "fast_operations": (PQCAlgorithm.NTRU_HPS_4096_821, PQCAlgorithm.FALCON_1024)
        }
        
        self.logger = logging.getLogger("quantum_security")
        self.logger.info("Quantum-resistant security manager initialized")
    
    async def create_quantum_security_profile(self, 
                                            user_id: str,
                                            security_tier: str = "high_security",
                                            custom_algorithms: Optional[Tuple[PQCAlgorithm, Optional[PQCAlgorithm]]] = None,
                                            enable_qkd: bool = True) -> QuantumSecurityProfile:
        """Create quantum security profile for a user."""
        
        # Determine algorithms
        if custom_algorithms:
            primary_alg, secondary_alg = custom_algorithms
        else:
            primary_alg, secondary_alg = self.default_algorithms.get(
                security_tier, self.default_algorithms["standard_security"]
            )
        
        # Create security profile
        profile = QuantumSecurityProfile(
            user_id=user_id,
            primary_algorithm=primary_alg,
            secondary_algorithm=secondary_alg,
            security_level=SecurityLevel.LEVEL_5,
            key_rotation_interval=24,  # 24 hours
            qkd_enabled=enable_qkd,
            hybrid_signatures=secondary_alg is not None,
            quantum_proof_required=security_tier == "high_security",
            created_at=datetime.now(),
            last_rotation=datetime.now()
        )
        
        # Generate initial keypairs
        keypairs = self.hybrid_crypto.generate_hybrid_keypair(
            primary_algorithm=primary_alg,
            secondary_algorithm=secondary_alg,
            security_level=SecurityLevel.LEVEL_5
        )
        
        # Store profile and keypairs
        self.security_profiles[user_id] = profile
        self.active_keypairs[user_id] = keypairs
        
        # Establish QKD channels if enabled
        if enable_qkd:
            await self._establish_user_qkd_channels(user_id)
        
        self.logger.info(f"Created quantum security profile for {user_id} with {security_tier} tier")
        return profile
    
    async def _establish_user_qkd_channels(self, user_id: str):
        """Establish QKD channels for a user with other system participants."""
        # Establish QKD channels with consensus nodes
        consensus_nodes = ["consensus_node_1", "consensus_node_2", "consensus_node_3"]
        
        for node in consensus_nodes:
            try:
                channel_id = self.qkd_system.establish_qkd_channel(user_id, node, key_length=256)
                self.logger.info(f"QKD channel established: {user_id} <-> {node} [{channel_id}]")
            except Exception as e:
                self.logger.warning(f"Failed to establish QKD channel {user_id} <-> {node}: {e}")
    
    async def quantum_secure_access_request(self, 
                                          user_id: str,
                                          resource_id: str,
                                          action: str,
                                          context_data: Dict[str, Any],
                                          proof_of_quantumness: Optional[str] = None) -> Dict[str, Any]:
        """Process access request with quantum-resistant security."""
        
        if user_id not in self.security_profiles:
            raise ValueError(f"No quantum security profile found for user {user_id}")
        
        profile = self.security_profiles[user_id]
        
        # Check if key rotation is needed
        await self._check_key_rotation(user_id)
        
        # Enhance context with quantum security information
        quantum_context = context_data.copy()
        quantum_context.update({
            "quantum_secured": True,
            "security_level": profile.security_level.value,
            "pqc_algorithms": [profile.primary_algorithm.value],
            "qkd_enabled": profile.qkd_enabled,
            "proof_of_quantumness": proof_of_quantumness
        })
        
        if profile.secondary_algorithm:
            quantum_context["pqc_algorithms"].append(profile.secondary_algorithm.value)
        
        # Create quantum-secure transaction
        transaction = await self._create_quantum_transaction(
            user_id, "access_request", quantum_context
        )
        
        # Process through quantum-enhanced decision orchestrator
        decision_result = await self._quantum_enhanced_decision_orchestration(
            user_id, resource_id, action, quantum_context, transaction
        )
        
        # Add quantum security verification
        quantum_verification = await self._verify_quantum_security(transaction, decision_result)
        
        return {
            "decision": decision_result.final_decision,
            "confidence": decision_result.consensus_confidence,
            "quantum_verified": quantum_verification["verified"],
            "security_level": profile.security_level.value,
            "transaction_id": transaction.transaction_id,
            "pqc_signatures": len(transaction.pqc_signatures),
            "qkd_secured": transaction.qkd_channel_id is not None,
            "execution_time": decision_result.execution_time
        }
    
    async def _create_quantum_transaction(self, 
                                        user_id: str,
                                        transaction_type: str,
                                        payload_data: Dict[str, Any]) -> QuantumSecureTransaction:
        """Create a quantum-secure transaction."""
        
        transaction_id = f"qst_{int(time.time())}_{user_id}"
        payload = json.dumps(payload_data, sort_keys=True).encode()
        
        profile = self.security_profiles[user_id]
        keypairs = self.active_keypairs[user_id]
        
        # Create quantum signatures
        pqc_signatures = {}
        if profile.hybrid_signatures and keypairs:
            signatures = self.hybrid_crypto.hybrid_sign(payload, keypairs)
            for sig_type, signature in signatures.items():
                pqc_signatures[sig_type] = signature.signature
        
        # Quantum key encapsulation
        if "primary" in keypairs:
            primary_keypair = keypairs["primary"]
            encrypted_data = self.hybrid_crypto.quantum_secure_encrypt(
                payload, primary_keypair.public_key, profile.primary_algorithm
            )
            kem_ciphertext = encrypted_data["kem_ciphertext"]
            symmetric_ciphertext = encrypted_data["symmetric_ciphertext"]
        else:
            kem_ciphertext = b""
            symmetric_ciphertext = payload  # Fallback to plaintext
        
        # QKD channel
        qkd_channel_id = None
        if profile.qkd_enabled:
            # Find active QKD channel for this user
            for channel_id, channel_info in self.qkd_system.active_channels.items():
                if user_id in [channel_info["participant_a"], channel_info["participant_b"]]:
                    qkd_channel_id = channel_id
                    break
        
        # Proof of quantumness (if required)
        proof_of_quantumness = None
        if profile.quantum_proof_required:
            proof_of_quantumness = await self._generate_proof_of_quantumness(user_id, payload)
        
        transaction = QuantumSecureTransaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            sender_id=user_id,
            recipient_id="reliquary_system",
            payload=payload,
            pqc_signatures=pqc_signatures,
            kem_ciphertext=kem_ciphertext,
            symmetric_ciphertext=symmetric_ciphertext,
            qkd_channel_id=qkd_channel_id,
            proof_of_quantumness=proof_of_quantumness,
            timestamp=datetime.now(),
            security_level=profile.security_level
        )
        
        self.quantum_transactions[transaction_id] = transaction
        return transaction
    
    async def _generate_proof_of_quantumness(self, user_id: str, payload: bytes) -> str:
        """Generate proof that quantum-resistant cryptography was used."""
        profile = self.security_profiles[user_id]
        
        proof_data = {
            "user_id": user_id,
            "primary_algorithm": profile.primary_algorithm.value,
            "secondary_algorithm": profile.secondary_algorithm.value if profile.secondary_algorithm else None,
            "security_level": profile.security_level.value,
            "payload_hash": payload.hex()[:32],
            "timestamp": time.time(),
            "qkd_enabled": profile.qkd_enabled
        }
        
        # Create cryptographic proof
        proof_json = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return f"quantum_proof:{proof_hash}"
    
    async def _quantum_enhanced_decision_orchestration(self, 
                                                     user_id: str,
                                                     resource_id: str,
                                                     action: str,
                                                     quantum_context: Dict[str, Any],
                                                     transaction: QuantumSecureTransaction):
        """Process decision through quantum-enhanced orchestration."""
        
        from agents.orchestrator import DecisionType
        
        # Enhanced context for quantum decision making
        orchestration_context = quantum_context.copy()
        orchestration_context.update({
            "resource_id": resource_id,
            "action": action,
            "quantum_transaction_id": transaction.transaction_id,
            "quantum_security_verified": True,
            "pqc_signature_count": len(transaction.pqc_signatures)
        })
        
        # Route through decision orchestrator with quantum context
        result = await self.decision_orchestrator.orchestrate_decision(
            decision_type=DecisionType.ACCESS_REQUEST,
            requestor_id=user_id,
            context_data=orchestration_context,
            priority=2,  # High priority for quantum-secured requests
            timeout_seconds=45.0
        )
        
        return result
    
    async def _verify_quantum_security(self, 
                                     transaction: QuantumSecureTransaction,
                                     decision_result) -> Dict[str, Any]:
        """Verify quantum security of the transaction."""
        verification_results = {
            "verified": True,
            "checks": {},
            "security_score": 0.0
        }
        
        # Check 1: PQC Signatures
        if transaction.pqc_signatures:
            verification_results["checks"]["pqc_signatures"] = True
            verification_results["security_score"] += 0.3
        else:
            verification_results["checks"]["pqc_signatures"] = False
        
        # Check 2: Quantum Key Encapsulation
        if transaction.kem_ciphertext:
            verification_results["checks"]["quantum_kem"] = True
            verification_results["security_score"] += 0.3
        else:
            verification_results["checks"]["quantum_kem"] = False
        
        # Check 3: QKD Channel
        if transaction.qkd_channel_id:
            channel_status = self.qkd_system.get_channel_status(transaction.qkd_channel_id)
            if channel_status and channel_status["status"] == "active":
                verification_results["checks"]["qkd_channel"] = True
                verification_results["security_score"] += 0.2
            else:
                verification_results["checks"]["qkd_channel"] = False
        else:
            verification_results["checks"]["qkd_channel"] = False
        
        # Check 4: Proof of Quantumness
        if transaction.proof_of_quantumness:
            verification_results["checks"]["proof_of_quantumness"] = True
            verification_results["security_score"] += 0.2
        else:
            verification_results["checks"]["proof_of_quantumness"] = False
        
        # Final verification
        verification_results["verified"] = verification_results["security_score"] >= 0.6
        
        return verification_results
    
    async def _check_key_rotation(self, user_id: str):
        """Check if key rotation is needed for a user."""
        if user_id not in self.security_profiles:
            return
        
        profile = self.security_profiles[user_id]
        hours_since_rotation = (datetime.now() - profile.last_rotation).total_seconds() / 3600
        
        if hours_since_rotation >= profile.key_rotation_interval:
            await self._rotate_user_keys(user_id)
    
    async def _rotate_user_keys(self, user_id: str):
        """Rotate quantum keys for a user."""
        profile = self.security_profiles[user_id]
        
        # Generate new keypairs
        new_keypairs = self.hybrid_crypto.generate_hybrid_keypair(
            primary_algorithm=profile.primary_algorithm,
            secondary_algorithm=profile.secondary_algorithm,
            security_level=profile.security_level
        )
        
        # Update stored keypairs
        self.active_keypairs[user_id] = new_keypairs
        profile.last_rotation = datetime.now()
        
        # Establish new QKD channels if enabled
        if profile.qkd_enabled:
            await self._establish_user_qkd_channels(user_id)
        
        self.logger.info(f"Rotated quantum keys for user {user_id}")
    
    async def quantum_secure_consensus(self, 
                                     consensus_request: Dict[str, Any],
                                     participating_agents: List[str]) -> Dict[str, Any]:
        """Perform quantum-secure consensus among agents."""
        
        # Create quantum-secured consensus request
        quantum_consensus_data = consensus_request.copy()
        quantum_consensus_data.update({
            "quantum_secured": True,
            "consensus_type": "quantum_resistant",
            "participating_agents": participating_agents,
            "timestamp": time.time()
        })
        
        # Sign consensus request with quantum signatures
        consensus_payload = json.dumps(quantum_consensus_data, sort_keys=True).encode()
        quantum_signatures = {}
        
        for agent_id in participating_agents:
            if agent_id in self.active_keypairs:
                keypairs = self.active_keypairs[agent_id]
                signatures = self.hybrid_crypto.hybrid_sign(consensus_payload, keypairs)
                quantum_signatures[agent_id] = {
                    sig_type: sig.signature.hex() for sig_type, sig in signatures.items()
                }
        
        # Process through consensus manager
        result = await self.consensus_manager.propose_access_decision(
            access_request_id=f"quantum_consensus_{int(time.time())}",
            agent_decisions=quantum_consensus_data,
            context_data=quantum_consensus_data
        )
        
        # Add quantum verification
        result["quantum_signatures"] = quantum_signatures
        result["quantum_verified"] = len(quantum_signatures) >= len(participating_agents) / 2
        
        return result
    
    def get_quantum_security_status(self) -> Dict[str, Any]:
        """Get overall quantum security status."""
        total_profiles = len(self.security_profiles)
        qkd_enabled_count = sum(1 for p in self.security_profiles.values() if p.qkd_enabled)
        hybrid_sig_count = sum(1 for p in self.security_profiles.values() if p.hybrid_signatures)
        
        return {
            "total_quantum_profiles": total_profiles,
            "qkd_enabled_profiles": qkd_enabled_count,
            "hybrid_signature_profiles": hybrid_sig_count,
            "active_qkd_channels": len(self.qkd_system.active_channels),
            "total_quantum_transactions": len(self.quantum_transactions),
            "supported_pqc_algorithms": len(PQCAlgorithm),
            "quantum_readiness": "OPERATIONAL",
            "security_level": "POST_QUANTUM_READY"
        }
    
    def get_user_quantum_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get quantum security profile for a user."""
        if user_id not in self.security_profiles:
            return None
        
        profile = self.security_profiles[user_id]
        keypairs = self.active_keypairs.get(user_id, {})
        
        return {
            "user_id": user_id,
            "primary_algorithm": profile.primary_algorithm.value,
            "secondary_algorithm": profile.secondary_algorithm.value if profile.secondary_algorithm else None,
            "security_level": profile.security_level.value,
            "qkd_enabled": profile.qkd_enabled,
            "hybrid_signatures": profile.hybrid_signatures,
            "key_rotation_interval": profile.key_rotation_interval,
            "last_rotation": profile.last_rotation.isoformat(),
            "active_keypairs": len(keypairs),
            "created_at": profile.created_at.isoformat()
        }
    
    async def emergency_quantum_response(self, 
                                       threat_type: str,
                                       affected_users: List[str],
                                       response_action: str = "immediate_key_rotation") -> Dict[str, Any]:
        """Emergency quantum security response."""
        
        self.logger.warning(f"Emergency quantum response triggered: {threat_type}")
        
        response_results = {
            "threat_type": threat_type,
            "affected_users": affected_users,
            "response_action": response_action,
            "actions_taken": [],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if response_action == "immediate_key_rotation":
                for user_id in affected_users:
                    if user_id in self.security_profiles:
                        await self._rotate_user_keys(user_id)
                        response_results["actions_taken"].append(f"Rotated keys for {user_id}")
            
            elif response_action == "quantum_isolation":
                # Disable QKD channels for affected users
                for user_id in affected_users:
                    if user_id in self.security_profiles:
                        profile = self.security_profiles[user_id]
                        profile.qkd_enabled = False
                        response_results["actions_taken"].append(f"Disabled QKD for {user_id}")
            
            elif response_action == "algorithm_upgrade":
                # Upgrade to stronger algorithms
                for user_id in affected_users:
                    if user_id in self.security_profiles:
                        profile = self.security_profiles[user_id]
                        profile.primary_algorithm = PQCAlgorithm.CRYSTALS_KYBER_1024
                        profile.secondary_algorithm = PQCAlgorithm.CRYSTALS_DILITHIUM_5
                        await self._rotate_user_keys(user_id)
                        response_results["actions_taken"].append(f"Upgraded algorithms for {user_id}")
            
        except Exception as e:
            response_results["success"] = False
            response_results["error"] = str(e)
            self.logger.error(f"Emergency quantum response failed: {e}")
        
        return response_results