#!/usr/bin/env python3
import asyncio
import time
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx
import json
from .config import Config
from .oauth import ETradeOAuth
from .risk_guardrails import risk_manager
from . import watchlists

app = Server("mcp-etrade")
config = Config()
oauth_client = None

if config.is_configured:
    oauth_client = ETradeOAuth(
        config.oauth_consumer_key,
        config.oauth_consumer_secret,
        config.sandbox
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
            name="list_accounts",
            description="List all E*TRADE accounts for the authenticated user. Returns accountId and accountIdKey — use accountIdKey for all other account tools.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_account_balance",
            description="Get account balance from E*TRADE",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"}
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
                    "account_id": {"type": "string", "description": "E*TRADE accountIdKey (from list_accounts)"},
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
    
    def _ok(payload):
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    async def _fetch_balance_numbers(account_id_key: str) -> tuple[float, float]:
        """Return (account_balance, cash_available_for_investment) from the live API."""
        resp = await oauth_client.request(
            "GET",
            f"/v1/accounts/{account_id_key}/balance.json",
            params={"instType": "BROKERAGE", "realTimeNAV": True},
        )
        br = resp.get("BalanceResponse", resp) if isinstance(resp, dict) else {}
        computed = br.get("Computed", {}) if isinstance(br, dict) else {}
        rtv = computed.get("RealTimeValues", {}) if isinstance(computed, dict) else {}
        account_balance = float(
            rtv.get("totalAccountValue")
            or computed.get("accountBalance")
            or computed.get("cashAvailableForInvestment")
            or 0.0
        )
        cash_available = float(computed.get("cashAvailableForInvestment") or account_balance)
        return account_balance, cash_available

    try:
        if name == "get_request_token":
            result = await oauth_client.get_request_token()
            return _ok(result)

        elif name == "get_authorization_url":
            url = oauth_client.get_authorization_url(arguments["oauth_token"])
            return _ok({"authorization_url": url})

        elif name == "get_access_token":
            result = await oauth_client.get_access_token(
                arguments["request_token"],
                arguments["request_token_secret"],
                arguments["verifier"],
            )
            return _ok(result)

        elif name == "renew_access_token":
            return _ok(await oauth_client.renew_access_token())

        elif name == "revoke_access_token":
            return _ok(await oauth_client.revoke_access_token())

        elif name == "list_accounts":
            return _ok(await oauth_client.request("GET", "/v1/accounts/list.json"))
        
        elif name == "get_account_balance":
            account_id_key = arguments["account_id"]
            params = {
                "instType": arguments.get("instType", "BROKERAGE"),
                "realTimeNAV": arguments.get("realTimeNAV", True),
            }
            if "accountType" in arguments:
                params["accountType"] = arguments["accountType"]
            return _ok(
                await oauth_client.request(
                    "GET", f"/v1/accounts/{account_id_key}/balance.json", params=params
                )
            )
        
        elif name == "list_transactions":
            account_id_key = arguments["account_id"]
            params = {
                k: arguments[k]
                for k in ("startDate", "endDate", "sortOrder", "count")
                if k in arguments
            }
            return _ok(
                await oauth_client.request(
                    "GET", f"/v1/accounts/{account_id_key}/transactions.json", params=params
                )
            )

        elif name == "get_transaction_details":
            account_id_key = arguments["account_id"]
            transaction_id = arguments["transaction_id"]
            return _ok(
                await oauth_client.request(
                    "GET",
                    f"/v1/accounts/{account_id_key}/transactions/{transaction_id}.json",
                )
            )

        elif name == "list_alerts":
            params = {
                k: arguments[k]
                for k in ("count", "category", "status", "direction", "search")
                if k in arguments
            }
            return _ok(
                await oauth_client.request("GET", "/v1/user/alerts.json", params=params)
            )

        elif name == "delete_alerts":
            alert_ids = arguments["alert_ids"]
            return _ok(
                await oauth_client.request("DELETE", f"/v1/user/alerts/{alert_ids}.json")
            )

        elif name == "get_alert_details":
            alert_id = arguments["alert_id"]
            params = {}
            if "htmlTags" in arguments:
                params["htmlTags"] = arguments["htmlTags"]
            return _ok(
                await oauth_client.request(
                    "GET", f"/v1/user/alerts/{alert_id}.json", params=params
                )
            )
        
        elif name == "view_portfolio":
            account_id_key = arguments["account_id"]
            params = {
                k: arguments[k]
                for k in ("count", "sortBy", "sortOrder", "view")
                if k in arguments
            }
            return _ok(
                await oauth_client.request(
                    "GET", f"/v1/accounts/{account_id_key}/portfolio.json", params=params
                )
            )
        
        elif name == "get_option_chains":
            params = {
                "symbol": arguments["symbol"],
            }
            for key in (
                "expiryYear", "expiryMonth", "expiryDay", "strikePriceNear",
                "noOfStrikes", "includeWeekly", "skipAdjusted",
                "optionCategory", "chainType", "priceType",
            ):
                if key in arguments:
                    params[key] = arguments[key]
            return _ok(
                await oauth_client.request(
                    "GET", "/v1/market/optionchains.json", params=params
                )
            )

        elif name == "get_option_expire_dates":
            params = {"symbol": arguments["symbol"]}
            if "expiryType" in arguments:
                params["expiryType"] = arguments["expiryType"]
            return _ok(
                await oauth_client.request(
                    "GET", "/v1/market/optionexpiredate.json", params=params
                )
            )

        elif name == "get_quotes":
            symbols = arguments["symbols"]
            params = {
                k: arguments[k]
                for k in (
                    "detailFlag", "requireEarningsDate",
                    "overrideSymbolCount", "skipMiniOptionsCheck",
                )
                if k in arguments
            }
            return _ok(
                await oauth_client.request(
                    "GET", f"/v1/market/quote/{symbols}.json", params=params
                )
            )

        elif name == "lookup_product":
            search = arguments["search"]
            return _ok(
                await oauth_client.request("GET", f"/v1/market/lookup/{search}.json")
            )
        
        elif name == "calculate_risk_parameters":
            account_id = arguments["account_id"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            account_balance, available_cash = await _fetch_balance_numbers(account_id)

            max_daily_risk = account_balance * (risk_percentage / 100)
            max_position_risk = max_daily_risk
            max_positions = int(available_cash / max_position_risk) if max_position_risk > 0 else 0

            return _ok({
                "accountId": account_id,
                "accountBalance": account_balance,
                "availableCash": available_cash,
                "riskPercentage": risk_percentage,
                "maxDailyRisk": max_daily_risk,
                "maxPositionRisk": max_position_risk,
                "maxPositions": max_positions,
            })
        
        elif name == "create_watch_list":
            return _ok(watchlists.create(
                arguments["account_id"],
                arguments["name"],
                arguments.get("symbols", []),
            ))

        elif name == "get_watch_lists":
            return _ok(watchlists.list_for(arguments["account_id"]))

        elif name == "update_watch_list":
            return _ok(watchlists.update(
                arguments["account_id"],
                arguments["watch_list_id"],
                name=arguments.get("name"),
                symbols=arguments.get("symbols"),
            ))

        elif name == "delete_watch_list":
            return _ok(watchlists.delete(
                arguments["account_id"], arguments["watch_list_id"]
            ))
        
        elif name == "validate_order_risk":
            account_id = arguments["account_id"]
            order_value = arguments["order_value"]
            risk_amount = arguments["risk_amount"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            current_daily_loss = arguments.get("current_daily_loss", 0.0)

            account_balance, _ = await _fetch_balance_numbers(account_id)

            is_valid, message = risk_manager.validate_order_risk(
                account_id, order_value, risk_amount, account_balance,
                risk_percentage, current_daily_loss,
            )
            return _ok({
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
            })

        elif name == "get_daily_risk_status":
            account_id = arguments["account_id"]
            risk_percentage = arguments.get("risk_percentage", 1.0)
            current_daily_loss = arguments.get("current_daily_loss", 0.0)
            account_balance, _ = await _fetch_balance_numbers(account_id)
            status = risk_manager.get_daily_risk_status(
                account_id, account_balance, risk_percentage, current_daily_loss
            )
            return _ok(status)

        elif name == "record_actual_loss":
            account_id = arguments["account_id"]
            loss_amount = arguments["loss_amount"]
            risk_manager.record_actual_loss(account_id, loss_amount)
            return _ok({
                "accountId": account_id,
                "lossAmount": loss_amount,
                "totalDailyLosses": risk_manager.daily_losses.get(account_id, 0.0),
                "recorded": True,
                "timestamp": int(time.time() * 1000),
            })
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
