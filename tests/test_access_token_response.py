import pytest
from unittest.mock import AsyncMock, patch
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("test_key", "test_secret", sandbox=False)

@pytest.mark.asyncio
async def test_access_token_response_format(oauth_client):
    """Test access token response matches E*TRADE specification format"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=%3TiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D&oauth_token_secret=%7RrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM%3D"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.get_access_token("req_token", "req_secret", "verifier")
        
        # parse_qs automatically URL decodes, so we get the decoded values
        assert result["oauth_token"] == "%3TiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU="
        assert result["oauth_token_secret"] == "%7RrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM="
        
        # Verify tokens are stored in client
        assert oauth_client.access_token == "%3TiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU="
        assert oauth_client.access_token_secret == "%7RrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM="

@pytest.mark.asyncio
async def test_access_token_url_decoding(oauth_client):
    """Test proper URL decoding of access token response"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=%3TiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D&oauth_token_secret=%7RrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM%3D"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await oauth_client.get_access_token("req_token", "req_secret", "verifier")
        
        # Verify the response format is handled correctly
        assert result["oauth_token"].startswith("%3T")  # Starts with %3T
        assert result["oauth_token"].endswith("=")      # Ends with =
        assert result["oauth_token_secret"].startswith("%7R")  # Starts with %7R
        assert result["oauth_token_secret"].endswith("=")
