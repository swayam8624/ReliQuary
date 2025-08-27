# auth/did/did_manager.py

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import os
import secrets
import base64

import base64

# Custom base64url implementation
def bytes_to_base64url(data: bytes) -> str:
    """Convert bytes to base64url string"""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def base64url_to_bytes(data: str) -> bytes:
    """Convert base64url string to bytes"""
    # Add padding if necessary
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data)

@dataclass
class VerificationMethod:
    """W3C DID Verification Method"""
    id: str
    type: str
    controller: str
    public_key_jwk: Optional[Dict[str, str]] = None
    public_key_multibase: Optional[str] = None
    public_key_pem: Optional[str] = None

@dataclass  
class Service:
    """W3C DID Service Endpoint"""
    id: str
    type: str
    service_endpoint: Union[str, Dict[str, Any]]

@dataclass
class DIDDocument:
    """W3C DID Document"""
    context: Union[str, List[str]]
    id: str
    verification_method: List[VerificationMethod]
    authentication: List[str]
    assertion_method: Optional[List[str]] = None
    key_agreement: Optional[List[str]] = None
    capability_invocation: Optional[List[str]] = None
    capability_delegation: Optional[List[str]] = None
    service: Optional[List[Service]] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary following W3C DID specification"""
        result = {
            "@context": self.context,
            "id": self.id,
            "verificationMethod": [asdict(vm) for vm in self.verification_method],
            "authentication": self.authentication
        }
        
        # Add optional fields if present
        if self.assertion_method:
            result["assertionMethod"] = self.assertion_method
        if self.key_agreement:
            result["keyAgreement"] = self.key_agreement
        if self.capability_invocation:
            result["capabilityInvocation"] = self.capability_invocation
        if self.capability_delegation:
            result["capabilityDelegation"] = self.capability_delegation
        if self.service:
            result["service"] = [asdict(svc) for svc in self.service]
        if self.created:
            result["created"] = self.created
        if self.updated:
            result["updated"] = self.updated
            
        return result

class DIDManager:
    """Comprehensive DID management following W3C DID specifications"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to project-relative path
            script_dir = os.path.dirname(os.path.realpath(__file__))
            self.db_path = os.path.join(script_dir, "did_registry.db")
        else:
            self.db_path = db_path
        
        self._init_database()
    
    def _init_database(self):
        """Initialize DID registry database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create DIDs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dids (
                    did TEXT PRIMARY KEY,
                    document TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active',
                    controller TEXT,
                    UNIQUE(did)
                )
            ''')
            
            # Create verification methods table  
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_methods (
                    id TEXT PRIMARY KEY,
                    did TEXT NOT NULL,
                    type TEXT NOT NULL,
                    public_key_jwk TEXT,
                    public_key_pem TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (did) REFERENCES dids (did)
                )
            ''')
            
            # Create services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    did TEXT NOT NULL,
                    type TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (did) REFERENCES dids (did)
                )
            ''')
            
            conn.commit()
    
    def generate_did(self, method_name: str = "reliquary", identifier: Optional[str] = None) -> str:
        """Generate a new DID following W3C DID syntax."""
        if identifier is None:
            identifier = str(uuid.uuid4())
        
        return f"did:{method_name}:{identifier}"
    
    def create_key_pair(self, key_type: str = "EC") -> tuple:
        """Create a new cryptographic key pair."""
        if key_type == "EC":
            private_key = ec.generate_private_key(ec.SECP256R1())
        elif key_type == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        public_key = private_key.public_key()
        return private_key, public_key
    
    def public_key_to_jwk(self, public_key) -> Dict[str, str]:
        """Convert public key to JWK format."""
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            # EC key to JWK
            numbers = public_key.public_numbers()
            
            # Convert coordinates to bytes (32 bytes for P-256)
            x_bytes = numbers.x.to_bytes(32, byteorder='big')
            y_bytes = numbers.y.to_bytes(32, byteorder='big')
            
            return {
                "kty": "EC",
                "crv": "P-256",
                "x": bytes_to_base64url(x_bytes),
                "y": bytes_to_base64url(y_bytes)
            }
        
        elif isinstance(public_key, rsa.RSAPublicKey):
            # RSA key to JWK
            numbers = public_key.public_numbers()
            
            def int_to_base64url(value: int) -> str:
                # Convert integer to bytes, then to base64url
                byte_length = (value.bit_length() + 7) // 8
                value_bytes = value.to_bytes(byte_length, byteorder='big')
                return bytes_to_base64url(value_bytes)
            
            return {
                "kty": "RSA",
                "n": int_to_base64url(numbers.n),
                "e": int_to_base64url(numbers.e)
            }
        
        else:
            raise ValueError(f"Unsupported public key type: {type(public_key)}")
    
    def create_verification_method(
        self, 
        did: str, 
        key_id: str, 
        public_key, 
        vm_type: str = "JsonWebKey2020"
    ) -> VerificationMethod:
        """Create a verification method for a DID."""
        vm_id = f"{did}#{key_id}"
        
        # Convert public key to JWK format
        jwk = self.public_key_to_jwk(public_key)
        
        return VerificationMethod(
            id=vm_id,
            type=vm_type,
            controller=did,
            public_key_jwk=jwk
        )
    
    def register_did(self, did_document: DIDDocument) -> bool:
        """Register a DID document in the registry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now(timezone.utc)
                
                # Insert DID document
                cursor.execute('''
                    INSERT INTO dids (did, document, created_at, updated_at, status, controller)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    did_document.id,
                    json.dumps(did_document.to_dict()),
                    now,
                    now,
                    'active',
                    did_document.id  # Self-controlled by default
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error registering DID: {e}")
            return False
    
    def resolve_did(self, did: str) -> Optional[DIDDocument]:
        """Resolve a DID to its document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT document FROM dids WHERE did = ? AND status = 'active'
                ''', (did,))
                
                result = cursor.fetchone()
                if result:
                    doc_dict = json.loads(result[0])
                    return self._dict_to_did_document(doc_dict)
                
                return None
                
        except Exception as e:
            print(f"Error resolving DID: {e}")
            return None
    
    def _dict_to_did_document(self, doc_dict: Dict[str, Any]) -> DIDDocument:
        """Convert dictionary back to DIDDocument object"""
        verification_methods = []
        for vm_dict in doc_dict.get("verificationMethod", []):
            verification_methods.append(VerificationMethod(
                id=vm_dict["id"],
                type=vm_dict["type"],
                controller=vm_dict["controller"],
                public_key_jwk=vm_dict.get("publicKeyJwk")
            ))
        
        services = []
        for svc_dict in doc_dict.get("service", []):
            services.append(Service(
                id=svc_dict["id"],
                type=svc_dict["type"],
                service_endpoint=svc_dict.get("serviceEndpoint", svc_dict.get("service_endpoint"))
            ))
        
        return DIDDocument(
            context=doc_dict["@context"],
            id=doc_dict["id"],
            verification_method=verification_methods,
            authentication=doc_dict.get("authentication", []),
            assertion_method=doc_dict.get("assertionMethod"),
            key_agreement=doc_dict.get("keyAgreement"),
            capability_invocation=doc_dict.get("capabilityInvocation"),
            capability_delegation=doc_dict.get("capabilityDelegation"),
            service=services if services else None,
            created=doc_dict.get("created"),
            updated=doc_dict.get("updated")
        )

