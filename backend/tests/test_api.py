"""
Integration tests for ChainSleuth REST API endpoints.
"""
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data


def test_providers_health(client: TestClient):
    resp = client.get("/api/v1/health/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert "providers" in data
    assert len(data["providers"]) >= 3


def test_supported_networks(client: TestClient):
    resp = client.get("/api/v1/settings/networks")
    assert resp.status_code == 200
    networks = resp.json()
    assert len(networks) >= 3
    slugs = [n["slug"] for n in networks]
    assert "ethereum_mainnet" in slugs


def test_create_and_query_investigation_lifecycle(client: TestClient):
    # Create investigation using demo fixture
    payload = {
        "target_identifier": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "network_name": "demo_sandbox",
        "chain_id": 1,
        "investigation_type": "comprehensive",
        "max_depth": 2,
        "max_transactions": 50,
        "use_demo_fixture": True,
        "investigator_notes": "Integration test automated run"
    }

    create_resp = client.post("/api/v1/investigations", json=payload)
    assert create_resp.status_code == 201
    inv_data = create_resp.json()
    inv_id = inv_data["id"]
    assert inv_data["status"] == "completed"

    # Query Status
    status_resp = client.get(f"/api/v1/investigations/{inv_id}/status")
    assert status_resp.status_code == 200
    st_data = status_resp.json()
    assert st_data["status"] == "completed"
    assert st_data["findings_count"] > 0
    assert st_data["transactions_count"] > 0

    # Query Graph
    graph_resp = client.get(f"/api/v1/investigations/{inv_id}/graph")
    assert graph_resp.status_code == 200
    g_data = graph_resp.json()
    assert g_data["total_nodes"] > 0
    assert g_data["total_edges"] > 0

    # Query Findings
    find_resp = client.get(f"/api/v1/investigations/{inv_id}/findings")
    assert find_resp.status_code == 200
    f_data = find_resp.json()
    assert f_data["total"] > 0
    assert len(f_data["findings"]) > 0

    # Query Report
    rep_resp = client.get(f"/api/v1/investigations/{inv_id}/report")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert len(rep_data["report_hash"]) == 64
    assert "markdown_content" in rep_data

    # Cryptographically verify the generated report
    verify_resp = client.post(
        "/api/v1/reports/verify",
        json={
            "report_id": rep_data["id"],
            "report_payload": rep_data["content_json"],
            "expected_hash": rep_data["report_hash"],
            "verify_on_chain": False
        }
    )
    assert verify_resp.status_code == 200
    ver_data = verify_resp.json()
    assert ver_data["is_valid"] is True
    assert ver_data["computed_hash"] == rep_data["report_hash"]
