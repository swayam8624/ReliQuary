# RELIQUARY: Context-Bound, Trust-Evolved Cryptographic Memory System

![How Vulnerable Are You?](How%20Vulnerable%20Are%20You_.gif)

**The World's First Post-Quantum Memory Vault**

Secure your digital assets against today's threats and tomorrow's quantum computers. Built with military-grade cryptography, zero-knowledge proofs, and intelligent multi-agent consensus for unparalleled protection.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Rust](https://img.shields.io/badge/Rust-1.70%2B-orange.svg)](https://www.rust-lang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)

## 🌐 Website

**Visit our live website:** [https://reliquary-liqsqvz67-swayamsingal2022-3626s-projects.vercel.app](https://reliquary-liqsqvz67-swayamsingal2022-3626s-projects.vercel.app)

## 🚀 Features

### 🔒 Post-Quantum Security
- **PQC Algorithms**: Lattice-based cryptography resistant to quantum attacks
- **Hybrid Encryption**: Combines classical and post-quantum algorithms for maximum security
- **Key Rotation**: Automatic key rotation with zero-downtime transitions

### 🧠 Intelligent Multi-Agent Consensus
- **Distributed Verification**: Multi-agent system validates all transactions
- **Adaptive Consensus**: Adjusts consensus mechanism based on network conditions
- **Fault Tolerance**: Byzantine Fault Tolerance with 99.99% uptime guarantee

### 🕵️ Zero-Knowledge Proofs
- **Privacy-Preserving**: Verify without revealing sensitive information
- **Efficient Proving**: Constant-time proof generation and verification
- **Selective Disclosure**: Choose what information to reveal in each context

### 📊 Performance Metrics

| Metric | Score | Industry Benchmark |
|--------|-------|-------------------|
| Security Rating | A+ | A |
| Load Time | < 1.2s | < 3s |
| Lighthouse Performance | 98/100 | 90+ |
| Mobile Score | 95/100 | 85+ |
| Accessibility | 92/100 | 80+ |

## 🛠 Getting Started

### Prerequisites

- `conda` (Anaconda or Miniconda)
- `Rust` (with `cargo`)
- `Node.js` (for SnarkJS, required for ZK proof generation/verification)
- `Docker` and `Docker Compose`

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SwayamSingal/ReliQuary.git
   cd ReliQuary
   ```

2. **Conda Environment Setup:**

   ```bash
   conda create -n reliquary-env python=3.11 -y
   conda activate reliquary-env
   ```

3. **Install Python Dependencies (using Poetry):**

   ```bash
   poetry install
   ```

4. **Install Rust Toolchain (if not already installed):**

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

5. **Build Rust Modules:**

   ```bash
   # From the root of the project
   cd rust_modules/encryptor
   cargo build --release
   cd ../merkle
   cargo build --release
   cd ../.. # Back to project root
   ```

6. **Install Node.js Dependencies for ZK (SnarkJS):**

   ```bash
   # Assuming Node.js is installed
   npm install -g snarkjs
   ```

7. **Run the API (Development Mode):**

   ```bash
   docker-compose up --build
   ```
   The API will be accessible at `http://localhost:8000`.

## 📁 Project Structure

```
.
├── agents/                     # Multi-agent quorum system based on LangGraph
├── apps/
│   └── api/                    # FastAPI backend for the core enterprise API
├── auth/                       # Identity management and API authentication
├── config/                     # Centralized configuration management
├── core/                       # Core logic including cryptography wrappers
├── docker/                     # Dockerfiles and Compose configurations
├── docs/                       # Developer guides and API reference
├── k8s/                        # Kubernetes deployment manifests
├── rust_modules/               # High-performance cryptographic backends in Rust
├── scripts/                    # Utility scripts for development and operations
├── sdk/                        # Client SDKs for enterprise integration
├── tests/                      # Comprehensive test suite
├── vaults/                     # Data models and pluggable storage management
├── website/                    # Next.js website for documentation and marketing
├── zk/                         # Zero-Knowledge Proof circuits and verifier
├── Dockerfile.agent-orchestrator
├── Dockerfile.platform
├── Dockerfile.simple
├── LICENSE
├── README.md
├── WORKFLOW.md
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## 🐳 Docker Deployment

ReliQuary provides official Docker images for easy deployment across multiple environments. Our images are built for multiple architectures (AMD64, ARM64, ARMv7) and are available on Docker Hub.

### Official Docker Images

| Image | Tag | Description |
|-------|-----|-------------|
| [swayamsingal/reliquary-platform](https://hub.docker.com/r/swayamsingal/reliquary-platform) | v5.0.0 | Main ReliQuary platform |
| [swayamsingal/reliquary-agent-orchestrator](https://hub.docker.com/r/swayamsingal/reliquary-agent-orchestrator) | v5.0.0 | Agent orchestrator service |
| [swayamsingal/reliquary-website](https://hub.docker.com/r/swayamsingal/reliquary-website) | v1.0.0 | Marketing website |

### Pull and Run Docker Images

```bash
# Pull the platform image
docker pull swayamsingal/reliquary-platform:v5.0.0

# Run the platform container
docker run -d \
  --name reliquary-platform \
  -p 8000:8000 \
  -e RELIQUARY_ENV=production \
  swayamsingal/reliquary-platform:v5.0.0

# Pull the website image
docker pull swayamsingal/reliquary-website:v1.0.0

# Run the website container
docker run -d \
  --name reliquary-website \
  -p 3000:3000 \
  swayamsingal/reliquary-website:v1.0.0
```

### Docker Compose Setup

For a complete development environment, use our Docker Compose configuration:

```bash
# Clone the repository
git clone https://github.com/SwayamSingal/ReliQuary.git
cd ReliQuary

# Start all services
docker-compose up -d
```

### Building from Source

To build Docker images from source:

```bash
# Build platform image
docker build -t reliquary/platform:v5.0.0 -f Dockerfile.platform --target production .

# Build orchestrator image
docker build -t reliquary/agent-orchestrator:v5.0.0 -f Dockerfile.agent-orchestrator .

# Build website image
docker build -t reliquary/website:v1.0.0 -f website/Dockerfile .
```

### Multi-Architecture Support

Our Docker images support multiple architectures:
- AMD64 (x86_64)
- ARM64 (aarch64)
- ARMv7 (armhf)

To build for specific architectures:
```bash
# Build for ARM64
docker buildx build --platform linux/arm64 -t reliquary/platform:v5.0.0 .

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t reliquary/platform:v5.0.0 .
```

## ☁️ Cloud Deployment

### Railway (Recommended)

The platform is currently deployed on Railway:

**API Endpoint:** [https://reliquary-production.up.railway.app](https://reliquary-production.up.railway.app)

To deploy to Railway:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

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

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/version` | GET | API version information |
| `/api/v1/vaults` | GET/POST | Manage cryptographic vaults |
| `/api/v1/auth` | POST | Authentication endpoints |
| `/api/v1/audit` | GET | Audit log retrieval |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suite
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=core tests/

# Run linting
flake8 .
```

## 📈 Performance Benchmarks

| Test | Score | Target |
|------|-------|--------|
| Lighthouse Performance | 98/100 | >95 |
| First Contentful Paint | < 1.2s | < 1.5s |
| Largest Contentful Paint | < 2.1s | < 2.5s |
| Cumulative Layout Shift | 0.01 | < 0.1 |
| Time to Interactive | < 2.8s | < 3.5s |

## 🔐 Security Features

### Post-Quantum Cryptography
- **Kyber-1024**: Key encapsulation mechanism
- **Falcon-1024**: Digital signature algorithm
- **AES-GCM-256**: Symmetric encryption

### Zero-Knowledge Proofs
- **ZK-SNARKs**: Privacy-preserving authentication
- **Context Verification**: Device, location, and pattern matching
- **Trust Scoring**: Dynamic trust assessment

### Multi-Agent Consensus
- **Quorum-Based**: Distributed decision making
- **Trust Engine**: Dynamic trust scoring
- **Merkle Logging**: Immutable audit trails

## 🌐 Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Supported |
| Firefox | 88+ | ✅ Supported |
| Safari | 14+ | ✅ Supported |
| Edge | 90+ | ✅ Supported |
| Mobile Safari | 14+ | ✅ Supported |
| Chrome Mobile | 90+ | ✅ Supported |

## 📚 Additional Resources

- [API Documentation](https://reliquary-production.up.railway.app/docs)
- [Developer Guides](docs/)
- [GitHub Repository](https://github.com/SwayamSingal/ReliQuary)
- [Docker Hub Images](https://hub.docker.com/u/swayamsingal)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Refer to [WORKFLOW.md](WORKFLOW.md) for the development roadmap and contribution guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

**Built with ❤️ by the ReliQuary Team**

*Securing the digital future against quantum threats*