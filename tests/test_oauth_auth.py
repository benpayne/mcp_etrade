import pytest
import re
from unittest.mock import AsyncMock, patch
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("test_consumer_key", "test_consumer_secret", sandbox=False)

def test_oauth_params_generation(oauth_client):
    """Test OAuth parameter generation includes all required fields"""
    with patch('time.time', return_value=1234567890):
        with patch('secrets.token_hex', return_value='test_nonce'):
            params = oauth_client._generate_oauth_params()
            
            assert params["oauth_consumer_key"] == "test_consumer_key"
            assert params["oauth_timestamp"] == "1234567890"
            assert params["oauth_nonce"] == "test_nonce"
            assert params["oauth_signature_method"] == "HMAC-SHA1"
            assert params["oauth_callback"] == "oob"

def test_signature_generation(oauth_client):
    """Test OAuth signature generation"""
    params = {
        "oauth_consumer_key": "test_consumer_key",
        "oauth_timestamp": "1234567890",
        "oauth_nonce": "test_nonce",
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_callback": "oob"
    }
    
    signature = oauth_client._generate_signature("GET", "https://api.etrade.com/oauth/request_token", params)
    
    # Signature should be base64 encoded
    assert isinstance(signature, str)
    assert len(signature) > 0

def test_auth_header_format(oauth_client):
    """Test authorization header contains all required OAuth parameters"""
    with patch('time.time', return_value=1234567890):
        with patch('secrets.token_hex', return_value='test_nonce'):
            header = oauth_client._get_auth_header("GET", "https://api.etrade.com/oauth/request_token")
            
            assert header.startswith("OAuth ")
            assert 'oauth_consumer_key="test_consumer_key"' in header
            assert 'oauth_timestamp="1234567890"' in header
            assert 'oauth_nonce="test_nonce"' in header
            assert 'oauth_signature_method="HMAC-SHA1"' in header
            assert 'oauth_callback="oob"' in header
            assert 'oauth_signature=' in header

@pytest.mark.asyncio
async def test_request_token_url_and_headers(oauth_client):
    """Test request token uses correct URL and headers"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=test_token&oauth_token_secret=test_secret&oauth_callback_confirmed=true"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = mock_client.return_value.__aenter__.return_value.get
        mock_get.return_value = mock_response
        
        await oauth_client.get_request_token()
        
        # Verify correct URL
        args, kwargs = mock_get.call_args
        assert args[0] == "https://api.etrade.com/oauth/request_token"
        
        # Verify headers
        headers = kwargs["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("OAuth ")
        assert "Content-Type" in headers

@pytest.mark.asyncio
async def test_live_url_used_for_production(oauth_client):
    """Test that production client uses live API URL"""
    assert oauth_client.base_url == "https://api.etrade.com"

@pytest.mark.asyncio
async def test_sandbox_url_used_for_sandbox():
    """Test that sandbox client uses sandbox URL"""
    sandbox_client = ETradeOAuth("key", "secret", sandbox=True)
    assert sandbox_client.base_url == "https://etgacb2.etrade.com"
