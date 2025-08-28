# ReliQuary Python SDK

Enterprise Python SDK for the ReliQuary multi-agent consensus platform.

## Installation

```bash
pip install reliquary-sdk
```

## Quick Start

```python
import asyncio
from reliquary_sdk import ReliQuaryClient, AuthCredentials

async def main():
    # Initialize client
    credentials = AuthCredentials(api_key="your-api-key")
    client = ReliQuaryClient("https://api.reliquary.io", credentials)

    # Connect to platform
    await client.connect()

    try:
        # Health check
        health = await client.health_check()
        print(f"System health: {health}")

        # Submit consensus request
        from reliquary_sdk import ConsensusRequest, ConsensusType

        request = ConsensusRequest(
            request_type=ConsensusType.ACCESS_REQUEST,
            context_data={"resource_sensitivity": "high"},
            user_id="user123",
            resource_path="/secure/data"
        )

        result = await client.submit_consensus_request(request)
        print(f"Consensus decision: {result.decision}")

    finally:
        # Disconnect
        await client.disconnect()

# Run the example
asyncio.run(main())
```

## Features

- **Multi-Agent Consensus**: Submit requests for distributed decision-making
- **Zero-Knowledge Proofs**: Generate and verify ZK proofs
- **AI/ML Enhanced Decisions**: Leverage machine learning for better security decisions
- **Cross-Chain Interactions**: Work with multiple blockchain networks
- **Observability**: Built-in metrics and monitoring
- **Asynchronous**: Fully async/await compatible

## Documentation

For full documentation, visit [docs.reliquary.io](https://docs.reliquary.io/sdk/python).

## License

This SDK is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
