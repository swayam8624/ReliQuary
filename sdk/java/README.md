# ReliQuary Java SDK

Enterprise Java SDK for the ReliQuary multi-agent consensus platform.

## Installation

### Maven

Add the following dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>io.reliquary</groupId>
    <artifactId>reliquary-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

Add the following dependency to your `build.gradle`:

```gradle
implementation 'io.reliquary:reliquary-sdk:1.0.0'
```

## Quick Start

```java
import io.reliquary.sdk.ReliQuaryClient;
import io.reliquary.sdk.ReliQuaryClient.AuthCredentials;
import io.reliquary.sdk.ReliQuaryClient.ConsensusRequest;
import io.reliquary.sdk.ReliQuaryClient.ConsensusType;

public class ReliQuaryExample {
    public static void main(String[] args) {
        // Initialize client
        AuthCredentials credentials = new AuthCredentials("your-api-key");
        ReliQuaryClient client = new ReliQuaryClient("https://api.reliquary.io", credentials);

        try {
            // Health check
            Map<String, Object> health = client.healthCheck();
            System.out.println("System health: " + health);

            // Submit consensus request
            Map<String, Object> contextData = new HashMap<>();
            contextData.put("resource_sensitivity", "high");

            ConsensusRequest request = new ConsensusRequest(
                ConsensusType.ACCESS_REQUEST,
                contextData,
                "user123",
                "/secure/data"
            );

            ReliQuaryClient.ConsensusResult result = client.submitConsensusRequest(request);
            System.out.println("Consensus decision: " + result.getDecision());

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // Disconnect
            client.close();
        }
    }
}
```

## Features

- **Multi-Agent Consensus**: Submit requests for distributed decision-making
- **Zero-Knowledge Proofs**: Generate and verify ZK proofs
- **AI/ML Enhanced Decisions**: Leverage machine learning for better security decisions
- **Cross-Chain Interactions**: Work with multiple blockchain networks
- **Observability**: Built-in metrics and monitoring
- **Synchronous and Asynchronous**: Both blocking and non-blocking APIs

## Documentation

For full documentation, visit [docs.reliquary.io](https://docs.reliquary.io/sdk/java).

## License

This SDK is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
