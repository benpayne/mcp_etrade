import pytest
import urllib.parse

def test_callback_url_simple_format():
    """Test callback URL format with oauth_verifier parameter - simple URL"""
    callback_url = "https://myapplicationsite.com/mytradingapp?oauth_verifier=WXYZ89"
    
    parsed = urllib.parse.urlparse(callback_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    assert parsed.scheme == "https"
    assert parsed.netloc == "myapplicationsite.com"
    assert parsed.path == "/mytradingapp"
    assert "oauth_verifier" in query_params
    assert query_params["oauth_verifier"][0] == "WXYZ89"

def test_callback_url_with_existing_params():
    """Test callback URL format with existing query parameters"""
    callback_url = "https://myapplicationsite.com?myapp=trading&oauth_verifier=WXYZ89"
    
    parsed = urllib.parse.urlparse(callback_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    assert parsed.scheme == "https"
    assert parsed.netloc == "myapplicationsite.com"
    assert parsed.path == ""
    assert "oauth_verifier" in query_params
    assert "myapp" in query_params
    assert query_params["oauth_verifier"][0] == "WXYZ89"
    assert query_params["myapp"][0] == "trading"

def test_extract_verifier_from_callback():
    """Test extracting oauth_verifier from callback URL"""
    callback_urls = [
        "https://myapplicationsite.com/mytradingapp?oauth_verifier=WXYZ89",
        "https://myapplicationsite.com?myapp=trading&oauth_verifier=WXYZ89"
    ]
    
    for callback_url in callback_urls:
        parsed = urllib.parse.urlparse(callback_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        verifier = query_params.get("oauth_verifier", [None])[0]
        
        assert verifier == "WXYZ89"
