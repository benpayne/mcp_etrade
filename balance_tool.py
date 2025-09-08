#!/usr/bin/env python3
"""
E*TRADE Account Balance Tool

This tool helps you verify your E*TRADE account balance using the mcp_etrade server.
It handles both authenticated and demo modes.

Usage:
    python balance_tool.py [account_id]
    
Environment Variables:
    ETRADE_OAUTH_CONSUMER_KEY    - Your E*TRADE OAuth consumer key
    ETRADE_OAUTH_CONSUMER_SECRET - Your E*TRADE OAuth consumer secret
"""

import asyncio
import json
import os
import sys
from typing import Optional, Dict, Any

async def get_account_balance(account_id: str) -> Optional[Dict[str, Any]]:
    """Get account balance using the mcp_etrade server."""
    # Import here to avoid issues with environment variables
    from mcp_etrade.server import call_tool
    
    try:
        result = await call_tool("get_account_balance", {"account_id": account_id})
        
        if not result or len(result) == 0:
            return None
            
        response_text = result[0].text
        
        if response_text.startswith("Error:"):
            print(f"❌ {response_text}")
            return None
        
        return json.loads(response_text)
        
    except Exception as e:
        print(f"❌ Error retrieving balance: {e}")
        return None

def display_balance(balance_data: Dict[str, Any]) -> None:
    """Display formatted account balance information."""
    
    print("=" * 50)
    print("📊 E*TRADE ACCOUNT BALANCE")
    print("=" * 50)
    
    # Account Info
    print(f"Account ID:    {balance_data['accountId']}")
    print(f"Account Type:  {balance_data['accountType']}")
    print(f"Description:   {balance_data['accountDescription']}")
    print(f"Authenticated: {'✅ Yes' if balance_data['authenticated'] else '❌ No (Mock Data)'}")
    
    # Cash Balances
    print("\n💰 CASH BALANCES")
    print("-" * 30)
    cash = balance_data['cash']
    print(f"Money Market Balance:    ${cash['moneyMktBalance']:>12,.2f}")
    print(f"Funds for Open Orders:  ${cash['fundsForOpenOrdersCash']:>12,.2f}")
    
    # Computed Balances
    print("\n📈 COMPUTED BALANCES")
    print("-" * 30)
    computed = balance_data['computedBalance']
    print(f"Total Account Balance:   ${computed['accountBalance']:>12,.2f}")
    print(f"Cash Balance:            ${computed['cashBalance']:>12,.2f}")
    print(f"Available for Investment:${computed['cashAvailableForInvestment']:>12,.2f}")
    print(f"Available for Withdrawal:${computed['cashAvailableForWithdrawal']:>12,.2f}")
    
    # Summary
    print("\n🎯 SUMMARY")
    print("-" * 30)
    print(f"Total Portfolio Value:   ${computed['accountBalance']:>12,.2f}")
    print(f"Available Cash:          ${computed['cashAvailableForInvestment']:>12,.2f}")
    
    # Status indicator
    if balance_data['authenticated']:
        print("\n✅ This is live account data from E*TRADE")
    else:
        print("\n⚠️  This is mock data for demonstration")
        print("   To get real data, complete OAuth authentication")

def check_credentials() -> bool:
    """Check if OAuth credentials are configured."""
    consumer_key = os.getenv('ETRADE_OAUTH_CONSUMER_KEY')
    consumer_secret = os.getenv('ETRADE_OAUTH_CONSUMER_SECRET')
    
    if not consumer_key or not consumer_secret:
        print("⚠️  OAuth credentials not found")
        print("\nTo use with real E*TRADE data:")
        print("  export ETRADE_OAUTH_CONSUMER_KEY='your_key'")
        print("  export ETRADE_OAUTH_CONSUMER_SECRET='your_secret'")
        print("\nUsing mock credentials for demonstration...\n")
        
        # Set mock credentials
        os.environ['ETRADE_OAUTH_CONSUMER_KEY'] = 'demo_key'
        os.environ['ETRADE_OAUTH_CONSUMER_SECRET'] = 'demo_secret'
        return False
    else:
        print(f"✅ OAuth credentials configured (Key: {consumer_key[:8]}...)")
        return True

async def main():
    """Main function."""
    print("E*TRADE Account Balance Tool")
    print("=" * 40)
    
    # Check credentials
    has_real_creds = check_credentials()
    
    # Get account ID from command line or use default
    account_id = sys.argv[1] if len(sys.argv) > 1 else "demo_account_123"
    
    if len(sys.argv) > 1:
        print(f"Using account ID: {account_id}")
    else:
        print(f"Using default account ID: {account_id}")
        print("(You can specify an account ID as a command line argument)")
    
    print()
    
    # Get and display balance
    balance_data = await get_account_balance(account_id)
    
    if balance_data:
        display_balance(balance_data)
        
        if not has_real_creds:
            print("\n📋 NEXT STEPS TO USE WITH REAL DATA:")
            print("1. Get E*TRADE OAuth credentials from developer.etrade.com")
            print("2. Set environment variables with your credentials")
            print("3. Run OAuth authentication flow using mcp_etrade tools")
            print("4. Use your actual account ID")
    else:
        print("❌ Failed to retrieve account balance")

if __name__ == "__main__":
    asyncio.run(main())
