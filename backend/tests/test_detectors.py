"""
Unit tests for deterministic fraud & laundering detectors (positive & negative cases).
"""
from app.services.detection.detectors.fan_in_out import FanInOutDetector
from app.services.detection.detectors.rapid_movement import RapidMovementDetector
from app.services.detection.detectors.circular import CircularTransferDetector
from app.services.detection.detectors.consolidation import ConsolidationDetector
from app.services.detection.detectors.repeated_transfers import RepeatedTransfersDetector
from app.services.detection.detectors.known_entity import KnownEntityDetector
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse, WalletNodeSchema, GraphEdgeSchema


def create_sample_tx(
    tx_hash: str,
    from_addr: str,
    to_addr: str,
    val_eth: float,
    timestamp: int
) -> NormalizedTransaction:
    return NormalizedTransaction(
        chain_id=1,
        tx_hash=tx_hash,
        block_number=1000,
        block_timestamp=timestamp,
        from_address=from_addr,
        to_address=to_addr,
        value_wei=str(int(val_eth * 1e18)),
        value_eth=val_eth
    )


def test_fan_out_detector_positive():
    detector = FanInOutDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    # Target disperses to 4 addresses within 120 seconds
    txs = [
        create_sample_tx("0x01", target, "0x1111111111111111111111111111111111111111", 5.0, 1000),
        create_sample_tx("0x02", target, "0x2222222222222222222222222222222222222222", 5.0, 1040),
        create_sample_tx("0x03", target, "0x3333333333333333333333333333333333333333", 5.0, 1080),
        create_sample_tx("0x04", target, "0x4444444444444444444444444444444444444444", 5.0, 1120)
    ]
    graph = GraphResponse(investigation_id="t", nodes=[], edges=[], total_nodes=0, total_edges=0, max_depth_explored=1, connected_components_count=1, topological_cycles_detected=0, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 1
    assert findings[0].severity == "HIGH"
    assert "Fan-Out" in findings[0].title


def test_fan_out_detector_negative():
    detector = FanInOutDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    # Target sends to only 1 recipient
    txs = [create_sample_tx("0x01", target, "0x1111111111111111111111111111111111111111", 5.0, 1000)]
    graph = GraphResponse(investigation_id="t", nodes=[], edges=[], total_nodes=0, total_edges=0, max_depth_explored=1, connected_components_count=1, topological_cycles_detected=0, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 0


def test_rapid_movement_detector_positive():
    detector = RapidMovementDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    # Inflow at t=1000, outflow at t=1120 (dwell = 120s < 1800s threshold)
    txs = [
        create_sample_tx("0x01", "0xaaaa", target, 10.0, 1000),
        create_sample_tx("0x02", target, "0xbbbb", 9.8, 1120)
    ]
    graph = GraphResponse(investigation_id="t", nodes=[], edges=[], total_nodes=0, total_edges=0, max_depth_explored=1, connected_components_count=1, topological_cycles_detected=0, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 1
    assert "Rapid Relay" in findings[0].title


def test_rapid_movement_detector_negative():
    detector = RapidMovementDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    # Inflow at t=1000, outflow 48 hours later (t=1000 + 172800)
    txs = [
        create_sample_tx("0x01", "0xaaaa", target, 10.0, 1000),
        create_sample_tx("0x02", target, "0xbbbb", 9.8, 1000 + 172800)
    ]
    graph = GraphResponse(investigation_id="t", nodes=[], edges=[], total_nodes=0, total_edges=0, max_depth_explored=1, connected_components_count=1, topological_cycles_detected=0, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 0


def test_circular_detector_positive():
    detector = CircularTransferDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    txs = [
        create_sample_tx("0x01", target, "0xbbbb", 5.0, 1000),
        create_sample_tx("0x02", "0xbbbb", "0xcccc", 4.9, 1050),
        create_sample_tx("0x03", "0xcccc", target, 4.8, 1100)
    ]
    edges = [
        GraphEdgeSchema(id="e1", source_address=target, target_address="0xbbbb", tx_hash="0x01", value_eth=5.0, asset_symbol="ETH", block_timestamp=1000),
        GraphEdgeSchema(id="e2", source_address="0xbbbb", target_address="0xcccc", tx_hash="0x02", value_eth=4.9, asset_symbol="ETH", block_timestamp=1050),
        GraphEdgeSchema(id="e3", source_address="0xcccc", target_address=target, tx_hash="0x03", value_eth=4.8, asset_symbol="ETH", block_timestamp=1100)
    ]
    graph = GraphResponse(investigation_id="t", nodes=[], edges=edges, total_nodes=3, total_edges=3, max_depth_explored=2, connected_components_count=1, topological_cycles_detected=1, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 1
    assert "Circular Transfer" in findings[0].title


def test_known_entity_detector():
    detector = KnownEntityDetector()
    target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    # Tornado Cash Router address
    tornado_router = "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"
    nodes = [
        WalletNodeSchema(id="n1", address=tornado_router, label="Tornado Cash Router", entity_type="mixer", risk_score=0.9, is_target=False, in_degree=1, out_degree=0, total_inflow_eth=10.0, total_outflow_eth=0.0)
    ]
    txs = [create_sample_tx("0x01", target, tornado_router, 10.0, 1000)]
    graph = GraphResponse(investigation_id="t", nodes=nodes, edges=[], total_nodes=1, total_edges=1, max_depth_explored=1, connected_components_count=1, topological_cycles_detected=0, fan_out_hubs=[], fan_in_hubs=[])
    findings = detector.detect(target, txs, graph)
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"
    assert "Tornado Cash" in findings[0].title
