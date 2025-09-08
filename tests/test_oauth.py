import pytest
from unittest.mock import AsyncMock, patch
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("test_key", "test_secret", sandbox=True)

@pytest.mark.asyncio
async def test_get_request_token(oauth_client):
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=test_token&oauth_token_secret=test_secret&oauth_callback_confirmed=true"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await oauth_client.get_request_token()
        
        assert result["oauth_token"] == "test_token"
        assert result["oauth_token_secret"] == "test_secret"

@pytest.mark.asyncio
async def test_get_access_token(oauth_client):
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=access_token&oauth_token_secret=access_secret"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.get_access_token("req_token", "req_secret", "verifier")
        
        assert result["oauth_token"] == "access_token"
        assert oauth_client.access_token == "access_token"

@pytest.mark.asyncio
async def test_revoke_access_token_without_token(oauth_client):
    with pytest.raises(ValueError, match="No access token to revoke"):
        await oauth_client.revoke_access_token()
