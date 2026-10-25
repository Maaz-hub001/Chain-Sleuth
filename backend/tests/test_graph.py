"""
Tests for GraphBuilder, topological algorithms, cycle detection, and limit enforcement.
"""
from app.services.graph.builder import GraphBuilder
from app.services.graph.algorithms import GraphAlgorithms
from app.services.blockchain.adapter import NormalizedTransaction


def test_graph_cycle_detection():
    # A -> B -> C -> A
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("x", "y")]
    cycles = GraphAlgorithms.detect_cycles(edges)
    assert len(cycles) > 0
    assert "a" in cycles[0]
    assert "b" in cycles[0]
    assert "c" in cycles[0]


def test_graph_no_cycles():
    # Linear DAG: A -> B -> C
    edges = [("a", "b"), ("b", "c"), ("c", "d")]
    cycles = GraphAlgorithms.detect_cycles(edges)
    assert len(cycles) == 0


def test_graph_connected_components():
    edges = [("a", "b"), ("b", "c"), ("x", "y")]
    nodes = ["a", "b", "c", "x", "y", "isolated"]
    comps = GraphAlgorithms.find_connected_components(nodes, edges)
    assert len(comps) == 3


def test_graph_builder_limits():
    builder = GraphBuilder()
    txs = []
    # Generate 50 transactions
    for i in range(50):
        tx = NormalizedTransaction(
            chain_id=1,
            tx_hash=f"0x{i:064x}",
            block_number=1000 + i,
            block_timestamp=1700000000 + i * 60,
            from_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            to_address=f"0x{i+1:040x}",
            value_wei="1000000000000000000",
            value_eth=1.0
        )
        txs.append(tx)

    # Build with max_nodes limit of 10
    graph = builder.build_graph(
        investigation_id="inv-test-limits",
        target_identifier="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        transactions=txs,
        max_depth=2,
        max_nodes=10,
        max_edges=15
    )

    assert graph.total_nodes <= 10
    assert graph.total_edges <= 15
    assert len(graph.fan_out_hubs) >= 1
