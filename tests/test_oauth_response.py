import pytest
from unittest.mock import AsyncMock, patch
import httpx
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("test_key", "test_secret", sandbox=False)

@pytest.mark.asyncio
async def test_successful_request_token_response(oauth_client):
    """Test successful 200 response with proper OAuth token format"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "oauth_token=%2FiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D&oauth_token_secret=%2FrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM%3D&oauth_callback_confirmed=true"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await oauth_client.get_request_token()
        
        assert result["oauth_token"] == "/iQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU="
        assert result["oauth_token_secret"] == "/rC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM="
        assert result["oauth_callback_confirmed"] == "true"

@pytest.mark.asyncio
async def test_400_bad_request_error(oauth_client):
    """Test 400 error handling for input issues"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "400 Bad Request", request=None, response=None
        )
        
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await oauth_client.get_request_token()
        
        assert "400" in str(exc_info.value)

@pytest.mark.asyncio
async def test_500_server_error(oauth_client):
    """Test 500 error handling for server issues"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=None, response=None
        )
        
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await oauth_client.get_request_token()
        
        assert "500" in str(exc_info.value)

@pytest.mark.asyncio
async def test_url_encoded_token_parsing(oauth_client):
    """Test proper URL decoding of OAuth tokens"""
    mock_response = AsyncMock()
    mock_response.text = "oauth_token=%2FiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D&oauth_token_secret=%2FrC9scEpzcwSEMy4vE7nodSzPLqfRINnTNY4voczyFM%3D&oauth_callback_confirmed=true"
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await oauth_client.get_request_token()
        
        # Verify URL decoding worked correctly
        assert "=" in result["oauth_token"]  # %3D should be decoded to =
        assert "/" in result["oauth_token"]  # %2F should be decoded to /
        assert result["oauth_token"].endswith("=")
        assert result["oauth_token_secret"].endswith("=")
