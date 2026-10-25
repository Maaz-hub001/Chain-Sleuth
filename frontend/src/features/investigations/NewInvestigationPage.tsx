import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  Sliders,
  Layers,
  FileText,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  Database
} from 'lucide-react';
import { api } from '../../services/api';

const ETH_ADDRESS_REGEX = /^0x[a-fA-F0-9]{40}$/;
const TX_HASH_REGEX = /^0x[a-fA-F0-9]{64}$/;

export const NewInvestigationPage: React.FC = () => {
  const navigate = useNavigate();

  const [target, setTarget] = useState('');
  const [network, setNetwork] = useState('ethereum_mainnet');
  const [chainId, setChainId] = useState(1);
  const [investigationType, setInvestigationType] = useState('comprehensive');
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxTxs, setMaxTxs] = useState(100);
  const [notes, setNotes] = useState('');
  const [useDemo, setUseDemo] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validate format
  const isAddress = ETH_ADDRESS_REGEX.test(target.trim());
  const isTxHash = TX_HASH_REGEX.test(target.trim());
  const isValidTarget = isAddress || isTxHash;

  const handlePreFillSample = (sampleType: 'demo' | 'tornado') => {
    if (sampleType === 'demo') {
      setTarget('0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
      setUseDemo(true);
      setNetwork('demo_sandbox');
      setNotes('Sample multi-hop laundering flow with fan-out, circular loops, and mixer interaction.');
    } else {
      setTarget('0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b');
      setUseDemo(false);
      setNetwork('ethereum_mainnet');
      setNotes('Investigate known Tornado Cash Router contract.');
    }
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidTarget) {
      setError('Please provide a valid 0x-prefixed 40-character address or 64-character transaction hash.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const inv = await api.createInvestigation({
        target_identifier: target.trim(),
        network_name: network,
        chain_id: network === 'ethereum_sepolia' ? 11155111 : network === 'base_mainnet' ? 8453 : 1,
        investigation_type: investigationType,
        max_depth: maxDepth,
        max_transactions: maxTxs,
        investigator_notes: notes.trim() || undefined,
        use_demo_fixture: useDemo
      });

      navigate(`/investigations/${inv.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to initialize investigation.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <ShieldAlert className="w-6 h-6 text-cyanAccent-400" />
          <span>Initiate Blockchain Investigation</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure scope, data ingestion limits, and network routing for multi-hop forensic analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-6 space-y-6">
        {/* Quick Sample Selector */}
        <div className="bg-sleuth-850/80 border border-sleuth-700/60 rounded-lg p-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <span className="text-slate-300 font-medium">Quick Preset Templates:</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handlePreFillSample('demo')}
              className="px-2.5 py-1 rounded bg-cyanAccent-500/10 border border-cyanAccent-500/30 text-cyanAccent-400 hover:bg-cyanAccent-500/20 font-mono transition-colors"
            >
              Load Multi-Hop Demo Wallet
            </button>
            <button
              type="button"
              onClick={() => handlePreFillSample('tornado')}
              className="px-2.5 py-1 rounded bg-sleuth-800 border border-sleuth-600 text-slate-300 hover:text-white font-mono transition-colors"
            >
              Load Tornado Router
            </button>
          </div>
        </div>

        {/* Target Input */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            Target EVM Identifier (Address or Transaction Hash) *
          </label>
          <div className="relative">
            <input
              type="text"
              value={target}
              onChange={(e) => {
                setTarget(e.target.value);
                if (error) setError(null);
              }}
              placeholder="0x742d35Cc6634C0532925a3b844Bc454e4438f44e or 0x4a8f93..."
              className={`w-full px-4 py-2.5 bg-sleuth-950 border rounded-lg font-mono text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none transition-all ${
                target && !isValidTarget
                  ? 'border-red-500 focus:ring-1 focus:ring-red-500'
                  : 'border-sleuth-700 focus:border-cyanAccent-400 focus:ring-1 focus:ring-cyanAccent-400'
              }`}
              required
            />
            {target && (
              <div className="absolute right-3 top-2.5 text-[11px] font-mono">
                {isAddress ? (
                  <span className="text-emerald-400">Valid Address</span>
                ) : isTxHash ? (
                  <span className="text-cyanAccent-400">Valid Tx Hash</span>
                ) : (
                  <span className="text-red-400">Invalid Format</span>
                )}
              </div>
            )}
          </div>
          <p className="text-[11px] text-slate-500 mt-1.5">
            Accepts 40-character 0x-hex EVM wallet/contract address or 64-character transaction hash.
          </p>
        </div>

        {/* Network & Investigation Type */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Blockchain Network
            </label>
            <select
              value={network}
              onChange={(e) => setNetwork(e.target.value)}
              className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded-lg text-xs text-slate-200 focus:border-cyanAccent-400 focus:outline-none"
            >
              <option value="ethereum_mainnet">Ethereum Mainnet (Chain ID 1)</option>
              <option value="ethereum_sepolia">Ethereum Sepolia (Testnet)</option>
              <option value="base_mainnet">Base Mainnet (Chain ID 8453)</option>
              <option value="demo_sandbox">Demo Sandbox (Offline Fixture)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Investigation Type
            </label>
            <select
              value={investigationType}
              onChange={(e) => setInvestigationType(e.target.value)}
              className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded-lg text-xs text-slate-200 focus:border-cyanAccent-400 focus:outline-none"
            >
              <option value="comprehensive">Comprehensive Forensic Audit</option>
              <option value="suspicious_pattern">Suspicious Pattern Detection</option>
              <option value="connected_wallet">Connected Counterparty Mapping</option>
              <option value="transaction_tracing">Linear Transaction Tracing</option>
              <option value="wallet_overview">High-Level Wallet Summary</option>
            </select>
          </div>
        </div>

        {/* Depth & Max Transactions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-sleuth-850/40 p-4 rounded-lg border border-sleuth-800">
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="font-semibold text-slate-300">Max Graph Depth:</span>
              <span className="font-mono text-cyanAccent-400 font-bold">{maxDepth} hops</span>
            </div>
            <input
              type="range"
              min="1"
              max="3"
              value={maxDepth}
              onChange={(e) => setMaxDepth(parseInt(e.target.value))}
              className="w-full accent-cyanAccent-500 cursor-pointer"
            />
            <p className="text-[10px] text-slate-500 mt-1">Bounded hop traversal to avoid unbounded graph sprawl.</p>
          </div>

          <div>
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="font-semibold text-slate-300">Max Transactions:</span>
              <span className="font-mono text-cyanAccent-400 font-bold">{maxTxs} records</span>
            </div>
            <input
              type="range"
              min="10"
              max="200"
              step="10"
              value={maxTxs}
              onChange={(e) => setMaxTxs(parseInt(e.target.value))}
              className="w-full accent-cyanAccent-500 cursor-pointer"
            />
            <p className="text-[10px] text-slate-500 mt-1">Hard limit enforced by backend provider adapter.</p>
          </div>
        </div>

        {/* Offline Demo Toggle */}
        <div className="flex items-center gap-3 p-3 bg-sleuth-850/60 rounded-lg border border-sleuth-800">
          <input
            type="checkbox"
            id="demoToggle"
            checked={useDemo}
            onChange={(e) => setUseDemo(e.target.checked)}
            className="w-4 h-4 rounded text-cyanAccent-500 accent-cyanAccent-500 bg-sleuth-950 border-sleuth-700 cursor-pointer"
          />
          <label htmlFor="demoToggle" className="text-xs text-slate-300 cursor-pointer">
            <span className="font-medium text-white">Use Reproducible Test Fixture (Offline Sandbox)</span>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Loads verified historical transaction records from disk. Ideal for demonstrations and testing without rate limits.
            </p>
          </label>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            Investigator Case Notes (Optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Document preliminary intelligence, victim reporting reference, or hypothesis to test..."
            className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded-lg text-xs text-slate-200 placeholder:text-slate-600 focus:border-cyanAccent-400 focus:outline-none"
          />
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3 bg-red-950/60 border border-red-800 rounded-lg flex items-center gap-2 text-xs text-red-300">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Submit */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-sleuth-800">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 rounded-lg bg-sleuth-800 text-slate-300 hover:text-white text-xs font-medium"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-bold text-xs tracking-wide transition-all shadow-md shadow-cyanAccent-500/20 disabled:opacity-50 active:scale-95"
          >
            <span>{submitting ? 'Executing Pipeline...' : 'Start Investigation'}</span>
            <ArrowRight className="w-4 h-4 text-slate-950" />
          </button>
        </div>
      </form>
    </div>
  );
};
