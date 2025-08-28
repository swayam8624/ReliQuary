# RELIQUARY: Enterprise Plug-in Core Workflow

**Owner:** Swayam Singal (Solo Architect, CTO)
**Goal:** Deliver a production-ready, secure, and auditable core cryptographic memory system designed as an API-first enterprise plug-in (Memory-as-a-Service). This workflow details the development phases, encompassing all components from foundational cryptography to deployment readiness, based on the current file tree.

---

## Phase 1: Foundational Setup & Core Cryptographic Backbone

**Objective:** Establish the project's base infrastructure and implement the high-performance, post-quantum cryptographic primitives, including immutable logging.

### **1.1 Project Initialization & Environment Setup**

- **Description:** Setting up the Python project, dependency management, version control, and initial Docker configurations.
- **Files Involved:**
  - `pyproject.toml`: Defines project metadata and dependencies.✅
  - `docker/docker-compose.yml`: Orchestrates API service.✅
  - `docker/Dockerfile.api`: Dockerfile for the FastAPI application.✅
  - `LICENSE`: Project licensing.✅
  - `README.md`: Project overview and setup instructions.
  - `WORKFLOW.md`: This document.✅

### **1.2 Rust Cryptographic Modules (rust_modules/)**

- **Description:** Implementing post-quantum key encapsulation (Kyber), digital signatures (Falcon), and secure symmetric encryption (AES-GCM) in Rust for performance, along with Merkle tree generation for logging. Exposing these functionalities via Foreign Function Interface (FFI) to Python.
- **Files Involved:**
  - `rust_modules/encryptor/Cargo.toml`: Rust package manifest for encryption.✅
  - `rust_modules/encryptor/src/lib.rs`: Rust implementation of PQC (Kyber, Falcon) and AES-GCM, exposing FFI.✅
  - `rust_modules/merkle/Cargo.toml`: Rust package manifest for Merkle tree.✅
  - `rust_modules/merkle/src/lib.rs`: Rust implementation of Merkle tree logic, exposing FFI.✅

### **1.3 Core Cryptography & Utilities (core/crypto/, core/utils/, core/constants.py)**

- **Description:** Developing Python wrappers for Rust FFI, implementing key sharding logic, and providing essential utility functions. Defining global constants.
- **Files Involved:**
  - `core/crypto/__init__.py`: Python package initialization.✅
  - `core/crypto/aes_gcm.py`: Python wrapper for AES-GCM (or direct implementation if not in Rust FFI).✅
  - `core/crypto/key_sharding.py`: Logic for key sharding.✅
  - `core/crypto/rust_ffi_wrappers.py`: Python bindings/wrappers for `rust_modules/encryptor` and `rust_modules/merkle` functionalities (should merge or replace `temp_delete_or_merge_into_wrappers.py` content).✅
  - `core/crypto/temp_delete_or_merge_into_wrappers.py`: (TEMP FILE - **Action: Merge content into `rust_ffi_wrappers.py` and delete this file.**) (NOT NEEDED ✅)
  - `core/constants.py`: Centralized file for global constants and configurations. ( changed to `config_package.py`)✅
  - `core/utils/device_fingerprint.py`: Utility for device fingerprinting.✅
  - `core/utils/file_utils.py`: General file utility functions.✅
  - `core/utils/time_utils.py`: Time-related utility functions.✅

### **1.4 Merkle-Logged Audit Trail (core/merkle_logging/, core/audit.py)**

- **Description:** Implementing an immutable, verifiable audit logging system based on Merkle trees, and preparing for structured audit log export.
- **Files Involved:**
  - `core/merkle_logging/hasher.py`: Hashing functions for Merkle tree.✅
  - `core/merkle_logging/merkle.py`: Merkle tree construction and verification logic.✅
  - `core/merkle_logging/writer.py`: Writes entries to the Merkle log.✅
  - `core/audit.py`: Handles structured audit log management and export mechanisms.✅

---

## Phase 2: Enterprise Identity & Pluggable Data Management

**Objective:** Implement enterprise-grade authentication/authorization and establish an extensible system for managing encrypted vault data.

