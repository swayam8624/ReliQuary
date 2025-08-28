# ReliQuary Enterprise SDKs

Enterprise-grade Software Development Kits (SDKs) for integrating with the ReliQuary multi-agent consensus and security platform.

## Overview

ReliQuary provides comprehensive SDKs for multiple programming languages, enabling seamless integration with our advanced multi-agent consensus, zero-knowledge proof, cross-chain, and AI/ML enhanced decision-making platform.

### Supported Languages

- **Python** - Full-featured async SDK with extensive type hints
- **JavaScript/TypeScript** - Modern async/await SDK with comprehensive TypeScript definitions
- **Java** - Enterprise-grade SDK with CompletableFuture support
- **Go** - High-performance SDK with context-aware operations

## Quick Start

### Python SDK

```bash
pip install reliquary-sdk
```

```python
import asyncio
from reliquary_sdk import ReliQuaryClient, AuthCredentials, ConsensusType, ConsensusRequest

async def main():
    credentials = AuthCredentials(api_key="your-api-key")

    async with ReliQuaryClient("http://localhost:8000", credentials) as client:
        # Health check
        health = await client.health_check()
        print(f"System health: {health}")

        # Submit consensus request
        request = ConsensusRequest(
            request_type=ConsensusType.ACCESS_REQUEST,
            context_data={"resource_sensitivity": "high"},
            user_id="user123",
            resource_path="/secure/data"
        )

        result = await client.submit_consensus_request(request)
        print(f"Consensus decision: {result.decision}")

asyncio.run(main())
```

### JavaScript/TypeScript SDK

```bash
npm install @reliquary/sdk
```

```typescript
import { ReliQuaryClient, ConsensusType } from "@reliquary/sdk";

async function main() {
  const client = new ReliQuaryClient({
    baseUrl: "http://localhost:8000",
    credentials: { apiKey: "your-api-key" },
  });

  await client.connect();

  try {
    // Health check
    const health = await client.healthCheck();
    console.log("System health:", health);

    // Submit consensus request
    const request = {
      requestType: ConsensusType.ACCESS_REQUEST,
      contextData: { resource_sensitivity: "high" },
      userId: "user123",
      resourcePath: "/secure/data",
    };

    const result = await client.submitConsensusRequest(request);
    console.log("Consensus decision:", result.decision);
  } finally {
    await client.disconnect();
  }
}

main().catch(console.error);
```

### Java SDK

```xml
<dependency>
    <groupId>io.reliquary</groupId>
    <artifactId>reliquary-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

```java
import io.reliquary.sdk.ReliQuaryClient;
import io.reliquary.sdk.ReliQuaryClient.ConsensusType;
import io.reliquary.sdk.ReliQuaryClient.ConsensusRequest;

public class Example {
    public static void main(String[] args) {
        ReliQuaryClient client = ReliQuaryClient.withApiKey("http://localhost:8000", "your-api-key");

        client.connect().thenCompose(v -> {
            // Health check
            return client.healthCheck();
        }).thenCompose(health -> {
            System.out.println("System health: " + health);

            // Submit consensus request
            ConsensusRequest request = new ConsensusRequest();
            request.setRequestType(ConsensusType.ACCESS_REQUEST);
            request.setContextData(Map.of("resource_sensitivity", "high"));
            request.setUserId("user123");
            request.setResourcePath("/secure/data");

            return client.submitConsensusRequest(request);
        }).thenRun(() -> {
            client.close();
        });
    }
}
```

### Go SDK

```bash
go get github.com/reliquary/sdk-go
```

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/reliquary/sdk-go/reliquary"
)

func main() {
    client := reliquary.NewClientWithAPIKey("http://localhost:8000", "your-api-key")
    ctx := context.Background()

    if err := client.Connect(ctx); err != nil {
        log.Fatal(err)
    }
    defer client.Disconnect()

    // Health check
    health, err := client.HealthCheck(ctx)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("System health: %+v\n", health)

    // Submit consensus request
    request := &reliquary.ConsensusRequest{
        RequestType:     reliquary.AccessRequest,
        ContextData:     map[string]interface{}{"resource_sensitivity": "high"},
        UserID:          "user123",
        ResourcePath:    "/secure/data",
        Priority:        5,
        TimeoutSeconds:  30,
        Metadata:        make(map[string]interface{}),
    }

    result, err := client.SubmitConsensusRequest(ctx, request)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Consensus decision: %s\n", result.Decision)
}
```

