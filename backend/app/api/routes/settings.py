"""
Settings and Provider Configuration API Routes.
"""
import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings
from app.core.security import validate_public_url
from app.schemas.settings import ProviderTestRequest, ProviderTestResponse
from app.services.blockchain.service import blockchain_service

router = APIRouter(prefix="/settings", tags=["Settings"])


SUPPORTED_NETWORKS = [
    {
        "chain_id": 1,
        "name": "Ethereum Mainnet",
        "slug": "ethereum_mainnet",
        "native_currency": "ETH",
        "rpc_url": settings.EVM_RPC_URL,
        "explorer_url": "https://etherscan.io",
        "is_default": True
    },
    {
        "chain_id": 11155111,
        "name": "Ethereum Sepolia (Testnet)",
        "slug": "ethereum_sepolia",
        "native_currency": "SepoliaETH",
        "rpc_url": settings.SEPOLIA_RPC_URL,
        "explorer_url": "https://sepolia.etherscan.io",
        "is_default": False
    },
    {
        "chain_id": 8453,
        "name": "Base Mainnet",
        "slug": "base_mainnet",
        "native_currency": "ETH",
        "rpc_url": settings.BASE_RPC_URL,
        "explorer_url": "https://basescan.org",
        "is_default": False
    },
    {
        "chain_id": 0,
        "name": "Local Sandbox (Demo Fixture)",
        "slug": "demo_sandbox",
        "native_currency": "ETH",
        "rpc_url": "local://fixture",
        "explorer_url": "local://graph",
        "is_default": False
    }
]


@router.get("/networks")
def get_supported_networks():
    return SUPPORTED_NETWORKS


@router.get("/providers")
async def get_providers():
    return await blockchain_service.get_all_providers_health()


@router.post("/providers/test", response_model=ProviderTestResponse)
async def test_provider(req: ProviderTestRequest):
    t0 = time.time()
    endpoint = req.endpoint_url or settings.EVM_RPC_URL
    try:
        clean_url = validate_public_url(endpoint)
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(
                clean_url,
                json={"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}
            )
            latency = round((time.time() - t0) * 1000, 2)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    block_num = int(data["result"], 16)
                    return ProviderTestResponse(
                        provider_name=req.provider_name,
                        success=True,
                        status="operational",
                        message=f"Successfully connected to RPC. Current block: {block_num}",
                        latency_ms=latency
                    )
            return ProviderTestResponse(
                provider_name=req.provider_name,
                success=False,
                status="degraded",
                message=f"HTTP {resp.status_code}: {resp.text[:120]}",
                latency_ms=latency
            )
    except Exception as e:
        latency = round((time.time() - t0) * 1000, 2)
        return ProviderTestResponse(
            provider_name=req.provider_name,
            success=False,
            status="error",
            message=f"Connection test failed: {str(e)}",
            latency_ms=latency
        )
