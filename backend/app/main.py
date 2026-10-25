"""
ChainSleuth Backend Main Application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    ChainSleuthException,
    ValidationException,
    ResourceNotFoundException,
    SecurityViolationException,
    ReportTamperingException
)
from app.db.session import init_db
from app.api.routes.health import router as health_router
from app.api.routes.investigations import router as investigations_router
from app.api.routes.reports import router as reports_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ChainSleuth API starting up...")
    init_db()
    yield
    logger.info("ChainSleuth API shutting down.")


app = FastAPI(
    title="ChainSleuth API",
    description="AI-Powered Blockchain Fraud Investigation & Evidence Intelligence Platform API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers (no raw stack traces)
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "detail": exc.message, "details": exc.details}
    )


@app.exception_handler(ResourceNotFoundException)
async def not_found_exception_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "detail": exc.message}
    )


@app.exception_handler(SecurityViolationException)
async def security_exception_handler(request: Request, exc: SecurityViolationException):
    logger.warning(f"Security violation caught: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "Security Violation", "detail": exc.message}
    )


@app.exception_handler(ReportTamperingException)
async def tampering_exception_handler(request: Request, exc: ReportTamperingException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Integrity Check Failed", "detail": exc.message}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred during investigation execution."}
    )


# API v1 routes
API_V1_PREFIX = "/api/v1"
app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(investigations_router, prefix=API_V1_PREFIX)
app.include_router(reports_router, prefix=API_V1_PREFIX)
app.include_router(intelligence_router, prefix=API_V1_PREFIX)
app.include_router(settings_router, prefix=API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tagline": "Investigate the chain. Follow the evidence.",
        "api_docs": "/docs",
        "health": "/api/v1/health"
    }
