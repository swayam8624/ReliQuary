# RELIQUARY: Context-Bound, Trust-Evolved Cryptographic Memory System

RELIQUARY is an innovative enterprise-grade cryptographic memory vault designed to provide context-aware secure data access. It leverages AI agents, trust-based consensus, post-quantum encryption, and Zero-Knowledge Proofs to redefine data access control.

This project is built as an API-first service, allowing enterprises to seamlessly plug its advanced security capabilities into their existing systems.

## Project Structure

- `agents/`: Multi-agent quorum system based on LangGraph.
- `apps/api/`: FastAPI backend for the core enterprise API.
- `auth/`: Identity management (DID, WebAuthn) and API authentication/authorization (OAuth 2.0, RBAC).
- `config/`: Centralized configuration management.
- `core/`: Core logic including cryptography wrappers, Merkle logging, trust engine, and utilities.
- `docker/`: Dockerfiles and Compose configurations.
- `docs/`: Developer guides and API reference.
- `k8s/`: Kubernetes deployment manifests.
- `rust_modules/`: High-performance cryptographic backends implemented in Rust.
- `scripts/`: Utility scripts for development, testing, and operations.
- `sdk/`: Client SDKs for enterprise integration (starting with Python).
- `tests/`: Comprehensive test suite.
- `vaults/`: Data models and pluggable storage management for encrypted vaults.
- `website/`: Next.js website for documentation and marketing.
- `zk/`: Zero-Knowledge Proof (ZKP) circuits and verifier.

## Getting Started

### Prerequisites

- `conda` (Anaconda or Miniconda)
- `Rust` (with `cargo`)
- `Node.js` (for SnarkJS, required for ZK proof generation/verification)
- `Docker` and `Docker Compose`

### Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/SwayamSingal/ReliQuary.git # Replace with your actual repo URL
    cd ReliQuary
    ```

2.  **Conda Environment Setup:**

    ```bash
    conda create -n reliquary-env python=3.11 -y
    conda activate reliquary-env
    ```

3.  **Install Python Dependencies (using Poetry):**

    ```bash
    poetry install
    ```

4.  **Install Rust Toolchain (if not already installed):**

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    ```

5.  **Build Rust Modules:**

    ```bash
    # From the root of the project
    cd rust_modules/encryptor
    cargo build --release
    cd ../merkle
    cargo build --release
    cd ../.. # Back to project root
    ```

6.  **Install Node.js Dependencies for ZK (SnarkJS):**

    ```bash
    # Assuming Node.js is installed
    npm install -g snarkjs
    ```

7.  **Run the API (Development Mode):**
    ```bash
    docker-compose up --build
    ```
    The API will be accessible at `http://localhost:8000`.

## Deployment Options

### Docker Images

Pre-built Docker images are available on Docker Hub:

- Platform: `swayamsingal/reliquary-platform:v5.0.0`
- Agent Orchestrator: `swayamsingal/reliquary-agent-orchestrator:v5.0.0`
- Website: `swayamsingal/reliquary-website:v1.0.0`

To pull and run any of these images:

```bash
docker pull swayamsingal/reliquary-platform:v5.0.0
docker run -p 8000:8000 swayamsingal/reliquary-platform:v5.0.0
```

### Cloud Deployment

The platform is currently deployed on Railway at: https://reliquary-production.up.railway.app

### Self-Hosted Deployment

For self-hosted deployments, you can use either Docker Compose or Kubernetes manifests:

1. **Docker Compose:**

   ```bash
   docker-compose up --build
   ```

2. **Kubernetes:**
   ```bash
   kubectl apply -f k8s/
   ```

## Website

The official website is built with Next.js and is deployed on Vercel at: https://reliquary-76aprovyg-swayamsingal2022-3626s-projects.vercel.app

Pre-built Docker images are also available for self-hosted deployments.

## Contributing

Refer to `WORKFLOW.md` for the development roadmap and contribution guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
