# ReliQuary API Endpoints Documentation

## Overview

This document provides a comprehensive overview of all API endpoints available in the ReliQuary platform. The API follows RESTful principles and uses JSON for request/response formatting.

## Authentication Endpoints

### GET /auth/health

**Description**: Check the health status of the authentication service

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T14:19:28.123456",
  "service": "auth-service"
}
```

### GET /auth/info

**Description**: Get information about the authentication system

**Response**:

```json
{
  "service": "ReliQuary Authentication",
  "version": "2.0.0",
  "features": [
    "OAuth 2.0",
    "WebAuthn biometrics",
    "DID management",
    "Enhanced RBAC"
  ]
}
```

### POST /auth/login

**Description**: Authenticate a user and obtain a JWT token

**Request**:

```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/register

**Description**: Register a new user account

**Request**:

```json
{
  "username": "newuser@example.com",
  "password": "secure_password",
  "full_name": "New User"
}
```

**Response**:

```json
{
  "user_id": "user-123",
  "username": "newuser@example.com",
  "created_at": "2025-08-29T14:19:28.123456"
}
```

## Health Check Endpoints

### GET /health

**Description**: Basic health check of the entire platform

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T14:19:28.123456",
  "version": "2.0.0",
  "service": "reliquary-api",
  "features": [
    "Merkle audit logging",
    "OAuth 2.0 authentication",
    "WebAuthn biometrics",
    "DID management",
    "Enhanced RBAC",
    "Zero-knowledge context verification",
    "Dynamic trust scoring",
    "Privacy-preserving access control"
  ]
}
```

### GET /health/detailed

**Description**: Detailed health check with component status

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T14:19:28.123456",
  "components": {
    "database": {
      "status": "healthy",
      "details": {
        "connections": 5,
        "pool_size": 10
      }
    },
    "cache": {
      "status": "healthy",
      "details": {
        "hit_rate": 0.95,
        "memory_usage": "45MB"
      }
    },
    "logger": {
      "status": "healthy",
      "details": {
        "entries": 1250,
        "integrity": true
      }
    }
  }
}
```

### GET /version

**Description**: Get the current version of the platform

**Response**:

```json
{
  "version": "2.0.0",
  "build": "20250829-141928",
  "commit": "a1b2c3d4e5f6"
}
```

## Vault Management Endpoints

### POST /vaults

**Description**: Create a new vault

**Request**:

```json
{
  "name": "Personal Documents",
  "description": "Secure storage for personal documents",
  "owner_id": "user-123"
}
```

**Response**:

```json
{
  "vault_id": "vault-456",
  "name": "Personal Documents",
  "description": "Secure storage for personal documents",
  "owner_id": "user-123",
  "created_at": "2025-08-29T14:19:28.123456",
  "updated_at": "2025-08-29T14:19:28.123456",
  "size_bytes": 0,
  "encryption_algorithm": "AES-GCM",
  "status": "active"
}
```

### GET /vaults/{vault_id}

**Description**: Get information about a specific vault

**Response**:

```json
{
  "vault_id": "vault-456",
  "name": "Personal Documents",
  "description": "Secure storage for personal documents",
  "owner_id": "user-123",
  "created_at": "2025-08-29T14:19:28.123456",
  "updated_at": "2025-08-29T14:19:28.123456",
  "size_bytes": 102400,
  "encryption_algorithm": "AES-GCM",
  "status": "active"
}
```

### GET /vaults

**Description**: List all vaults for a user

**Query Parameters**:

- `owner_id` (optional): Filter by owner ID

**Response**:

```json
[
  {
    "vault_id": "vault-456",
    "name": "Personal Documents",
    "description": "Secure storage for personal documents",
    "owner_id": "user-123",
    "created_at": "2025-08-29T14:19:28.123456",
    "updated_at": "2025-08-29T14:19:28.123456",
    "size_bytes": 102400,
    "encryption_algorithm": "AES-GCM",
    "status": "active"
  }
]
```

### PUT /vaults/{vault_id}

**Description**: Update a vault

**Request**:

```json
{
  "name": "Updated Personal Documents",
  "description": "Updated secure storage for personal documents"
}
```

**Response**:

```json
{
  "vault_id": "vault-456",
  "name": "Updated Personal Documents",
  "description": "Updated secure storage for personal documents",
  "owner_id": "user-123",
  "created_at": "2025-08-29T14:19:28.123456",
  "updated_at": "2025-08-29T14:20:15.654321",
  "size_bytes": 102400,
  "encryption_algorithm": "AES-GCM",
  "status": "active"
}
```

### DELETE /vaults/{vault_id}

**Description**: Delete a vault

**Response**:

```json
{
  "message": "Vault deleted successfully",
  "vault_id": "vault-456"
}
```

### POST /vaults/{vault_id}/secrets

**Description**: Store a secret in a vault

**Request**:

```json
{
  "secret_name": "api_key",
  "secret_value": "sk-1234567890abcdef",
  "metadata": {
    "description": "API key for external service",
    "environment": "production"
  }
}
```

**Response**:

```json
{
  "secret_id": "secret-789",
  "vault_id": "vault-456",
  "secret_name": "api_key",
  "metadata": {
    "description": "API key for external service",
    "environment": "production"
  },
  "created_at": "2025-08-29T14:19:28.123456",
  "updated_at": "2025-08-29T14:19:28.123456",
  "version": 1
}
```

### GET /vaults/{vault_id}/secrets/{secret_name}

**Description**: Retrieve a secret from a vault

**Response**:

