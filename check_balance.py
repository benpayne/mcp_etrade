#!/usr/bin/env python3
"""E*TRADE Account Balance Checker Tool"""

import asyncio
import json
import os
from mcp_etrade.server import call_tool

async def check_account_balance(account_id: str = None):
    """Check E*TRADE account balance with proper error handling."""
    
    print("=== E*TRADE Account Balance Checker ===\n")
    
    # Check if OAuth credentials are configured
    consumer_key = os.getenv('ETRADE_OAUTH_CONSUMER_KEY')
    consumer_secret = os.getenv('ETRADE_OAUTH_CONSUMER_SECRET')
    
    if not consumer_key or not consumer_secret:
        print("❌ OAuth credentials not configured")
        print("\nTo use this tool, you need to set:")
        print("  export ETRADE_OAUTH_CONSUMER_KEY='your_key'")
        print("  export ETRADE_OAUTH_CONSUMER_SECRET='your_secret'")
        print("\nTesting with mock data instead...\n")
    else:
        print("✅ OAuth credentials configured")
        print(f"   Consumer Key: {consumer_key[:8]}...")
    
    # Use default account ID if not provided
    if not account_id:
        account_id = "test_account_123"
    
    try:
        # Call the account balance tool
        result = await call_tool("get_account_balance", {"account_id": account_id})
        
        if not result or len(result) == 0:
            print("❌ No result returned from account balance tool")
            return None
            
        response_text = result[0].text
        
        # Check if it's an error message
        if response_text.startswith("Error:"):
            print(f"❌ {response_text}")
            return None
        
        # Parse JSON response
        try:
            balance_data = json.loads(response_text)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response_text}")
            return None
        
        # Display account information
        print(f"📊 Account ID: {balance_data['accountId']}")
        print(f"🏦 Account Type: {balance_data['accountType']}")
        print(f"📝 Description: {balance_data['accountDescription']}")
        print(f"🔐 Authenticated: {'✅' if balance_data['authenticated'] else '❌'}")
        
        # Display cash balances
        print("\n💰 Cash Balances:")
        cash = balance_data['cash']
        print(f"   Money Market: ${cash['moneyMktBalance']:,.2f}")
        print(f"   Open Orders:  ${cash['fundsForOpenOrdersCash']:,.2f}")
        
        # Display computed balances
        print("\n📈 Computed Balances:")
        computed = balance_data['computedBalance']
        print(f"   Account Balance:      ${computed['accountBalance']:,.2f}")
        print(f"   Cash Balance:         ${computed['cashBalance']:,.2f}")
        print(f"   Available Investment: ${computed['cashAvailableForInvestment']:,.2f}")
        print(f"   Available Withdrawal: ${computed['cashAvailableForWithdrawal']:,.2f}")
        
        # Summary
        print(f"\n🎯 Summary:")
        print(f"   Total Account Value: ${computed['accountBalance']:,.2f}")
        print(f"   Available Cash:      ${computed['cashAvailableForInvestment']:,.2f}")
        
        return balance_data
        
    except Exception as e:
        print(f"❌ Error checking account balance: {e}")
        return None

async def main():
    """Main function to run the balance checker."""
    import sys
    
    account_id = None
    if len(sys.argv) > 1:
        account_id = sys.argv[1]
        print(f"Using account ID: {account_id}\n")
    
    await check_account_balance(account_id)

if __name__ == "__main__":
    asyncio.run(main())
