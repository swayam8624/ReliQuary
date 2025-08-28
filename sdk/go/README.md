# ReliQuary Go SDK

Enterprise Go SDK for the ReliQuary multi-agent consensus platform.

## Installation

```bash
go get github.com/reliquary/go-sdk
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/reliquary/go-sdk"
)

func main() {
    // Initialize client
    client := reliquary.NewClientWithAPIKey(
        "https://api.reliquary.io",
        "your-api-key",
        reliquary.WithTimeout(30*time.Second),
    )

    ctx := context.Background()

    // Connect to platform
    if err := client.Connect(ctx); err != nil {
        log.Fatal("Failed to connect:", err)
    }

    // Health check
    health, err := client.HealthCheck(ctx)
    if err != nil {
        log.Fatal("Health check failed:", err)
    }
    fmt.Printf("System health: %+v\n", health)

    // Submit consensus request
    contextData := map[string]interface{}{
        "resource_sensitivity": "high",
    }

    request := &reliquary.ConsensusRequest{
        RequestType:    reliquary.AccessRequest,
        ContextData:    contextData,
        UserID:         "user123",
        ResourcePath:   "/secure/data",
        Priority:       5,
        TimeoutSeconds: 30,
    }

    result, err := client.SubmitConsensusRequest(ctx, request)
    if err != nil {
        log.Fatal("Consensus request failed:", err)
    }
    fmt.Printf("Consensus decision: %s\n", result.Decision)
}
```

## Features

- **Multi-Agent Consensus**: Submit requests for distributed decision-making
- **Zero-Knowledge Proofs**: Generate and verify ZK proofs
- **AI/ML Enhanced Decisions**: Leverage machine learning for better security decisions
- **Cross-Chain Interactions**: Work with multiple blockchain networks
- **Observability**: Built-in metrics and monitoring
- **Context-Aware**: Full context-based security controls
- **Go Modules**: Modern Go dependency management

## Documentation

For full documentation, visit [docs.reliquary.io](https://docs.reliquary.io/sdk/go).

## License

This SDK is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
