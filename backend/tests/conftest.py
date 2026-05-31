"""Pytest configuration and shared fixtures."""

import sys
import os
from pathlib import Path

# Setup path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Set environment for testing
os.environ.setdefault("ENVIRONMENT", "test")


import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


@pytest.fixture(scope="session")
def backend_path():
    """Get backend directory path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_path():
    """Get data directory path."""
    return Path(__file__).parent.parent.parent / "data"
