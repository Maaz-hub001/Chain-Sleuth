import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  ShieldCheck,
  Download,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Search,
  Copy,
  Check
} from 'lucide-react';
import { api } from '../../services/api';
import type { Report } from '../../types';
import { Badge } from '../../components/Badge';

export const ReportArchivePage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    api.getAllReports()
      .then((data) => {
        setReports(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleCopyHash = (hash: string, id: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <FileText className="w-6 h-6 text-cyanAccent-400" />
          <span>Investigation Reports Archive</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Historical record of cryptographically hashed and anchored forensic reports.
        </p>
      </div>

      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-sleuth-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Generated Reports ({reports.length})</h2>
          <span className="text-xs text-slate-500 font-mono">SHA-256 Canonical Hashing</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading reports archive...</div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-sm font-semibold text-white">No Reports Generated Yet</p>
            <p className="text-xs text-slate-500 mt-1 mb-4">
              Launch an investigation to generate a source-linked, verifiable report.
            </p>
            <Link
              to="/investigations/new"
              className="px-4 py-2 bg-cyanAccent-500/10 border border-cyanAccent-500/30 text-cyanAccent-400 hover:bg-cyanAccent-500/20 text-xs font-semibold rounded"
            >
              Start Investigation
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-sleuth-850 text-slate-400 uppercase font-mono text-[11px] border-b border-sleuth-800">
                <tr>
                  <th className="px-4 py-3">Report ID</th>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">SHA-256 Digest</th>
                  <th className="px-4 py-3">Anchored</th>
                  <th className="px-4 py-3">Generated</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sleuth-800/60 font-sans">
                {reports.map((rep) => (
                  <tr key={rep.id} className="hover:bg-sleuth-850/50 transition-colors">
                    <td className="px-4 py-3 font-mono text-cyanAccent-400 font-semibold">
                      <Link to={`/investigations/${rep.investigation_id}`} className="hover:underline">
                        {rep.id}
                      </Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {rep.target_identifier.slice(0, 10)}...{rep.target_identifier.slice(-6)}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400">
                      <div className="flex items-center gap-1.5">
                        <span>{rep.report_hash.slice(0, 16)}...</span>
                        <button
                          onClick={() => handleCopyHash(rep.report_hash, rep.id)}
                          className="p-1 rounded hover:bg-sleuth-800 text-slate-500 hover:text-slate-300"
                        >
                          {copiedId === rep.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {rep.is_anchored ? (
                        <Badge variant="verified">Anchored</Badge>
                      ) : (
                        <Badge variant="neutral">Off-Chain</Badge>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(rep.generated_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <Link
                        to={`/investigations/${rep.investigation_id}`}
                        className="px-2.5 py-1 bg-sleuth-800 hover:bg-sleuth-700 text-slate-200 rounded text-xs"
                      >
                        Inspect
                      </Link>
                      <button
                        onClick={() => {
                          const blob = new Blob([JSON.stringify(rep.content_json, null, 2)], { type: 'application/json' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `chainsleuth-report-${rep.id}.json`;
                          a.click();
                        }}
                        className="px-2.5 py-1 bg-sleuth-800 hover:bg-sleuth-700 text-slate-300 rounded text-xs inline-flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" />
                        <span>JSON</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
