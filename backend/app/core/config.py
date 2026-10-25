"""
Configuration and settings management for ChainSleuth.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application settings
    APP_NAME: str = "ChainSleuth"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./chainsleuth.db"

    # EVM & Blockchain Configuration
    EVM_RPC_URL: str = "https://rpc.ankr.com/eth"
    SEPOLIA_RPC_URL: str = "https://rpc.ankr.com/eth_sepolia"
    BASE_RPC_URL: str = "https://mainnet.base.org"
    CHAIN_ID: int = 1

    # Explorer APIs
    ETHERSCAN_API_KEY: Optional[str] = None
    ETHERSCAN_API_URL: str = "https://api.etherscan.io/api"
    BLOCKSCOUT_API_URL: str = "https://eth.blockscout.com/api"

    # AI & Agent Configuration
    LLM_PROVIDER: str = "heuristic"  # heuristic, openai, anthropic, gemini, ollama
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # RAG & Embeddings
    EMBEDDING_PROVIDER: str = "hybrid_local"  # hybrid_local, openai
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE: str = "in_memory"  # in_memory, qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # Smart Contract / Anchoring
    REPORT_REGISTRY_ADDRESS: Optional[str] = None
    REPORT_ANCHOR_RPC_URL: str = "https://rpc.ankr.com/eth_sepolia"
    REPORT_ANCHOR_PRIVATE_KEY: Optional[str] = None

    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    KNOWLEDGE_BASE_DIR: str = os.path.join(DATA_DIR, "knowledge_base")
    FIXTURES_DIR: str = os.path.join(DATA_DIR, "fixtures")

    # Safety and limits
    MAX_GRAPH_DEPTH: int = 3
    MAX_NODES: int = 150
    MAX_EDGES: int = 300
    MAX_TRANSACTIONS_PER_ADDRESS: int = 100
    MAX_PROVIDER_REQUESTS: int = 25
    REQUEST_TIMEOUT_SECONDS: int = 15


settings = Settings()
