"""
Health check endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.session import get_db
from app.services.blockchain.service import blockchain_service
from app.schemas.settings import HealthResponse, ProvidersHealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def get_health(db: Session = Depends(get_db)):
    db_status = "operational"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy" if "unhealthy" not in db_status else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        providers_summary={
            "blockchain_rpc": settings.EVM_RPC_URL,
            "llm_provider": settings.LLM_PROVIDER,
            "vector_store": settings.VECTOR_STORE,
            "database_dialect": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
        }
    )


@router.get("/providers", response_model=ProvidersHealthResponse)
async def get_providers_health():
    provider_statuses = await blockchain_service.get_all_providers_health()
    return ProvidersHealthResponse(
        timestamp=datetime.utcnow().isoformat() + "Z",
        providers=provider_statuses
    )
