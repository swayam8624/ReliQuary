# ReliQuary System Architecture and Flow Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    A[Client Applications] --> B[API Gateway & Load Balancer]
    B --> C[Authentication Service]
    B --> D[Core API Services]
    B --> E[Agent System]
    B --> F[Admin Portal]

    C --> G[PostgreSQL<br/>Structured Data]
    C --> H[Redis<br/>Session Cache]

    D --> I[Cryptographic Layer]
    D --> J[Data Storage Layer]
    D --> K[Merkle Logging]

    I --> L[Kyber/Falcon<br/>Post-Quantum Crypto]
    I --> M[AES-GCM<br/>Data Encryption]
    I --> N[Circom/SnarkJS<br/>ZK Proofs]

    J --> O[S3-Compatible<br/>Encrypted Objects]
    J --> G
    J --> P[Object Storage]

    K --> Q[Merkle Tree<br/>Immutable Logs]

    E --> R[LangGraph<br/>Workflow Management]
    E --> S[Agent Nodes<br/>Decision Making]
    E --> T[Threshold Crypto<br/>Secret Sharing]

    S --> U[Neutral Agent]
    S --> V[Permissive Agent]
    S --> W[Strict Agent]
    S --> X[Watchdog Agent]

    subgraph "Core Services"
        C
        D
        E
        F
    end

    subgraph "Data & Storage"
        G
        H
        O
        P
        Q
    end

    subgraph "Cryptographic Engine"
        L
        M
        N
    end

    subgraph "Agent System"
        R
        S
        T
        U
        V
        W
        X
    end
```

## 2. Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant Auth as Auth Service
    participant DID as DID Registry
    participant WebAuthn as WebAuthn Server
    participant JWT as JWT Manager

    Client->>API: Request authentication
    API->>Auth: Forward request
    Auth->>Client: Challenge response
    Client->>WebAuthn: Biometric verification
    WebAuthn->>Auth: Verification result
    Auth->>DID: DID resolution
    DID->>Auth: Identity verification
    Auth->>JWT: Generate token
    JWT->>Auth: JWT token
    Auth->>Client: JWT token
```

## 3. Data Access Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Core API
    participant ZK as ZK Verifier
    participant Trust as Trust Engine
    participant Agents as Agent System
    participant Crypto as Crypto Service
    participant DB as Database

    Client->>API: Request data access
    API->>ZK: Context verification
    ZK->>API: ZK proof verification
    API->>Trust: Evaluate trust
    Trust->>API: Trust score
    API->>Agents: Consensus decision
    Agents->>API: Decision result
    API->>DB: Retrieve encrypted data
    DB->>API: Encrypted data
    API->>Crypto: Decrypt data
    Crypto->>API: Decrypted data
    API->>Client: Response
```

## 4. Multi-Agent Consensus Flow

```mermaid
sequenceDiagram
    participant Orchestrator
    participant Neutral
    participant Permissive
    participant Strict
    participant Watchdog

    Orchestrator->>Neutral: Evaluate request
    Orchestrator->>Permissive: Evaluate request
    Orchestrator->>Strict: Evaluate request
    Orchestrator->>Watchdog: Evaluate request

    Neutral->>Orchestrator: Decision
    Permissive->>Orchestrator: Decision
    Strict->>Orchestrator: Decision
    Watchdog->>Orchestrator: Decision

    Orchestrator->>Orchestrator: Aggregate votes
    Orchestrator->>Orchestrator: Weighted decision
```

## 5. Trust Scoring Engine

```mermaid
graph TD
    A[User Context Data] --> B[Trust Metrics Calculation]
    B --> C[Device Consistency<br/>20%]
    B --> D[Temporal Patterns<br/>15%]
    B --> E[Geographic Consistency<br/>15%]
    B --> F[Behavioral Patterns<br/>20%]
    B --> G[Access Frequency<br/>10%]
    B --> H[Risk Indicators<br/>10%]
    B --> I[Compliance Score<br/>5%]
    B --> J[Historical Reliability<br/>5%]

    C --> K[Weighted Trust Score]
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K --> L[Adaptive Thresholds]
    K --> M[Risk Assessment]
    K --> N[Recommendations]
```

## 6. Zero-Knowledge Proof Workflow

```mermaid
graph LR
    A[Context Data] --> B[Circom Circuit<br/>Device Verification]
    A --> C[Circom Circuit<br/>Timestamp Verification]
    A --> D[Circom Circuit<br/>Location Verification]
    A --> E[Circom Circuit<br/>Pattern Matching]

    B --> F[SnarkJS<br/>Proof Generation]
    C --> F
    D --> F
    E --> F

    F --> G[ZK Proof]
    G --> H[Verification<br/>Without Data Exposure]
```

## 7. Post-Quantum Cryptography Pipeline

```mermaid
graph TD
    A[Plaintext Data] --> B[Kyber Key Encapsulation]
    B --> C[Shared Secret]
    C --> D[AES-GCM Encryption]
    D --> E[Encrypted Data]
    E --> F[Merkle Tree Logging]
    F --> G[Immutable Audit Trail]
```

## 8. System Deployment Architecture

```mermaid
graph TB
    A[Client Applications] --> B[Load Balancer]

    subgraph "Kubernetes Cluster"
        B --> C[API Service Pods]
        B --> D[Agent Pods]
        B --> E[Database Pods]
        B --> F[Cache Pods]

        C --> G[PostgreSQL<br/>Primary]
        C --> H[Redis<br/>Cache]
        C --> I[S3 Storage]

        D --> J[Neutral Agents]
        D --> K[Permissive Agents]
        D --> L[Strict Agents]
        D --> M[Watchdog Agents]

        E --> G
        F --> H
    end

    subgraph "Monitoring"
        N[Prometheus]
        O[Grafana]
        P[Jaeger]
    end

    C --> N
    D --> N
    G --> N
    H --> N

    N --> O
    C --> P
    D --> P
```

## 9. Data Flow Through the System

```mermaid
graph LR
    A[User Request] --> B[API Gateway]
    B --> C[Authentication<br/>JWT Verification]
    C --> D[Context Verification<br/>ZK Proofs]
    D --> E[Trust Evaluation<br/>Dynamic Scoring]
    E --> F[Agent Consensus<br/>Multi-Party Decision]
    F --> G[Data Retrieval<br/>Encrypted Storage]
    G --> H[Data Decryption<br/>Key Management]
    H --> I[Response to User]

    subgraph "Security Layers"
        C
        D
        E
        F
    end

    subgraph "Data Operations"
        G
        H
    end
```

## 10. API Endpoints Overview

```mermaid
graph TB
    A[ReliQuary API v2.0.0] --> B[Health Endpoints]
    A --> C[Authentication Endpoints]
    A --> D[Vault Management]
    A --> E[Context Verification]
    A --> F[Trust Scoring]
    A --> G[Agent Orchestration]
    A --> H[Audit Logging]
    A --> I[Zero-Knowledge Proofs]

    B --> B1[/health]
    B --> B2[/health/detailed]

    C --> C1[/auth/health]
    C --> C2[/auth/info]
    C --> C3[/auth/login]
    C --> C4[/auth/register]

    D --> D1[/vaults]
    D --> D2[/vaults/{id}]
    D --> D3[/vaults/{id}/secrets]

    E --> E1[/context/verify]
    E --> E2[/context/history]

    F --> F1[/trust/score]
    F --> F2[/trust/history]

    G --> G1[/agents/evaluate]
    G --> G2[/agents/status]

    H --> H1[/logs/summary]
    H --> H2[/logs/entry]

    I --> I1[/zk/verify]
    I --> I2[/zk/generate]
```
