import pytest
import json
from unittest.mock import patch, AsyncMock
from mcp_etrade.server import call_tool
from mcp.types import TextContent


class TestAccountsAPI:
    """Test suite for E*TRADE Accounts API functionality"""

    @pytest.mark.asyncio
    async def test_get_account_balance_success(self):
        """Test successful account balance retrieval"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("get_account_balance", {"account_id": "12345", "instType": "BROKERAGE"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["accountId"] == "12345"
                assert response_data["institutionType"] == "BROKERAGE"
                assert response_data["accountType"] == "PDT_ACCOUNT"
                assert response_data["cash"]["moneyMktBalance"] == 10000.00
                assert response_data["computedBalance"]["accountBalance"] == 10000.00
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_account_balance_unconfigured(self):
        """Test account balance with unconfigured OAuth"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("get_account_balance", {"account_id": "12345", "instType": "BROKERAGE"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error: E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_list_transactions_success(self):
        """Test successful transactions retrieval"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("list_transactions", {"account_id": "12345"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["accountId"] == "12345"
                assert response_data["transactionId"] == 18144100000861
                assert response_data["amount"] == -2.0
                assert response_data["description"] == "ACH WITHDRAWL REFID:77521276;"
                assert response_data["brokerage"]["transactionType"] == "Transfer"
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_list_transactions_unconfigured(self):
        """Test transactions with unconfigured OAuth"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("list_transactions", {"account_id": "12345"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error: E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_account_balance_missing_account_id(self):
        """Test account balance with missing account_id parameter"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("get_account_balance", {"instType": "BROKERAGE"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_transactions_missing_account_id(self):
        """Test transactions with missing account_id parameter"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("list_transactions", {})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_account_balance_no_access_token(self):
        """Test account balance when OAuth client has no access token"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = None
                
                result = await call_tool("get_account_balance", {"account_id": "12345", "instType": "BROKERAGE"})
                response_data = json.loads(result[0].text)
                assert response_data["authenticated"] is False

    @pytest.mark.asyncio
    async def test_transactions_no_access_token(self):
        """Test transactions when OAuth client has no access token"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = None
                
                result = await call_tool("list_transactions", {"account_id": "12345"})
                response_data = json.loads(result[0].text)
                assert response_data["authenticated"] is False

    @pytest.mark.asyncio
    async def test_get_transaction_details_success(self):
        """Test successful transaction details retrieval"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("get_transaction_details", {"account_id": "12345", "transaction_id": "18144100000861"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["transactionId"] == 18144100000861
                assert response_data["accountId"] == "12345"
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_list_alerts_success(self):
        """Test successful alerts listing"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("list_alerts", {})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["totalAlerts"] == 2
                assert len(response_data["alerts"]) == 2
                assert response_data["alerts"][0]["id"] == 6774
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_delete_alerts_success(self):
        """Test successful alert deletion"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("delete_alerts", {"alert_ids": "6774,6775"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["result"] == "SUCCESS"
                assert response_data["deletedAlerts"] == ["6774", "6775"]
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_alert_details_success(self):
        """Test successful alert details retrieval"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("get_alert_details", {"alert_id": "6774"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert response_data["id"] == 6774
                assert response_data["subject"] == "Transfer failed-Insufficient Funds"
                assert response_data["status"] == "UNREAD"
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_view_portfolio_success(self):
        """Test successful portfolio retrieval"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("view_portfolio", {"account_id": "12345"})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                
                response_data = json.loads(result[0].text)
                assert len(response_data["accountPortfolio"]) == 1
                assert response_data["accountPortfolio"][0]["accountId"] == "12345"
                position = response_data["accountPortfolio"][0]["position"][0]
                assert position["product"]["symbol"] == "AAPL"
                assert position["quantity"] == 100
                assert response_data["authenticated"] is True

    @pytest.mark.asyncio
    async def test_view_portfolio_unconfigured(self):
        """Test portfolio with unconfigured OAuth"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("view_portfolio", {"account_id": "12345"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error: E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """Test error handling for unknown tool"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("unknown_tool", {})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error: Unknown tool: unknown_tool" in result[0].text
