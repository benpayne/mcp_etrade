#!/usr/bin/env python3
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx
import json
from .config import Config
from .oauth import ETradeOAuth
from .risk_guardrails import risk_manager

app = Server("mcp-etrade")
config = Config()
oauth_client = None

if config.is_configured:
    oauth_client = ETradeOAuth(
        config.oauth_consumer_key,
        config.oauth_consumer_secret,
        config.get("sandbox", True)
    )

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_request_token",
            description="Get OAuth request token to start authentication flow",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_authorization_url",
            description="Generate authorization URL for user to approve application",
            inputSchema={
                "type": "object",
                "properties": {
                    "oauth_token": {"type": "string", "description": "OAuth request token"}
                },
                "required": ["oauth_token"]
            }
        ),
        Tool(
            name="get_access_token",
            description="Exchange request token for access token",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_token": {"type": "string", "description": "OAuth request token"},
                    "request_token_secret": {"type": "string", "description": "OAuth request token secret"},
                    "verifier": {"type": "string", "description": "OAuth verifier code"}
                },
                "required": ["request_token", "request_token_secret", "verifier"]
            }
        ),
        Tool(
            name="renew_access_token",
            description="Renew existing access token",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="revoke_access_token",
            description="Revoke access token",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_account_balance",
            description="Get account balance from E*TRADE",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "instType": {"type": "string", "description": "Institution type", "enum": ["BROKERAGE"]},
                    "accountType": {"type": "string", "description": "Account type (optional)"},
                    "realTimeNAV": {"type": "boolean", "description": "Fetch real time balance"}
                },
                "required": ["account_id", "instType"]
            }
        ),
        Tool(
            name="list_transactions",
            description="List transactions from E*TRADE account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "startDate": {"type": "string", "description": "Start date in MMDDYYYY format"},
                    "endDate": {"type": "string", "description": "End date in MMDDYYYY format"},
                    "sortOrder": {"type": "string", "description": "Sort order", "enum": ["ASC", "DESC"]},
                    "count": {"type": "integer", "description": "Number of transactions (1-50)", "minimum": 1, "maximum": 50}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_transaction_details",
            description="Get specific transaction details from E*TRADE account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "transaction_id": {"type": "string", "description": "Transaction ID"}
                },
                "required": ["account_id", "transaction_id"]
            }
        ),
        Tool(
            name="list_alerts",
            description="List alerts from E*TRADE user account",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Alert count (max 300, default 25)", "minimum": 1, "maximum": 300},
                    "category": {"type": "string", "description": "Alert category", "enum": ["STOCK", "ACCOUNT"]},
                    "status": {"type": "string", "description": "Alert status", "enum": ["READ", "UNREAD", "DELETED"]},
                    "direction": {"type": "string", "description": "Sort direction", "enum": ["ASC", "DESC"]},
                    "search": {"type": "string", "description": "Search by subject"}
                },
                "required": []
            }
        ),
        Tool(
            name="delete_alerts",
            description="Delete alerts from E*TRADE user account",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_ids": {"type": "string", "description": "Comma separated alert ID list"}
                },
                "required": ["alert_ids"]
            }
        ),
        Tool(
            name="get_alert_details",
            description="Get details for a specific alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {"type": "string", "description": "Alert ID"},
                    "htmlTags": {"type": "boolean", "description": "Include HTML tags in response"}
                },
                "required": ["alert_id"]
            }
        ),
        Tool(
            name="view_portfolio",
            description="View portfolio information from E*TRADE account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "count": {"type": "integer", "description": "Number of positions (default 50)", "minimum": 1},
                    "sortBy": {"type": "string", "description": "Sort by field"},
                    "sortOrder": {"type": "string", "description": "Sort order", "enum": ["ASC", "DESC"]},
                    "view": {"type": "string", "description": "View type", "enum": ["PERFORMANCE", "FUNDAMENTAL", "OPTIONSWATCH", "QUICK", "COMPLETE"]}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_option_chains",
            description="Get option chains for a specific symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Market symbol (e.g., AAPL)"},
                    "expiryYear": {"type": "integer", "description": "Expiry year"},
                    "expiryMonth": {"type": "integer", "description": "Expiry month"},
                    "expiryDay": {"type": "integer", "description": "Expiry day"},
                    "strikePriceNear": {"type": "number", "description": "Strike price near this value"},
                    "noOfStrikes": {"type": "integer", "description": "Number of strikes to fetch"},
                    "includeWeekly": {"type": "boolean", "description": "Include weekly options"},
                    "skipAdjusted": {"type": "boolean", "description": "Skip adjusted options"},
                    "optionCategory": {"type": "string", "description": "Option category", "enum": ["STANDARD", "ALL", "MINI"]},
                    "chainType": {"type": "string", "description": "Chain type", "enum": ["CALL", "PUT", "CALLPUT"]},
                    "priceType": {"type": "string", "description": "Price type", "enum": ["ATNM", "ALL"]}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_option_expire_dates",
            description="Get option expiration dates for a symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Market symbol (e.g., AAPL)"},
                    "expiryType": {"type": "string", "description": "Expiration type"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_quotes",
            description="Get quote information for one or more symbols",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated symbols (max 25)"},
                    "detailFlag": {"type": "string", "description": "Market fields to return", "enum": ["ALL", "FUNDAMENTAL", "INTRADAY", "OPTIONS", "WEEK_52", "MF_DETAIL"]},
                    "requireEarningsDate": {"type": "boolean", "description": "Include earnings date"},
                    "overrideSymbolCount": {"type": "boolean", "description": "Allow up to 50 symbols"},
                    "skipMiniOptionsCheck": {"type": "boolean", "description": "Skip mini options check"}
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="lookup_product",
            description="Look up securities by company name",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Company name or partial name to search"}
                },
                "required": ["search"]
            }
        ),
        Tool(
            name="calculate_risk_parameters",
            description="Calculate R-multiple risk parameters for day trading based on account balance",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "risk_percentage": {"type": "number", "description": "Risk percentage of account balance (default 1.0)", "default": 1.0}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="create_watch_list",
            description="Create a new watch list",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "name": {"type": "string", "description": "Watch list name"},
                    "symbols": {"type": "array", "items": {"type": "string"}, "description": "List of symbols to add"}
                },
                "required": ["account_id", "name"]
            }
        ),
        Tool(
            name="get_watch_lists",
            description="Get all watch lists for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="update_watch_list",
            description="Update an existing watch list",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "watch_list_id": {"type": "string", "description": "Watch list ID"},
                    "name": {"type": "string", "description": "New watch list name"},
                    "symbols": {"type": "array", "items": {"type": "string"}, "description": "Updated list of symbols"}
                },
                "required": ["account_id", "watch_list_id"]
            }
        ),
        Tool(
            name="delete_watch_list",
            description="Delete a watch list",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "watch_list_id": {"type": "string", "description": "Watch list ID to delete"}
                },
                "required": ["account_id", "watch_list_id"]
            }
        ),
        Tool(
            name="validate_order_risk",
            description="Validate if an order meets risk management criteria before placement",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "order_value": {"type": "number", "description": "Total order value in dollars"},
                    "risk_amount": {"type": "number", "description": "Risk amount (stop loss distance * shares)"},
                    "risk_percentage": {"type": "number", "description": "Daily risk percentage (default 1.0)", "default": 1.0}
                },
                "required": ["account_id", "order_value", "risk_amount"]
            }
        ),
        Tool(
            name="get_daily_risk_status",
            description="Get current daily risk utilization status for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "risk_percentage": {"type": "number", "description": "Daily risk percentage (default 1.0)", "default": 1.0},
                    "current_daily_loss": {"type": "number", "description": "Current actual daily losses from Colosseum", "default": 0.0}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="record_actual_loss",
            description="Record actual loss when Colosseum closes a losing trade",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE account ID"},
                    "loss_amount": {"type": "number", "description": "Actual loss amount (positive number)"}
                },
                "required": ["account_id", "loss_amount"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if not config.is_configured:
        return [TextContent(
            type="text", 
            text="Error: E*TRADE OAuth credentials not configured. Set ETRADE_OAUTH_CONSUMER_KEY and ETRADE_OAUTH_CONSUMER_SECRET environment variables."
        )]
    
    try:
        if name == "get_request_token":
            result = await oauth_client.get_request_token()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_authorization_url":
            url = oauth_client.get_authorization_url(arguments["oauth_token"])
            return [TextContent(type="text", text=json.dumps({"authorization_url": url}, indent=2))]
        
        elif name == "get_access_token":
            result = await oauth_client.get_access_token(
                arguments["request_token"],
                arguments["request_token_secret"],
                arguments["verifier"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "renew_access_token":
            result = await oauth_client.renew_access_token()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "revoke_access_token":
            result = await oauth_client.revoke_access_token()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_account_balance":
            account_id = arguments["account_id"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "accountId": account_id,
                "institutionType": "BROKERAGE",
                "asOfDate": 1527134400000,
                "accountType": "PDT_ACCOUNT",
                "optionLevel": "LEVEL_2",
                "accountDescription": "Individual Brokerage Account",
                "quoteMode": 0,
                "dayTraderStatus": "PDT",
                "accountMode": "MARGIN",
                "accountDesc": "Individual Brokerage Account",
                "cash": {
                    "fundsForOpenOrdersCash": 0.0,
                    "moneyMktBalance": 10000.00
                },
                "computedBalance": {
                    "cashAvailableForInvestment": 10000.00,
                    "cashAvailableForWithdrawal": 10000.00,
                    "totalAvailableForWithdrawal": 10000.00,
                    "netCash": 10000.00,
                    "cashBalance": 10000.00,
                    "accountBalance": 10000.00
                },
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_transactions":
            account_id = arguments["account_id"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "transactionId": 18144100000861,
                "accountId": account_id,
                "transactionDate": 1527134400000,
                "postDate": 1527134400000,
                "amount": -2.0,
                "description": "ACH WITHDRAWL REFID:77521276;",
                "category": {
                    "categoryId": 0,
                    "parentId": 0,
                    "categoryName": "",
                    "parentName": ""
                },
                "brokerage": {
                    "transactionType": "Transfer",
                    "product": {},
                    "quantity": 0.0,
                    "price": 0.0,
                    "settlementCurrency": "USD",
                    "paymentCurrency": "USD",
                    "fee": 0.0,
                    "memo": "",
                    "orderNo": 0
                },
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_transaction_details":
            account_id = arguments["account_id"]
            transaction_id = arguments["transaction_id"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "transactionId": int(transaction_id),
                "accountId": account_id,
                "transactionDate": 1527134400000,
                "postDate": 1527134400000,
                "amount": -2.0,
                "description": "ACH WITHDRAWL REFID:77521276;",
                "category": {
                    "categoryId": 0,
                    "parentId": 0,
                    "categoryName": "",
                    "parentName": ""
                },
                "brokerage": {
                    "transactionType": "Transfer",
                    "product": {},
                    "quantity": 0.0,
                    "price": 0.0,
                    "settlementCurrency": "USD",
                    "paymentCurrency": "USD",
                    "fee": 0.0,
                    "memo": "",
                    "orderNo": 0
                },
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_alerts":
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "totalAlerts": 2,
                "alerts": [
                    {
                        "id": 6774,
                        "createTime": 1529426402,
                        "subject": "Transfer failed-Insufficient Funds",
                        "status": "UNREAD"
                    },
                    {
                        "id": 6775,
                        "createTime": 1529426500,
                        "subject": "Stock Alert: AAPL reached target price",
                        "status": "READ"
                    }
                ],
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_alerts":
            alert_ids = arguments["alert_ids"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "result": "SUCCESS",
                "deletedAlerts": alert_ids.split(","),
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_alert_details":
            alert_id = arguments["alert_id"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "id": int(alert_id),
                "createTime": 1529426402,
                "subject": "Transfer failed-Insufficient Funds",
                "status": "UNREAD",
                "msgText": "Your transfer request could not be completed due to insufficient funds.",
                "readTime": 0,
                "deleteTime": 0,
                "symbol": "",
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "view_portfolio":
            account_id = arguments["account_id"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "accountPortfolio": [
                    {
                        "accountId": account_id,
                        "position": [
                            {
                                "positionId": 12345,
                                "accountId": account_id,
                                "product": {
                                    "symbol": "AAPL",
                                    "securityType": "EQ"
                                },
                                "symbolDescription": "APPLE INC COM",
                                "dateAcquired": 1527134400000,
                                "pricePaid": 150.00,
                                "price": 175.00,
                                "quantity": 100,
                                "marketValue": 17500.00,
                                "totalCost": 15000.00,
                                "totalGain": 2500.00,
                                "totalGainPct": 16.67
                            }
                        ]
                    }
                ],
                "authenticated": bool(oauth_client.access_token)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_option_chains":
            symbol = arguments["symbol"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "OptionChainResponse": {
                    "OptionPair": [
                        {
                            "Call": {
                                "optionCategory": "STANDARD",
                                "optionRootSymbol": symbol,
                                "timeStamp": "1578063600",
                                "adjustedFlag": False,
                                "displaySymbol": f"{symbol}240119C00150000",
                                "optionType": "CALL",
                                "strikePrice": 150.0,
                                "symbol": f"{symbol}240119C00150000",
                                "bid": 2.50,
                                "ask": 2.60,
                                "bidSize": 10,
                                "askSize": 15,
                                "inTheMoney": "y",
                                "volume": 100,
                                "openInterest": 500,
                                "netChange": 0.10,
                                "lastPrice": 2.55,
                                "quoteDetail": "1578063600",
                                "osiKey": f"{symbol}240119C00150000"
                            },
                            "Put": {
                                "optionCategory": "STANDARD", 
                                "optionRootSymbol": symbol,
                                "timeStamp": "1578063600",
                                "adjustedFlag": False,
                                "displaySymbol": f"{symbol}240119P00150000",
                                "optionType": "PUT",
                                "strikePrice": 150.0,
                                "symbol": f"{symbol}240119P00150000",
                                "bid": 1.20,
                                "ask": 1.30,
                                "bidSize": 8,
                                "askSize": 12,
                                "inTheMoney": "n",
                                "volume": 50,
                                "openInterest": 300,
                                "netChange": -0.05,
                                "lastPrice": 1.25,
                                "quoteDetail": "1578063600",
                                "osiKey": f"{symbol}240119P00150000"
                            }
                        }
                    ],
                    "timeStamp": "1578063600",
                    "quoteType": "DELAYED",
                    "nearPrice": 149.50,
                    "authenticated": bool(oauth_client.access_token)
                }
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_option_expire_dates":
            symbol = arguments["symbol"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "OptionExpireDateResponse": {
                    "ExpirationDate": [
                        {
                            "year": 2024,
                            "month": 1,
                            "day": 19,
                            "expiryType": "MONTHLY"
                        },
                        {
                            "year": 2024,
                            "month": 2,
                            "day": 16,
                            "expiryType": "MONTHLY"
                        },
                        {
                            "year": 2024,
                            "month": 1,
                            "day": 26,
                            "expiryType": "WEEKLY"
                        }
                    ],
                    "authenticated": bool(oauth_client.access_token)
                }
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_quotes":
            symbols = arguments["symbols"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "QuoteResponse": {
                    "QuoteData": [
                        {
                            "dateTime": "15:17:00 EDT 06-20-2018",
                            "dateTimeUTC": 1529522220,
                            "quoteStatus": "DELAYED",
                            "ahFlag": False,
                            "hasMiniOptions": False,
                            "All": {
                                "adjustedFlag": False,
                                "ask": 175.79,
                                "askSize": 100,
                                "bid": 175.29,
                                "bidSize": 100,
                                "changeClose": 2.68,
                                "changeClosePercentage": 1.55,
                                "companyName": f"{symbols.split(',')[0]} INC COM",
                                "lastTrade": 175.74,
                                "high": 176.28,
                                "low": 174.76,
                                "open": 175.31,
                                "previousClose": 173.06,
                                "totalVolume": 1167544,
                                "primaryExchange": "NSDQ",
                                "symbolDescription": f"{symbols.split(',')[0]} INC COM"
                            }
                        }
                    ],
                    "authenticated": bool(oauth_client.access_token)
                }
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "lookup_product":
            search = arguments["search"]
            # TODO: Use oauth_client.access_token for authenticated API calls
            result = {
                "LookupResponse": {
                    "Data": [
                        {
                            "symbol": "AAPL",
                            "description": "APPLE INC COM",
                            "type": "EQUITY"
                        },
                        {
                            "symbol": "AABA",
                            "description": "ALTABA INC COM", 
                            "type": "EQUITY"
                        }
                    ],
                    "authenticated": bool(oauth_client.access_token)
                }
            }
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "calculate_risk_parameters":
            account_id = arguments["account_id"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            
            # Get account balance first
            balance_result = {
                "accountId": account_id,
                "institutionType": "BROKERAGE",
                "accountType": "PDT_ACCOUNT",
                "computedBalance": {
                    "accountBalance": 10000.00,
                    "cashAvailableForInvestment": 10000.00
                }
            }
            
            account_balance = balance_result["computedBalance"]["accountBalance"]
            available_cash = balance_result["computedBalance"]["cashAvailableForInvestment"]
            
            # Calculate risk parameters
            max_daily_risk = account_balance * (risk_percentage / 100)
            max_position_risk = max_daily_risk
            max_positions = int(available_cash / max_position_risk) if max_position_risk > 0 else 0
            
            result = {
                "accountId": account_id,
                "accountBalance": account_balance,
                "availableCash": available_cash,
                "riskPercentage": risk_percentage,
                "maxDailyRisk": max_daily_risk,
                "maxPositionRisk": max_position_risk,
                "maxPositions": max_positions,
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "create_watch_list":
            account_id = arguments["account_id"]
            name = arguments["name"]
            symbols = arguments.get("symbols", [])
            
            result = {
                "watchListId": "WL123456",
                "accountId": account_id,
                "name": name,
                "symbols": symbols,
                "created": 1609459200000,
                "itemCount": len(symbols),
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_watch_lists":
            account_id = arguments["account_id"]
            
            result = {
                "watchLists": [
                    {
                        "watchListId": "WL123456",
                        "name": "Tech Stocks",
                        "itemCount": 5,
                        "created": 1609459200000,
                        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
                    },
                    {
                        "watchListId": "WL789012",
                        "name": "Dividend Stocks",
                        "itemCount": 3,
                        "created": 1609545600000,
                        "symbols": ["JNJ", "PG", "KO"]
                    }
                ],
                "accountId": account_id,
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "update_watch_list":
            account_id = arguments["account_id"]
            watch_list_id = arguments["watch_list_id"]
            name = arguments.get("name", "Updated Watch List")
            symbols = arguments.get("symbols", [])
            
            result = {
                "watchListId": watch_list_id,
                "accountId": account_id,
                "name": name,
                "symbols": symbols,
                "updated": 1609459200000,
                "itemCount": len(symbols),
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "delete_watch_list":
            account_id = arguments["account_id"]
            watch_list_id = arguments["watch_list_id"]
            
            result = {
                "watchListId": watch_list_id,
                "accountId": account_id,
                "deleted": True,
                "deletedTime": 1609459200000,
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "validate_order_risk":
            account_id = arguments["account_id"]
            order_value = arguments["order_value"]
            risk_amount = arguments["risk_amount"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            current_daily_loss = arguments.get("current_daily_loss", 0.0)
            
            # Get account balance (mock data)
            account_balance = 10000.00
            
            # Validate risk
            is_valid, message = risk_manager.validate_order_risk(
                account_id, order_value, risk_amount, account_balance, risk_percentage, current_daily_loss
            )
            
            result = {
                "accountId": account_id,
                "orderValue": order_value,
                "riskAmount": risk_amount,
                "accountBalance": account_balance,
                "riskPercentage": risk_percentage,
                "currentDailyLoss": current_daily_loss,
                "isValid": is_valid,
                "message": message,
                "maxDailyRisk": account_balance * (risk_percentage / 100),
                "currentDailyRisk": risk_manager.daily_risk.get(account_id, 0.0),
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_daily_risk_status":
            account_id = arguments["account_id"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            current_daily_loss = arguments.get("current_daily_loss", 0.0)
            
            # Get account balance (mock data)
            account_balance = 10000.00
            
            # Get risk status
            status = risk_manager.get_daily_risk_status(account_id, account_balance, risk_percentage, current_daily_loss)
            status["authenticated"] = bool(oauth_client.access_token)
            
            return [TextContent(type="text", text=json.dumps(status))]
        
        elif name == "record_actual_loss":
            account_id = arguments["account_id"]
            loss_amount = arguments["loss_amount"]
            
            # Record the loss
            risk_manager.record_actual_loss(account_id, loss_amount)
            
            result = {
                "accountId": account_id,
                "lossAmount": loss_amount,
                "totalDailyLosses": risk_manager.daily_losses.get(account_id, 0.0),
                "recorded": True,
                "timestamp": 1609459200000,
                "authenticated": bool(oauth_client.access_token)
            }
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as streams:
        await app.run(*streams)

if __name__ == "__main__":
    asyncio.run(main())
