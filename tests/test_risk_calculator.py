"""Tests for calculate_risk_parameters tool."""

import pytest
import json
from unittest.mock import patch
from mcp_etrade.server import call_tool


class TestRiskCalculator:
    """Test risk calculator functionality."""

    @pytest.mark.asyncio
    async def test_calculate_risk_parameters_default(self):
        """Test risk calculation with default 1% risk."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("calculate_risk_parameters", {"account_id": "test_account"})
                
                assert len(result) == 1
                data = json.loads(result[0].text)
                
                assert data["accountId"] == "test_account"
                assert data["accountBalance"] == 10000.0
                assert data["riskPercentage"] == 1.0
                assert data["maxDailyRisk"] == 100.0
                assert data["maxPositionRisk"] == 100.0
                assert data["maxPositions"] == 100

    @pytest.mark.asyncio
    async def test_calculate_risk_parameters_custom_risk(self):
        """Test risk calculation with custom risk percentage."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("calculate_risk_parameters", {
                    "account_id": "test_account",
                    "risk_percentage": 2.5
                })
                
                data = json.loads(result[0].text)
                
                assert data["riskPercentage"] == 2.5
                assert data["maxDailyRisk"] == 250.0
                assert data["maxPositionRisk"] == 250.0
                assert data["maxPositions"] == 40

    @pytest.mark.asyncio
    async def test_calculate_risk_parameters_structure(self):
        """Test that response has correct structure."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("calculate_risk_parameters", {"account_id": "test"})
                data = json.loads(result[0].text)
                
                required_fields = [
                    "accountId", "accountBalance", "availableCash", 
                    "riskPercentage", "maxDailyRisk", "maxPositionRisk", 
                    "maxPositions", "authenticated"
                ]
                
                for field in required_fields:
                    assert field in data

    @pytest.mark.asyncio
    async def test_calculate_risk_parameters_math(self):
        """Test risk calculation math is correct."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("calculate_risk_parameters", {
                    "account_id": "test",
                    "risk_percentage": 1.5
                })
                
                data = json.loads(result[0].text)
                
                # Verify calculations
                expected_risk = 10000.0 * (1.5 / 100)
                assert data["maxDailyRisk"] == expected_risk
                assert data["maxPositionRisk"] == expected_risk
                
                expected_positions = int(10000.0 / expected_risk)
                assert data["maxPositions"] == expected_positions
