#!/usr/bin/env python3
"""Tests for E*TRADE option chains functionality"""

import pytest
import json
from unittest.mock import Mock, patch
from mcp_etrade.server import call_tool
from mcp.types import TextContent


class TestOptionChains:
    """Test option chains functionality"""

    @pytest.mark.asyncio
    async def test_get_option_chains_success(self):
        """Test successful option chains retrieval"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            result = await call_tool("get_option_chains", {"symbol": "AAPL"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            # Verify response structure
            assert "OptionChainResponse" in response_data
            option_chain = response_data["OptionChainResponse"]
            
            assert "OptionPair" in option_chain
            assert len(option_chain["OptionPair"]) == 1
            
            option_pair = option_chain["OptionPair"][0]
            assert "Call" in option_pair
            assert "Put" in option_pair
            
            # Verify call option structure
            call = option_pair["Call"]
            assert call["optionCategory"] == "STANDARD"
            assert call["optionRootSymbol"] == "AAPL"
            assert call["optionType"] == "CALL"
            assert call["strikePrice"] == 150.0
            assert "AAPL240119C00150000" in call["symbol"]
            assert call["bid"] == 2.50
            assert call["ask"] == 2.60
            
            # Verify put option structure
            put = option_pair["Put"]
            assert put["optionCategory"] == "STANDARD"
            assert put["optionRootSymbol"] == "AAPL"
            assert put["optionType"] == "PUT"
            assert put["strikePrice"] == 150.0
            assert "AAPL240119P00150000" in put["symbol"]
            assert put["bid"] == 1.20
            assert put["ask"] == 1.30
            
            # Verify metadata
            assert option_chain["timeStamp"] == "1578063600"
            assert option_chain["quoteType"] == "DELAYED"
            assert option_chain["nearPrice"] == 149.50
            assert option_chain["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_option_chains_with_parameters(self):
        """Test option chains with optional parameters"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            params = {
                "symbol": "TSLA",
                "expiryYear": 2024,
                "expiryMonth": 3,
                "strikePriceNear": 200.0,
                "noOfStrikes": 5,
                "includeWeekly": True,
                "chainType": "CALL"
            }
            
            result = await call_tool("get_option_chains", params)
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            # Verify response contains option chain data
            assert "OptionChainResponse" in response_data
            option_chain = response_data["OptionChainResponse"]
            assert "OptionPair" in option_chain
            assert option_chain["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_option_chains_no_oauth(self):
        """Test option chains without OAuth configuration"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("get_option_chains", {"symbol": "AAPL"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_get_option_chains_missing_symbol(self):
        """Test option chains with missing required symbol parameter"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("get_option_chains", {})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error:" in result[0].text


class TestOptionExpireDates:
    """Test option expiration dates functionality"""

    @pytest.mark.asyncio
    async def test_get_option_expire_dates_success(self):
        """Test successful option expiration dates retrieval"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            result = await call_tool("get_option_expire_dates", {"symbol": "AAPL"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            # Verify response structure
            assert "OptionExpireDateResponse" in response_data
            expire_response = response_data["OptionExpireDateResponse"]
            
            assert "ExpirationDate" in expire_response
            assert len(expire_response["ExpirationDate"]) == 3
            
            # Verify first expiration date
            first_date = expire_response["ExpirationDate"][0]
            assert first_date["year"] == 2024
            assert first_date["month"] == 1
            assert first_date["day"] == 19
            assert first_date["expiryType"] == "MONTHLY"
            
            # Verify second expiration date
            second_date = expire_response["ExpirationDate"][1]
            assert second_date["year"] == 2024
            assert second_date["month"] == 2
            assert second_date["day"] == 16
            assert second_date["expiryType"] == "MONTHLY"
            
            # Verify weekly expiration date
            weekly_date = expire_response["ExpirationDate"][2]
            assert weekly_date["year"] == 2024
            assert weekly_date["month"] == 1
            assert weekly_date["day"] == 26
            assert weekly_date["expiryType"] == "WEEKLY"
            
            assert expire_response["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_option_expire_dates_with_expiry_type(self):
        """Test option expiration dates with expiry type parameter"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            params = {
                "symbol": "MSFT",
                "expiryType": "MONTHLY"
            }
            
            result = await call_tool("get_option_expire_dates", params)
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            # Verify response contains expiration dates
            assert "OptionExpireDateResponse" in response_data
            expire_response = response_data["OptionExpireDateResponse"]
            assert "ExpirationDate" in expire_response
            assert expire_response["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_option_expire_dates_no_oauth(self):
        """Test option expiration dates without OAuth configuration"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("get_option_expire_dates", {"symbol": "AAPL"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_get_option_expire_dates_missing_symbol(self):
        """Test option expiration dates with missing required symbol parameter"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("get_option_expire_dates", {})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_get_option_expire_dates_different_symbols(self):
        """Test option expiration dates for different symbols"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            symbols = ["AAPL", "GOOGL", "TSLA", "MSFT"]
            
            for symbol in symbols:
                result = await call_tool("get_option_expire_dates", {"symbol": symbol})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                response_data = json.loads(result[0].text)
                
                # Verify response structure is consistent
                assert "OptionExpireDateResponse" in response_data
                expire_response = response_data["OptionExpireDateResponse"]
                assert "ExpirationDate" in expire_response
                assert expire_response["authenticated"] is True
                assert len(expire_response["ExpirationDate"]) > 0


class TestOptionChainsIntegration:
    """Integration tests for option chains functionality"""

    @pytest.mark.asyncio
    async def test_option_chains_workflow(self):
        """Test complete option chains workflow"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            symbol = "AAPL"
            
            # Step 1: Get expiration dates
            expire_result = await call_tool("get_option_expire_dates", {"symbol": symbol})
            expire_data = json.loads(expire_result[0].text)
            
            assert "OptionExpireDateResponse" in expire_data
            expiration_dates = expire_data["OptionExpireDateResponse"]["ExpirationDate"]
            assert len(expiration_dates) > 0
            
            # Step 2: Get option chains using expiration date
            first_expiry = expiration_dates[0]
            chains_params = {
                "symbol": symbol,
                "expiryYear": first_expiry["year"],
                "expiryMonth": first_expiry["month"],
                "expiryDay": first_expiry["day"]
            }
            
            chains_result = await call_tool("get_option_chains", chains_params)
            chains_data = json.loads(chains_result[0].text)
            
            assert "OptionChainResponse" in chains_data
            option_pairs = chains_data["OptionChainResponse"]["OptionPair"]
            assert len(option_pairs) > 0
            
            # Verify option pair contains both call and put
            first_pair = option_pairs[0]
            assert "Call" in first_pair
            assert "Put" in first_pair
            
            # Verify both options have the same strike price
            call_strike = first_pair["Call"]["strikePrice"]
            put_strike = first_pair["Put"]["strikePrice"]
            assert call_strike == put_strike

    @pytest.mark.asyncio
    async def test_option_chains_error_handling(self):
        """Test error handling in option chains functionality"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            # Test with invalid tool name
            result = await call_tool("invalid_tool", {"symbol": "AAPL"})
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Unknown tool" in result[0].text or "Error:" in result[0].text
