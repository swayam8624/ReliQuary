# ReliQuary SDK Documentation

## Overview

The ReliQuary SDK provides developers with easy-to-use interfaces to integrate the ReliQuary platform into their applications. The SDK is available in multiple languages to support diverse development environments.

## Language Support

1. **Python** - Native Python implementation with full feature parity
2. **JavaScript/TypeScript** - Node.js and browser-compatible libraries
3. **Java** - Enterprise Java integration with Maven support
4. **Go** - High-performance Go libraries for system applications

## Installation

### Python SDK

```bash
pip install reliquary-sdk
```

```python
from reliquary import ReliQuaryClient

client = ReliQuaryClient(api_key="your-api-key")
```

### JavaScript SDK

```bash
npm install @reliquary/sdk
```

```javascript
import { ReliQuaryClient } from "@reliquary/sdk";

const client = new ReliQuaryClient({ apiKey: "your-api-key" });
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
import io.reliquary.ReliquaryClient;

ReliquaryClient client = new ReliquaryClient("your-api-key");
```

### Go SDK

```bash
go get github.com/reliquary/sdk/go
```

```go
import "github.com/reliquary/sdk/go"

client := reliquary.NewClient("your-api-key")
```

## Core Concepts

### Authentication

All SDKs require an API key for authentication. API keys can be generated in the ReliQuary dashboard.

### Context Verification

ReliQuary uses context-aware security to verify access requests based on:

- Device fingerprinting
- Location verification
- Timestamp validation
- Behavioral patterns

### Trust Scoring

The platform dynamically evaluates trust levels based on:

- Historical behavior analysis
- Risk assessment algorithms
- Anomaly detection
- Machine learning models

## Python SDK Tutorial

### Basic Setup

```python
from reliquary import ReliQuaryClient

# Initialize client
client = ReliQuaryClient(
    api_key="your-api-key",
    api_url="https://api.reliquary.io"
)

# Verify context
context = client.verify_context()
print(f"Context verified: {context.verified}")
```

### Data Operations

```python
# Store encrypted data
data_id = client.store_data(
    data={"sensitive": "information"},
    context=context
)

# Retrieve data
retrieved_data = client.retrieve_data(data_id)
```

### Trust Management

```python
# Get trust score
trust_score = client.get_trust_score(user_id="user-123")
print(f"Trust score: {trust_score.score}")

# Update trust factors
client.update_trust_factors(
    user_id="user-123",
    factors={
        "login_frequency": 0.8,
        "location_consistency": 0.9
    }
)
```

## JavaScript SDK Tutorial

### Basic Setup

```javascript
import { ReliQuaryClient } from "@reliquary/sdk";

// Initialize client
const client = new ReliQuaryClient({
  apiKey: "your-api-key",
  apiUrl: "https://api.reliquary.io",
});

// Verify context
const context = await client.verifyContext();
console.log(`Context verified: ${context.verified}`);
```

### Data Operations

```javascript
// Store encrypted data
const dataId = await client.storeData({
  data: { sensitive: "information" },
  context: context,
});

// Retrieve data
const retrievedData = await client.retrieveData(dataId);
```

### Trust Management

```javascript
// Get trust score
const trustScore = await client.getTrustScore({ userId: "user-123" });
console.log(`Trust score: ${trustScore.score}`);

// Update trust factors
await client.updateTrustFactors({
  userId: "user-123",
  factors: {
    loginFrequency: 0.8,
    locationConsistency: 0.9,
  },
});
```

## Java SDK Tutorial

### Basic Setup

```java
import io.reliquary.ReliquaryClient;
import io.reliquary.model.Context;

// Initialize client
ReliquaryClient client = new ReliquaryClient("your-api-key");

// Verify context
Context context = client.verifyContext();
System.out.println("Context verified: " + context.isVerified());
```

### Data Operations

```java
// Store encrypted data
String dataId = client.storeData(
    Map.of("sensitive", "information"),
    context
);

// Retrieve data
Map<String, Object> retrievedData = client.retrieveData(dataId);
```

### Trust Management

```java
// Get trust score
TrustScore trustScore = client.getTrustScore("user-123");
System.out.println("Trust score: " + trustScore.getScore());

// Update trust factors
Map<String, Double> factors = Map.of(
    "loginFrequency", 0.8,
    "locationConsistency", 0.9
);
client.updateTrustFactors("user-123", factors);
```

## Go SDK Tutorial

### Basic Setup

```go
package main

import (
    "fmt"
    "github.com/reliquary/sdk/go"
)

func main() {
    // Initialize client
    client := reliquary.NewClient("your-api-key")

    // Verify context
    context, err := client.VerifyContext()
    if err != nil {
        panic(err)
    }
    fmt.Printf("Context verified: %v\n", context.Verified)
}
```

### Data Operations

```go
// Store encrypted data
dataId, err := client.StoreData(map[string]interface{}{
    "sensitive": "information",
}, context)
if err != nil {
    panic(err)
}

// Retrieve data
retrievedData, err := client.RetrieveData(dataId)
if err != nil {
    panic(err)
}
```

### Trust Management

```go
// Get trust score
trustScore, err := client.GetTrustScore("user-123")
if err != nil {
    panic(err)
}
fmt.Printf("Trust score: %f\n", trustScore.Score)

// Update trust factors
factors := map[string]float64{
    "loginFrequency": 0.8,
    "locationConsistency": 0.9,
}
err = client.UpdateTrustFactors("user-123", factors)
if err != nil {
    panic(err)
}
```

## Error Handling

All SDKs provide consistent error handling patterns:

### Python

```python
try:
    data = client.retrieve_data("invalid-id")
except ReliQuaryError as e:
    print(f"Error: {e.message}")
    print(f"Error code: {e.code}")
```

### JavaScript

```javascript
try {
  const data = await client.retrieveData("invalid-id");
} catch (error) {
  console.error(`Error: ${error.message}`);
  console.error(`Error code: ${error.code}`);
}
```

### Java

```java
try {
    Map<String, Object> data = client.retrieveData("invalid-id");
} catch (ReliQuaryException e) {
    System.err.println("Error: " + e.getMessage());
    System.err.println("Error code: " + e.getCode());
}
```

### Go

```go
data, err := client.RetrieveData("invalid-id")
if err != nil {
    if reliquaryError, ok := err.(*reliquary.Error); ok {
        fmt.Printf("Error: %s\n", reliquaryError.Message)
        fmt.Printf("Error code: %s\n", reliquaryError.Code)
    }
}
```

## Advanced Features

### Zero-Knowledge Proofs

All SDKs support Zero-Knowledge Proof verification for privacy-preserving authentication:

```python
# Python
proof = client.generate_zk_proof(challenge="auth-challenge")
verification = client.verify_zk_proof(proof)
```

### Multi-Agent Consensus

For enterprise applications, the SDKs support multi-agent consensus workflows:

```javascript
// JavaScript
const decision = await client.requestConsensus({
  action: "data-access",
  context: context,
  agents: ["agent-1", "agent-2", "agent-3"],
});
```

## Best Practices

1. **API Key Security**: Never hardcode API keys in client-side code
2. **Context Verification**: Always verify context before sensitive operations
3. **Error Handling**: Implement comprehensive error handling
4. **Rate Limiting**: Respect API rate limits
5. **Logging**: Use appropriate log levels for debugging

## Support

For issues with the SDK, please:

1. Check the documentation and examples
2. Review the API reference
3. Contact support through the ReliQuary dashboard
4. Submit issues on the GitHub repository