### **2.1 Enterprise API Authentication & Authorization (auth/)**

- **Description:** Setting up OAuth 2.0 for API client authentication and Role-Based Access Control (RBAC) for granular permissions, alongside the internal DID/WebAuthn for user identity proof.
- **Files Involved:**
  - `auth/did/did_doc.json`: Example DID document.✅
  - `auth/did/resolver.py`: Resolves DIDs.✅
  - `auth/did/signer.py`: Signs DID-related data.✅
  - `auth/oauth.py`: Implementation for OAuth 2.0 client credentials flow and JWT handling.✅
  - `auth/rbac.py`: Defines roles, permissions, and access control logic for API consumers.✅
  - `auth/webauthn/keys.db`: Database for WebAuthn credential storage.✅
  - `auth/webauthn/register.py`: Handles WebAuthn registration.✅
  - `auth/webauthn/verify.py`: Handles WebAuthn verification.✅

### **2.2 Centralized Configuration Management (config/)**

- **Description:** Consolidating and centralizing application configuration for easier management and deployment.
- **Files Involved:**
  - `config/api_config.py`: Configuration for the FastAPI application.✅
  - `config/trust_defaults.json`: Default configuration for trust engine weights.✅
  - `config/vault_trust_templates.yaml`: Templates for vault-specific trust configurations.✅

### **2.3 Pluggable Vault Storage (vaults/storage/)**

- **Description:** Designing an abstract interface for vault storage, with initial implementations for local file storage and placeholders for cloud (S3) and decentralized (IPFS/Arweave) options.
- **Files Involved:**
  - `vaults/storage/base.py`: Abstract base class for storage interfaces.✅
  - `vaults/storage/local.py`: Concrete implementation for local file system storage.✅
  - `vaults/storage/s3.py`: Placeholder for S3/cloud object storage implementation.✅
  - `vaults/storage/ipfs.py`: Placeholder for IPFS integration (V2).✅
  - `vaults/storage/arweave.py`: Placeholder for Arweave integration (V2).✅

### **2.4 Vault Data Models & Manager (vaults/)**

- **Description:** Defining the data models for vaults, their metadata, and the core manager responsible for interacting with the pluggable storage layer.
- **Files Involved:**
  - `vaults/__init__.py`: Python package initialization.✅
  - `vaults/backups`: Directory for local vault backups (for development/testing).
  - `vaults/manager.py`: Orchestrates vault operations (create, retrieve, update, delete) using the chosen `vaults/storage` backend.✅
  - `vaults/models/context_proof.json`: Schema for context proofs associated with vaults.✅
  - `vaults/models/meta.json`: Schema for vault metadata.✅
  - `vaults/models/vault.json`: Schema for encrypted vault data.✅
  - `vaults/trust/trust_score.json`: (Consider moving `trust_score.json` management to `agents/memory/db_manager.py` for persistence, or use as a transient cache/example.)✅
  - `vaults/trust/config.yaml`: (If this is for _per-vault_ trust config, `vaults/manager` should load/manage it, potentially using templates from `config/`).✅
  - `vaults/vault.py`: Defines the Vault object/entity.✅

---

## Phase 3: Contextual Trust & Zero-Knowledge Proof Integration

**Objective:** Implement the core logic for context verification using ZK-SNARKs and the dynamic trust scoring engine.

### **3.1 ZK Circuits & Verifier (zk/)**

- **Description:** Designing and implementing the Zero-Knowledge SNARK circuits for privacy-preserving verification of contextual data, along with the Python runner and verifier.
- **Files Involved:**
  - `zk/circuits/context_proof.circom`: Generic context proof circuit.
  - `zk/circuits/device_proof.circom`: Circuit for device fingerprint verification.
  - `zk/circuits/location_chain.circom`: Circuit for IP/location proof.
  - `zk/circuits/pattern_match.circom`: Circuit for access pattern matching.
  - `zk/circuits/timestamp_verifier.circom`: Circuit for timestamp verification.
  - `zk/examples/inputs/device_input.json`: Example input for device proof circuit.
  - `zk/examples/inputs/location_input.json`: Example input for location proof circuit.
  - `zk/examples/inputs/pattern_input.json`: Example input for pattern proof circuit.
  - `zk/proofs/inputs`: Directory for proofs inputs (from `generate_proof.sh`).
  - `zk/verifier/groth16.json`: Groth16 verification key.
  - `zk/verifier/zk_batch_verifier.py`: Python script for batch ZK proof verification.
  - `zk/verifier/zk_runner.py`: Python script to generate inputs, compute witness, and generate/verify proofs.

