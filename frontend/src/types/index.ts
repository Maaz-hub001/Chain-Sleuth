/**
 * Frontend TypeScript Data Contracts for ChainSleuth.
 * Mirrors FastAPI Pydantic contracts under /api/v1.
 */

export interface InvestigationCreate {
  target_identifier: string;
  network_name?: string;
  chain_id?: number;
  investigation_type?: string;
  max_depth?: number;
  max_transactions?: number;
  investigator_notes?: string;
  use_demo_fixture?: boolean;
}

export interface Investigation {
  id: string;
  target_identifier: string;
  target_type: 'address' | 'transaction';
  network_name: string;
  chain_id: number;
  investigation_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  max_depth: number;
  max_transactions: number;
  investigator_notes?: string;
  coverage_summary?: CoverageSummary;
  metrics?: {
    transactions_count?: number;
    nodes_count?: number;
    edges_count?: number;
    findings_count?: number;
    cycles_count?: number;
  };
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface CoverageSummary {
  provider: string;
  network_name: string;
  chain_id: number;
  coverage_level: string;
  is_complete: boolean;
  transactions_retrieved: number;
  limitations: string[];
  data_retrieved_at: string;
}

export interface Transaction {
  id: string;
  investigation_id: string;
  chain_id: number;
  tx_hash: string;
  block_number: number;
  block_timestamp: number;
  from_address: string;
  to_address?: string;
  value_wei: string;
  value_eth: number;
  asset_symbol: string;
  token_address?: string;
  gas_used?: number;
  gas_price_gwei?: number;
  is_error: boolean;
  tx_type: string;
  provider: string;
  source_url?: string;
  retrieved_at: string;
}

export interface WalletNode {
  id: string;
  address: string;
  label?: string;
  entity_type: 'target' | 'wallet' | 'contract' | 'mixer' | 'exchange' | 'sanctioned_entity' | 'intermediate_relay';
  risk_score: number;
  is_target: boolean;
  in_degree: number;
  out_degree: number;
  total_inflow_eth: number;
  total_outflow_eth: number;
  metadata_json?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source_address: string;
  target_address: string;
  tx_hash: string;
  value_eth: number;
  asset_symbol: string;
  block_timestamp: number;
  edge_metadata?: Record<string, any>;
}

export interface GraphResponse {
  investigation_id: string;
  nodes: WalletNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
  max_depth_explored: number;
  connected_components_count: number;
  topological_cycles_detected: number;
  fan_out_hubs: string[];
  fan_in_hubs: string[];
}

export interface Finding {
  id: string;
  investigation_id: string;
  detector_id: string;
  title: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'confirmed_observation' | 'suspicious_pattern' | 'unverified_intelligence' | 'insufficient_evidence';
  explanation: string;
  detection_method: string;
  confidence: number;
  confidence_basis: string;
  counterevidence?: string;
  alternative_explanations?: string[];
  limitations?: string;
  recommended_next_step?: string;
  evidence_ids?: string[];
  relevant_tx_hashes?: string[];
  relevant_addresses?: string[];
  created_at: string;
}

export interface Evidence {
  id: string;
  evidence_type: string;
  title: string;
  description: string;
  raw_reference: string;
  data_provenance: string;
  payload?: Record<string, any>;
  created_at: string;
}

export interface Report {
  id: string;
  investigation_id: string;
  schema_version: string;
  canonical_version: string;
  hash_algorithm: string;
  report_hash: string;
  target_identifier: string;
  target_type: string;
  chain_id: number;
  network_name: string;
  content_json: Record<string, any>;
  markdown_content: string;
  is_anchored: boolean;
  registry_chain_id?: number;
  registry_contract_address?: string;
  registry_tx_hash?: string;
  anchored_timestamp?: number;
  generated_at: string;
}

export interface ReportVerificationResult {
  is_valid: boolean;
  computed_hash: string;
  claimed_hash: string;
  hash_algorithm: string;
  canonical_version: string;
  mismatch_fields: string[];
  on_chain_checked: boolean;
  on_chain_verified: boolean;
  on_chain_block?: number;
  on_chain_reporter?: string;
  on_chain_timestamp?: number;
  registry_contract_address?: string;
  status_summary: string;
}

export interface IntelligenceDocument {
  id: string;
  title: string;
  publisher: string;
  source_url?: string;
  document_type: string;
  chunk_count: number;
}

export interface IntelligenceSearchResult {
  document_id: string;
  chunk_id: string;
  title: string;
  publisher: string;
  source_url?: string;
  snippet: string;
  similarity_score: number;
  retrieval_method: string;
}

export interface ProviderStatus {
  name: string;
  category: string;
  status: 'operational' | 'not_configured' | 'degraded' | 'error';
  endpoint_display: string;
  details?: string;
  response_time_ms?: number;
}
