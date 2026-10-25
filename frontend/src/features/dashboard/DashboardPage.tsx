import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FolderSearch,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  Shield,
  Activity,
  Plus,
  PlayCircle,
  ExternalLink
} from 'lucide-react';
import { api } from '../../services/api';
import type { Investigation, ProviderStatus } from '../../types';
import { Badge } from '../../components/Badge';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingDemo, setStartingDemo] = useState(false);

  useEffect(() => {
    Promise.all([api.getInvestigations(), api.getProvidersHealth()])
      .then(([invs, prov]) => {
        setInvestigations(invs);
        setProviders(prov.providers || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleLaunchDemo = async () => {
    try {
      setStartingDemo(true);
      const res = await api.createInvestigation({
        target_identifier: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        network_name: 'demo_sandbox',
        chain_id: 1,
        investigation_type: 'comprehensive',
        max_depth: 2,
        max_transactions: 100,
        use_demo_fixture: true,
        investigator_notes: 'Demonstration investigation on verified multi-hop laundering flow.'
      });
      navigate(`/investigations/${res.id}`);
    } catch (err: any) {
      alert(`Demo creation failed: ${err.message}`);
      setStartingDemo(false);
    }
  };

  const totalInvs = investigations.length;
  const completedInvs = investigations.filter((i) => i.status === 'completed').length;
  const activeInvs = investigations.filter((i) => i.status === 'processing').length;

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Investigator Workspace</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time blockchain intelligence analytics, active cases, and provider telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleLaunchDemo}
            disabled={startingDemo}
            className="flex items-center gap-2 px-3.5 py-2 rounded-md bg-sleuth-800 hover:bg-sleuth-700 text-cyanAccent-400 border border-sleuth-600 font-medium text-xs transition-all disabled:opacity-50"
          >
            <PlayCircle className="w-4 h-4 text-cyanAccent-400" />
            <span>{startingDemo ? 'Launching Demo...' : 'Launch Demo Case'}</span>
          </button>

          <Link
            to="/investigations/new"
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-cyanAccent-500/20"
          >
            <Plus className="w-4 h-4 text-slate-950" />
            <span>New Investigation</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-sleuth-900 border border-sleuth-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Investigations</span>
            <FolderSearch className="w-4 h-4 text-slate-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{totalInvs}</div>
          <p className="text-[11px] text-slate-500 mt-1">Logged cases</p>
        </div>

        <div className="bg-sleuth-900 border border-sleuth-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Completed Audits</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">{completedInvs}</div>
          <p className="text-[11px] text-slate-500 mt-1">Evidence verified</p>
        </div>

        <div className="bg-sleuth-900 border border-sleuth-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Ingestions</span>
            <Clock className="w-4 h-4 text-cyanAccent-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyanAccent-400">{activeInvs}</div>
          <p className="text-[11px] text-slate-500 mt-1">Running in background</p>
        </div>

        <div className="bg-sleuth-900 border border-sleuth-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Providers</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300">
            {providers.filter((p) => p.status === 'operational').length} / {providers.length}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">EVM RPC & explorer nodes</p>
        </div>
      </div>

      {/* Main Grid: Recent Cases & Provider Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Recent Investigations */}
        <div className="lg:col-span-2 bg-sleuth-900 border border-sleuth-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-sleuth-800 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Recent Investigations</h2>
            <Link to="/investigations/new" className="text-xs text-cyanAccent-400 hover:underline">
              Create New +
            </Link>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading cases...</div>
          ) : investigations.length === 0 ? (
            <div className="p-12 text-center">
              <FolderSearch className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-300">No investigations yet</p>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
                Submit an EVM address or transaction hash, or run the demo sandbox case to view multi-hop graph analysis.
              </p>
              <button
                onClick={handleLaunchDemo}
                className="px-4 py-2 rounded bg-cyanAccent-500/10 border border-cyanAccent-500/30 text-cyanAccent-400 hover:bg-cyanAccent-500/20 text-xs font-semibold"
              >
                Launch Verified Demo Case
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-sleuth-850/80 text-slate-400 font-mono text-[11px] uppercase border-b border-sleuth-800">
                  <tr>
                    <th className="px-4 py-3">Target</th>
                    <th className="px-4 py-3">Network</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Findings</th>
                    <th className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sleuth-800/60 font-sans">
                  {investigations.map((inv) => (
                    <tr key={inv.id} className="hover:bg-sleuth-850/50 transition-colors">
                      <td className="px-4 py-3 font-mono text-slate-200">
                        <Link to={`/investigations/${inv.id}`} className="hover:text-cyanAccent-400 flex items-center gap-1.5">
                          <span>{inv.target_identifier.slice(0, 10)}...{inv.target_identifier.slice(-6)}</span>
                          <span className="text-[10px] text-slate-500 uppercase">({inv.target_type})</span>
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-slate-400">
                        {inv.network_name}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={inv.status === 'completed' ? 'verified' : inv.status === 'failed' ? 'critical' : 'warning'}>
                          {inv.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 font-mono text-slate-300">
                        {inv.metrics?.findings_count ?? '0'} alerts
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/investigations/${inv.id}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-sleuth-800 hover:bg-sleuth-700 text-slate-200 text-xs"
                        >
                          <span>Open</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right: Data Provider Health Telemetry */}
        <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-4 flex flex-col">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-sleuth-800">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyanAccent-400" />
              <span>Provider Telemetry</span>
            </h2>
            <Link to="/settings" className="text-xs text-slate-400 hover:text-cyanAccent-400">
              Manage
            </Link>
          </div>

          <div className="space-y-3 flex-1">
            {providers.map((p, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-sleuth-850/60 border border-sleuth-800/80">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-slate-200">{p.name}</span>
                  <Badge variant={p.status === 'operational' ? 'verified' : p.status === 'not_configured' ? 'neutral' : 'warning'}>
                    {p.status}
                  </Badge>
                </div>
                <p className="text-[11px] font-mono text-slate-400 truncate mb-1">
                  {p.endpoint_display}
                </p>
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{p.category}</span>
                  {p.response_time_ms && (
                    <span className="font-mono text-cyanAccent-400">{p.response_time_ms} ms</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-3 border-t border-sleuth-800/60 text-[11px] text-slate-400 text-center">
            Zero synthetic data fabricated when live APIs fail.
          </div>
        </div>
      </div>
    </div>
  );
};
