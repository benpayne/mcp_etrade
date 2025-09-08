import httpx
import time
import secrets
import hmac
import hashlib
import base64
import urllib.parse
from typing import Optional, Dict, Any

class ETradeOAuth:
    def __init__(self, consumer_key: str, consumer_secret: str, sandbox: bool = True):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = "https://etgacb2.etrade.com" if sandbox else "https://api.etrade.com"
        self.access_token = None
        self.access_token_secret = None
    
    def _generate_oauth_params(self, token: str = "", callback: str = "oob", verifier: str = "") -> Dict[str, str]:
        """Generate OAuth 1.0a parameters"""
        params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_token": token
        }
        
        if callback:
            params["oauth_callback"] = callback
        if verifier:
            params["oauth_verifier"] = verifier
            
        return params
    
    def _generate_signature(self, method: str, url: str, params: Dict[str, str], token_secret: str = "") -> str:
        """Generate OAuth 1.0a signature"""
        # Remove oauth_signature if present
        params = {k: v for k, v in params.items() if k != "oauth_signature"}
        
        # Sort parameters
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
        
        # Create signature base string
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def _get_auth_header(self, method: str, url: str, token: str = "", token_secret: str = "", verifier: str = "") -> str:
        """Generate OAuth 1.0a authorization header"""
        # Only include callback for request token requests
        callback = "oob" if not token else ""
        params = self._generate_oauth_params(token, callback=callback, verifier=verifier)
        params["oauth_signature"] = self._generate_signature(method, url, params, token_secret)
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        auth_params = [f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in params.items()]
        return f"OAuth realm=\"\",{', '.join(auth_params)}"
    
    async def get_request_token(self) -> Dict[str, Any]:
        """Get OAuth request token"""
        url = f"{self.base_url}/oauth/request_token"
        headers = {
            "Authorization": self._get_auth_header("GET", url),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse response
            params = urllib.parse.parse_qs(response.text)
            return {
                "oauth_token": params["oauth_token"][0],
                "oauth_token_secret": params["oauth_token_secret"][0],
                "oauth_callback_confirmed": params.get("oauth_callback_confirmed", [False])[0]
            }
    
    def get_authorization_url(self, oauth_token: str) -> str:
        """Generate authorization URL for user to approve application"""
        encoded_token = urllib.parse.quote(oauth_token, safe='')
        return f"https://us.etrade.com/e/t/etws/authorize?key={self.consumer_key}&token={encoded_token}"
    
    async def get_access_token(self, request_token: str, request_token_secret: str, verifier: str) -> Dict[str, Any]:
        """Exchange request token for access token"""
        url = f"{self.base_url}/oauth/access_token"
        headers = {
            "Authorization": self._get_auth_header("POST", url, request_token, request_token_secret, verifier),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            
            # Parse response
            params = urllib.parse.parse_qs(response.text)
            self.access_token = params["oauth_token"][0]
            self.access_token_secret = params["oauth_token_secret"][0]
            
            return {
                "oauth_token": self.access_token,
                "oauth_token_secret": self.access_token_secret
            }
    
    async def renew_access_token(self) -> Dict[str, Any]:
        """Renew existing access token"""
        if not self.access_token:
            raise ValueError("No access token to renew")
        
        url = f"{self.base_url}/oauth/renew_access_token"
        headers = {
            "Authorization": self._get_auth_header("POST", url, self.access_token, self.access_token_secret),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            
            # Response is just text confirmation, tokens remain the same
            return {
                "oauth_token": self.access_token,
                "oauth_token_secret": self.access_token_secret,
                "renewed": True
            }
    
    async def revoke_access_token(self) -> Dict[str, Any]:
        """Revoke access token"""
        if not self.access_token:
            raise ValueError("No access token to revoke")
        
        url = f"{self.base_url}/oauth/revoke_access_token"
        headers = {
            "Authorization": self._get_auth_header("POST", url, self.access_token, self.access_token_secret),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            
            self.access_token = None
            self.access_token_secret = None
            
            return {"revoked": True}
