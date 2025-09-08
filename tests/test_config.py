import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
from mcp_etrade.config import Config

def test_config_with_env_vars():
    with patch.dict(os.environ, {
        'ETRADE_OAUTH_CONSUMER_KEY': 'test_key',
        'ETRADE_OAUTH_CONSUMER_SECRET': 'test_secret'
    }):
        config = Config()
        assert config.oauth_consumer_key == 'test_key'
        assert config.oauth_consumer_secret == 'test_secret'
        assert config.is_configured is True

def test_config_without_env_vars():
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.oauth_consumer_key is None
        assert config.oauth_consumer_secret is None
        assert config.is_configured is False

def test_config_file_loading():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_data = {"sandbox": False, "timeout": 60}
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        with patch('mcp_etrade.config.user_config_dir', return_value=tmpdir):
            config = Config()
            assert config.get("sandbox") is False
            assert config.get("timeout") == 60
