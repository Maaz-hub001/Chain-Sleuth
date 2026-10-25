"""
Pytest configuration and shared fixtures for ChainSleuth.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add app to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.session import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()


@pytest.fixture
def client():
    return TestClient(app)
