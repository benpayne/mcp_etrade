#!/usr/bin/env python3
"""Demo E*TRADE Account Balance Checker with Mock Data"""

import asyncio
import json
import os

# Set mock credentials for demo
os.environ['ETRADE_OAUTH_CONSUMER_KEY'] = 'demo_key'
os.environ['ETRADE_OAUTH_CONSUMER_SECRET'] = 'demo_secret'

from mcp_etrade.server import call_tool

async def demo_account_balance():
    """Demo account balance check with mock credentials."""
    
    print("=== E*TRADE Account Balance Demo ===\n")
    print("✅ Using mock OAuth credentials for demonstration")
    
    try:
        # Call the account balance tool
        result = await call_tool("get_account_balance", {"account_id": "demo_account_123"})
        
        if not result or len(result) == 0:
            print("❌ No result returned")
            return None
            
        response_text = result[0].text
        balance_data = json.loads(response_text)
        
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
        
        print(f"\n📝 Note: This is mock data. To get real data:")
        print(f"   1. Set your actual E*TRADE OAuth credentials")
        print(f"   2. Complete OAuth authentication flow")
        print(f"   3. Use your real account ID")
        
        return balance_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(demo_account_balance())
