#!/usr/bin/env python3
"""Tests for E*TRADE market tools functionality"""

import pytest
import json
from unittest.mock import patch
from mcp_etrade.server import call_tool
from mcp.types import TextContent


class TestQuotes:
    """Test quotes functionality"""

    @pytest.mark.asyncio
    async def test_get_quotes_success(self):
        """Test successful quotes retrieval"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            result = await call_tool("get_quotes", {"symbols": "AAPL"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            assert "QuoteResponse" in response_data
            quote_response = response_data["QuoteResponse"]
            assert "QuoteData" in quote_response
            assert len(quote_response["QuoteData"]) == 1
            
            quote_data = quote_response["QuoteData"][0]
            assert "dateTime" in quote_data
            assert "quoteStatus" in quote_data
            assert "All" in quote_data
            assert quote_data["All"]["companyName"] == "AAPL INC COM"
            assert quote_response["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_quotes_multiple_symbols(self):
        """Test quotes with multiple symbols"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            result = await call_tool("get_quotes", {"symbols": "AAPL,GOOGL,MSFT"})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert "QuoteResponse" in response_data
            assert response_data["QuoteResponse"]["authenticated"] is True

    @pytest.mark.asyncio
    async def test_get_quotes_no_oauth(self):
        """Test quotes without OAuth configuration"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("get_quotes", {"symbols": "AAPL"})
            
            assert len(result) == 1
            assert "E*TRADE OAuth credentials not configured" in result[0].text


class TestProductLookup:
    """Test product lookup functionality"""

    @pytest.mark.asyncio
    async def test_lookup_product_success(self):
        """Test successful product lookup"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            result = await call_tool("lookup_product", {"search": "apple"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            response_data = json.loads(result[0].text)
            
            assert "LookupResponse" in response_data
            lookup_response = response_data["LookupResponse"]
            assert "Data" in lookup_response
            assert len(lookup_response["Data"]) >= 1
            
            first_result = lookup_response["Data"][0]
            assert "symbol" in first_result
            assert "description" in first_result
            assert "type" in first_result
            assert first_result["type"] == "EQUITY"
            assert lookup_response["authenticated"] is True

    @pytest.mark.asyncio
    async def test_lookup_product_no_oauth(self):
        """Test product lookup without OAuth configuration"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = False
            
            result = await call_tool("lookup_product", {"search": "apple"})
            
            assert len(result) == 1
            assert "E*TRADE OAuth credentials not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_lookup_product_missing_search(self):
        """Test product lookup with missing search parameter"""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            result = await call_tool("lookup_product", {})
            
            assert len(result) == 1
            assert "Error:" in result[0].text


class TestMarketIntegration:
    """Integration tests for market functionality"""

    @pytest.mark.asyncio
    async def test_lookup_then_quote_workflow(self):
        """Test lookup product then get quote workflow"""
        with patch('mcp_etrade.server.config') as mock_config, \
             patch('mcp_etrade.server.oauth_client') as mock_oauth:
            
            mock_config.is_configured = True
            mock_oauth.access_token = "test_token"
            
            # Step 1: Lookup product
            lookup_result = await call_tool("lookup_product", {"search": "apple"})
            lookup_data = json.loads(lookup_result[0].text)
            
            assert "LookupResponse" in lookup_data
            symbols = [item["symbol"] for item in lookup_data["LookupResponse"]["Data"]]
            assert len(symbols) > 0
            
            # Step 2: Get quotes for found symbols
            quote_result = await call_tool("get_quotes", {"symbols": symbols[0]})
            quote_data = json.loads(quote_result[0].text)
            
            assert "QuoteResponse" in quote_data
            assert len(quote_data["QuoteResponse"]["QuoteData"]) == 1
