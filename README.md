# ChainSleuth

> **Investigate the chain. Follow the evidence.**

ChainSleuth is an AI-assisted blockchain forensic investigation platform that helps security analysts, compliance officers, and auditors trace EVM transactions, construct interactive counterparty graphs, evaluate suspicious multi-hop laundering topologies, retrieve relevant threat intelligence, and generate tamper-evident investigation reports.

---

## 1. System Architecture & Features

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ChainSleuth Investigator UI                     │
│    (React 18, TypeScript, Tailwind CSS, React Flow Graph, Recharts)     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP REST (FastAPI /api/v1)
┌──────────────────────────────────▼─────────────────────────────────────┐
│                          ChainSleuth Backend API                       │
│    - Controlled State Machine Workflow (12-stage forensic agent)       │
│    - Deterministic Detection Engine (6 topological & temporal rules)   │
│    - Bounded Multi-Hop Graph Builder (Cycle detection, Hub analysis)   │
│    - Hybrid RAG Pipeline (BM25 Keyword + Local Cosine Vectorizer)      │
│    - Canonical JSON Serializer & SHA-256 Hasher                        │
└───────┬──────────────────────────┬───────────────────────────┬─────────┘
        │                          │                           │
┌───────▼──────────────┐ ┌─────────▼──────────────┐ ┌──────────▼─────────┐
│ Blockchain Adapters  │ │ Database Persistence   │ │ Smart Contract     │
│ - Blockscout API     │ │ - PostgreSQL 16        │ │ - Solidity 0.8.20  │
│ - EVM JSON-RPC       │ │ - SQLite (local zero-  │ │   Investigation    │
│ - Etherscan API      │ │   config fallback)     │ │   Registry         │
│ - Offline Fixture    │ │ - SQLAlchemy 2.0       │ │ - SHA-256 Anchoring│
└──────────────────────┘ └────────────────────────┘ └────────────────────┘
```

### Key Capabilities
1. **Real Blockchain Data Ingestion**: Clean provider adapter supporting public Blockscout indexing, direct EVM JSON-RPC nodes, optional Etherscan developer APIs, and reproducible offline sandbox fixtures.
2. **Interactive Transaction Graph**: Built with React Flow featuring custom styled nodes (Target, Wallet, Mixer, Sanctioned Entity, Exchange, Contract) with directional transfer values and a slide-out metadata drawer.
3. **Deterministic Detection Rules**:
   - `DET_KNOWN_ENTITY`: Curated attribution matches against OFAC/sanctions lists and known exploits.
   - `DET_CIRCULAR_LOOP`: Closed directed graph cycle detection (round-tripping & wash trading).
   - `DET_RAPID_RELAY`: Short dwell time (< 30 min) transit wallets.
   - `DET_FAN_IN_OUT`: Explosive disbursement across multiple counterparties.
   - `DET_CONSOLIDATION`: Inflow pooling followed by bulk sweep.
   - `DET_REPEATED_STRUCTURING`: Smurfing patterns with near-identical amounts.
4. **Threat Intelligence RAG**: Pre-loaded starter corpus of verified advisories (Tornado Cash sanctions, Euler Finance flash loan trace, Permit phishing, laundering topologies) with zero heavy model dependencies.
5. **Tamper-Evident Report Verification**: Canonical JSON serialization (recursive sorted keys, float normalization, excluded mutable fields) and SHA-256 verification. Includes an interactive anti-tampering sandbox where altering a single byte produces an immediate hash mismatch.
6. **Smart Contract Anchoring**: Solidity `InvestigationRegistry.sol` for immutable on-chain proof of existence without storing private data on-chain.

---

## 2. Quick Start & Local Setup

### Prerequisites
- **Node.js** v18+ and **npm**
- **Python** 3.11+
- **Docker & Docker Compose** (Optional, for containerized run)

### Method A: Local Native Development (Recommended)

1. **Clone and Configure Environment:**
   ```bash
   # Copy environment template
   copy .env.example .env
   ```

2. **Setup Python Virtual Environment & Install Backend Dependencies:**
   ```powershell
   python -m venv backend/.venv
   backend\.venv\Scripts\pip install -r backend/requirements.txt
   ```

3. **Install Contract & Frontend Dependencies:**
   ```powershell
   cd contracts && npm install && cd ..
   cd frontend && npm install && cd ..
   ```

4. **Launch Application:**
   - **Windows:** Run `scripts\run_dev.bat`
   - **Or Manual Commands:**
     ```powershell
     # Terminal 1: Backend API (FastAPI)
     $env:PYTHONPATH='backend'
     backend\.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload

     # Terminal 2: Frontend (Vite)
     cd frontend
     npm run dev
     ```

5. Access the application:
   - **Investigator Workspace:** [http://localhost:5173](http://localhost:5173)
   - **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **API Health Telemetry:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Method B: Docker Compose Deployment

```bash
docker compose up --build
```
This builds and starts:
- `db`: PostgreSQL 16 container with persistent volumes
- `backend`: FastAPI Python service connected to PostgreSQL
- `frontend`: React static build served via Nginx with reverse proxy to `/api/`

---

## 3. Automated Test Suite

ChainSleuth includes an end-to-end automated test suite spanning smart contracts, backend unit/integration tests, and frontend production builds.

To run the complete test suite at once:
- **Windows:** Run `scripts\test_all.bat`
- **Linux/macOS:** Run `npm run test` across workspaces

### Individual Test Commands:
```powershell
# 1. Smart Contract Tests (Hardhat)
cd contracts
npx hardhat test

# 2. Backend Unit & Integration Tests (Pytest)
$env:PYTHONPATH='backend'
backend\.venv\Scripts\pytest backend/tests -v

# 3. Frontend Type-Check & Production Build (Vite)
cd frontend
npm run build
```

---

## 4. Reproducible Demonstration Walkthrough

Refer to [DEMO_GUIDE.md](file:///c:/Users/ac/HH_GOA/DEMO_GUIDE.md) for the complete 10-step walkthrough:
1. Submitting a wallet investigation.
2. Ingesting transactions and rendering the multi-hop graph.
3. Reviewing deterministic fraud findings and counterevidence.
4. RAG threat intelligence matching.
5. Generating and cryptographically verifying the canonical SHA-256 report hash.
6. Anchoring to the testnet smart contract.
7. Demonstrating tamper detection failure in the interactive anti-tampering sandbox.

---

## 5. Architectural & Implementation Decisions

All engineering decisions, data contracts, and design trade-offs are documented in [DECISION.md](file:///c:/Users/ac/HH_GOA/DECISION.md).
Current build status and verified test metrics are tracked in [BUILD_STATUS.md](file:///c:/Users/ac/HH_GOA/BUILD_STATUS.md).
