# ReliQuary API Reference

> **Enterprise-Grade Cryptographic Memory Platform API v5.0**

## Overview

The ReliQuary API provides secure, context-aware access to cryptographic memory vaults through multi-agent consensus, zero-knowledge proofs, and post-quantum encryption. This API is designed for enterprise integration with comprehensive security, scalability, and reliability features.

### Base URL

```
Production: https://api.reliquary.io
Staging: https://staging-api.reliquary.io
Local Development: http://localhost:8000
```

### API Versioning

The API uses URL versioning. Current version: `v1`

```
https://api.reliquary.io/v1/{endpoint}
```

## Authentication

### Methods Supported

1. **API Key Authentication** (Recommended for server-to-server)
2. **OAuth 2.0** (For web applications)
3. **DID Authentication** (For advanced cryptographic auth)
4. **WebAuthn** (For biometric authentication)

### API Key Authentication

```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     https://api.reliquary.io/v1/health
```

### OAuth 2.0 Flow

```bash
# 1. Get authorization URL
GET /v1/auth/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=read:vaults+write:vaults

# 2. Exchange code for token
POST /v1/auth/oauth/token
{
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
```

### Bearer Token Usage

```bash
curl -H "Authorization: Bearer your-access-token" \
     https://api.reliquary.io/v1/vaults
```

## Core Endpoints

### Health & Status

#### GET /v1/health

