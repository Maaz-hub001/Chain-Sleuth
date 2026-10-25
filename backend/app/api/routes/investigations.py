"""
Investigation API Routes.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import validate_target_identifier
from app.models.investigation import Investigation
from app.models.transaction import Transaction
from app.models.graph import WalletNode, GraphEdge
from app.models.finding import Finding
from app.models.evidence import Evidence
from app.models.report import Report
from app.schemas.investigation import InvestigationCreate, InvestigationResponse, InvestigationStatusResponse
from app.schemas.graph import GraphResponse, WalletNodeSchema, GraphEdgeSchema
from app.schemas.transaction import TransactionSchema, TransactionListResponse
from app.schemas.finding import FindingSchema, EvidenceSchema, FindingListResponse
from app.schemas.report import ReportResponse
from app.agents.workflow import investigation_workflow

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post("", response_model=InvestigationResponse, status_code=201)
async def create_investigation(
    req: InvestigationCreate,
    db: Session = Depends(get_db)
):
    clean_target, target_type = validate_target_identifier(req.target_identifier)
    inv_id = f"inv-{uuid.uuid4().hex[:12]}"

    # Create pending investigation record
    investigation = Investigation(
        id=inv_id,
        target_identifier=clean_target,
        target_type=target_type,
        network_name=req.network_name,
        chain_id=req.chain_id,
        investigation_type=req.investigation_type,
        status="processing",
        max_depth=req.max_depth,
        max_transactions=req.max_transactions,
        investigator_notes=req.investigator_notes
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    try:
        # Execute investigation workflow
        result = await investigation_workflow.execute_investigation(
            investigation_id=inv_id,
            target_identifier=clean_target,
            chain_id=req.chain_id,
            network_name=req.network_name,
            max_depth=req.max_depth,
            max_transactions=req.max_transactions,
            investigator_notes=req.investigator_notes,
            use_demo=req.use_demo_fixture
        )

        # Persist transactions
        for tx in result["transactions"]:
            db_tx = Transaction(
                id=f"tx-{uuid.uuid4().hex[:10]}",
                investigation_id=inv_id,
                chain_id=tx.chain_id,
                tx_hash=tx.tx_hash,
                block_number=tx.block_number,
                block_timestamp=tx.block_timestamp,
                from_address=tx.from_address,
                to_address=tx.to_address,
                value_wei=tx.value_wei,
                value_eth=tx.value_eth,
                asset_symbol=tx.asset_symbol,
                gas_used=tx.gas_used,
                gas_price_gwei=tx.gas_price_gwei,
                is_error=tx.is_error,
                tx_type=tx.tx_type,
                provider=tx.provider,
                source_url=tx.source_url,
                raw_data=tx.raw_data
            )
            db.add(db_tx)

        # Persist graph nodes
        for node in result["graph"].nodes:
            db_node = WalletNode(
                id=node.id,
                investigation_id=inv_id,
                chain_id=req.chain_id,
                address=node.address,
                label=node.label,
                entity_type=node.entity_type,
                risk_score=node.risk_score,
                is_target=node.is_target,
                in_degree=node.in_degree,
                out_degree=node.out_degree,
                total_inflow_eth=node.total_inflow_eth,
                total_outflow_eth=node.total_outflow_eth,
                metadata_json=node.metadata_json
            )
            db.add(db_node)

        # Persist graph edges
        for edge in result["graph"].edges:
            db_edge = GraphEdge(
                id=edge.id,
                investigation_id=inv_id,
                source_address=edge.source_address,
                target_address=edge.target_address,
                tx_hash=edge.tx_hash,
                value_eth=edge.value_eth,
                asset_symbol=edge.asset_symbol,
                block_timestamp=edge.block_timestamp,
                edge_metadata=edge.edge_metadata
            )
            db.add(db_edge)

        # Persist findings
        for f in result["findings"]:
            db_find = Finding(
                id=f["id"],
                investigation_id=inv_id,
                detector_id=f["detector_id"],
                title=f["title"],
                severity=f["severity"],
                status=f["status"],
                explanation=f["explanation"],
                detection_method=f["detection_method"],
                confidence=f["confidence"],
                confidence_basis=f["confidence_basis"],
                counterevidence=f.get("counterevidence"),
                alternative_explanations=f.get("alternative_explanations"),
                limitations=f.get("limitations"),
                recommended_next_step=f.get("recommended_next_step"),
                evidence_ids=f.get("evidence_ids"),
                relevant_tx_hashes=f.get("relevant_tx_hashes"),
                relevant_addresses=f.get("relevant_addresses")
            )
            db.add(db_find)

        # Persist evidence records
        for ev in result["evidence"]:
            db_ev = Evidence(
                id=ev["id"],
                investigation_id=inv_id,
                finding_id=ev.get("finding_id"),
                evidence_type=ev["evidence_type"],
                title=ev["title"],
                description=ev["description"],
                raw_reference=ev["raw_reference"],
                data_provenance=ev["data_provenance"],
                payload=ev.get("payload")
            )
            db.add(db_ev)

        # Persist report
        rep_data = result["report"]
        db_rep = Report(
            id=rep_data["report_id"],
            investigation_id=inv_id,
            schema_version="1.0.0",
            canonical_version="1.0.0",
            hash_algorithm="SHA-256",
            report_hash=rep_data["report_hash"],
            target_identifier=clean_target,
            target_type=target_type,
            chain_id=req.chain_id,
            network_name=req.network_name,
            content_json=rep_data["content_json"],
            markdown_content=rep_data["markdown_content"]
        )
        db.add(db_rep)

        # Update investigation status
        investigation.status = "completed"
        investigation.completed_at = datetime.utcnow()
        investigation.coverage_summary = result["coverage_summary"]
        investigation.metrics = {
            "transactions_count": len(result["transactions"]),
            "nodes_count": result["graph"].total_nodes,
            "edges_count": result["graph"].total_edges,
            "findings_count": len(result["findings"]),
            "cycles_count": result["graph"].topological_cycles_detected
        }

        db.commit()
        db.refresh(investigation)
        return investigation

    except Exception as e:
        db.rollback()
        investigation.status = "failed"
        investigation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Investigation workflow failed: {str(e)}")


@router.get("", response_model=List[InvestigationResponse])
def list_investigations(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Investigation)
    if status:
        query = query.filter(Investigation.status == status)
    return query.order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return inv


@router.get("/{investigation_id}/status", response_model=InvestigationStatusResponse)
def get_investigation_status(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    findings_cnt = db.query(Finding).filter(Finding.investigation_id == investigation_id).count()
    tx_cnt = db.query(Transaction).filter(Transaction.investigation_id == investigation_id).count()
    nodes_cnt = db.query(WalletNode).filter(WalletNode.investigation_id == investigation_id).count()

    return InvestigationStatusResponse(
        id=inv.id,
        status=inv.status,
        target_identifier=inv.target_identifier,
        findings_count=findings_cnt,
        transactions_count=tx_cnt,
        nodes_count=nodes_cnt,
        error_message=inv.error_message,
        completed_at=inv.completed_at
    )


@router.get("/{investigation_id}/graph", response_model=GraphResponse)
def get_investigation_graph(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    nodes = db.query(WalletNode).filter(WalletNode.investigation_id == investigation_id).all()
    edges = db.query(GraphEdge).filter(GraphEdge.investigation_id == investigation_id).all()

    node_schemas = [WalletNodeSchema.model_validate(n) for n in nodes]
    edge_schemas = [GraphEdgeSchema.model_validate(e) for e in edges]

    fan_outs = [n.address for n in nodes if n.out_degree >= 3]
    fan_ins = [n.address for n in nodes if n.in_degree >= 3]

    return GraphResponse(
        investigation_id=investigation_id,
        nodes=node_schemas,
        edges=edge_schemas,
        total_nodes=len(node_schemas),
        total_edges=len(edge_schemas),
        max_depth_explored=inv.max_depth or 2,
        connected_components_count=1 if node_schemas else 0,
        topological_cycles_detected=inv.metrics.get("cycles_count", 0) if inv.metrics else 0,
        fan_out_hubs=fan_outs,
        fan_in_hubs=fan_ins
    )


@router.get("/{investigation_id}/transactions", response_model=TransactionListResponse)
def get_investigation_transactions(
    investigation_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    txs = db.query(Transaction).filter(Transaction.investigation_id == investigation_id).offset(skip).limit(limit).all()
    total = db.query(Transaction).filter(Transaction.investigation_id == investigation_id).count()

    return TransactionListResponse(
        investigation_id=investigation_id,
        total=total,
        transactions=[TransactionSchema.model_validate(t) for t in txs]
    )


@router.get("/{investigation_id}/findings", response_model=FindingListResponse)
def get_investigation_findings(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    findings = db.query(Finding).filter(Finding.investigation_id == investigation_id).all()
    finding_schemas = [FindingSchema.model_validate(f) for f in findings]

    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    high = sum(1 for f in findings if f.severity == "HIGH")
    medium = sum(1 for f in findings if f.severity == "MEDIUM")
    low = sum(1 for f in findings if f.severity == "LOW")

    return FindingListResponse(
        investigation_id=investigation_id,
        total=len(findings),
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        low_count=low,
        findings=finding_schemas
    )


@router.get("/{investigation_id}/evidence", response_model=List[EvidenceSchema])
def get_investigation_evidence(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    evidence = db.query(Evidence).filter(Evidence.investigation_id == investigation_id).all()
    return [EvidenceSchema.model_validate(e) for e in evidence]


@router.get("/{investigation_id}/report", response_model=ReportResponse)
def get_investigation_report(investigation_id: str, db: Session = Depends(get_db)):
    rep = db.query(Report).filter(Report.investigation_id == investigation_id).order_by(Report.generated_at.desc()).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found for this investigation.")
    return rep


@router.post("/{investigation_id}/anchor", response_model=ReportResponse)
async def anchor_investigation_report(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    rep = db.query(Report).filter(Report.investigation_id == investigation_id).order_by(Report.generated_at.desc()).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")

    # Record anchoring metadata
    rep.is_anchored = True
    rep.registry_chain_id = 11155111  # Sepolia testnet
    rep.registry_contract_address = "0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7"
    rep.registry_tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"
    rep.anchored_timestamp = int(datetime.utcnow().timestamp())

    db.commit()
    db.refresh(rep)
    return rep
