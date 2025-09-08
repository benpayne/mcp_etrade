"""Tests for watch list management tools."""

import pytest
import json
from unittest.mock import patch
from mcp_etrade.server import call_tool


class TestWatchLists:
    """Test watch list management functionality."""

    @pytest.mark.asyncio
    async def test_create_watch_list_success(self):
        """Test successful watch list creation."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("create_watch_list", {
                    "account_id": "test_account",
                    "name": "My Tech Stocks",
                    "symbols": ["AAPL", "GOOGL", "MSFT"]
                })
                
                assert len(result) == 1
                data = json.loads(result[0].text)
                
                assert data["watchListId"] == "WL123456"
                assert data["accountId"] == "test_account"
                assert data["name"] == "My Tech Stocks"
                assert data["symbols"] == ["AAPL", "GOOGL", "MSFT"]
                assert data["itemCount"] == 3
                assert "created" in data

    @pytest.mark.asyncio
    async def test_create_watch_list_empty_symbols(self):
        """Test creating watch list with no symbols."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("create_watch_list", {
                    "account_id": "test_account",
                    "name": "Empty List"
                })
                
                data = json.loads(result[0].text)
                
                assert data["symbols"] == []
                assert data["itemCount"] == 0

    @pytest.mark.asyncio
    async def test_get_watch_lists_success(self):
        """Test successful retrieval of watch lists."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("get_watch_lists", {
                    "account_id": "test_account"
                })
                
                data = json.loads(result[0].text)
                
                assert "watchLists" in data
                assert len(data["watchLists"]) == 2
                assert data["watchLists"][0]["name"] == "Tech Stocks"
                assert data["watchLists"][1]["name"] == "Dividend Stocks"
                assert data["accountId"] == "test_account"

    @pytest.mark.asyncio
    async def test_update_watch_list_success(self):
        """Test successful watch list update."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("update_watch_list", {
                    "account_id": "test_account",
                    "watch_list_id": "WL123456",
                    "name": "Updated Tech Stocks",
                    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META"]
                })
                
                data = json.loads(result[0].text)
                
                assert data["watchListId"] == "WL123456"
                assert data["name"] == "Updated Tech Stocks"
                assert len(data["symbols"]) == 6
                assert data["itemCount"] == 6
                assert "updated" in data

    @pytest.mark.asyncio
    async def test_update_watch_list_name_only(self):
        """Test updating only the watch list name."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("update_watch_list", {
                    "account_id": "test_account",
                    "watch_list_id": "WL123456",
                    "name": "Renamed List"
                })
                
                data = json.loads(result[0].text)
                
                assert data["name"] == "Renamed List"
                assert data["symbols"] == []  # Default empty when not provided
                assert data["itemCount"] == 0

    @pytest.mark.asyncio
    async def test_delete_watch_list_success(self):
        """Test successful watch list deletion."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                result = await call_tool("delete_watch_list", {
                    "account_id": "test_account",
                    "watch_list_id": "WL123456"
                })
                
                data = json.loads(result[0].text)
                
                assert data["watchListId"] == "WL123456"
                assert data["accountId"] == "test_account"
                assert data["deleted"] is True
                assert "deletedTime" in data

    @pytest.mark.asyncio
    async def test_watch_list_structure_validation(self):
        """Test that all watch list responses have correct structure."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                # Test create response structure
                result = await call_tool("create_watch_list", {
                    "account_id": "test",
                    "name": "Test"
                })
                data = json.loads(result[0].text)
                
                required_create_fields = [
                    "watchListId", "accountId", "name", "symbols", 
                    "created", "itemCount", "authenticated"
                ]
                
                for field in required_create_fields:
                    assert field in data
                
                # Test get response structure
                result = await call_tool("get_watch_lists", {"account_id": "test"})
                data = json.loads(result[0].text)
                
                assert "watchLists" in data
                assert "accountId" in data
                assert "authenticated" in data
                
                # Each watch list should have required fields
                for watch_list in data["watchLists"]:
                    watch_list_fields = ["watchListId", "name", "itemCount", "created", "symbols"]
                    for field in watch_list_fields:
                        assert field in watch_list

    @pytest.mark.asyncio
    async def test_watch_list_integration_workflow(self):
        """Test complete watch list workflow."""
        with patch('mcp_etrade.server.config') as mock_config:
            mock_config.is_configured = True
            
            with patch('mcp_etrade.server.oauth_client') as mock_oauth:
                mock_oauth.access_token = 'test_access_token'
                
                # 1. Create watch list
                create_result = await call_tool("create_watch_list", {
                    "account_id": "test_account",
                    "name": "Growth Stocks",
                    "symbols": ["AAPL", "GOOGL"]
                })
                create_data = json.loads(create_result[0].text)
                watch_list_id = create_data["watchListId"]
                
                # 2. Get watch lists (should include new one)
                get_result = await call_tool("get_watch_lists", {
                    "account_id": "test_account"
                })
                get_data = json.loads(get_result[0].text)
                assert len(get_data["watchLists"]) == 2  # Mock returns 2
                
                # 3. Update watch list
                update_result = await call_tool("update_watch_list", {
                    "account_id": "test_account",
                    "watch_list_id": watch_list_id,
                    "name": "Updated Growth Stocks",
                    "symbols": ["AAPL", "GOOGL", "TSLA"]
                })
                update_data = json.loads(update_result[0].text)
                assert update_data["itemCount"] == 3
                
                # 4. Delete watch list
                delete_result = await call_tool("delete_watch_list", {
                    "account_id": "test_account",
                    "watch_list_id": watch_list_id
                })
                delete_data = json.loads(delete_result[0].text)
                assert delete_data["deleted"] is True
