import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_vars():
    """
    Injects all required environment variables before every test.

    Sets LLM_PROVIDER=mock so the agent framework never tries to instantiate
    a real HTTP client or validate a real API key. All other keys are set to
    safe dummy values so initialization guards don't raise ValueError.
    """
    mock_env = {
        "LLM_PROVIDER": "mock",
        "OPENROUTER_API_KEY": "dummy_openrouter_key_for_testing",
        "AWS_ACCESS_KEY_ID": "dummy_aws_key",
        "AWS_SECRET_ACCESS_KEY": "dummy_aws_secret",
    }
    with patch.dict(os.environ, mock_env):
        # Clear the lru_cache on settings so it re-reads the patched env.
        from app.core import config
        config.get_settings.cache_clear()
        yield
    # Restore the cache after the test.
    from app.core import config
    config.get_settings.cache_clear()
