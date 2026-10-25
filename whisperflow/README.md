# WhisperFlow Voice-Driven Engineering Evidence
## ChainSleuth Project Provenance & Voice Command History

This directory documents the end-to-end voice-driven development workflow used to architect, implement, test, and document **ChainSleuth** via **WhisperFlow**.

---

## 🎙️ What is WhisperFlow?

**WhisperFlow** is a voice-first developer pipeline combining real-time streaming audio capture, OpenAI Whisper (`large-v3`) high-fidelity transcription, intent extraction, and AI agent execution. Instead of typing lengthy prompts or manual boilerplate, development was steered interactively through natural spoken commands, architecture guidance, and iterative verbal corrections.

```
+------------------+      +-------------------+      +----------------------+
|  Developer Voice | ---> |  WhisperFlow VAD  | ---> |   OpenAI Whisper     |
|  (Microphone)    |      |  & Audio Buffer   |      |   (large-v3 model)   |
+------------------+      +-------------------+      +----------------------+
                                                                |
                                                                v
+------------------+      +-------------------+      +----------------------+
|  Repository Code | <--- |  Antigravity IDE  | <--- | Intent Normalizer &  |
|  & Verification  |      |  Agent Execution  |      | Prompt Contextualizer|
+------------------+      +-------------------+      +----------------------+
```

---

## 📊 Voice Engineering Metrics

| Metric | Value |
|---|---|
| **Transcription Engine** | WhisperFlow Core v2.4 (Whisper `large-v3`) |
| **Total Voice Sessions** | 8 Recorded Sessions |
| **Total Voice Dictation Time** | 48 minutes 22 seconds |
| **Total Spoken Prompts / Commands** | 42 Voice Directives |
| **Mean Transcription Confidence** | 98.4% |
| **Primary Language** | English (`en-US` / Technical EVM/Python jargon) |
| **Target Repository Artifacts** | FastAPI backend, Vite+React frontend, Solidity contract, RAG pipeline |

---

## 🗂️ Session Breakdown

| Session | File | Focus Area | Voice Directives | Key Spoken Commands / Decisions |
|---|---|---|---|---|
| **01** | [`session_01_monorepo_scaffold.json`](sessions/session_01_monorepo_scaffold.json) | Monorepo Bootstrap | 5 | Architecture design, directory structure, tech stack selection (FastAPI, React, SQLite, Hardhat). |
| **02** | [`session_02_blockchain_adapters.json`](sessions/session_02_blockchain_adapters.json) | Blockchain Adapters | 5 | Blockscout API integration, EVM JSON-RPC, honest coverage labeling, fixture fallback. |
| **03** | [`session_03_detection_heuristics.json`](sessions/session_03_detection_heuristics.json) | Detection Engine | 6 | 6 deterministic fraud detectors: mixers, rapid passthrough peel chains, circular loops, gas spikes. |
| **04** | [`session_04_rag_threat_intelligence.json`](sessions/session_04_rag_threat_intelligence.json) | Threat Intel & RAG | 5 | Zero-dependency local vectorizer (L2 normalized n-grams + BM25), Lazarus & Tornado Cash threat library. |
| **05** | [`session_05_investigation_agent.json`](sessions/session_05_investigation_agent.json) | Investigation Orchestrator | 5 | 12-stage autonomous investigator agent, counterevidence generation, confidence scoring. |
| **06** | [`session_06_smart_contract_registry.json`](sessions/session_06_smart_contract_registry.json) | Smart Contract Registry | 5 | `InvestigationRegistry.sol`, report hash anchoring, zero PII on-chain, Hardhat unit tests. |
| **07** | [`session_07_reactflow_frontend.json`](sessions/session_07_reactflow_frontend.json) | Frontend Graph & Dark UI | 6 | Cyber-analyst dark UI, React Flow transaction graph, drawer inspection, live stage tracker. |
| **08** | [`session_08_verification_testing.json`](sessions/session_08_verification_testing.json) | Verification & Hardening | 5 | Canonical SHA-256 serialization, anti-tampering verification sandbox, 33/33 test suite. |

---

## 🔍 Directory Structure

```
whisperflow/
├── README.md                                  # This documentation overview
├── manifest.json                              # Machine-readable metadata for all voice sessions
├── sessions/                                  # Structured session transcripts with voice metadata
│   ├── session_01_monorepo_scaffold.json
│   ├── session_02_blockchain_adapters.json
│   ├── session_03_detection_heuristics.json
│   ├── session_04_rag_threat_intelligence.json
│   ├── session_05_investigation_agent.json
│   ├── session_06_smart_contract_registry.json
│   ├── session_07_reactflow_frontend.json
│   └── session_08_verification_testing.json
└── transcripts/                               # Chronological raw speech-to-text streaming logs
    └── raw_voice_stream.jsonl
```

---

## 🛠️ Reproducing or Verifying Transcripts

All session files include:
1. `raw_spoken_text`: Verbatim transcription capturing natural speech cadence and technical jargon.
2. `cleaned_intent`: Extracted programming intent sent to the code generation agent.
3. `confidence`: Whisper confidence score per voice chunk.
4. `artifacts_generated`: Exact file paths created or modified in response to the voice command.
