import httpx
import time
import secrets
import hmac
import hashlib
import base64
import json
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, Mapping

from platformdirs import user_config_dir


class ETradeOAuth:
    def __init__(self, consumer_key: str, consumer_secret: str, sandbox: bool = True):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.sandbox = sandbox
        self.base_url = "https://apisb.etrade.com" if sandbox else "https://api.etrade.com"
        self.access_token: Optional[str] = None
        self.access_token_secret: Optional[str] = None
        self._token_file = Path(user_config_dir("mcp-etrade")) / "tokens.json"
        self._load_tokens()

    # ----- token persistence --------------------------------------------------

    def _load_tokens(self) -> None:
        try:
            data = json.loads(self._token_file.read_text())
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return
        env = "sandbox" if self.sandbox else "production"
        tok = data.get(env)
        if isinstance(tok, dict):
            self.access_token = tok.get("oauth_token")
            self.access_token_secret = tok.get("oauth_token_secret")

    def _save_tokens(self) -> None:
        try:
            self._token_file.parent.mkdir(parents=True, exist_ok=True)
            existing: Dict[str, Any] = {}
            if self._token_file.exists():
                try:
                    existing = json.loads(self._token_file.read_text())
                except json.JSONDecodeError:
                    existing = {}
            env = "sandbox" if self.sandbox else "production"
            if self.access_token and self.access_token_secret:
                existing[env] = {
                    "oauth_token": self.access_token,
                    "oauth_token_secret": self.access_token_secret,
                }
            else:
                existing.pop(env, None)
            self._token_file.write_text(json.dumps(existing, indent=2))
            try:
                self._token_file.chmod(0o600)
            except OSError:
                pass
        except OSError:
            pass

    # ----- OAuth 1.0a signing -------------------------------------------------

    def _oauth_params(self, token: str = "", callback: str = "", verifier: str = "") -> Dict[str, str]:
        params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_version": "1.0",
        }
        if token:
            params["oauth_token"] = token
        if callback:
            params["oauth_callback"] = callback
        if verifier:
            params["oauth_verifier"] = verifier
        return params

    def _sign(
        self,
        method: str,
        url: str,
        oauth_params: Dict[str, str],
        query_params: Optional[Mapping[str, Any]] = None,
        token_secret: str = "",
    ) -> str:
        all_params: Dict[str, str] = {k: v for k, v in oauth_params.items() if k != "oauth_signature"}
        if query_params:
            for k, v in query_params.items():
                if v is None:
                    continue
                all_params[k] = str(v)

        sorted_params = sorted(all_params.items())
        param_string = "&".join(
            f"{urllib.parse.quote(str(k), safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted_params
        )
        base_string = (
            f"{method.upper()}&"
            f"{urllib.parse.quote(url, safe='')}&"
            f"{urllib.parse.quote(param_string, safe='')}"
        )
        signing_key = (
            f"{urllib.parse.quote(self.consumer_secret, safe='')}&"
            f"{urllib.parse.quote(token_secret or '', safe='')}"
        )
        digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        return base64.b64encode(digest).decode()

    def _auth_header(
        self,
        method: str,
        url: str,
        token: str = "",
        token_secret: str = "",
        verifier: str = "",
        callback: str = "",
        query_params: Optional[Mapping[str, Any]] = None,
    ) -> str:
        oauth_params = self._oauth_params(token=token, callback=callback, verifier=verifier)
        oauth_params["oauth_signature"] = self._sign(
            method, url, oauth_params, query_params=query_params, token_secret=token_secret
        )
        parts = [
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in oauth_params.items()
            if v
        ]
        return 'OAuth realm="",' + ", ".join(parts)

    # ----- OAuth dance --------------------------------------------------------

    async def get_request_token(self) -> Dict[str, Any]:
        url = f"{self.base_url}/oauth/request_token"
        headers = {
            "Authorization": self._auth_header("GET", url, callback="oob"),
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            params = urllib.parse.parse_qs(response.text)
            return {
                "oauth_token": params["oauth_token"][0],
                "oauth_token_secret": params["oauth_token_secret"][0],
                "oauth_callback_confirmed": params.get("oauth_callback_confirmed", ["false"])[0],
            }

    def get_authorization_url(self, oauth_token: str) -> str:
        encoded_token = urllib.parse.quote(oauth_token, safe="")
        return (
            f"https://us.etrade.com/e/t/etws/authorize?"
            f"key={self.consumer_key}&token={encoded_token}"
        )

    async def get_access_token(
        self, request_token: str, request_token_secret: str, verifier: str
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/oauth/access_token"
        headers = {
            "Authorization": self._auth_header(
                "GET", url, token=request_token, token_secret=request_token_secret, verifier=verifier
            ),
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            params = urllib.parse.parse_qs(response.text)
            self.access_token = params["oauth_token"][0]
            self.access_token_secret = params["oauth_token_secret"][0]
            self._save_tokens()
            return {
                "oauth_token": self.access_token,
                "oauth_token_secret": self.access_token_secret,
            }

    async def renew_access_token(self) -> Dict[str, Any]:
        if not self.access_token:
            raise ValueError("No access token to renew. Run get_access_token first.")
        url = f"{self.base_url}/oauth/renew_access_token"
        headers = {
            "Authorization": self._auth_header(
                "GET", url, token=self.access_token, token_secret=self.access_token_secret or ""
            ),
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {
                "oauth_token": self.access_token,
                "oauth_token_secret": self.access_token_secret,
                "renewed": True,
            }

    async def revoke_access_token(self) -> Dict[str, Any]:
        if not self.access_token:
            raise ValueError("No access token to revoke.")
        url = f"{self.base_url}/oauth/revoke_access_token"
        headers = {
            "Authorization": self._auth_header(
                "GET", url, token=self.access_token, token_secret=self.access_token_secret or ""
            ),
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        self.access_token = None
        self.access_token_secret = None
        self._save_tokens()
        return {"revoked": True}

    # ----- authenticated API helper -------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Make an authenticated JSON API call. `path` is relative (e.g. '/v1/accounts/list')."""
        if not self.access_token or not self.access_token_secret:
            raise RuntimeError(
                "Not authenticated. Run get_request_token -> get_authorization_url "
                "-> get_access_token first."
            )

        # Drop None values from params
        clean_params: Dict[str, Any] = {}
        if params:
            for k, v in params.items():
                if v is None:
                    continue
                if isinstance(v, bool):
                    clean_params[k] = "true" if v else "false"
                else:
                    clean_params[k] = v

        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": self._auth_header(
                method,
                url,
                token=self.access_token,
                token_secret=self.access_token_secret,
                query_params=clean_params or None,
            ),
            "Accept": "application/json",
            "Consumer-Key": self.consumer_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method.upper(), url, headers=headers, params=clean_params or None
            )

        if response.status_code == 204 or not response.content:
            return {"status": response.status_code}

        try:
            return response.json()
        except ValueError:
            # Not JSON — return raw text with status
            if response.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"{response.status_code} {response.reason_phrase}: {response.text}",
                    request=response.request,
                    response=response,
                )
            return {"status": response.status_code, "text": response.text}
