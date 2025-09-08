import pytest
from mcp_etrade.server import list_tools


class TestAccountsTools:
    """Test suite for Accounts API tool registration and schemas"""

    @pytest.mark.asyncio
    async def test_accounts_tools_registered(self):
        """Test that account-related tools are properly registered"""
        tools = await list_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "get_account_balance" in tool_names
        assert "list_transactions" in tool_names

    @pytest.mark.asyncio
    async def test_get_account_balance_schema(self):
        """Test get_account_balance tool schema"""
        tools = await list_tools()
        balance_tool = next(tool for tool in tools if tool.name == "get_account_balance")
        
        assert balance_tool.description == "Get account balance from E*TRADE"
        assert balance_tool.inputSchema["type"] == "object"
        assert "account_id" in balance_tool.inputSchema["properties"]
        assert "instType" in balance_tool.inputSchema["properties"]
        assert balance_tool.inputSchema["properties"]["account_id"]["type"] == "string"
        assert balance_tool.inputSchema["properties"]["instType"]["type"] == "string"
        assert "account_id" in balance_tool.inputSchema["required"]
        assert "instType" in balance_tool.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_list_transactions_schema(self):
        """Test list_transactions tool schema"""
        tools = await list_tools()
        transactions_tool = next(tool for tool in tools if tool.name == "list_transactions")
        
        assert transactions_tool.description == "List transactions from E*TRADE account"
        assert transactions_tool.inputSchema["type"] == "object"
        assert "account_id" in transactions_tool.inputSchema["properties"]
        assert transactions_tool.inputSchema["properties"]["account_id"]["type"] == "string"
        assert "account_id" in transactions_tool.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_view_portfolio_schema(self):
        """Test view_portfolio tool schema"""
        tools = await list_tools()
        portfolio_tool = next(tool for tool in tools if tool.name == "view_portfolio")
        
        assert portfolio_tool.description == "View portfolio information from E*TRADE account"
        assert portfolio_tool.inputSchema["type"] == "object"
        assert "account_id" in portfolio_tool.inputSchema["properties"]
        assert portfolio_tool.inputSchema["properties"]["account_id"]["type"] == "string"
        assert "account_id" in portfolio_tool.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_all_tools_count(self):
        """Test that all expected tools are registered"""
        tools = await list_tools()
        expected_tools = [
            "get_request_token",
            "get_authorization_url", 
            "get_access_token",
            "renew_access_token",
            "revoke_access_token",
            "get_account_balance",
            "list_transactions",
            "get_transaction_details",
            "list_alerts",
            "delete_alerts",
            "get_alert_details",
            "view_portfolio",
            "get_option_chains",
            "get_option_expire_dates",
            "get_quotes",
            "lookup_product",
            "calculate_risk_parameters",
            "create_watch_list",
            "get_watch_lists",
            "update_watch_list",
            "delete_watch_list",
            "validate_order_risk",
            "get_daily_risk_status",
            "record_actual_loss"
        ]
        
        tool_names = [tool.name for tool in tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        assert len(tools) == len(expected_tools)

    @pytest.mark.asyncio
    async def test_oauth_tools_schemas(self):
        """Test OAuth-related tool schemas"""
        tools = await list_tools()
        tool_dict = {tool.name: tool for tool in tools}
        
        # Test get_request_token
        request_token_tool = tool_dict["get_request_token"]
        assert request_token_tool.description == "Get OAuth request token to start authentication flow"
        assert request_token_tool.inputSchema["type"] == "object"
        assert request_token_tool.inputSchema["properties"] == {}
        
        # Test get_authorization_url
        auth_url_tool = tool_dict["get_authorization_url"]
        assert "oauth_token" in auth_url_tool.inputSchema["required"]
        
        # Test get_access_token
        access_token_tool = tool_dict["get_access_token"]
        required_fields = access_token_tool.inputSchema["required"]
        assert "request_token" in required_fields
        assert "request_token_secret" in required_fields
        assert "verifier" in required_fields

    @pytest.mark.asyncio
    async def test_option_chains_tools_schemas(self):
        """Test option chains tool schemas"""
        tools = await list_tools()
        tool_dict = {tool.name: tool for tool in tools}
        
        # Test get_option_chains schema
        option_chains_tool = tool_dict["get_option_chains"]
        assert option_chains_tool.description == "Get option chains for a specific symbol"
        assert option_chains_tool.inputSchema["type"] == "object"
        assert "symbol" in option_chains_tool.inputSchema["properties"]
        assert "symbol" in option_chains_tool.inputSchema["required"]
        assert option_chains_tool.inputSchema["properties"]["symbol"]["type"] == "string"
        
        # Test optional parameters
        optional_params = ["expiryYear", "expiryMonth", "expiryDay", "strikePriceNear", 
                          "noOfStrikes", "includeWeekly", "skipAdjusted", "optionCategory", 
                          "chainType", "priceType"]
        for param in optional_params:
            assert param in option_chains_tool.inputSchema["properties"]
        
        # Test enum values
        assert option_chains_tool.inputSchema["properties"]["optionCategory"]["enum"] == ["STANDARD", "ALL", "MINI"]
        assert option_chains_tool.inputSchema["properties"]["chainType"]["enum"] == ["CALL", "PUT", "CALLPUT"]
        assert option_chains_tool.inputSchema["properties"]["priceType"]["enum"] == ["ATNM", "ALL"]
        
        # Test get_option_expire_dates schema
        expire_dates_tool = tool_dict["get_option_expire_dates"]
        assert expire_dates_tool.description == "Get option expiration dates for a symbol"
        assert expire_dates_tool.inputSchema["type"] == "object"
        assert "symbol" in expire_dates_tool.inputSchema["properties"]
        assert "symbol" in expire_dates_tool.inputSchema["required"]
        assert expire_dates_tool.inputSchema["properties"]["symbol"]["type"] == "string"
        assert "expiryType" in expire_dates_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_market_tools_schemas(self):
        """Test market tools schemas"""
        tools = await list_tools()
        tool_dict = {tool.name: tool for tool in tools}
        
        # Test get_quotes schema
        quotes_tool = tool_dict["get_quotes"]
        assert quotes_tool.description == "Get quote information for one or more symbols"
        assert quotes_tool.inputSchema["type"] == "object"
        assert "symbols" in quotes_tool.inputSchema["properties"]
        assert "symbols" in quotes_tool.inputSchema["required"]
        assert quotes_tool.inputSchema["properties"]["symbols"]["type"] == "string"
        
        # Test optional parameters
        optional_params = ["detailFlag", "requireEarningsDate", "overrideSymbolCount", "skipMiniOptionsCheck"]
        for param in optional_params:
            assert param in quotes_tool.inputSchema["properties"]
        
        # Test enum values for detailFlag
        assert quotes_tool.inputSchema["properties"]["detailFlag"]["enum"] == ["ALL", "FUNDAMENTAL", "INTRADAY", "OPTIONS", "WEEK_52", "MF_DETAIL"]
        
        # Test lookup_product schema
        lookup_tool = tool_dict["lookup_product"]
        assert lookup_tool.description == "Look up securities by company name"
        assert lookup_tool.inputSchema["type"] == "object"
        assert "search" in lookup_tool.inputSchema["properties"]
        assert "search" in lookup_tool.inputSchema["required"]
        assert lookup_tool.inputSchema["properties"]["search"]["type"] == "string"