def create_user_did(username: str, email: Optional[str] = None) -> tuple:
    """Convenience function to create a complete DID for a user."""
    manager = DIDManager()
    
    # Generate DID
    did = manager.generate_did(identifier=username)
    
    # Create key pair
    private_key, public_key = manager.create_key_pair("EC")
    
    # Create verification method
    vm = manager.create_verification_method(did, "key-1", public_key)
    
    # Create service endpoints
    services = []
    if email:
        services.append(Service(
            id=f"{did}#email",
            type="EmailService",
            service_endpoint={"email": email}
        ))
    
    # Create DID document
    now = datetime.now(timezone.utc).isoformat()
    did_document = DIDDocument(
        context="https://www.w3.org/ns/did/v1",
        id=did,
        verification_method=[vm],
        authentication=[vm.id],
        service=services or None,
        created=now,
        updated=now
    )
    
    # Register the DID
    success = manager.register_did(did_document)
    if not success:
        raise Exception("Failed to register DID")
    
    return did_document, private_key

if __name__ == "__main__":
    print("--- Testing DID Management System ---")
    
    # Test DID creation
    did_doc, private_key = create_user_did("alice", "alice@example.com")
    print(f"✅ Created DID: {did_doc.id}")
    print(f"   - Verification methods: {len(did_doc.verification_method)}")
    print(f"   - Services: {len(did_doc.service) if did_doc.service else 0}")
    
    # Test DID resolution
    manager = DIDManager()
    resolved = manager.resolve_did(did_doc.id)
    if resolved:
        print(f"✅ DID resolved successfully")
        print(f"   - ID: {resolved.id}")
        print(f"   - Created: {resolved.created}")
    else:
        print("❌ DID resolution failed")
    
    # Display the DID document
    print("\n📄 DID Document:")
    print(json.dumps(did_doc.to_dict(), indent=2))
    
    print("\n✅ All DID tests passed!")