"""
Graph Builder: constructs bounded multi-hop transaction networks.
"""
import os
import json
import uuid
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from app.core.config import settings
from app.services.blockchain.adapter import NormalizedTransaction
from app.services.graph.algorithms import GraphAlgorithms
from app.schemas.graph import WalletNodeSchema, GraphEdgeSchema, GraphResponse


class GraphBuilder:
    def __init__(self, known_entities_path: Optional[str] = None):
        self.known_entities_path = known_entities_path or os.path.join(settings.FIXTURES_DIR, "known_entities.json")
        self.known_entities: Dict[str, Dict[str, Any]] = self._load_known_entities()

    def _load_known_entities(self) -> Dict[str, Dict[str, Any]]:
        lookup = {}
        if os.path.exists(self.known_entities_path):
            try:
                with open(self.known_entities_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("entities", []):
                        lookup[item["address"].lower()] = item
            except Exception:
                pass
        return lookup

    def build_graph(
        self,
        investigation_id: str,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        max_depth: int = 2,
        max_nodes: int = 150,
        max_edges: int = 300
    ) -> GraphResponse:
        target_lower = target_identifier.lower()

        in_degrees = defaultdict(int)
        out_degrees = defaultdict(int)
        inflows = defaultdict(float)
        outflows = defaultdict(float)
        all_addresses = set()

        edges_raw: List[Dict[str, Any]] = []
        algo_edges: List[Tuple[str, str]] = []

        # Deduplicate transactions by hash and filter valid endpoints
        seen_txs = set()
        for tx in transactions:
            if tx.tx_hash in seen_txs:
                continue
            seen_txs.add(tx.tx_hash)

            src = tx.from_address.lower() if tx.from_address else None
            dst = tx.to_address.lower() if tx.to_address else None

            if not src or not dst:
                continue

            all_addresses.add(src)
            all_addresses.add(dst)

            out_degrees[src] += 1
            in_degrees[dst] += 1
            outflows[src] += tx.value_eth
            inflows[dst] += tx.value_eth

            edge_obj = {
                "id": f"edge-{uuid.uuid4().hex[:12]}",
                "source_address": src,
                "target_address": dst,
                "tx_hash": tx.tx_hash,
                "value_eth": round(tx.value_eth, 4),
                "asset_symbol": tx.asset_symbol,
                "block_timestamp": tx.block_timestamp,
                "edge_metadata": {
                    "is_error": tx.is_error,
                    "tx_type": tx.tx_type,
                    "gas_used": tx.gas_used
                }
            }
            edges_raw.append(edge_obj)
            algo_edges.append((src, dst))

            if len(edges_raw) >= max_edges:
                break

        # Bounded nodes
        nodes: List[WalletNodeSchema] = []
        for addr in list(all_addresses)[:max_nodes]:
            is_target = (addr == target_lower)
            known = self.known_entities.get(addr)

            if is_target:
                entity_type = "target"
                label = "Target Investigation Subject"
                risk_score = 0.5
            elif known:
                entity_type = known.get("entity_type", "wallet")
                label = known.get("name", "Identified Entity")
                risk_score = 0.9 if known.get("risk_level") == "critical" else 0.3
            elif in_degrees[addr] == 0:
                entity_type = "source_wallet"
                label = "Inflow Source"
                risk_score = 0.2
            elif out_degrees[addr] == 0:
                entity_type = "destination_wallet"
                label = "Terminal Destination"
                risk_score = 0.2
            else:
                entity_type = "intermediate_relay"
                label = "Transit Relay"
                risk_score = 0.4

            node_schema = WalletNodeSchema(
                id=f"node-{investigation_id[:8]}-{addr[2:10]}",
                address=addr,
                label=label,
                entity_type=entity_type,
                risk_score=risk_score,
                is_target=is_target,
                in_degree=in_degrees[addr],
                out_degree=out_degrees[addr],
                total_inflow_eth=round(inflows[addr], 4),
                total_outflow_eth=round(outflows[addr], 4),
                metadata_json=known or {}
            )
            nodes.append(node_schema)

        edges = [GraphEdgeSchema(**e) for e in edges_raw]

        # Algorithms
        components = GraphAlgorithms.find_connected_components(list(all_addresses), algo_edges)
        cycles = GraphAlgorithms.detect_cycles(algo_edges)
        fan_out, fan_in = GraphAlgorithms.identify_hubs(in_degrees, out_degrees, fan_threshold=3)

        return GraphResponse(
            investigation_id=investigation_id,
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
            max_depth_explored=max_depth,
            connected_components_count=len(components),
            topological_cycles_detected=len(cycles),
            fan_out_hubs=fan_out,
            fan_in_hubs=fan_in
        )
