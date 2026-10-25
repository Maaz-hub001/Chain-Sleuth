import React, { useEffect, useState } from 'react';
import {
  Database,
  Search,
  Plus,
  ExternalLink,
  FileText,
  ShieldAlert,
  Sparkles,
  BookOpen,
  X,
  Check
} from 'lucide-react';
import { api } from '../../services/api';
import type { IntelligenceDocument, IntelligenceSearchResult } from '../../types';
import { Badge } from '../../components/Badge';

export const ThreatIntelPage: React.FC = () => {
  const [documents, setDocuments] = useState<IntelligenceDocument[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<IntelligenceSearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  // Ingestion modal state
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [title, setTitle] = useState('');
  const [publisher, setPublisher] = useState('');
  const [content, setContent] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [docType, setDocType] = useState('advisory');
  const [ingesting, setIngesting] = useState(false);

  // Selected document viewer
  const [selectedDoc, setSelectedDoc] = useState<IntelligenceDocument | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = () => {
    setLoading(true);
    api.getIntelligenceDocuments()
      .then((docs) => {
        setDocuments(docs);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await api.searchIntelligence(searchQuery.trim(), 4);
      setSearchResults(res.results || []);
    } catch (err: any) {
      alert(`Search failed: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngesting(true);
    try {
      await api.ingestIntelligenceDocument({
        title,
        publisher,
        content,
        source_url: sourceUrl.trim() || undefined,
        document_type: docType
      });
      setShowIngestModal(false);
      setTitle('');
      setPublisher('');
      setContent('');
      setSourceUrl('');
      loadDocuments();
      alert('Security intelligence document successfully ingested and indexed into RAG store.');
    } catch (err: any) {
      alert(`Ingestion error: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-cyanAccent-400" />
            <span>Threat Intelligence Knowledge Base</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Curated repository of OFAC sanctions, mixer analyses, exploit post-mortems, and phishing drainer briefs.
          </p>
        </div>

        <button
          onClick={() => setShowIngestModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-semibold text-xs tracking-wide transition-all shadow-md shadow-cyanAccent-500/20 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4 text-slate-950" />
          <span>Ingest New Advisory</span>
        </button>
      </div>

      {/* RAG Retrieval Search Sandbox (Section 5 Page G requirement) */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl p-5 mb-8">
        <h2 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyanAccent-400" />
          <span>Interactive Hybrid RAG Retrieval Sandbox</span>
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Test semantic vector cosine and BM25 keyword retrieval against loaded threat intelligence documents.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search patterns (e.g. 'Tornado Cash mixer zk-SNARKs', 'Euler exploit', 'Permit2 drainer')..."
            className="flex-1 px-4 py-2 bg-sleuth-950 border border-sleuth-700 rounded-lg text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyanAccent-400"
          />
          <button
            type="submit"
            disabled={searching}
            className="px-5 py-2 rounded-lg bg-sleuth-800 hover:bg-sleuth-700 text-cyanAccent-400 border border-sleuth-600 text-xs font-semibold disabled:opacity-50"
          >
            {searching ? 'Querying...' : 'Search'}
          </button>
        </form>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-4 pt-4 border-t border-sleuth-800 space-y-3">
            <span className="text-xs font-semibold text-slate-300">Retrieved Passages & Citations:</span>
            {searchResults.map((res, idx) => (
              <div key={idx} className="p-3.5 rounded-lg bg-sleuth-850 border border-sleuth-700/80 text-xs">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-white">{res.title}</span>
                  <span className="font-mono text-[11px] text-cyanAccent-400">
                    Score: {(res.similarity_score * 100).toFixed(1)}% ({res.retrieval_method})
                  </span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed mb-2 italic">
                  "{res.snippet}"
                </p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>Publisher: {res.publisher}</span>
                  {res.source_url && (
                    <a
                      href={res.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-cyanAccent-400 hover:underline flex items-center gap-1"
                    >
                      <span>Authority Source</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Library Table */}
      <div className="bg-sleuth-900 border border-sleuth-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-sleuth-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Indexed Threat Intelligence Documents ({documents.length})</h2>
          <span className="text-xs text-slate-500">Source Attributed & Cryptographically Hashed</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading intelligence library...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-sleuth-850 text-slate-400 uppercase font-mono text-[11px] border-b border-sleuth-800">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Publisher</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Chunks</th>
                  <th className="px-4 py-3 text-right">Source Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sleuth-800/60 font-sans">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-sleuth-850/50 transition-colors">
                    <td className="px-4 py-3 text-slate-200 font-medium">
                      {doc.title}
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {doc.publisher}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="info">{doc.document_type}</Badge>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400">
                      {doc.chunk_count} chunks
                    </td>
                    <td className="px-4 py-3 text-right">
                      {doc.source_url ? (
                        <a
                          href={doc.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyanAccent-400 hover:underline inline-flex items-center gap-1 text-xs"
                        >
                          <span>Open</span>
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
        )}
      </div>

      {/* Ingestion Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-sleuth-900 border border-sleuth-700 rounded-xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-sleuth-800">
              <h3 className="text-sm font-bold text-white">Ingest Security Advisory into RAG</h3>
              <button onClick={() => setShowIngestModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleIngest} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Lazarus Group Campaign Red Flags"
                  className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded text-slate-200 focus:outline-none focus:border-cyanAccent-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Publisher *</label>
                  <input
                    type="text"
                    required
                    value={publisher}
                    onChange={(e) => setPublisher(e.target.value)}
                    placeholder="e.g. CISA / FBI Cyber Division"
                    className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded text-slate-200 focus:outline-none focus:border-cyanAccent-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Document Type</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded text-slate-200 focus:outline-none focus:border-cyanAccent-400"
                  >
                    <option value="advisory">Security Advisory</option>
                    <option value="exploit_analysis">Exploit Post-Mortem</option>
                    <option value="typology_report">Typology / Laundering Report</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Source URL (Optional, SSRF Validated)</label>
                <input
                  type="url"
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded text-slate-200 focus:outline-none focus:border-cyanAccent-400 font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Content / Advisory Body *</label>
                <textarea
                  required
                  rows={5}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Paste verified intelligence text..."
                  className="w-full px-3 py-2 bg-sleuth-950 border border-sleuth-700 rounded text-slate-200 focus:outline-none focus:border-cyanAccent-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-sleuth-800">
                <button
                  type="button"
                  onClick={() => setShowIngestModal(false)}
                  className="px-4 py-2 bg-sleuth-800 text-slate-300 rounded hover:bg-sleuth-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={ingesting}
                  className="px-5 py-2 bg-cyanAccent-500 hover:bg-cyanAccent-400 text-slate-950 font-bold rounded"
                >
                  {ingesting ? 'Indexing...' : 'Index Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
