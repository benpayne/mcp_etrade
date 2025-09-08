import pytest
from unittest.mock import AsyncMock, patch
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    client = ETradeOAuth("282683cc9e4b8fc81dea6bc687d46758", "test_secret", sandbox=False)
    # Set existing access token for renewal
    client.access_token = "/iQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU="
    client.access_token_secret = "test_token_secret"
    return client

def test_renew_access_token_header_format(oauth_client):
    """Test renew access token request header format matches E*TRADE specification"""
    with patch('time.time', return_value=1273254425):
        with patch('secrets.token_hex', return_value='LTg2ODUzOTQ5MTEzMTY3MzQwMzE='):
            header = oauth_client._get_auth_header(
                "POST", 
                "https://api.etrade.com/oauth/renew_access_token",
                oauth_client.access_token,
                oauth_client.access_token_secret
            )
            
            # Verify header format matches specification
            assert header.startswith('OAuth realm="",')
            assert 'oauth_consumer_key="282683cc9e4b8fc81dea6bc687d46758"' in header
            assert 'oauth_timestamp="1273254425"' in header
            assert 'oauth_signature_method="HMAC-SHA1"' in header
            assert 'oauth_token="%2FiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D"' in header
            assert 'oauth_signature=' in header
            assert 'oauth_nonce=' in header

def test_renew_access_token_required_components(oauth_client):
    """Test all required OAuth components are in renew access token header"""
    header = oauth_client._get_auth_header(
        "POST",
        "https://api.etrade.com/oauth/renew_access_token", 
        oauth_client.access_token,
        oauth_client.access_token_secret
    )
    
    required_components = [
        "oauth_consumer_key=",
        "oauth_timestamp=",
        "oauth_nonce=",
        "oauth_signature_method=",
        "oauth_signature=",
        "oauth_token="
    ]
    
    for component in required_components:
        assert component in header
    
    # Should NOT contain oauth_verifier or oauth_callback for renewal
    assert "oauth_verifier=" not in header
    assert "oauth_callback=" not in header

@pytest.mark.asyncio
async def test_renew_access_token_url_and_method(oauth_client):
    """Test renew access token uses correct URL and POST method"""
    mock_response = AsyncMock()
    mock_response.text = "Access Token has been renewed"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_post = mock_client.return_value.__aenter__.return_value.post
        mock_post.return_value = mock_response
        
        await oauth_client.renew_access_token()
        
        # Verify correct URL and method
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.etrade.com/oauth/renew_access_token"
        
        # Verify headers contain Authorization
        headers = kwargs["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("OAuth realm=\"\"")

@pytest.mark.asyncio
async def test_renew_access_token_response_handling(oauth_client):
    """Test renew access token response is properly handled"""
    mock_response = AsyncMock()
    mock_response.text = "Access Token has been renewed"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.renew_access_token()
        
        # Should return renewed status but keep same tokens
        assert result["renewed"] is True
        assert "oauth_token" in result
        assert "oauth_token_secret" in result

@pytest.mark.asyncio
async def test_renew_access_token_without_existing_token():
    """Test renew access token fails without existing access token"""
    oauth_client = ETradeOAuth("test_key", "test_secret", sandbox=False)
    # No access token set
    
    with pytest.raises(ValueError, match="No access token to renew"):
        await oauth_client.renew_access_token()

@pytest.mark.asyncio
async def test_renew_access_token_preserves_tokens(oauth_client):
    """Test renew access token preserves existing token values"""
    original_token = oauth_client.access_token
    original_secret = oauth_client.access_token_secret
    
    mock_response = AsyncMock()
    mock_response.text = "Access Token has been renewed"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.renew_access_token()
        
        # Tokens should remain the same after renewal
        assert oauth_client.access_token == original_token
        assert oauth_client.access_token_secret == original_secret
        assert result["oauth_token"] == original_token
        assert result["oauth_token_secret"] == original_secret
