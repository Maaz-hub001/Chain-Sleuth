# ChainSleuth Architecture & Engineering Decisions Log (DECISION.md)

This document records all architectural, technical, security, design, and implementation decisions taken during the engineering of the **ChainSleuth** platform.

---

## Decision Index

1. [DEC-001: Monorepo Structure & Separation of Concerns](#dec-001-monorepo-structure--separation-of-concerns)
2. [DEC-002: Dual-Mode Database Strategy (PostgreSQL & SQLite Fallback)](#dec-002-dual-mode-database-strategy-postgresql--sqlite-fallback)
3. [DEC-003: Provider-Independent Blockchain Data Ingestion Layer](#dec-003-provider-independent-blockchain-data-ingestion-layer)
4. [DEC-004: Multi-Layer Deterministic Detection Engine Before LLM Invocations](#dec-004-multi-layer-deterministic-detection-engine-before-llm-invocations)
5. [DEC-005: Zero-Cost Offline AI Investigation Agent with Extensible LLM Support](#dec-005-zero-cost-offline-ai-investigation-agent-with-extensible-llm-support)
6. [DEC-006: Hybrid RAG Pipeline (BM25 Keyword + Vector Cosine Similarity)](#dec-006-hybrid-rag-pipeline-bm25-keyword--vector-cosine-similarity)
7. [DEC-007: Canonical Report Serialization & Dual-Level SHA-256 Verification](#dec-007-canonical-report-serialization--dual-level-sha-256-verification)
8. [DEC-008: Smart Contract Anchoring via Minimalist Registry](#dec-008-smart-contract-anchoring-via-minimalist-registry)
9. [DEC-009: Dark-Mode Investigator Workspace & Graph Visualization Strategy](#dec-009-dark-mode-investigator-workspace--graph-visualization-strategy)
10. [DEC-010: Evidence Chain of Custody & Traceability Rules](#dec-010-evidence-chain-of-custody--traceability-rules)
11. [DEC-011: Investigation-Scoped Node Keying Strategy](#dec-011-investigation-scoped-node-keying-strategy)
12. [DEC-012: Zero-Dependency Local Vectorization Strategy](#dec-012-zero-dependency-local-vectorization-strategy)

---

### DEC-001: Monorepo Structure & Separation of Concerns
- **Context:** The application requires a modern React frontend, a FastAPI backend, smart contracts, threat intelligence datasets, and Docker infrastructure.
- **Decision:** Place `frontend/`, `backend/`, `contracts/`, `data/`, and `scripts/` in the repository root. Maintain strict isolation: frontend interacts only via standard HTTP/JSON REST API (`/api/v1`), backend holds all secrets, smart contracts compile independently.
- **Consequence:** Clean developer experience, isolated testing, straightforward containerization.

---

### DEC-002: Dual-Mode Database Strategy (PostgreSQL & SQLite Fallback)
- **Context:** The production specification targets PostgreSQL with SQLAlchemy, but local environments and offline tests might not have a running PostgreSQL daemon.
- **Decision:** Implement SQLAlchemy database models using portable types (`JSON`, `String`, `DateTime`, `Boolean`) that operate identically on PostgreSQL (`postgresql://...`) and SQLite (`sqlite:///./chainsleuth.db`). The backend checks `DATABASE_URL` and defaults gracefully to SQLite if PostgreSQL is not configured, while docker-compose provisions a full PostgreSQL 16 container.
- **Consequence:** Immediate zero-friction local development and testing, zero external dependencies to run basic tests, while retaining 100% production-ready PostgreSQL compliance.

---

### DEC-003: Provider-Independent Blockchain Data Ingestion Layer
- **Context:** EVM JSON-RPC nodes do not index complete transaction histories for arbitrary wallet addresses without an archival tracing node. Etherscan requires API keys; public Blockscout provides open endpoints; offline demos need reproducible fixtures.
- **Decision:** Implement an abstract `BlockchainAdapter` with 4 concrete providers:
  1. `EtherscanAdapter`: Standard indexed API when an API key is provided.
  2. `BlockscoutAdapter`: Open-source block explorer API requiring no mandatory API keys.
  3. `RpcAdapter`: Standard EVM JSON-RPC provider (via Web3.py) for direct block, tx receipt, and code inspection.
  4. `DemoFixtureAdapter`: Fully documented, realistic local data provider loaded with verifiable exploit flows (e.g., Ronin exploiter, Tornado Cash, fan-out disbursement) for offline verification.
  - The adapter engine includes explicit coverage metadata: `coverage_level`, `data_source`, `limitations`.
- **Consequence:** Transparent handling of missing data without fabricating results.

---

### DEC-004: Multi-Layer Deterministic Detection Engine Before LLM Invocations
- **Context:** Relying solely on LLMs for financial fraud detection introduces hallucinations, non-determinism, and high token costs.
- **Decision:** Build a suite of 7 deterministic graph-based and transaction-based detectors:
  - `UnusualFanInOutDetector`
  - `RapidMovementDetector`
  - `ConsolidationDetector`
  - `CircularTransferDetector`
  - `RepeatedTransfersDetector`
  - `KnownEntityDetector`
  - `HighGasZeroValueSpamDetector`
  Every finding outputs explicit fields: `detector_id`, `severity`, `status` (Confirmed observation vs Suspicious pattern vs Insufficient evidence), `confidence`, `evidence_ids`, and `counterevidence`.
- **Consequence:** 100% auditable, repeatable findings where every claim maps directly to transaction records.

---

### DEC-005: Zero-Cost Offline AI Investigation Agent with Extensible LLM Support
- **Context:** Requirement mandates that the application must NOT require paid API keys to start and run core investigation workflows.
- **Decision:** Implement a controlled multi-step state machine agent. If `LLM_PROVIDER` is set to `heuristic` (default), the agent uses a deterministic synthesis engine that evaluates findings, aggregates counterevidence, matches threat intelligence, and constructs the validated Pydantic report. If configured with `openai`, `gemini`, `anthropic`, or local `ollama`, the agent enhances the analysis with an LLM prompt under strict guardrails.
- **Consequence:** Core application works offline immediately without any external API billing.

---

### DEC-006: Hybrid RAG Pipeline (BM25 Keyword + Vector Cosine Similarity)
- **Context:** RAG must retrieve relevant threat advisories and exploit post-mortems without mandatory external vector database daemons or cloud embedding APIs.
- **Decision:** Implement a hybrid retrieval system combining TF-IDF / BM25 term matching with local vector cosine similarity, alongside pluggable Qdrant vector store support. Store authentic threat intelligence documents in `data/knowledge_base/` with cryptographic content hashes.
- **Consequence:** Fast, local, reproducible document retrieval with verifiable citations down to source URLs and document hashes.

---

### DEC-007: Canonical Report Serialization & Dual-Level SHA-256 Verification
- **Context:** Reports must have tamper-evident integrity that can be verified independently on-chain or off-chain.
- **Decision:** Establish a strict canonical JSON schema (recursive sorted keys, formatted floats, excluded mutable fields like timestamps of verification) and compute SHA-256 over canonical UTF-8 bytes. Verification operates in two modes:
  1. *Local Cryptographic Verification*: Recomputes the canonical SHA-256 and compares against the recorded hash.
  2. *On-Chain Anchor Verification*: Queries the `InvestigationRegistry` smart contract to verify whether the hash was anchored to an EVM testnet/mainnet.
- **Consequence:** Allows the frontend to demonstrate live tampering detection (editing 1 character immediately invalidates the cryptographic hash).

---

### DEC-008: Smart Contract Anchoring via Minimalist Registry
- **Context:** Reports need verifiable immutable proof of existence without storing private data, full reports, or personal identifiers on-chain.
- **Decision:** Implement `InvestigationRegistry.sol` storing only `(bytes32 reportHash, string reportId, string targetIdentifier, address reporter, uint256 timestamp)`. Prevent duplicate registration and emit indexed events.
- **Consequence:** Minimal gas consumption, zero PII on-chain, and clean verification via public view methods.

---

### DEC-009: Dark-Mode Investigator Workspace & Graph Visualization Strategy
- **Context:** The frontend must provide a credible, high-density, professional cybersecurity UI for analysts.
- **Decision:** Use Tailwind CSS with a tailored slate/navy palette (`#090D16`, `#0F172A`, `#1E293B`, `#38BDF8`), Lucide icons, and React Flow for transaction graphs with custom nodes: Target Node, Normal Wallet Node, Contract Node, and Verified Known Entity Node. Include edge metrics (amount, asset, direction, tx hash).
- **Consequence:** High-impact, responsive, professional investigator experience.

---

### DEC-010: Evidence Chain of Custody & Traceability Rules
- **Context:** Analysts and compliance officers cannot rely on black-box alerts.
- **Decision:** Every generated finding must cite unique `evidence_ids` referring to observed transaction hashes, graph paths, or threat document chunks. Findings must include counterevidence and explicit limitations.
- **Consequence:** Prevents over-claiming and enforces investigative rigor.

---

### DEC-011: Investigation-Scoped Node Keying Strategy
- **Context:** Node IDs generated as short prefixes (`node-0x...`) collided across multiple investigations in the database under SQLite/PostgreSQL unique constraints.
- **Decision:** Scope node identifiers with both the target investigation ID and the normalized address substring (`node-{inv_id[:8]}-{addr[2:10]}`).
- **Consequence:** Guarantees strict cross-investigation isolation, prevents primary key collisions, and maintains referential integrity.

---

### DEC-012: Zero-Dependency Local Vectorization Strategy
- **Context:** RAG pipelines frequently require heavy ML model downloads (several GBs) or network-dependent embedding APIs that fail offline or run into rate limits.
- **Decision:** Implement a deterministic `LocalHybridVectorizer` that hashes token n-grams into a fixed 128-dimensional L2-normalized vector space, combined with BM25 keyword matching. Provide an optional OpenAI embedding hook when an API key is explicitly configured.
- **Consequence:** Instantaneous offline initialization, zero multi-gigabyte model downloads, and robust semantic search across cybersecurity threat documents.

---

### DEC-013: WhisperFlow Voice-Driven Engineering Workflow & Prompt Provenance
- **Context:** Rapid full-stack development of complex cybersecurity and blockchain architectures benefits from voice-driven dictation, prompt streaming, and conversational steering over manual boilerplate typing.
- **Decision:** Capture and preserve all voice-driven commands, architectural prompts, and iterative steering directives in a structured `whisperflow/` repository archive (`whisperflow/manifest.json`, `whisperflow/sessions/*.json`, and `whisperflow/transcripts/raw_voice_stream.jsonl`). Use OpenAI Whisper (`large-v3`) transcription with voice activity detection (VAD), chunk offsets, and confidence metrics.
- **Consequence:** Provides verifiable provenance of voice-directed engineering, documents prompt evolution across all 8 development sessions, and demonstrates end-to-end voice-to-code workflow execution.

