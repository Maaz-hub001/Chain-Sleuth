"""
Pydantic schemas for Transaction Graph.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class WalletNodeSchema(BaseModel):
    id: str
    address: str
    label: Optional[str] = None
    entity_type: str
    risk_score: float
    is_target: bool
    in_degree: int
    out_degree: int
    total_inflow_eth: float
    total_outflow_eth: float
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class GraphEdgeSchema(BaseModel):
    id: str
    source_address: str
    target_address: str
    tx_hash: str
    value_eth: float
    asset_symbol: str
    block_timestamp: int
    edge_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class GraphResponse(BaseModel):
    investigation_id: str
    nodes: List[WalletNodeSchema]
    edges: List[GraphEdgeSchema]
    total_nodes: int
    total_edges: int
    max_depth_explored: int
    connected_components_count: int
    topological_cycles_detected: int
    fan_out_hubs: List[str]
    fan_in_hubs: List[str]
