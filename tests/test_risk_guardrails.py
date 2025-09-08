"""Tests for risk management guardrails."""

import pytest
import json
from unittest.mock import patch
from mcp_etrade.server import call_tool


class TestRiskGuardrails:
    """Test risk management guardrails functionality."""

    @pytest.mark.asyncio
    async def test_validate_order_risk_success(self):
        """Test successful order risk validation."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("validate_order_risk", {
                    "account_id": "test_account",
                    "order_value": 1000.00,
                    "risk_amount": 50.00,
                    "risk_percentage": 1.0
                })
                
                data = json.loads(result[0].text)
                
                assert data["accountId"] == "test_account"
                assert data["orderValue"] == 1000.00
                assert data["riskAmount"] == 50.00
                assert data["isValid"] is True
                assert "passes risk validation" in data["message"]
                assert data["maxDailyRisk"] == 100.00  # 1% of 10000

    @pytest.mark.asyncio
    async def test_validate_order_risk_exceeds_daily_limit(self):
        """Test order validation when exceeding daily risk limit."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("validate_order_risk", {
                    "account_id": "test_account",
                    "order_value": 2000.00,
                    "risk_amount": 150.00,  # Exceeds 1% of 10000
                    "risk_percentage": 1.0
                })
                
                data = json.loads(result[0].text)
                
                assert data["isValid"] is False
                assert "exceed daily risk limit" in data["message"]
                assert data["maxDailyRisk"] == 100.00

    @pytest.mark.asyncio
    async def test_validate_order_risk_exceeds_position_size(self):
        """Test order validation when exceeding position size limit."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("validate_order_risk", {
                    "account_id": "test_account",
                    "order_value": 6000.00,  # Exceeds 50% of 10000
                    "risk_amount": 50.00,
                    "risk_percentage": 1.0
                })
                
                data = json.loads(result[0].text)
                
                assert data["isValid"] is False
                assert "exceeds 50% of account balance" in data["message"]

    @pytest.mark.asyncio
    async def test_get_daily_risk_status_initial(self):
        """Test getting daily risk status for new account."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("get_daily_risk_status", {
                    "account_id": "new_account",
                    "risk_percentage": 2.0
                })
                
                data = json.loads(result[0].text)
                
                assert data["accountId"] == "new_account"
                assert data["maxDailyRisk"] == 200.00  # 2% of 10000
                assert data["currentDailyRisk"] == 0.00
                assert data["remainingDailyRisk"] == 200.00
                assert data["riskUtilization"] == 0.0
                assert data["canTrade"] is True

    @pytest.mark.asyncio
    async def test_risk_validation_with_custom_percentage(self):
        """Test risk validation with custom risk percentage."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("validate_order_risk", {
                    "account_id": "test_account",
                    "order_value": 1500.00,
                    "risk_amount": 150.00,
                    "risk_percentage": 2.0  # 2% = $200 max daily risk
                })
                
                data = json.loads(result[0].text)
                
                assert data["isValid"] is True
                assert data["maxDailyRisk"] == 200.00
                assert data["riskPercentage"] == 2.0

    @pytest.mark.asyncio
    async def test_risk_structure_validation(self):
        """Test that risk responses have correct structure."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                # Test validate_order_risk structure
                result = await call_tool("validate_order_risk", {
                    "account_id": "test",
                    "order_value": 1000.00,
                    "risk_amount": 50.00
                })
                data = json.loads(result[0].text)
                
                required_fields = [
                    "accountId", "orderValue", "riskAmount", "accountBalance",
                    "riskPercentage", "isValid", "message", "maxDailyRisk",
                    "currentDailyRisk", "authenticated"
                ]
                
                for field in required_fields:
                    assert field in data
                
                # Test get_daily_risk_status structure
                result = await call_tool("get_daily_risk_status", {"account_id": "test"})
                data = json.loads(result[0].text)
                
                status_fields = [
                    "accountId", "maxDailyRisk", "currentDailyRisk", 
                    "remainingDailyRisk", "riskUtilization", "canTrade", "authenticated"
                ]
                
                for field in status_fields:
                    assert field in data