Returns comprehensive system health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-27T10:30:00Z",
  "version": "v5.0.0",
  "uptime_seconds": 86400,
  "response_time_ms": 45.2,
  "components": {
    "api_server": "healthy",
    "database": "healthy",
    "consensus_system": "healthy",
    "cryptographic_system": "healthy"
  },
  "system_info": {
    "platform": "kubernetes",
    "cpu_count": 8,
    "memory_total_gb": 32.0
  },
  "ready_for_traffic": true
}
```

#### GET /v1/health/ready

Kubernetes readiness probe endpoint.

**Response:**

```json
{
  "ready": true,
  "timestamp": "2025-08-27T10:30:00Z",
  "checks": {
    "database_ok": true,
    "consensus_ok": true,
    "crypto_ok": true
  }
}
```

#### GET /v1/health/live

Kubernetes liveness probe endpoint.

**Response:**

```json
{
  "alive": true,
  "timestamp": "2025-08-27T10:30:00Z",
  "uptime_seconds": 86400
}
```

#### GET /v1/version

Returns API version information.

**Response:**

```json
{
  "version": "v5.0.0",
  "build_date": "2025-08-27T00:00:00Z",
  "git_commit": "abc123def456",
  "api_version": "v1",
  "features": [
    "post_quantum_crypto",
    "multi_agent_consensus",
    "zero_knowledge_proofs",
    "multi_tenancy"
  ]
}
```

### Authentication Endpoints

#### POST /v1/auth/login

Authenticate with username/password.

**Request:**

```json
{
  "username": "user@company.com",
  "password": "secure-password",
  "tenant_id": "acme-corp"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "rt_abc123def456",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": "usr_123456",
  "tenant_id": "acme-corp",
  "permissions": ["vault:read", "vault:write", "consensus:submit"]
}
```

#### POST /v1/auth/refresh

Refresh access token.

**Request:**

```json
{
  "refresh_token": "rt_abc123def456"
}
```

#### POST /v1/auth/logout

Revoke access token.

**Request:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Multi-Agent Consensus

#### POST /v1/consensus/submit

Submit a request for multi-agent consensus decision.

**Request:**

```json
{
  "request_type": "access_request",
  "context_data": {
    "user_id": "usr_123456",
    "resource_path": "/vaults/sensitive-data",
    "action": "read",
    "device_trust_score": 0.85,
    "location": "office_network",
    "time_of_day": "business_hours"
  },
  "requestor_id": "usr_123456",
  "priority": 5,
  "timeout_seconds": 30,
  "required_agents": ["security_agent", "compliance_agent"],
  "metadata": {
    "department": "finance",
    "classification": "confidential"
  }
}
```

**Response:**

```json
{
  "consensus_id": "cons_789012",
  "decision": "allow",
  "confidence_score": 0.92,
  "reasoning": "High user trust score, secure location, business hours access",
  "agent_votes": {
    "security_agent": {
      "vote": "allow",
      "confidence": 0.89,
      "reasoning": "Device meets security requirements"
    },
    "compliance_agent": {
      "vote": "allow",
      "confidence": 0.95,
      "reasoning": "Access pattern complies with data governance policy"
    }
  },
  "processing_time_ms": 1250,
  "timestamp": "2025-08-27T10:30:00Z"
}
```

#### GET /v1/consensus/{consensus_id}

Get consensus decision status and details.

**Response:**

```json
{
  "consensus_id": "cons_789012",
  "status": "completed",
  "decision": "allow",
  "created_at": "2025-08-27T10:30:00Z",
  "completed_at": "2025-08-27T10:30:01Z",
  "agent_votes": { "...": "..." },
  "audit_trail": [
    {
      "timestamp": "2025-08-27T10:30:00Z",
      "action": "request_received",
      "agent": "orchestrator"
    },
    {
      "timestamp": "2025-08-27T10:30:01Z",
      "action": "decision_reached",
      "agent": "orchestrator"
    }
  ]
}
```

### Cryptographic Vaults

#### POST /v1/vaults

Create a new cryptographic vault.

**Request:**

```json
{
  "name": "Customer PII Vault",
  "description": "Secure storage for customer personally identifiable information",
  "encryption_algorithm": "kyber_1024_aes_gcm",
  "access_policy": {
    "required_consensus": true,
    "minimum_agents": 2,
    "access_hours": "business_hours",
    "allowed_locations": ["office_network"]
  },
  "metadata": {
    "classification": "pii",
    "retention_days": 2555,
    "compliance_frameworks": ["gdpr", "ccpa"]
  }
}
```

**Response:**

```json
{
  "vault_id": "vault_abc123",
  "name": "Customer PII Vault",
  "created_at": "2025-08-27T10:30:00Z",
  "encryption_key_id": "key_xyz789",
  "status": "active",
  "size_bytes": 0,
  "access_policy": { "...": "..." }
}
```

#### GET /v1/vaults

List all accessible vaults for the authenticated user.

**Query Parameters:**

- `limit`: Maximum number of results (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)
- `filter`: Filter by vault name or metadata
- `classification`: Filter by data classification level

**Response:**

```json
{
  "vaults": [
    {
      "vault_id": "vault_abc123",
      "name": "Customer PII Vault",
      "description": "Secure storage for customer PII",
      "created_at": "2025-08-27T10:30:00Z",
      "size_bytes": 1048576,
      "item_count": 150,
      "classification": "pii",
      "status": "active"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

#### GET /v1/vaults/{vault_id}

Get detailed information about a specific vault.

#### POST /v1/vaults/{vault_id}/data

Store encrypted data in vault.

**Request:**

```json
{
  "key": "customer_record_123",
  "data": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "ssn": "123-45-6789"
  },
  "metadata": {
    "data_type": "customer_pii",
    "created_by": "usr_123456"
  },
  "context_requirements": {
    "require_consensus": true,
    "zk_proof_required": true
  }
}
```

**Response:**

```json
{
  "data_id": "data_def456",
  "key": "customer_record_123",
  "stored_at": "2025-08-27T10:30:00Z",
  "encrypted_size_bytes": 2048,
  "merkle_proof": "0x1234567890abcdef...",
  "access_log_id": "log_ghi789"
}
```

#### GET /v1/vaults/{vault_id}/data/{key}

Retrieve encrypted data from vault (requires consensus approval).

**Response:**

```json
{
  "data_id": "data_def456",
  "key": "customer_record_123",
  "data": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "ssn": "123-45-6789"
  },
  "metadata": {
    "data_type": "customer_pii",
    "created_by": "usr_123456",
    "created_at": "2025-08-27T10:30:00Z"
  },
  "access_granted_by": "cons_789012",
  "retrieved_at": "2025-08-27T11:00:00Z"
}
```

### Zero-Knowledge Proofs

#### POST /v1/zk/generate-proof

Generate zero-knowledge proof for context verification.

**Request:**

```json
{
  "context_data": {
    "device_fingerprint": "fp_abc123",
    "location_hash": "loc_xyz789",
    "timestamp_range": "2025-08-27T09:00:00Z_2025-08-27T18:00:00Z",
    "behavior_pattern": "pattern_def456"
  },
  "proof_type": "context_verification",
  "public_inputs": ["location_zone", "time_window"],
  "private_inputs": ["exact_coordinates", "device_id"]
}
```

**Response:**

```json
{
  "proof_id": "proof_abc123",
  "zk_proof": {
    "pi_a": ["0x123...", "0x456..."],
    "pi_b": [
      ["0x789...", "0xabc..."],
      ["0xdef...", "0x012..."]
    ],
    "pi_c": ["0x345...", "0x678..."]
  },
  "public_signals": ["office_zone", "business_hours"],
  "verification_key_id": "vk_xyz789",
  "generated_at": "2025-08-27T10:30:00Z"
}
```

#### POST /v1/zk/verify-proof

Verify a zero-knowledge proof.

**Request:**

```json
{
  "proof_id": "proof_abc123",
  "zk_proof": { "...": "..." },
  "public_signals": ["office_zone", "business_hours"],
  "verification_key_id": "vk_xyz789"
}
```

**Response:**

```json
{
  "valid": true,
  "verification_time_ms": 45,
  "verified_at": "2025-08-27T10:30:00Z",
  "confidence_score": 0.98
}
```

### Audit & Logging

#### GET /v1/audit/logs

Retrieve audit logs with Merkle tree verification.

**Query Parameters:**

- `start_date`: ISO 8601 date string
- `end_date`: ISO 8601 date string
- `event_type`: Filter by event type
- `user_id`: Filter by user
- `resource_id`: Filter by resource
- `limit`: Maximum results (default: 100)

**Response:**

```json
{
  "logs": [
    {
      "log_id": "log_123456",
      "timestamp": "2025-08-27T10:30:00Z",
      "event_type": "vault_access",
      "user_id": "usr_123456",
      "resource_id": "vault_abc123",
      "action": "data_retrieved",
      "result": "success",
      "metadata": {
        "consensus_id": "cons_789012",
        "data_key": "customer_record_123"
      },
      "merkle_proof": {
        "hash": "0x1234567890abcdef...",
        "proof_path": ["0xabc...", "0xdef..."],
        "root_hash": "0x9876543210fedcba..."
      }
    }
  ],
  "merkle_root": "0x9876543210fedcba...",
  "pagination": { "...": "..." }
}
```

#### GET /v1/audit/merkle-root

Get current Merkle tree root for log integrity verification.

**Response:**

```json
{
  "root_hash": "0x9876543210fedcba...",
  "timestamp": "2025-08-27T10:30:00Z",
  "log_count": 15647,
  "last_update": "2025-08-27T10:29:45Z"
}
```

### Metrics & Monitoring

#### GET /v1/metrics

Prometheus metrics endpoint.

**Response:**

```
# HELP reliquary_requests_total Total number of API requests
# TYPE reliquary_requests_total counter
reliquary_requests_total{method="GET",endpoint="/health",status="200"} 1234

# HELP reliquary_consensus_operations_total Total consensus operations
# TYPE reliquary_consensus_operations_total counter
reliquary_consensus_operations_total{operation_type="access_request",result="allow"} 567

# HELP reliquary_response_time_seconds Request response time
# TYPE reliquary_response_time_seconds histogram
reliquary_response_time_seconds_bucket{le="0.1"} 100
reliquary_response_time_seconds_bucket{le="0.5"} 200
reliquary_response_time_seconds_bucket{le="1.0"} 250
```

#### GET /v1/observability/dashboard

Get system dashboard data for monitoring.

**Response:**

```json
{
  "system_status": {
    "health_score": 0.98,
    "active_agents": 7,
    "consensus_success_rate": 0.995,
    "average_response_time_ms": 156.7,
    "error_rate": 0.002
  },
  "performance_metrics": {
    "requests_per_second": 45.2,
    "consensus_operations_per_minute": 12.8,
    "vault_operations_per_hour": 342,
    "zk_proof_generation_time_ms": 89.3
  },
  "security_metrics": {
    "failed_auth_attempts_last_hour": 2,
    "suspicious_patterns_detected": 0,
    "consensus_denials_last_24h": 8
  },
  "resource_utilization": {
    "cpu_usage_percent": 23.4,
    "memory_usage_percent": 45.7,
    "storage_usage_gb": 128.9
  }
}
```

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Access denied by consensus or policy
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., vault already exists)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - System maintenance or overload

### Error Response Format

```json
{
  "error": {
    "code": "CONSENSUS_DENIED",
    "message": "Access denied by multi-agent consensus",
    "details": {
      "consensus_id": "cons_789012",
      "denial_reasons": [
        "Unusual access pattern detected",
        "Device trust score below threshold"
      ]
    },
    "request_id": "req_abc123def456",
    "timestamp": "2025-08-27T10:30:00Z"
  }
}
```

### Common Error Codes

- `INVALID_API_KEY` - API key is missing or invalid
- `TOKEN_EXPIRED` - Access token has expired
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `CONSENSUS_DENIED` - Multi-agent consensus denied access
- `CONSENSUS_TIMEOUT` - Consensus decision timed out
- `ZK_PROOF_INVALID` - Zero-knowledge proof verification failed
- `VAULT_NOT_FOUND` - Requested vault does not exist
- `ENCRYPTION_ERROR` - Cryptographic operation failed
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded
- `TENANT_QUOTA_EXCEEDED` - Tenant resource quota exceeded

## Rate Limiting

### Default Limits

- **API Requests**: 1000 per hour per API key
- **Consensus Operations**: 100 per hour per user
- **ZK Proof Generation**: 50 per hour per user
- **Vault Operations**: 500 per hour per user

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 985
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

## SDKs and Integration

### Official SDKs

- **Python**: `pip install reliquary-sdk`
- **JavaScript/TypeScript**: `npm install @reliquary/sdk`
- **Java**: Maven/Gradle dependency available
- **Go**: `go get github.com/reliquary/go-sdk`

### Quick Start Example

```python
from reliquary_sdk import ReliQuaryClient, AuthCredentials

async def main():
    credentials = AuthCredentials(api_key="your-api-key")
    client = ReliQuaryClient("https://api.reliquary.io", credentials)

    await client.connect()

    # Submit consensus request
    result = await client.submit_consensus_request({
        "request_type": "access_request",
        "context_data": {"user_id": "usr_123"},
        "requestor_id": "usr_123"
    })

    print(f"Decision: {result['decision']}")

    await client.disconnect()
```

## Webhook Notifications

### Supported Events

- `consensus.completed` - Consensus decision reached
- `vault.created` - New vault created
- `vault.accessed` - Vault data accessed
- `security.alert` - Security event detected
- `audit.logged` - New audit log entry

### Webhook Configuration

```bash
POST /v1/webhooks
{
  "url": "https://your-app.com/webhooks/reliquary",
  "events": ["consensus.completed", "security.alert"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload Example

```json
{
  "event": "consensus.completed",
  "timestamp": "2025-08-27T10:30:00Z",
  "data": {
    "consensus_id": "cons_789012",
    "decision": "allow",
    "requestor_id": "usr_123456"
  },
  "webhook_id": "wh_abc123"
}
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

- **Interactive Docs**: https://api.reliquary.io/docs
- **ReDoc**: https://api.reliquary.io/redoc
- **OpenAPI JSON**: https://api.reliquary.io/openapi.json

---

## Support & Resources

- **Documentation**: https://docs.reliquary.io
- **Developer Portal**: https://developers.reliquary.io
- **Status Page**: https://status.reliquary.io
- **Support**: api-support@reliquary.io

---

_ReliQuary API Reference v5.0 - Last Updated: 2025-08-27_
