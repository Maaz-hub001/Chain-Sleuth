# ChainSleuth Forensic Investigation Demonstration Walkthrough

This guide provides a reproducible walkthrough demonstrating the end-to-end capabilities of **ChainSleuth**.

---

## Prerequisites & Startup

1. **Start the Platform:**
   - **Windows:** Double-click `scripts\run_dev.bat` or run:
     ```powershell
     # Terminal 1: Backend
     $env:PYTHONPATH='backend'
     backend\.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload

     # Terminal 2: Frontend
     cd frontend
     npm run dev
     ```
   - **Docker:**
     ```bash
     docker compose up --build
     ```

2. Open the investigator workspace in your browser at:  
   👉 **`http://localhost:5173`**

---

## 10-Step Demonstration Walkthrough

### Step 1: Landing Page & Capabilities Overview
- Navigate to `http://localhost:5173`.
- Observe the dark-mode cyber forensic workspace, architectural pillars, and the honest disclosure of what public on-chain heuristics can and cannot establish.
- Click **"Launch Investigation"** or **"Open Dashboard"**.

---

### Step 2: Initiating a Multi-Hop Investigation
- On the **New Investigation** page (`/investigations/new`):
- Click the preset button: **"Load Multi-Hop Demo Wallet"**.
- This pre-populates:
  - **Target Identifier:** `0x742d35Cc6634C0532925a3b844Bc454e4438f44e`
  - **Network:** `Demo Sandbox (Offline Fixture)`
  - **Max Graph Depth:** `2 hops`
  - **Max Transactions:** `100`
  - **Fixture Toggle:** Checked (enabling reproducible offline forensic traces without third-party rate limits).
- Click **"Start Investigation"**.

---

### Step 3: Automated Forensic Ingestion & Detection
- The platform executes the 12-stage state machine workflow:
  1. Identifies target as a 40-character EVM address.
  2. Ingests normalized transactions (inflows from Lazarus/Ronin tagged entity, rapid outbound fan-out).
  3. Constructs the bounded directed network graph.
  4. Runs 6 deterministic rule detectors.
  5. Queries the Threat Intelligence RAG knowledge base for matched topologies (Tornado Cash, rapid relay, laundering patterns).
  6. Generates a structured report and calculates its canonical SHA-256 digest.
- Automatically redirects to the **Investigation Detail Workspace** (`/investigations/{id}`).

---

### Step 4: Inspecting Summary & Coverage
- On the **Summary** tab:
  - Observe target address, chain ID, data provider (`demo_fixture` / `blockscout_indexed`), and coverage limitations.
  - Review risk alert badges: `CRITICAL`, `HIGH`, `MEDIUM`.

---

### Step 5: Interactive Transaction Graph Exploration
- Click the **"Transaction Graph"** tab.
- Observe the React Flow canvas rendering:
  - **Target Node** (Electric Cyan center node: `0x742d...f44e`)
  - **Attributed Mixer Node** (Red node: `0xd90e...31b` Tornado Cash Router)
  - **Sanctioned Inflow Node** (Red node: `0x098b...f96` Ronin Exploiter 1)
  - **Exchange Node** (Amber node: `0x28c6...1d60` Binance Hot Wallet 14)
  - **Transit Relays** (Intermediate hopping nodes)
- **Interactive actions:**
  - Click on the **Tornado Cash node** to open the details drawer showing verified OFAC attribution.
  - Click on any **directed edge** to inspect transferred ETH amount, block number, and tx hash.
  - Use the top-left search input to filter or highlight any address.

---

### Step 6: Reviewing Chronological Timeline
- Click the **"Timeline"** tab.
- Inspect the timestamp-ordered transaction stream.
- Note how 50 ETH inflows were rapidly divided into ~15 ETH tranches within 75 seconds.

---

### Step 7: Evaluating Forensic Findings & Counterevidence
- Click the **"Findings"** tab.
- Inspect rule-based findings:
  1. **Direct Counterparty Attribution: Tornado Cash: Router (CRITICAL)**
  2. **Direct Counterparty Attribution: Ronin Exploiter 1 (CRITICAL)**
  3. **Rapid Relay Transit Pattern Detected (HIGH)**
  4. **Circular Transfer Pattern / Round-Tripping (HIGH)**
  5. **Rapid Fan-Out Fund Dispersion (HIGH)**
  6. **Structured Repeated Transfers (MEDIUM)**
- Notice that every finding explicitly articulates **Alternative Explanations** and **Counterevidence** to prevent premature false-positive accusations.

---

### Step 8: Verifying RAG Citations & Threat Intelligence
- Click the **"AI Analysis"** tab.
- Review the synthesized narrative detailing hypotheses H1, H2, and H3.
- In the report preview, notice citations to authentic published security advisories (OFAC Sanctions Bulletin, FATF Red Flag Indicators, Euler Exploit Case Study).

---

### Step 9: Cryptographic Report Verification & Testnet Anchoring
- Click the **"Report & Verification"** tab.
- Observe the **Canonical SHA-256 Digest**:
  ```
  e.g., 45e39296ca30b5bcff12d40621d08ac0143d40aff4bd749f72d54c070d60362a
  ```
- Click **"Verify Cryptographic Integrity"**:
  - The backend recalculates SHA-256 over canonical JSON bytes.
  - Displays green verification confirmation: `VERIFIED: Canonical report content is cryptographically authentic`.
- Click **"Anchor to Sepolia Registry"**:
  - Simulates recording the cryptographic hash to the `InvestigationRegistry` smart contract.
  - Badge updates to `On-Chain Anchored`.

---

### Step 10: Live Anti-Tampering Demonstration
- In the **Report & Verification** tab, click **"Test Tamper Detection Demonstration"** to open the interactive sandbox.
- In the JSON text area, alter any single value (e.g. change `"severity": "CRITICAL"` to `"severity": "LOW"` or modify an amount).
- Click **"Re-Verify Tampered Payload"**.
- **Result:**
  - Notice the instant catastrophic hash change.
  - Red alert displays:
    `INTEGRITY ALERT: Report content has been altered or tampered with. Hash mismatch.`
- Click **"Reset to Authentic"** to restore original bytes.
