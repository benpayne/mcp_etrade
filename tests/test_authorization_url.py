import pytest
from mcp_etrade.oauth import ETradeOAuth

@pytest.fixture
def oauth_client():
    return ETradeOAuth("282683cc9e4b8fc81dea6bc687d46758", "test_secret", sandbox=False)

def test_authorization_url_format(oauth_client):
    """Test authorization URL matches E*TRADE specification"""
    token = "/iQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU="
    
    url = oauth_client.get_authorization_url(token)
    
    expected_url = "https://us.etrade.com/e/t/etws/authorize?key=282683cc9e4b8fc81dea6bc687d46758&token=%2FiQRgQCRGPo7Xdk6G8QDSEzX0Jsy6sKNcULcDavAGgU%3D"
    assert url == expected_url

def test_authorization_url_components(oauth_client):
    """Test authorization URL contains required components"""
    token = "test_token"
    
    url = oauth_client.get_authorization_url(token)
    
    assert url.startswith("https://us.etrade.com/e/t/etws/authorize")
    assert f"key={oauth_client.consumer_key}" in url
    assert "token=test_token" in url

def test_authorization_url_encoding(oauth_client):
    """Test special characters in token are properly URL encoded"""
    token = "/test+token="
    
    url = oauth_client.get_authorization_url(token)
    
    # Should encode / as %2F, + as %2B, = as %3D
    assert "%2Ftest%2Btoken%3D" in url
    assert "/test+token=" not in url
