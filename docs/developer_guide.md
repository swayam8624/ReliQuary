# ReliQuary Developer Guide

> **Enterprise Cryptographic Memory Platform - Developer Integration Guide**

## Quick Start

### 1. Get API Credentials

```bash
# Register at https://console.reliquary.io
# Get your API key from the dashboard
export RELIQUARY_API_KEY="your-api-key-here"
export RELIQUARY_BASE_URL="https://api.reliquary.io"
```

### 2. Install SDK

**Python:**

```bash
pip install reliquary-sdk
```

**JavaScript:**

```bash
npm install @reliquary/sdk
```

**Java:**

```xml
<dependency>
    <groupId>io.reliquary</groupId>
    <artifactId>reliquary-sdk</artifactId>
    <version>5.0.0</version>
</dependency>
```

### 3. Basic Integration

```python
import asyncio
from reliquary_sdk import ReliQuaryClient, AuthCredentials

async def main():
    # Initialize client
    credentials = AuthCredentials(api_key="your-api-key")
    client = ReliQuaryClient("https://api.reliquary.io", credentials)

    await client.connect()

    # Check system health
    health = await client.health_check()
    print(f"System status: {health['status']}")

    # Submit consensus request
    result = await client.submit_consensus_request({
        "request_type": "access_request",
        "context_data": {
            "user_id": "user123",
            "resource_path": "/secure/data",
            "action": "read"
        },
        "requestor_id": "user123"
    })

    if result['decision'] == 'allow':
        print("Access granted by consensus")
    else:
        print(f"Access denied: {result['reasoning']}")

    await client.disconnect()

asyncio.run(main())
```

## Core Concepts

### Multi-Agent Consensus

ReliQuary uses AI agents to make access decisions based on context:

```python
# Context-aware access request
context = {
    "user_id": "emp_12345",
    "device_trust_score": 0.9,
    "location": "office_network",
    "time_of_day": "business_hours",
    "data_sensitivity": "high"
}

result = await client.submit_consensus_request({
    "request_type": "access_request",
    "context_data": context,
    "requestor_id": "emp_12345",
    "timeout_seconds": 30
})
```

### Cryptographic Vaults

Secure data storage with post-quantum encryption:

```python
# Create vault
vault = await client.create_vault({
    "name": "Customer Data Vault",
    "encryption_algorithm": "kyber_1024_aes_gcm",
    "access_policy": {
        "required_consensus": True,
        "minimum_agents": 2
    }
})

# Store encrypted data
data_id = await client.store_vault_data(
    vault_id=vault['vault_id'],
    key="customer_123",
    data={"name": "John Doe", "email": "john@example.com"}
)

# Retrieve data (requires consensus)
data = await client.retrieve_vault_data(
    vault_id=vault['vault_id'],
    key="customer_123"
)
```

### Zero-Knowledge Proofs

Privacy-preserving context verification:

```python
# Generate ZK proof
proof = await client.generate_zk_proof({
    "context_data": {
        "device_fingerprint": "fp_abc123",
        "location_hash": "office_zone",
        "timestamp_range": "business_hours"
    },
    "proof_type": "context_verification"
})

# Verify proof
valid = await client.verify_zk_proof(
    proof_id=proof['proof_id'],
    zk_proof=proof['zk_proof']
)
```

## Authentication Methods

### API Key (Recommended)

```python
credentials = AuthCredentials(api_key="rlq_abc123def456")
```

### OAuth 2.0

```python
# Get authorization URL
auth_url = client.get_oauth_auth_url(
    client_id="your_client_id",
    scopes=["vault:read", "vault:write"]
)

# Exchange code for token
token = await client.exchange_oauth_code(
    code="auth_code_from_callback",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

credentials = AuthCredentials(access_token=token['access_token'])
```

### DID Authentication

```python
credentials = AuthCredentials(
    did_private_key="your_did_private_key"
)
```

## Error Handling

```python
from reliquary_sdk import ReliQuaryError, ConsensusError, AuthenticationError

try:
    result = await client.submit_consensus_request(request)
except ConsensusError as e:
    print(f"Consensus denied: {e.message}")
    print(f"Reasons: {e.denial_reasons}")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except ReliQuaryError as e:
    print(f"API error: {e.message}")
    print(f"Error code: {e.error_code}")
```

## Best Practices

### 1. Connection Management

```python
# Use context managers
async with ReliQuaryClient(base_url, credentials) as client:
    # Operations here
    pass  # Automatic cleanup
```

### 2. Rate Limiting

```python
# Implement exponential backoff
import asyncio
from random import uniform

async def retry_with_backoff(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + uniform(0, 1)
            await asyncio.sleep(delay)
```

### 3. Security