### **3.2 Context Verification Service (apps/api/services/context_verifier.py)**

- **Description:** Orchestrates the use of ZK circuits to verify context data provided by enterprise clients.
- **Files Involved:**
  - `apps/api/services/context_verifier.py`: Integrates with `zk/verifier/zk_runner.py` to handle context verification via ZK proofs.

### **3.3 Contextual Trust Engine (core/trust/)**

- **Description:** Implementing the logic for calculating dynamic trust scores based on verified context and historical behavior.
- **Files Involved:**
  - `core/trust/history/sample_history.json`: Example historical behavior data. (For production, this should integrate with `agents/memory/db_manager.py`).
  - `core/trust/scorer.py`: Calculates the trust score based on inputs (verified context, history).
  - `core/rules/examples/default_rule.yaml`: Example of a default rule set. (Should be loaded from `config/` or `vaults/trust/config.yaml` in production).
  - `core/rules/schema.yml`: Schema definition for trust rules.
  - `core/rules/validator.py`: Validates trust rule configurations.
  - `apps/api/services/trust_engine.py`: API service layer for the trust engine.
  - `apps/api/services/rule_enforcer.py`: Enforces rules based on trust scores.

---

## Phase 4: Multi-Agent Consensus & Enterprise API Development

**Objective:** Develop the intelligent multi-agent quorum for access decisions and expose all core functionalities via a robust FastAPI API.

### **4.1 Multi-Agent Quorum (agents/)**

- **Description:** Implementing the LangGraph-based multi-agent system, defining individual agent behaviors, and managing their persistent memory.
- **Files Involved:**
  - `agents/decision_orchestrator.py`: Orchestrates the overall agent decision process.
  - `agents/graph.py`: Defines the LangGraph structure and agent workflow.
  - `agents/memory/db_manager.py`: Manages persistent storage for agent memory and trust history.
  - `agents/memory/encrypted_memory.py`: Handles encryption of sensitive agent memory.
  - `agents/nodes/neutral_agent.py`: Logic for the neutral agent.
  - `agents/nodes/permissive_agent.py`: Logic for the permissive agent.
  - `agents/nodes/strict_agent.py`: Logic for the strict agent.
  - `agents/nodes/watchdog_agent.py`: Logic for the watchdog agent.
  - `agents/tools/context_checker.py`: Tool for agents to check context details.
  - `agents/tools/decrypt_tool.py`: Tool for agents to (potentially) trigger decryption.
  - `agents/tools/trust_checker.py`: Tool for agents to evaluate trust scores.

### **4.2 Agent Orchestration Service (apps/api/services/agent_orchestrator.py)**

- **Description:** The API service responsible for invoking the multi-agent quorum and receiving their consensus decision.
- **Files Involved:**
  - `apps/api/services/agent_orchestrator.py`: Integrates with `agents/decision_orchestrator.py`.

### **4.3 FastAPI Enterprise API (apps/api/)**