```json
{
  "secret_id": "secret-789",
  "vault_id": "vault-456",
  "secret_name": "api_key",
  "secret_value": "sk-1234567890abcdef",
  "metadata": {
    "description": "API key for external service",
    "environment": "production"
  },
  "created_at": "2025-08-29T14:19:28.123456",
  "updated_at": "2025-08-29T14:19:28.123456",
  "version": 1
}
```

## Context Verification Endpoints

### POST /context/verify

**Description**: Verify context for access request

**Request**:

```json
{
  "device_fingerprint": "device-123",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.006
  },
  "timestamp": "2025-08-29T14:19:28.123456"
}
```

**Response**:

```json
{
  "verified": true,
  "confidence": 0.95,
  "verification_id": "verify-123",
  "timestamp": "2025-08-29T14:19:28.123456"
}
```

### GET /context/history

**Description**: Get context verification history

**Response**:

```json
[
  {
    "verification_id": "verify-123",
    "user_id": "user-123",
    "verified": true,
    "confidence": 0.95,
    "timestamp": "2025-08-29T14:19:28.123456"
  }
]
```

## Trust Scoring Endpoints

### GET /trust/score

**Description**: Get current trust score for a user

**Query Parameters**:

- `user_id`: User ID to get trust score for

**Response**:

```json
{
  "user_id": "user-123",
  "trust_score": 85.5,
  "risk_level": "low",
  "last_updated": "2025-08-29T14:19:28.123456"
}
```

### GET /trust/history

**Description**: Get trust score history for a user

**Query Parameters**:

- `user_id`: User ID to get trust history for
- `limit` (optional): Number of records to return (default: 10)

**Response**:

```json
[
  {
    "timestamp": "2025-08-29T14:19:28.123456",
    "trust_score": 85.5,
    "risk_level": "low"
  },
  {
    "timestamp": "2025-08-29T13:19:28.123456",
    "trust_score": 82.0,
    "risk_level": "low"
  }
]
```

## Agent Orchestration Endpoints

### POST /agents/evaluate

**Description**: Request multi-agent evaluation for a decision

**Request**:

```json
{
  "request_id": "request-123",
  "user_id": "user-123",
  "resource_path": "/vaults/vault-456",
  "context_data": {
    "device_fingerprint": "device-123",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.006
    }
  }
}
```

**Response**:

```json
{
  "decision": "approved",
  "confidence": 0.92,
  "agents_consulted": ["neutral", "permissive", "strict", "watchdog"],
  "timestamp": "2025-08-29T14:19:28.123456"
}
```

### GET /agents/status

**Description**: Get status of all agents

**Response**:

```json
{
  "agents": {
    "neutral": {
      "status": "active",
      "last_heartbeat": "2025-08-29T14:19:28.123456"
    },
    "permissive": {
      "status": "active",
      "last_heartbeat": "2025-08-29T14:19:28.123456"
    },
    "strict": {
      "status": "active",
      "last_heartbeat": "2025-08-29T14:19:28.123456"
    },
    "watchdog": {
      "status": "active",
      "last_heartbeat": "2025-08-29T14:19:28.123456"
    }
  }
}
```

## Audit Logging Endpoints

### GET /logs/summary

**Description**: Get summary of audit logs

**Response**:

```json
{
  "total_entries": 1250,
  "integrity_verified": true,
  "last_entry_timestamp": "2025-08-29T14:19:28.123456"
}
```

### GET /logs/entry/{entry_id}

**Description**: Get specific audit log entry

**Response**:

```json
{
  "entry_id": "entry-123",
  "timestamp": "2025-08-29T14:19:28.123456",
  "event_type": "vault_access",
  "user_id": "user-123",
  "resource_id": "vault-456",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true
}
```

## Zero-Knowledge Proof Endpoints

### POST /zk/generate

**Description**: Generate a zero-knowledge proof

**Request**:

```json
{
  "circuit": "context_proof",
  "inputs": {
    "device_fingerprint": "device-123",
    "current_timestamp": 1630234768,
    "current_latitude": 40.7128,
    "current_longitude": -74.006
  }
}
```

**Response**:

```json
{
  "proof_id": "proof-123",
  "proof": "zk-proof-data-here",
  "verification_key": "verification-key-here",
  "public_inputs": {
    "expected_device_hash": "hash-value"
  }
}
```

### POST /zk/verify

**Description**: Verify a zero-knowledge proof

**Request**:

```json
{
  "proof": "zk-proof-data-here",
  "verification_key": "verification-key-here",
  "public_inputs": {
    "expected_device_hash": "hash-value"
  }
}
```

**Response**:

```json
{
  "verified": true,
  "verification_time_ms": 15.2,
  "timestamp": "2025-08-29T14:19:28.123456"
}
```

### GET /zk/system-status

**Description**: Get status of the ZK system

**Response**:

```json
{
  "status": "operational",
  "supported_circuits": ["context_proof", "device_proof", "timestamp_verifier"],
  "last_verification": "2025-08-29T14:19:28.123456"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters"
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous requests**: 100 requests per hour
- **Authenticated requests**: 1000 requests per hour
- **Administrative endpoints**: 100 requests per hour

Exceeding rate limits will result in a 429 Too Many Requests response:

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Try again in 60 minutes.",
  "retry_after": 3600
}
```

## Security Considerations

1. **Authentication**: All endpoints (except health checks) require authentication
2. **Encryption**: All data is encrypted at rest and in transit
3. **Audit Logging**: All access attempts are logged with Merkle tree integrity
4. **Zero-Knowledge**: Sensitive verification data is processed using ZK proofs
5. **Post-Quantum**: Cryptographic operations use quantum-resistant algorithms

## Versioning

The API uses semantic versioning. Breaking changes will result in a new major version number.

Current version: v2.0.0

## Support

For API support, please contact the ReliQuary development team or refer to the documentation.