## Core Features

### 1. Authentication & Authorization

All SDKs support multiple authentication methods:

- **API Key**: Simple token-based authentication
- **Username/Password**: Traditional credential authentication
- **DID (Decentralized Identifiers)**: Advanced cryptographic authentication
- **OAuth 2.0**: Industry-standard authorization

### 2. Multi-Agent Consensus

Submit requests for distributed consensus across multiple specialized agents:

- **Access Requests**: Resource access decisions
- **Governance Decisions**: Organizational policy decisions
- **Emergency Response**: Critical security decisions
- **Security Validation**: Threat assessment and validation

### 3. Zero-Knowledge Proofs

Generate and verify cryptographic proofs without revealing sensitive information:

- **Context Verification**: Prove context without exposing data
- **Identity Verification**: Authenticate without revealing identity details
- **Compliance Proofs**: Demonstrate compliance without sharing private data

### 4. AI/ML Enhanced Decisions

Leverage artificial intelligence for intelligent decision-making:

- **Trust Prediction**: ML-based trust scoring
- **Anomaly Detection**: Behavioral pattern analysis
- **Decision Optimization**: AI-enhanced recommendation generation
- **Threat Classification**: Automated security assessment

### 5. Cross-Chain Operations

Interact with multiple blockchain networks:

- **Transaction Submission**: Cross-chain transaction processing
- **Status Monitoring**: Real-time transaction tracking
- **Bridge Operations**: Seamless blockchain interoperability

### 6. Observability & Monitoring

Comprehensive monitoring and alerting capabilities:

- **Metric Recording**: Custom metric collection
- **Alert Management**: Intelligent alerting system
- **Dashboard Data**: Real-time system monitoring
- **Performance Analytics**: Detailed performance insights

## Advanced Features

### Batch Operations

Process multiple requests efficiently:

```python
# Python batch consensus
requests = [consensus_request_1, consensus_request_2, consensus_request_3]
results = await client.submit_batch_consensus(requests)
```

### Real-time Monitoring

Monitor system performance and health:

```typescript
// JavaScript monitoring
const dashboard = await client.getSystemDashboard();
console.log(`Active agents: ${dashboard.system_status.active_agents}`);
console.log(`Health score: ${dashboard.system_status.health_score}`);
```

### Secret Management

Securely store and retrieve sensitive data:

```java
// Java secret storage
client.storeSecret("vault-id", "api-key", "secret-value", metadata)
    .thenCompose(result -> {
        return client.retrieveSecret("vault-id", "api-key");
    });
```

### Performance Optimization

Built-in performance monitoring and optimization:

```go
// Go performance tracking
stats := client.GetClientStats()
fmt.Printf("Average response time: %.2fms\n", stats.AverageResponseTimeMs)
fmt.Printf("Success rate: %.2f%%\n", 100-stats.ErrorRatePercent)
```

## Error Handling

All SDKs implement comprehensive error handling:

### Python

```python
try:
    result = await client.submit_consensus_request(request)
except ReliQuaryError as e:
    print(f"ReliQuary error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### JavaScript

```typescript
try {
  const result = await client.submitConsensusRequest(request);
} catch (error) {
  if (error instanceof ReliQuaryError) {
    console.error("ReliQuary error:", error.message);
  } else {
    console.error("Unexpected error:", error);
  }
}
```

### Java

```java
client.submitConsensusRequest(request)
    .exceptionally(throwable -> {
        System.err.println("Request failed: " + throwable.getMessage());
        return null;
    });
```

### Go

```go
result, err := client.SubmitConsensusRequest(ctx, request)
if err != nil {
    log.Printf("Request failed: %v", err)
    return
}
```

## Configuration

### Connection Settings

```yaml
# config.yaml
reliquary:
  base_url: "https://api.reliquary.io"
  timeout: 30s
  max_retries: 3