- **Description:** Building the primary API endpoints for vault management, context submission, trust evaluation, and data access. Includes schema definitions and middleware.
- **Files Involved:**
  - `apps/api/main.py`: Main FastAPI application instance.
  - `apps/api/middleware/logging.py`: Custom logging middleware.
  - `apps/api/requirements.txt`: (Will be superseded by `pyproject.toml`).
  - `apps/api/schemas/agent.py`: Pydantic schemas for agent-related data.
  - `apps/api/schemas/context.py`: Pydantic schemas for context data.
  - `apps/api/schemas/trust.py`: Pydantic schemas for trust data.
  - `apps/api/schemas/vault.py`: Pydantic schemas for vault data.
  - `apps/api/services/encryptor.py`: Service for invoking Rust encryption/decryption (via `core/crypto/rust_ffi_wrappers.py`).
  - `apps/api/endpoints/agent.py`: API router for agent-related queries/config.
  - `apps/api/endpoints/audit.py`: API router for audit log retrieval.
  - `apps/api/endpoints/context.py`: API router for context submission/verification.
  - `apps/api/endpoints/trust.py`: API router for trust evaluation/queries.
  - `apps/api/endpoints/vault.py`: API router for vault creation, access, and management.

---

## Phase 5: SDK, Observability, Testing & Deployment Readiness

**Objective:** Provide robust SDKs for enterprise integration, comprehensive system observability, thorough testing, and production deployment artifacts.

### **5.1 Enterprise SDK Development (sdk/python/)**

- **Description:** Creating a user-friendly Python SDK for enterprises to interact with the RELIQUARY API.
- **Files Involved:**
  - `sdk/python/__init__.py`: Python package initialization. ✅
  - `sdk/python/client.py`: The core Python client for the RELIQUARY API. ✅
  - `sdk/python/exceptions.py`: Custom exceptions for the SDK. ✅
  - `sdk/python/models/api_schemas.py`: Replicated/imported API schemas for type-safe SDK usage. ✅

### **5.2 System Observability & Monitoring (core/metrics.py, apps/api/middleware/logging.py)**

- **Description:** Implementing metrics exposition and structured logging for monitoring system health, performance, and security events.
- **Files Involved:**
  - `core/metrics.py`: Exposes Prometheus/OpenTelemetry metrics. ✅
  - `apps/api/middleware/logging.py`: Ensures all API interactions are logged in a structured format. ✅

### **5.3 Comprehensive Testing (tests/)**

- **Description:** Developing unit, integration, and SDK tests to ensure functionality, security, and performance.
- **Files Involved:**
  - `tests/api/test_vault_access.py`: Integration tests for vault access API. ✅
  - `tests/sdk/test_python_client.py`: Tests for the Python SDK. ✅
  - `tests/test_agent_decision.py`: Unit/integration tests for agent decision logic. ✅
  - `tests/test_context_proof.py`: Tests for ZK context proof generation and verification. ✅
  - `tests/test_crypto.py`: Tests for Rust cryptographic modules and Python wrappers. ✅
  - `tests/test_rule_enforcement.py`: Tests for the trust rule enforcement. ✅

### **5.4 Operational Scripts (scripts/)**

- **Description:** Providing utility scripts for development, testing, and enterprise client setup.
- **Files Involved:**
  - `scripts/create_vault_template.py`: Helps create new vault schemas/templates for enterprises. ✅
  - `scripts/demo_access.py`: Script for demonstrating API access flow. ✅
  - `scripts/dev_start.sh`: Starts the development environment. ✅
  - `scripts/generate_api_key.py`: Utility to generate API keys for enterprise clients. ✅
  - `scripts/generate_proof.sh`: Script to generate ZK proofs for testing. ✅
  - `scripts/health_check.py`: Basic health check script for API endpoint. ✅
  - `scripts/reset_vault.py`: Utility to reset vault data for testing. ✅

### **5.5 Kubernetes Deployment Readiness (k8s/)**

- **Description:** Preparing Kubernetes manifests for cloud-native deployment and scalability.
- **Files Involved:**
  - `k8s/deployment.yaml`: Kubernetes Deployment manifest. ✅
  - `k8s/ingress.yaml`: Kubernetes Ingress controller configuration. ✅
  - `k8s/service.yaml`: Kubernetes Service manifest. ✅

### **5.6 Documentation (docs/)**

- **Description:** Creating comprehensive documentation for developers and enterprise integrators.
- **Files Involved:**
  - `docs/api_reference.md`: Detailed API reference documentation (e.g., generated from OpenAPI spec). ✅
  - `docs/developer_guide.md`: Guides for setting up, integrating, and using RELIQUARY. ✅
