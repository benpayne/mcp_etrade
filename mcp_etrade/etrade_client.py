"""E*TRADE API client for Orders functionality."""

import httpx
import json
from typing import Dict, Any, Optional, List
from .oauth import ETradeOAuth


class ETradeClient:
    """E*TRADE API client for Orders operations."""
    
    def __init__(self, oauth_client: Optional[ETradeOAuth] = None):
        """Initialize the E*TRADE client."""
        self.oauth = oauth_client
        self.base_url = "https://apisb.etrade.com/v1" if oauth_client and oauth_client.sandbox else "https://api.etrade.com/v1"
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to E*TRADE API."""
        if not self.oauth or not self.oauth.client:
            raise ValueError("OAuth client not configured")
        
        if method.upper() == "GET":
            response = self.oauth.client.get(url)
        elif method.upper() == "POST":
            response = self.oauth.client.post(url, json=data)
        elif method.upper() == "PUT":
            response = self.oauth.client.put(url, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        return response.json()
    
    def list_orders(
        self,
        account_id_key: str,
        marker: Optional[str] = None,
        count: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        symbol: Optional[str] = None,
        security_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        market_session: Optional[str] = None
    ) -> Dict[str, Any]:
        """List orders for an account."""
        url = f"{self.base_url}/accounts/{account_id_key}/orders"
        
        params = []
        if marker:
            params.append(f"marker={marker}")
        if count:
            params.append(f"count={count}")
        if status:
            params.append(f"status={status}")
        if from_date:
            params.append(f"fromDate={from_date}")
        if to_date:
            params.append(f"toDate={to_date}")
        if symbol:
            params.append(f"symbol={symbol}")
        if security_type:
            params.append(f"securityType={security_type}")
        if transaction_type:
            params.append(f"transactionType={transaction_type}")
        if market_session:
            params.append(f"marketSession={market_session}")
        
        if params:
            url += "?" + "&".join(params)
        
        return self._make_request("GET", url)
    
    def preview_order(self, account_id_key: str, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Preview an order before placing it."""
        if "order" not in order_request:
            raise ValueError("Order request must contain 'order' field")
        
        url = f"{self.base_url}/accounts/{account_id_key}/orders/preview"
        return self._make_request("POST", url, order_request)
    
    def place_order(self, account_id_key: str, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order after previewing it."""
        if "previewIds" not in order_request:
            raise ValueError("Order request must contain 'previewIds' field")
        
        url = f"{self.base_url}/accounts/{account_id_key}/orders/place"
        return self._make_request("POST", url, order_request)
    
    def cancel_order(self, account_id_key: str, cancel_request: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an existing order."""
        url = f"{self.base_url}/accounts/{account_id_key}/orders/cancel"
        return self._make_request("PUT", url, cancel_request)
    
    def preview_changed_order(
        self, 
        account_id_key: str, 
        order_id: str, 
        change_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview a changed order."""
        url = f"{self.base_url}/accounts/{account_id_key}/orders/{order_id}/change/preview"
        return self._make_request("POST", url, change_request)
    
    def place_changed_order(
        self, 
        account_id_key: str, 
        order_id: str, 
        change_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Place a changed order."""
        url = f"{self.base_url}/accounts/{account_id_key}/orders/{order_id}/change/place"
        return self._make_request("PUT", url, change_request)