```python
# Store credentials securely
import os
from keyring import get_password

api_key = os.getenv('RELIQUARY_API_KEY') or get_password('reliquary', 'api_key')

# Use environment-specific URLs
base_url = {
    'production': 'https://api.reliquary.io',
    'staging': 'https://staging-api.reliquary.io',
    'development': 'http://localhost:8000'
}[os.getenv('ENVIRONMENT', 'development')]
```

### 4. Monitoring

```python
# Track performance
import time

start_time = time.time()
result = await client.submit_consensus_request(request)
latency = (time.time() - start_time) * 1000

print(f"Consensus latency: {latency:.2f}ms")

# Get client statistics
stats = client.get_client_stats()
print(f"Success rate: {100 - stats.error_rate_percent:.1f}%")
```

## Multi-Language Examples

### JavaScript/TypeScript

```typescript
import { ReliQuaryClient, AuthCredentials } from "@reliquary/sdk";

const client = new ReliQuaryClient({
  baseUrl: "https://api.reliquary.io",
  credentials: { apiKey: process.env.RELIQUARY_API_KEY },
});

await client.connect();

const result = await client.submitConsensusRequest({
  requestType: "access_request",
  contextData: { userId: "user123" },
  requestorId: "user123",
});

console.log(`Decision: ${result.decision}`);
```

### Java

```java
import io.reliquary.ReliQuaryClient;
import io.reliquary.AuthCredentials;

ReliQuaryClient client = ReliQuaryClient.builder()
    .baseUrl("https://api.reliquary.io")
    .credentials(AuthCredentials.apiKey(apiKey))
    .build();

ConsensusRequest request = ConsensusRequest.builder()
    .requestType("access_request")
    .contextData(Map.of("userId", "user123"))
    .requestorId("user123")
    .build();

ConsensusResult result = client.submitConsensusRequest(request)
    .get(30, TimeUnit.SECONDS);

System.out.println("Decision: " + result.getDecision());
```

### Go

```go
import "github.com/reliquary/go-sdk"

client := reliquary.NewClient(
    "https://api.reliquary.io",
    reliquary.WithAPIKey(apiKey),
)

request := &reliquary.ConsensusRequest{
    RequestType: "access_request",
    ContextData: map[string]interface{}{"userId": "user123"},
    RequestorID: "user123",
}

result, err := client.SubmitConsensusRequest(ctx, request)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Decision: %s\n", result.Decision)
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from reliquary_sdk import ReliQuaryClient

@pytest.mark.asyncio
async def test_consensus_request():
    with patch('reliquary_sdk.ReliQuaryClient') as mock_client:
        mock_client.return_value.submit_consensus_request = AsyncMock(
            return_value={'decision': 'allow', 'confidence_score': 0.95}
        )

        client = ReliQuaryClient("https://api.test.com", None)
        result = await client.submit_consensus_request({})

        assert result['decision'] == 'allow'
        assert result['confidence_score'] > 0.9
```

### Integration Testing

```python
@pytest.mark.integration
async def test_full_workflow():
    client = ReliQuaryClient(
        "https://staging-api.reliquary.io",
        AuthCredentials(api_key=test_api_key)
    )

    await client.connect()

    # Test health check
    health = await client.health_check()
    assert health['status'] == 'healthy'

    # Test consensus
    result = await client.submit_consensus_request({
        "request_type": "access_request",
        "context_data": {"test": True},
        "requestor_id": "test_user"
    })

    assert result['decision'] in ['allow', 'deny']

    await client.disconnect()
```

## Deployment

### Environment Configuration

```yaml
# config/production.yaml
reliquary:
  base_url: "https://api.reliquary.io"
  timeout: 30s
  max_retries: 3

auth:
  api_key: "${RELIQUARY_API_KEY}"

logging:
  level: "info"
  format: "json"
```

### Docker Integration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV RELIQUARY_BASE_URL="https://api.reliquary.io"
CMD ["python", "main.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reliquary-client
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: app
          image: your-app:latest
          env:
            - name: RELIQUARY_API_KEY
              valueFrom:
                secretKeyRef:
                  name: reliquary-secrets
                  key: api-key
            - name: RELIQUARY_BASE_URL
              value: "https://api.reliquary.io"
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**

   - Check API key validity
   - Verify tenant permissions
   - Ensure correct base URL

2. **Consensus Timeouts**

   - Increase timeout value
   - Check agent availability
   - Review context data quality

3. **Rate Limiting**
   - Implement backoff retry
   - Monitor quota usage
   - Consider upgrading tier

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Client debug mode
client = ReliQuaryClient(
    base_url,
    credentials,
    debug=True
)
```

## Resources

- **API Reference**: [docs/api_reference.md](api_reference.md)
- **SDK Examples**: [github.com/reliquary/examples](https://github.com/reliquary/examples)
- **Status Page**: [status.reliquary.io](https://status.reliquary.io)
- **Support**: [support@reliquary.io](mailto:support@reliquary.io)

---

_ReliQuary Developer Guide v5.0 - Last Updated: 2025-08-27_
