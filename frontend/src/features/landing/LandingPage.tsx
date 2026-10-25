import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  GitFork,
  Search,
  FileCheck2,
  Lock,
  ArrowRight,
  Database,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  ExternalLink
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-sleuth-950 text-slate-100 flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 border-b border-sleuth-800">
        <div className="absolute inset-0 cyber-grid opacity-40 pointer-events-none" />
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-cyanAccent-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sleuth-850 border border-sleuth-700 text-xs text-cyanAccent-400 font-mono mb-6">
            <span className="w-2 h-2 rounded-full bg-cyanAccent-400 animate-ping" />
            EVM Blockchain Fraud & Evidence Intelligence Platform
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-6">
            Investigate the chain. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyanAccent-400 to-sky-300">
              Follow the evidence.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-300 leading-relaxed mb-8">
            ChainSleuth is an AI-assisted blockchain forensic investigation platform that traces wallet counterparties,
            detects multi-hop laundering topologies, cross-references security threat advisories, and generates tamper-evident reports.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/investigations/new"
              className="flex items-center gap-2 px-6 py-3 rounded-lg bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-bold text-sm tracking-wide transition-all shadow-lg shadow-cyanAccent-500/20 active:scale-95"
            >
              <span>Launch Investigation</span>
              <ArrowRight className="w-4 h-4 text-slate-950" />
            </Link>

            <Link
              to="/dashboard"
              className="flex items-center gap-2 px-6 py-3 rounded-lg bg-sleuth-850 hover:bg-sleuth-800 text-slate-200 border border-sleuth-700 font-medium text-sm transition-all"
            >
              <span>Open Dashboard</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 4 Architecture Pillars */}
      <section className="py-16 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Ground-Truth Investigative Intelligence</h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Every finding links back to raw transactions, graph paths, or verified security advisories. Zero fabricated evidence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl hover:border-sleuth-700 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-cyanAccent-500/10 border border-cyanAccent-500/30 flex items-center justify-center text-cyanAccent-400 mb-4">
              <GitFork className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base mb-2">Multi-Hop Graph Tracing</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Explores bounded directional transactions, cycle loops, rapid relay transit nodes, and asset disbursement topologies.
            </p>
          </div>

          <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl hover:border-sleuth-700 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base mb-2">Deterministic Detectors</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Six rule-based detection algorithms identifying fan-out dispersion, smurfing, circular round-trips, and mixer counterparties.
            </p>
          </div>

          <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl hover:border-sleuth-700 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base mb-2">Threat Intelligence RAG</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Hybrid keyword and vector retrieval cross-referencing OFAC sanction notices, exploit post-mortems, and drainer advisories.
            </p>
          </div>

          <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl hover:border-sleuth-700 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 mb-4">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base mb-2">Cryptographic Integrity</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Canonical JSON report serialization with SHA-256 verification and optional testnet smart contract registry anchoring.
            </p>
          </div>
        </div>
      </section>

      {/* Honest Capabilities & Limits Disclosure */}
      <section className="py-12 bg-sleuth-900/40 border-y border-sleuth-800">
        <div className="max-w-4xl mx-auto px-4">
          <div className="border border-sleuth-700/80 rounded-xl bg-sleuth-850/60 p-6">
            <div className="flex items-center gap-2 mb-4 text-cyanAccent-400 font-semibold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Investigative Standards & Legal Scope</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300">
              <div className="space-y-2">
                <p className="text-slate-200 font-medium flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> What ChainSleuth Establishes:
                </p>
                <ul className="list-disc list-inside space-y-1 text-slate-400">
                  <li>Observed on-chain token and native asset transfers.</li>
                  <li>Directed mathematical network paths between public addresses.</li>
                  <li>Algorithmic matching against documented sanction lists.</li>
                  <li>Cryptographic proof of investigation report integrity.</li>
                </ul>
              </div>

              <div className="space-y-2">
                <p className="text-slate-200 font-medium flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> What Requires Off-Chain Subpoena:
                </p>
                <ul className="list-disc list-inside space-y-1 text-slate-400">
                  <li>Common beneficial ownership across separate private keys.</li>
                  <li>Off-chain individual real-world identity or physical jurisdiction.</li>
                  <li>Internal centralized exchange ledger trades.</li>
                  <li>Conclusive proof of criminal mens rea (guilty mind).</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-sleuth-800 text-center text-xs text-slate-500">
        <p>ChainSleuth Forensic Intelligence Platform • Built for Security Researchers, Compliance Analysts, and Auditors</p>
      </footer>
    </div>
  );
};
