"""
Pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (use real database)"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests (full API testing)"
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running tests")


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Configure async backend for pytest-asyncio.
    """
    return "asyncio"
