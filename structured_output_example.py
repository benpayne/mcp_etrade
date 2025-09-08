#!/usr/bin/env python3
"""Example of structured MCP output with schemas"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json

app = Server("structured-etrade")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_account_balance",
            description="Get structured account balance data",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Account ID"}
                },
                "required": ["account_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    
    if name == "get_account_balance":
        # Return structured data as properly formatted JSON
        structured_response = {
            "accountId": arguments["account_id"],
            "accountType": "PDT_ACCOUNT", 
            "accountDescription": "Individual Brokerage Account",
            "authenticated": True,
            "cash": {
                "moneyMktBalance": 10000.00,
                "fundsForOpenOrdersCash": 0.00
            },
            "computedBalance": {
                "accountBalance": 10000.00,
                "cashBalance": 10000.00,
                "cashAvailableForInvestment": 10000.00,
                "cashAvailableForWithdrawal": 10000.00
            }
        }
        
        # Return as clean JSON without extra indentation
        return [TextContent(
            type="text", 
            text=json.dumps(structured_response)
        )]
    
    else:
        return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]
