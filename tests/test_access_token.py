import pytest
from unittest.mock import AsyncMock, patch
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("282683cc9e4b8fc81dea6bc687d46758", "test_secret", sandbox=False)

def test_access_token_header_format(oauth_client):
    """Test access token request header format matches E*TRADE specification"""
    with patch('time.time', return_value=1273254425):
        with patch('secrets.token_hex', return_value='LTg2ODUzOTQ5MTEzMTY3MzQwMzE='):
            header = oauth_client._get_auth_header(
                "POST", 
                "https://api.etrade.com/oauth/access_token",
                "/iQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU=",
                "token_secret",
                "Y27X25F"
            )
            
            # Verify header format
            assert header.startswith('OAuth realm="",')
            assert 'oauth_consumer_key="282683cc9e4b8fc81dea6bc687d46758"' in header
            assert 'oauth_timestamp="1273254425"' in header
            assert 'oauth_signature_method="HMAC-SHA1"' in header
            assert 'oauth_verifier="Y27X25F"' in header
            assert 'oauth_token="%2FiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D"' in header
            assert 'oauth_signature=' in header

@pytest.mark.asyncio
async def test_access_token_url_and_method(oauth_client):
    """Test access token uses correct URL and POST method"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=access_token&oauth_token_secret=access_secret"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_post = mock_client.return_value.__aenter__.return_value.post
        mock_post.return_value = mock_response
        
        await oauth_client.get_access_token("req_token", "req_secret", "verifier")
        
        # Verify correct URL and method
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.etrade.com/oauth/access_token"
        
        # Verify headers contain Authorization
        headers = kwargs["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("OAuth realm=\"\"")

def test_access_token_header_components(oauth_client):
    """Test all required OAuth components are in access token header"""
    header = oauth_client._get_auth_header(
        "POST",
        "https://api.etrade.com/oauth/access_token", 
        "test_token",
        "test_secret",
        "test_verifier"
    )
    
    required_components = [
        "oauth_signature=",
        "oauth_nonce=",
        "oauth_signature_method=",
        "oauth_consumer_key=",
        "oauth_timestamp=",
        "oauth_verifier=",
        "oauth_token="
    ]
    
    for component in required_components:
        assert component in header

@pytest.mark.asyncio
async def test_access_token_response_parsing(oauth_client):
    """Test access token response is properly parsed"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=final_access_token&oauth_token_secret=final_access_secret"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.get_access_token("req_token", "req_secret", "verifier")
        
        assert result["oauth_token"] == "final_access_token"
        assert result["oauth_token_secret"] == "final_access_secret"
        assert oauth_client.access_token == "final_access_token"
        assert oauth_client.access_token_secret == "final_access_secret"
