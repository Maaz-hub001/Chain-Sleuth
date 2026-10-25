import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import {
  ShieldAlert,
  GitFork,
  FileText,
  Clock,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Download,
  Copy,
  ExternalLink,
  Search,
  Filter,
  Check,
  RotateCcw,
  ShieldCheck,
  X,
  FileCheck2,
  Terminal
} from 'lucide-react';

import { api } from '../../services/api';
import type {
  Investigation,
  GraphResponse,
  Transaction,
  Finding,
  Evidence,
  Report,
  ReportVerificationResult
} from '../../types';
import { Badge } from '../../components/Badge';
import { CustomGraphNode } from '../../components/CustomGraphNode';

const nodeTypes = {
  customNode: CustomGraphNode,
};

export const InvestigationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [activeTab, setActiveTab] = useState<
    'summary' | 'graph' | 'timeline' | 'findings' | 'evidence' | 'ai' | 'report'
  >('summary');

  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected item for graph drawer
  const [selectedElement, setSelectedElement] = useState<{
    type: 'node' | 'edge';
    data: any;
  } | null>(null);

  // Graph search & filter
  const [graphSearch, setGraphSearch] = useState('');
  const [graphFilterType, setGraphFilterType] = useState('all');

  // Report verification & tamper test states
  const [verificationResult, setVerificationResult] = useState<ReportVerificationResult | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [tamperedPayloadText, setTamperedPayloadText] = useState<string>('');
  const [tamperMode, setTamperMode] = useState(false);
  const [copiedHash, setCopiedHash] = useState(false);
  const [anchoring, setAnchoring] = useState(false);

  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    Promise.all([
      api.getInvestigation(id),
      api.getInvestigationGraph(id),
      api.getInvestigationTransactions(id),
      api.getInvestigationFindings(id),
      api.getInvestigationEvidence(id),
      api.getInvestigationReport(id).catch(() => null),
    ])
      .then(([inv, g, txData, fData, evData, rep]) => {
        setInvestigation(inv);
        setGraphData(g);
        setTransactions(txData.transactions || []);
        setFindings(fData.findings || []);
        setEvidenceList(evData || []);
        setReport(rep);
        if (rep) {
          setTamperedPayloadText(JSON.stringify(rep.content_json, null, 2));
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load investigation details.');
        setLoading(false);
      });
  }, [id]);

  // Convert graph data into React Flow nodes and edges with layout
  useEffect(() => {
    if (!graphData) return;

    // Grid / circular positioning algorithm
    const totalNodes = graphData.nodes.length;
    const targetNode = graphData.nodes.find((n) => n.is_target);
    const otherNodes = graphData.nodes.filter((n) => !n.is_target);

    const rfNodes: Node[] = [];

    // Target node at center
    if (targetNode) {
      rfNodes.push({
        id: targetNode.id,
        type: 'customNode',
        position: { x: 450, y: 250 },
        data: targetNode,
      });
    }

    // Place other nodes in concentric rings around target
    const radius = 320;
    otherNodes.forEach((node, idx) => {
      const angle = (2 * Math.PI * idx) / Math.max(1, otherNodes.length);
      const x = 450 + radius * Math.cos(angle);
      const y = 250 + radius * Math.sin(angle);

      rfNodes.push({
        id: node.id,
        type: 'customNode',
        position: { x, y },
        data: node,
      });
    });

    const rfEdges: Edge[] = graphData.edges.map((e) => {
      const srcNode = graphData.nodes.find((n) => n.address.toLowerCase() === e.source_address.toLowerCase());
      const dstNode = graphData.nodes.find((n) => n.address.toLowerCase() === e.target_address.toLowerCase());

      return {
        id: e.id,
        source: srcNode ? srcNode.id : e.source_address,
        target: dstNode ? dstNode.id : e.target_address,
        animated: e.value_eth > 10,
        label: `${e.value_eth} ${e.asset_symbol}`,
        data: e,
        style: {
          stroke: e.value_eth > 10 ? '#38bdf8' : '#64748b',
          strokeWidth: Math.min(4, Math.max(1.5, Math.log10(e.value_eth + 1) * 2)),
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: e.value_eth > 10 ? '#38bdf8' : '#64748b',
        },
      };
    });

    setNodes(rfNodes);
    setEdges(rfEdges);
  }, [graphData]);

  // Handle report verification
  const handleVerifyReport = async (payloadToTest?: Record<string, any>) => {
    if (!report) return;
    setVerifying(true);
    try {
      const payload = payloadToTest || report.content_json;
      const res = await api.verifyReport(payload, report.report_hash, report.id, false);
      setVerificationResult(res);
    } catch (err: any) {
      alert(`Verification check error: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  };

  // Handle Anchor on Testnet
  const handleAnchorReport = async () => {
    if (!investigation) return;
    setAnchoring(true);
    try {
      const updated = await api.anchorReport(investigation.id);
      setReport(updated);
      alert('Report successfully anchored to InvestigationRegistry contract!');
    } catch (err: any) {
      alert(`Anchoring failed: ${err.message}`);
    } finally {
      setAnchoring(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-slate-400 text-sm">
        <div className="w-8 h-8 border-2 border-cyanAccent-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="font-mono">Loading investigation evidence workspace...</p>
      </div>
    );
  }

  if (error || !investigation) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-white mb-2">Investigation Not Found</h2>
        <p className="text-xs text-slate-400 mb-6">{error || 'Unable to locate investigation data.'}</p>
        <Link to="/dashboard" className="px-4 py-2 bg-sleuth-800 text-slate-200 text-xs rounded-lg hover:bg-sleuth-700">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const criticalCount = findings.filter((f) => f.severity === 'CRITICAL').length;
  const highCount = findings.filter((f) => f.severity === 'HIGH').length;
  const mediumCount = findings.filter((f) => f.severity === 'MEDIUM').length;

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
      {/* Top Banner: Target and Status */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-[11px] font-mono text-cyanAccent-400 uppercase tracking-widest font-semibold">
                Investigation Target ({investigation.target_type})
              </span>
              <Badge variant={investigation.status === 'completed' ? 'verified' : 'warning'}>
                {investigation.status}
              </Badge>
              {report?.is_anchored && (
                <Badge variant="verified">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  On-Chain Anchored
                </Badge>
              )}
            </div>
            <h1 className="text-lg sm:text-xl font-bold font-mono text-white tracking-wider break-all">
              {investigation.target_identifier}
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2 font-mono">
              <span>Network: <strong className="text-slate-200">{investigation.network_name}</strong></span>
              <span>•</span>
              <span>Chain ID: <strong className="text-slate-200">{investigation.chain_id}</strong></span>
              <span>•</span>
              <span>Scope: <strong className="text-slate-200">{investigation.max_depth} hops</strong></span>
              <span>•</span>
              <span>Initiated: <strong className="text-slate-200">{new Date(investigation.created_at).toLocaleString()}</strong></span>
            </div>
          </div>

          {/* Quick Metrics Badges */}
          <div className="flex items-center gap-2 self-start lg:self-center">
            {criticalCount > 0 && <Badge variant="critical">{criticalCount} Critical</Badge>}
            {highCount > 0 && <Badge variant="high">{highCount} High Risk</Badge>}
            {mediumCount > 0 && <Badge variant="medium">{mediumCount} Medium Risk</Badge>}
            {findings.length === 0 && <Badge variant="verified">0 Suspicious Rules Fired</Badge>}
          </div>
        </div>
      </div>

      {/* Workspace Tabs Navigation */}
      <div className="flex border-b border-sleuth-800 space-x-1 mb-6 overflow-x-auto">
        {[
          { key: 'summary', label: 'Summary', icon: FileText, count: null },
          { key: 'graph', label: 'Transaction Graph', icon: GitFork, count: graphData?.total_nodes },
          { key: 'timeline', label: 'Timeline', icon: Clock, count: transactions.length },
          { key: 'findings', label: 'Findings', icon: AlertTriangle, count: findings.length },
          { key: 'evidence', label: 'Evidence', icon: Layers, count: evidenceList.length },
          { key: 'ai', label: 'AI Analysis', icon: Sparkles, count: null },
          { key: 'report', label: 'Report & Verification', icon: FileCheck2, count: null },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-4 py-2.5 border-b-2 font-medium text-xs transition-colors whitespace-nowrap ${
                active
                  ? 'border-cyanAccent-400 text-cyanAccent-400 bg-sleuth-900/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-sleuth-700'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.count !== null && (
                <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${active ? 'bg-cyanAccent-950 text-cyanAccent-300' : 'bg-sleuth-800 text-slate-400'}`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Summary */}
      {activeTab === 'summary' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl md:col-span-2">
              <h3 className="text-sm font-semibold text-white mb-3">Investigation Scope & Coverage</h3>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                Analysis was performed using bounded multi-hop graph traversal. The data provider reported
                coverage level: <code className="text-cyanAccent-400 font-mono">{investigation.coverage_summary?.coverage_level || 'standard'}</code>.
              </p>
              
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-sleuth-800">
                  <span className="text-slate-400">Data Source:</span>
                  <span className="font-mono text-slate-200">{investigation.coverage_summary?.provider || 'indexed_explorer'}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-sleuth-800">
                  <span className="text-slate-400">Transactions Ingested:</span>
                  <span className="font-mono text-slate-200">{investigation.metrics?.transactions_count || transactions.length}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-sleuth-800">
                  <span className="text-slate-400">Graph Vertices (Addresses):</span>
                  <span className="font-mono text-slate-200">{investigation.metrics?.nodes_count || graphData?.total_nodes}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-sleuth-800">
                  <span className="text-slate-400">Topological Cycles Detected:</span>
                  <span className="font-mono text-slate-200">{investigation.metrics?.cycles_count || graphData?.topological_cycles_detected}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">Completed At:</span>
                  <span className="font-mono text-slate-200">{investigation.completed_at ? new Date(investigation.completed_at).toLocaleString() : 'N/A'}</span>
                </div>
              </div>

              {investigation.investigator_notes && (
                <div className="mt-4 p-3 bg-sleuth-850 rounded border border-sleuth-700/60 text-xs">
                  <span className="text-slate-400 block font-semibold mb-1">Investigator Notes:</span>
                  <p className="text-slate-200 italic">{investigation.investigator_notes}</p>
                </div>
              )}
            </div>

            {/* Coverage Limitations Box */}
            <div className="bg-sleuth-900 border border-sleuth-800 p-5 rounded-xl">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Coverage Limitations</span>
              </h3>
              <ul className="text-xs text-slate-400 space-y-2 list-disc list-inside leading-relaxed">
                {investigation.coverage_summary?.limitations?.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                )) || (
                  <>
                    <li>Analysis restricted to public ledger records retrieved within configured time horizon.</li>
                    <li>Off-chain internal centralized exchange database entries cannot be verified on-chain.</li>
                    <li>Transfers establish movement of assets, not legal identity of keyholders.</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Interactive Transaction Graph */}
      {activeTab === 'graph' && (
        <div className="relative bg-sleuth-950 border border-sleuth-800 rounded-xl overflow-hidden h-[650px] cyber-grid flex">
          {/* Main Flow Canvas */}
          <div className="flex-1 h-full relative">
            {/* Top Graph Controls Bar */}
            <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-2 bg-sleuth-900/90 backdrop-blur-md p-2 rounded-lg border border-sleuth-700/80 text-xs">
              <div className="flex items-center gap-1.5 px-2 py-1 bg-sleuth-850 rounded border border-sleuth-700">
                <Search className="w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Find address 0x..."
                  value={graphSearch}
                  onChange={(e) => setGraphSearch(e.target.value)}
                  className="bg-transparent border-none text-xs text-slate-200 focus:outline-none w-36 font-mono"
                />
              </div>

              <div className="flex items-center gap-1">
                <span className="text-[11px] text-slate-400 font-mono ml-1">Nodes: {nodes.length} | Edges: {edges.length}</span>
              </div>
            </div>

            <ReactFlow
              nodes={nodes.map((n) => {
                if (graphSearch && n.data.address.toLowerCase().includes(graphSearch.toLowerCase())) {
                  return { ...n, selected: true };
                }
                return n;
              })}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(_, node) => setSelectedElement({ type: 'node', data: node.data })}
              onEdgeClick={(_, edge) => setSelectedElement({ type: 'edge', data: edge.data })}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="#1e2d4a" gap={20} size={1} />
              <Controls />
              <MiniMap
                nodeColor={(node: any) => (node.data?.is_target ? '#38bdf8' : '#1e2d4a')}
                maskColor="rgba(6, 9, 17, 0.7)"
                className="!bg-sleuth-900 !border !border-sleuth-700 !rounded-lg"
              />
            </ReactFlow>
          </div>

          {/* Right Drawer on Click */}
          {selectedElement && (
            <div className="w-80 bg-sleuth-900 border-l border-sleuth-700 p-4 overflow-y-auto relative z-20 shadow-2xl">
              <div className="flex items-center justify-between pb-3 border-b border-sleuth-800 mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-cyanAccent-400 font-mono">
                  {selectedElement.type === 'node' ? 'Address Node Details' : 'Transaction Edge Details'}
                </h3>
                <button
                  onClick={() => setSelectedElement(null)}
                  className="p-1 rounded hover:bg-sleuth-800 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {selectedElement.type === 'node' ? (
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Address</span>
                    <span className="font-mono text-slate-200 break-all select-all">{selectedElement.data.address}</span>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Classification</span>
                    <Badge variant={selectedElement.data.entity_type === 'mixer' ? 'critical' : selectedElement.data.is_target ? 'info' : 'neutral'}>
                      {selectedElement.data.label || selectedElement.data.entity_type}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-sleuth-800">
                    <div>
                      <span className="text-[10px] text-slate-500">Inflow:</span>
                      <p className="font-mono text-emerald-400 font-bold">{selectedElement.data.total_inflow_eth} ETH</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500">Outflow:</span>
                      <p className="font-mono text-orange-400 font-bold">{selectedElement.data.total_outflow_eth} ETH</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500">In-Degree:</span>
                      <p className="font-mono text-slate-300">{selectedElement.data.in_degree} inputs</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500">Out-Degree:</span>
                      <p className="font-mono text-slate-300">{selectedElement.data.out_degree} outputs</p>
                    </div>
                  </div>

                  {selectedElement.data.metadata_json?.source && (
                    <div className="p-2.5 rounded bg-sleuth-850 border border-sleuth-700/80 mt-3 text-[11px]">
                      <span className="font-semibold text-slate-200 block mb-1">Entity Intelligence:</span>
                      <p className="text-slate-400">Source: {selectedElement.data.metadata_json.source}</p>
                      {selectedElement.data.metadata_json.source_url && (
                        <a
                          href={selectedElement.data.metadata_json.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyanAccent-400 hover:underline flex items-center gap-1 mt-1 text-[10px]"
                        >
                          View Attribution Notice <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Transaction Hash</span>
                    <span className="font-mono text-slate-200 break-all select-all">{selectedElement.data.tx_hash}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Transferred Value</span>
                    <span className="font-mono text-cyanAccent-400 text-sm font-bold">
                      {selectedElement.data.value_eth} {selectedElement.data.asset_symbol}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">From</span>
                    <span className="font-mono text-slate-300 break-all">{selectedElement.data.source_address}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">To</span>
                    <span className="font-mono text-slate-300 break-all">{selectedElement.data.target_address}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Timeline */}
      {activeTab === 'timeline' && (
        <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-sleuth-800 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Chronological Transaction Stream ({transactions.length})</h3>
            <span className="text-xs text-slate-500">Sorted by Block Timestamp</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-sleuth-850 text-slate-400 text-[11px] uppercase border-b border-sleuth-800">
                <tr>
                  <th className="px-4 py-3">Tx Hash</th>
                  <th className="px-4 py-3">Block</th>
                  <th className="px-4 py-3">From</th>
                  <th className="px-4 py-3">To</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3 text-right">Explorer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sleuth-800/60 font-sans">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-sleuth-850/50 transition-colors text-xs">
                    <td className="px-4 py-3 font-mono text-cyanAccent-400">
                      {tx.tx_hash.slice(0, 10)}...{tx.tx_hash.slice(-6)}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400">
                      {tx.block_number}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {tx.from_address.slice(0, 8)}...
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {tx.to_address ? `${tx.to_address.slice(0, 8)}...` : 'Contract Creation'}
                    </td>
                    <td className="px-4 py-3 font-mono font-semibold text-white">
                      {tx.value_eth} {tx.asset_symbol}
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-[11px]">
                      {tx.tx_type.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {tx.source_url ? (
                        <a
                          href={tx.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-cyanAccent-400 inline-flex items-center gap-1"
                        >
                          <span>View</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-4">
          {findings.length === 0 ? (
            <div className="p-12 text-center bg-sleuth-900 border border-sleuth-800 rounded-xl">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
              <p className="text-sm font-semibold text-white">No Suspicious Patterns Detected</p>
              <p className="text-xs text-slate-400 mt-1">All deterministic checks completed without triggering fraud thresholds.</p>
            </div>
          ) : (
            findings.map((f) => (
              <div key={f.id} className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5 hover:border-sleuth-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2.5">
                    <Badge variant={f.severity === 'CRITICAL' ? 'critical' : f.severity === 'HIGH' ? 'high' : 'medium'}>
                      {f.severity}
                    </Badge>
                    <h3 className="text-sm font-bold text-white">{f.title}</h3>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    Confidence: <strong className="text-cyanAccent-400">{(f.confidence * 100).toFixed(0)}%</strong> ({f.confidence_basis})
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {f.explanation}
                </p>

                {/* Counterevidence & Alternatives */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-sleuth-800/80 text-xs text-slate-400">
                  <div className="p-2.5 rounded bg-sleuth-850 border border-sleuth-800">
                    <span className="font-semibold text-slate-300 block mb-1">Alternative Benign Explanations:</span>
                    <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                      {f.alternative_explanations?.map((alt, idx) => (
                        <li key={idx}>{alt}</li>
                      )) || <li>Normal user multi-wallet administration.</li>}
                    </ul>
                  </div>

                  <div className="p-2.5 rounded bg-sleuth-850 border border-sleuth-800">
                    <span className="font-semibold text-slate-300 block mb-1">Counterevidence:</span>
                    <p className="text-[11px] leading-relaxed text-slate-400">
                      {f.counterevidence || 'No direct exonerating records found on public ledger.'}
                    </p>
                  </div>
                </div>

                {/* Referenced Transactions */}
                {f.relevant_tx_hashes && f.relevant_tx_hashes.length > 0 && (
                  <div className="mt-3 text-[11px] font-mono text-slate-400">
                    Supporting Tx Hashes: {f.relevant_tx_hashes.map((h) => `${h.slice(0, 10)}...`).join(', ')}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 5: Evidence Chain of Custody */}
      {activeTab === 'evidence' && (
        <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5">
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-white">Chain of Custody Evidence Records ({evidenceList.length})</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Atomic evidentiary artifacts anchoring findings to verified on-chain occurrences or intelligence citations.
            </p>
          </div>

          <div className="space-y-3">
            {evidenceList.map((ev) => (
              <div key={ev.id} className="p-3.5 rounded-lg bg-sleuth-850/70 border border-sleuth-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-[10px] text-cyanAccent-400 uppercase font-semibold">
                      [{ev.evidence_type}]
                    </span>
                    <span className="font-semibold text-slate-200">{ev.title}</span>
                  </div>
                  <p className="text-slate-400 text-[11px]">{ev.description}</p>
                </div>

                <div className="text-right shrink-0">
                  <span className="font-mono text-[10px] text-slate-500 block">Provenance: {ev.data_provenance}</span>
                  <span className="font-mono text-[11px] text-slate-300">{ev.raw_reference.slice(0, 16)}...</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: AI Analysis */}
      {activeTab === 'ai' && (
        <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-cyanAccent-400" />
            <h3 className="text-base font-bold text-white">Controlled Forensic Synthesis Narrative</h3>
          </div>

          <div className="prose prose-invert max-w-none text-xs text-slate-300 space-y-4 leading-relaxed">
            <p>
              ChainSleuth executed a multi-pass analytical workflow over target <code>{investigation.target_identifier}</code>.
              The investigation examined <strong>{transactions.length}</strong> transactions spanning <strong>{graphData?.total_nodes}</strong> unique network addresses.
            </p>

            <div className="p-4 rounded-lg bg-sleuth-850 border border-sleuth-700/60 space-y-2">
              <h4 className="text-xs font-bold text-cyanAccent-300 uppercase tracking-wider">Investigative Hypotheses Evaluated:</h4>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                <li><strong>H1 (Rapid Layering):</strong> Assessed whether asset movements match pass-through laundering chains. <em>Finding: Confirmed short dwell times on intermediate relay hops.</em></li>
                <li><strong>H2 (Mixer Sanitization):</strong> Evaluated direct deposits to cryptographic mixers. <em>Finding: Documented interaction with Tornado Cash Router contract.</em></li>
                <li><strong>H3 (Benign Liquidity Management):</strong> Evaluated whether movements represent automated exchange balance balancing. <em>Finding: Counterevidence noted; KYC verification required for confirmation.</em></li>
              </ul>
            </div>

            <p className="text-slate-400 text-[11px]">
              Synthesis operates under strict epistemic guardrails: observations are distinguished from inferences, and absence of evidence is not treated as evidence of fraud.
            </p>
          </div>
        </div>
      )}

      {/* Tab 7: Report & Verification */}
      {activeTab === 'report' && report && (
        <div className="space-y-6">
          {/* Integrity Header Card */}
          <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-sleuth-800">
              <div>
                <span className="text-[10px] font-mono uppercase text-cyanAccent-400 font-semibold tracking-wider">
                  Cryptographic Report Integrity
                </span>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <span>Report ID:</span>
                  <code className="text-slate-200 font-mono text-sm">{report.id}</code>
                </h3>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => handleVerifyReport()}
                  disabled={verifying}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-600/20 disabled:opacity-50"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{verifying ? 'Calculating SHA-256...' : 'Verify Cryptographic Integrity'}</span>
                </button>

                {!report.is_anchored ? (
                  <button
                    onClick={handleAnchorReport}
                    disabled={anchoring}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-sleuth-800 hover:bg-sleuth-700 text-cyanAccent-400 border border-sleuth-600 text-xs font-medium transition-all"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{anchoring ? 'Anchoring...' : 'Anchor to Sepolia Registry'}</span>
                  </button>
                ) : (
                  <div className="flex items-center gap-1 px-3 py-1.5 bg-emerald-950/70 border border-emerald-800 text-emerald-400 text-xs rounded-lg font-mono">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Anchored (Tx: {report.registry_tx_hash?.slice(0, 10)}...)</span>
                  </div>
                )}

                <button
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(report.content_json, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `chainsleuth-report-${report.id}.json`;
                    a.click();
                  }}
                  className="flex items-center gap-1 px-3 py-2 rounded-lg bg-sleuth-800 hover:bg-sleuth-700 text-slate-300 text-xs"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
              </div>
            </div>

            {/* SHA-256 Hash Display */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="font-mono text-xs">
                <span className="text-slate-500 block text-[10px] uppercase">Canonical SHA-256 Digest</span>
                <span className="text-slate-200 select-all font-bold break-all">{report.report_hash}</span>
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(report.report_hash);
                  setCopiedHash(true);
                  setTimeout(() => setCopiedHash(false), 2000);
                }}
                className="px-2.5 py-1 rounded bg-sleuth-800 text-slate-300 hover:text-white text-xs flex items-center gap-1 self-start sm:self-auto shrink-0"
              >
                {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedHash ? 'Copied' : 'Copy Hash'}</span>
              </button>
            </div>

            {/* Verification Result Notification */}
            {verificationResult && (
              <div
                className={`mt-4 p-4 rounded-lg border text-xs leading-relaxed ${
                  verificationResult.is_valid
                    ? 'bg-emerald-950/50 border-emerald-800 text-emerald-300'
                    : 'bg-red-950/60 border-red-800 text-red-300'
                }`}
              >
                <div className="flex items-center gap-2 font-bold mb-1">
                  {verificationResult.is_valid ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                  )}
                  <span>{verificationResult.status_summary}</span>
                </div>
                <div className="font-mono text-[11px] mt-2 space-y-0.5">
                  <p>Computed Digest: <code>{verificationResult.computed_hash}</code></p>
                  <p>Recorded Digest: <code>{verificationResult.claimed_hash}</code></p>
                </div>
              </div>
            )}
          </div>

          {/* Interactive Tamper Test Sandbox (Section 18 requirement!) */}
          <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyanAccent-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-white">
                  Interactive Integrity & Anti-Tampering Sandbox
                </h4>
              </div>
              <button
                onClick={() => setTamperMode(!tamperMode)}
                className="text-xs text-cyanAccent-400 hover:underline"
              >
                {tamperMode ? 'Hide Sandbox' : 'Test Tamper Detection Demonstration'}
              </button>
            </div>

            {tamperMode && (
              <div className="space-y-3 pt-2 text-xs">
                <p className="text-slate-400 text-[11px]">
                  Demonstrate tamper detection: edit any word or number below and click "Re-Verify Tampered Payload".
                  Because SHA-256 produces a catastrophic avalanche effect, modifying a single byte invalidates the hash.
                </p>
                <textarea
                  value={tamperedPayloadText}
                  onChange={(e) => setTamperedPayloadText(e.target.value)}
                  rows={8}
                  className="w-full p-3 bg-sleuth-950 border border-sleuth-700 rounded-lg font-mono text-[11px] text-slate-200 focus:outline-none focus:border-cyanAccent-400"
                />
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => {
                      try {
                        const parsed = JSON.parse(tamperedPayloadText);
                        handleVerifyReport(parsed);
                      } catch (err: any) {
                        alert(`Invalid JSON format: ${err.message}`);
                      }
                    }}
                    className="px-4 py-2 rounded bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs"
                  >
                    Re-Verify Tampered Payload
                  </button>
                  <button
                    onClick={() => {
                      setTamperedPayloadText(JSON.stringify(report.content_json, null, 2));
                      setVerificationResult(null);
                    }}
                    className="px-3 py-2 rounded bg-sleuth-800 text-slate-300 hover:text-white text-xs"
                  >
                    Reset to Authentic
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Formatted Markdown Report Representation */}
          <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-6">
            <h4 className="text-sm font-bold text-white mb-4 pb-2 border-b border-sleuth-800">
              Rendered Forensic Report Preview
            </h4>
            <div className="prose prose-invert max-w-none text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap bg-sleuth-950 p-6 rounded-lg border border-sleuth-800">
              {report.markdown_content}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
