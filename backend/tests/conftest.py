import pytest
from unittest.mock import patch
import os

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Automatically injects dummy keys for all tests to bypass initialization checks."""
    mock_env = {
        "OPENROUTER_API_KEY": "dummy_openrouter_key_for_testing",
        "AWS_ACCESS_KEY_ID": "dummy_aws_key",
        "AWS_SECRET_ACCESS_KEY": "dummy_aws_secret"
    }
    with patch.dict(os.environ, mock_env):
        yield
