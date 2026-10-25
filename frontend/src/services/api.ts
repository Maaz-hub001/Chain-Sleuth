/**
 * API client communicating with ChainSleuth FastAPI backend (/api/v1).
 */
import type {
  Investigation,
  InvestigationCreate,
  GraphResponse,
  Transaction,
  Finding,
  Evidence,
  Report,
  ReportVerificationResult,
  IntelligenceDocument,
  IntelligenceSearchResult,
  ProviderStatus
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'API request failed';
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorJson.error || errorDetail;
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Investigations
  async createInvestigation(data: InvestigationCreate): Promise<Investigation> {
    const res = await fetch(`${API_BASE}/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<Investigation>(res);
  },

  async getInvestigations(): Promise<Investigation[]> {
    const res = await fetch(`${API_BASE}/investigations`);
    return handleResponse<Investigation[]>(res);
  },

  async getInvestigation(id: string): Promise<Investigation> {
    const res = await fetch(`${API_BASE}/investigations/${id}`);
    return handleResponse<Investigation>(res);
  },

  async getInvestigationStatus(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/investigations/${id}/status`);
    return handleResponse<any>(res);
  },

  async getInvestigationGraph(id: string): Promise<GraphResponse> {
    const res = await fetch(`${API_BASE}/investigations/${id}/graph`);
    return handleResponse<GraphResponse>(res);
  },

  async getInvestigationTransactions(id: string): Promise<{ total: number; transactions: Transaction[] }> {
    const res = await fetch(`${API_BASE}/investigations/${id}/transactions`);
    return handleResponse<{ total: number; transactions: Transaction[] }>(res);
  },

  async getInvestigationFindings(id: string): Promise<{ total: number; critical_count: number; high_count: number; medium_count: number; low_count: number; findings: Finding[] }> {
    const res = await fetch(`${API_BASE}/investigations/${id}/findings`);
    return handleResponse<any>(res);
  },

  async getInvestigationEvidence(id: string): Promise<Evidence[]> {
    const res = await fetch(`${API_BASE}/investigations/${id}/evidence`);
    return handleResponse<Evidence[]>(res);
  },

  async getInvestigationReport(id: string): Promise<Report> {
    const res = await fetch(`${API_BASE}/investigations/${id}/report`);
    return handleResponse<Report>(res);
  },

  async anchorReport(investigationId: string): Promise<Report> {
    const res = await fetch(`${API_BASE}/investigations/${investigationId}/anchor`, {
      method: 'POST'
    });
    return handleResponse<Report>(res);
  },

  // Verification
  async verifyReport(
    reportPayload: Record<string, any>,
    expectedHash?: string,
    reportId?: string,
    verifyOnChain: boolean = false
  ): Promise<ReportVerificationResult> {
    const res = await fetch(`${API_BASE}/reports/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        report_id: reportId,
        report_payload: reportPayload,
        expected_hash: expectedHash,
        verify_on_chain: verifyOnChain,
      }),
    });
    return handleResponse<ReportVerificationResult>(res);
  },

  async getAllReports(): Promise<Report[]> {
    const res = await fetch(`${API_BASE}/reports`);
    return handleResponse<Report[]>(res);
  },

  // Threat Intelligence
  async getIntelligenceDocuments(): Promise<IntelligenceDocument[]> {
    const res = await fetch(`${API_BASE}/intelligence/documents`);
    return handleResponse<IntelligenceDocument[]>(res);
  },

  async ingestIntelligenceDocument(doc: {
    title: string;
    publisher: string;
    content: string;
    source_url?: string;
    publication_date?: string;
    document_type?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/intelligence/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(doc),
    });
    return handleResponse<any>(res);
  },

  async searchIntelligence(query: string, topK: number = 3): Promise<{ query: string; total_results: number; results: IntelligenceSearchResult[] }> {
    const res = await fetch(`${API_BASE}/intelligence/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK }),
    });
    return handleResponse<any>(res);
  },

  // Settings & Providers
  async getProvidersHealth(): Promise<{ timestamp: string; providers: ProviderStatus[] }> {
    const res = await fetch(`${API_BASE}/health/providers`);
    return handleResponse<any>(res);
  },

  async getSupportedNetworks(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/settings/networks`);
    return handleResponse<any[]>(res);
  },

  async testProvider(providerName: string, endpointUrl?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/settings/providers/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_name: providerName, endpoint_url: endpointUrl }),
    });
    return handleResponse<any>(res);
  },
};