authentication:
  method: "api_key" # api_key, credentials, did
  api_key: "${RELIQUARY_API_KEY}"

observability:
  enable_metrics: true
  enable_tracing: true
  log_level: "info"
```

### Environment Variables

```bash
export RELIQUARY_BASE_URL="https://api.reliquary.io"
export RELIQUARY_API_KEY="your-api-key"
export RELIQUARY_TIMEOUT="30s"
export RELIQUARY_MAX_RETRIES="3"
```

## Enterprise Features

### High Availability

- **Connection Pooling**: Efficient connection management
- **Load Balancing**: Automatic request distribution
- **Failover Support**: Seamless error recovery
- **Circuit Breaker**: Prevent cascade failures

### Security

- **TLS Encryption**: End-to-end encryption
- **Certificate Pinning**: Enhanced security verification
- **Request Signing**: Cryptographic request integrity
- **Audit Logging**: Comprehensive audit trails

### Performance

- **Async Operations**: Non-blocking request processing
- **Connection Reuse**: Optimal connection management
- **Compression**: Reduced bandwidth usage
- **Caching**: Intelligent response caching

### Monitoring

- **Metrics Collection**: Automatic performance metrics
- **Health Checks**: Built-in health monitoring
- **Alerting**: Proactive issue detection
- **Tracing**: Distributed request tracing

## Best Practices

### 1. Connection Management

```python
# Use context managers for automatic cleanup
async with ReliQuaryClient(base_url, credentials) as client:
    # Client operations
    pass  # Automatic cleanup
```

### 2. Error Handling

```typescript
// Implement proper error handling
try {
  const result = await client.operation();
  return result;
} catch (error) {
  // Log error and implement fallback
  logger.error("Operation failed", error);
  return fallbackResult();
}
```

### 3. Performance Monitoring

```java
// Monitor client performance
ClientStats stats = client.getClientStats();
if (stats.getErrorRatePercent() > 5.0) {
    // Implement error mitigation
    handleHighErrorRate();
}
```

### 4. Resource Management

```go
// Always close resources
defer client.Disconnect()

// Use context for timeout control
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
```

## Testing

### Unit Testing

Each SDK includes comprehensive test suites:

```bash
# Python
pytest tests/

# JavaScript
npm test

# Java
mvn test

# Go
go test ./...
```

### Integration Testing

Test against live ReliQuary instances:

```bash
# Set test environment
export RELIQUARY_TEST_URL="http://localhost:8000"
export RELIQUARY_TEST_API_KEY="test-api-key"

# Run integration tests
npm run test:integration
```

## Support

### Documentation

- **API Reference**: Complete API documentation
- **Examples**: Practical usage examples
- **Tutorials**: Step-by-step guides
- **Best Practices**: Enterprise implementation guidance

### Community

- **GitHub**: Source code and issue tracking
- **Discord**: Community support and discussions
- **Stack Overflow**: Tag questions with `reliquary`

### Enterprise Support

- **24/7 Support**: Round-the-clock assistance
- **Dedicated Success Manager**: Personalized support
- **Custom Integration**: Tailored implementation assistance
- **Training**: Comprehensive developer training

## Roadmap

### Upcoming Features

- **GraphQL Support**: Alternative query interface
- **WebSocket Streaming**: Real-time event streaming
- **Offline Mode**: Offline operation capabilities
- **Mobile SDKs**: iOS and Android support

### Language Support

- **Rust**: High-performance native SDK
- **C#/.NET**: Enterprise .NET integration
- **PHP**: Web application integration
- **Ruby**: Rapid development support

## License

ReliQuary Enterprise SDKs are licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**ReliQuary v5.6 - Enterprise SDK Suite**

**Achievement**: Comprehensive multi-language SDK suite providing enterprise-grade integration capabilities for the ReliQuary platform across Python, JavaScript, Java, and Go ecosystems.

_© 2025 ReliQuary Project - Enterprise Integration Excellence_
