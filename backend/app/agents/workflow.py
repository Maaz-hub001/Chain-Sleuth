"""
Controlled AI Investigation Agent Workflow:
Executes the 12-stage forensic investigation state machine.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.services.blockchain.service import blockchain_service
from app.services.graph.builder import GraphBuilder
from app.services.detection.engine import detection_engine
from app.services.rag.service import rag_service
from app.services.reports.generator import ReportGenerator
import httpx


class InvestigationWorkflow:
    def __init__(self):
        self.graph_builder = GraphBuilder()

    async def execute_investigation(
        self,
        investigation_id: str,
        target_identifier: str,
        chain_id: int = 1,
        network_name: str = "ethereum_mainnet",
        max_depth: int = 2,
        max_transactions: int = 100,
        investigator_notes: Optional[str] = None,
        use_demo: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the bounded 12-step investigation pipeline:
        1. Parse & validate target
        2. Check provider health
        3. Retrieve blockchain transactions within configured limits
        4. Normalize transactions
        5. Build bounded multi-hop graph
        6. Run deterministic detectors
        7. Query RAG threat intelligence for matched patterns
        8. Cross-reference evidence and synthesize counterevidence
        9. Generate structured report
        10. Validate report against schema
        11. Calculate canonical SHA-256 report hash
        12. Return complete execution artifact
        """
        logger.info(f"Starting Investigation Workflow for {target_identifier} (ID: {investigation_id})")

        # Step 1-4: Blockchain Ingestion
        txs, coverage, target_type = await blockchain_service.fetch_target_transactions(
            target_identifier=target_identifier,
            chain_id=chain_id,
            max_transactions=max_transactions,
            use_demo=use_demo
        )

        coverage_dict = {
            "provider": coverage.provider,
            "network_name": coverage.network_name,
            "chain_id": coverage.chain_id,
            "coverage_level": coverage.coverage_level,
            "is_complete": coverage.is_complete,
            "transactions_retrieved": coverage.transactions_retrieved,
            "limitations": coverage.limitations,
            "data_retrieved_at": coverage.data_retrieved_at
        }

        # Step 5: Build Graph
        graph = self.graph_builder.build_graph(
            investigation_id=investigation_id,
            target_identifier=target_identifier,
            transactions=txs,
            max_depth=max_depth,
            max_nodes=settings.MAX_NODES,
            max_edges=settings.MAX_EDGES
        )

        # Step 6: Deterministic Detection
        findings_data, evidence_data = detection_engine.run_all(
            investigation_id=investigation_id,
            target_identifier=target_identifier,
            transactions=txs,
            graph=graph
        )

        # Step 7: RAG Threat Intelligence Retrieval
        # Construct search query based on observed patterns
        query_terms = [target_identifier]
        for f in findings_data:
            query_terms.append(f["title"])
            if f.get("detector_id") == "DET_KNOWN_ENTITY":
                query_terms.append("tornado cash mixer sanctions")
            if f.get("detector_id") == "DET_CIRCULAR_LOOP":
                query_terms.append("circular wash laundering topology")
            if f.get("detector_id") == "DET_RAPID_RELAY":
                query_terms.append("transit wallet peel chain rapid relay")

        rag_query = " ".join(query_terms[:4])
        retrieved_intel = rag_service.search_intelligence(rag_query, top_k=3)

        # Step 8-11: Report Generation & Canonical Hasher
        graph_summary = {
            "total_nodes": graph.total_nodes,
            "total_edges": graph.total_edges,
            "max_depth_explored": graph.max_depth_explored,
            "connected_components_count": graph.connected_components_count,
            "topological_cycles_detected": graph.topological_cycles_detected,
            "fan_out_hubs": graph.fan_out_hubs,
            "fan_in_hubs": graph.fan_in_hubs
        }

        report_result = ReportGenerator.generate_report(
            investigation_id=investigation_id,
            target_identifier=target_identifier,
            target_type=target_type,
            chain_id=chain_id,
            network_name=network_name,
            coverage_summary=coverage_dict,
            findings_data=findings_data,
            evidence_data=evidence_data,
            intel_references=retrieved_intel,
            graph_summary=graph_summary,
            ai_synthesis_notes=[]
        )

        logger.info(f"Investigation {investigation_id} completed. Generated report hash: {report_result['report_hash']}")

        return {
            "investigation_id": investigation_id,
            "target_identifier": target_identifier,
            "target_type": target_type,
            "chain_id": chain_id,
            "network_name": network_name,
            "transactions": txs,
            "graph": graph,
            "findings": findings_data,
            "evidence": evidence_data,
            "coverage_summary": coverage_dict,
            "report": report_result,
            "status": "completed",
            "completed_at": datetime.utcnow()
        }


investigation_workflow = InvestigationWorkflow()
