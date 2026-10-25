import React, { useEffect, useState } from 'react';
import {
  Settings,
  Activity,
  Globe,
  Key,
  CheckCircle2,
  AlertTriangle,
  Play,
  Clock,
  Server
} from 'lucide-react';
import { api } from '../../services/api';
import type { ProviderStatus } from '../../types';
import { Badge } from '../../components/Badge';

export const SettingsPage: React.FC = () => {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [networks, setNetworks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Connection test tool
  const [testEndpoint, setTestEndpoint] = useState('https://rpc.ankr.com/eth');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any | null>(null);

  useEffect(() => {
    Promise.all([api.getProvidersHealth(), api.getSupportedNetworks()])
      .then(([pData, nData]) => {
        setProviders(pData.providers || []);
        setNetworks(nData || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleRunTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.testProvider('Custom EVM RPC', testEndpoint.trim());
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        status: 'error',
        message: err.message || 'Connection test failed',
        latency_ms: null,
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-cyanAccent-400" />
          <span>Platform & Provider Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          EVM network endpoints, blockchain provider health status, and live RPC latency diagnostics.
        </p>
      </div>

      {/* Provider Health Overview */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-6">
        <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyanAccent-400" />
          <span>Connected Blockchain & Data Adapters</span>
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Status of external node infrastructure. Unconfigured providers fall back gracefully without fabricating records.
        </p>

        {loading ? (
          <div className="text-xs text-slate-500 py-4">Checking provider health...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providers.map((p, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-sleuth-850 border border-sleuth-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{p.name}</span>
                  <Badge variant={p.status === 'operational' ? 'verified' : p.status === 'not_configured' ? 'neutral' : 'warning'}>
                    {p.status}
                  </Badge>
                </div>
                <p className="font-mono text-[11px] text-slate-400 truncate">
                  {p.endpoint_display}
                </p>
                {p.details && (
                  <p className="text-[11px] text-slate-400 leading-relaxed italic">
                    {p.details}
                  </p>
                )}
                {p.response_time_ms && (
                  <div className="text-[10px] text-cyanAccent-400 font-mono">
                    Round-Trip Latency: {p.response_time_ms} ms
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Live RPC Diagnostic Tool */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-6">
        <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
          <Server className="w-4 h-4 text-cyanAccent-400" />
          <span>RPC Node Connectivity & Latency Tester</span>
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Test any EVM JSON-RPC endpoint. Validates SSRF safety rules, checks block height, and measures round-trip response time.
        </p>

        <form onSubmit={handleRunTest} className="space-y-4">
          <div className="flex gap-2">
            <input
              type="url"
              required
              value={testEndpoint}
              onChange={(e) => setTestEndpoint(e.target.value)}
              placeholder="https://..."
              className="flex-1 px-4 py-2 bg-sleuth-950 border border-sleuth-700 rounded-lg font-mono text-xs text-slate-200 focus:outline-none focus:border-cyanAccent-400"
            />
            <button
              type="submit"
              disabled={testing}
              className="px-5 py-2 rounded-lg bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-semibold text-xs disabled:opacity-50 flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{testing ? 'Testing...' : 'Test Connection'}</span>
            </button>
          </div>

          {testResult && (
            <div
              className={`p-4 rounded-lg border text-xs ${
                testResult.success
                  ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                  : 'bg-red-950/40 border-red-800 text-red-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold flex items-center gap-1.5">
                  {testResult.success ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-red-400" />}
                  {testResult.message}
                </span>
                {testResult.latency_ms && (
                  <span className="font-mono text-[11px] text-cyanAccent-400">
                    {testResult.latency_ms} ms
                  </span>
                )}
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Supported EVM Networks */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-sleuth-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Globe className="w-4 h-4 text-cyanAccent-400" />
            <span>Configured EVM Networks</span>
          </h2>
          <span className="text-xs text-slate-500">Read-Only Investigation</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-sleuth-850 text-slate-400 uppercase text-[11px] border-b border-sleuth-800">
              <tr>
                <th className="px-4 py-3">Network Name</th>
                <th className="px-4 py-3">Chain ID</th>
                <th className="px-4 py-3">Currency</th>
                <th className="px-4 py-3">RPC Endpoint</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sleuth-800/60 font-sans">
              {networks.map((net, idx) => (
                <tr key={idx} className="hover:bg-sleuth-850/50">
                  <td className="px-4 py-3 text-slate-200 font-medium">
                    {net.name} {net.is_default && <span className="text-[10px] text-cyanAccent-400 font-mono">(Default)</span>}
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-400">{net.chain_id}</td>
                  <td className="px-4 py-3 font-mono text-slate-300">{net.native_currency}</td>
                  <td className="px-4 py-3 font-mono text-slate-400 truncate max-w-xs">{net.rpc_url}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
