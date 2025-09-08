#!/usr/bin/env python3
"""R-Multiple Risk Calculator for Day Trading"""

import asyncio
import json
import os
from typing import Dict, Any

# Set mock credentials for demo
os.environ['ETRADE_OAUTH_CONSUMER_KEY'] = 'demo_key'
os.environ['ETRADE_OAUTH_CONSUMER_SECRET'] = 'demo_secret'

from mcp_etrade.server import call_tool

async def calculate_risk_parameters(account_id: str, risk_percentage: float = 1.0):
    """Calculate R-multiple risk parameters based on account balance."""
    
    # Get account balance
    result = await call_tool("get_account_balance", {"account_id": account_id})
    balance_data = json.loads(result[0].text)
    
    account_balance = balance_data['computedBalance']['accountBalance']
    available_cash = balance_data['computedBalance']['cashAvailableForInvestment']
    
    # Calculate risk amounts
    max_daily_risk = account_balance * (risk_percentage / 100)
    max_position_risk = max_daily_risk  # Conservative: 1 position = full daily risk
    
    return {
        "accountBalance": account_balance,
        "availableCash": available_cash,
        "riskPercentage": risk_percentage,
        "maxDailyRisk": max_daily_risk,
        "maxPositionRisk": max_position_risk,
        "maxPositions": int(available_cash / max_position_risk) if max_position_risk > 0 else 0
    }

def calculate_position_size(entry_price: float, stop_loss: float, risk_amount: float) -> Dict[str, Any]:
    """Calculate position size based on R-multiple risk."""
    
    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share == 0:
        return {"error": "Entry price and stop loss cannot be the same"}
    
    shares = int(risk_amount / risk_per_share)
    position_value = shares * entry_price
    actual_risk = shares * risk_per_share
    
    return {
        "shares": shares,
        "entryPrice": entry_price,
        "stopLoss": stop_loss,
        "riskPerShare": risk_per_share,
        "positionValue": position_value,
        "actualRisk": actual_risk,
        "rMultiple": 1.0  # This is 1R by definition
    }

def calculate_r_multiple(entry_price: float, exit_price: float, stop_loss: float) -> float:
    """Calculate R-multiple for a completed trade."""
    risk_per_share = abs(entry_price - stop_loss)
    profit_per_share = exit_price - entry_price
    return profit_per_share / risk_per_share if risk_per_share > 0 else 0

async def main():
    """Interactive risk calculator."""
    import sys
    
    account_id = sys.argv[1] if len(sys.argv) > 1 else "demo_account_123"
    risk_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    print("=== R-Multiple Risk Calculator ===\n")
    
    # Get risk parameters
    risk_params = await calculate_risk_parameters(account_id, risk_pct)
    
    print(f"📊 Account Balance: ${risk_params['accountBalance']:,.2f}")
    print(f"💰 Available Cash: ${risk_params['availableCash']:,.2f}")
    print(f"⚠️  Risk Percentage: {risk_params['riskPercentage']}%")
    print(f"🔴 Max Daily Risk (R): ${risk_params['maxDailyRisk']:,.2f}")
    print(f"📈 Max Position Risk: ${risk_params['maxPositionRisk']:,.2f}")
    print(f"🎯 Max Positions: {risk_params['maxPositions']}")
    
    print(f"\n=== Position Sizing Example ===")
    
    # Example position sizing
    entry = 100.0
    stop = 98.0
    position = calculate_position_size(entry, stop, risk_params['maxPositionRisk'])
    
    print(f"Entry Price: ${entry}")
    print(f"Stop Loss: ${stop}")
    print(f"Risk per Share: ${position['riskPerShare']:.2f}")
    print(f"Position Size: {position['shares']} shares")
    print(f"Position Value: ${position['positionValue']:,.2f}")
    print(f"Actual Risk: ${position['actualRisk']:,.2f}")
    
    print(f"\n=== R-Multiple Examples ===")
    
    # R-multiple examples
    targets = [102, 104, 106, 110]
    for target in targets:
        r_mult = calculate_r_multiple(entry, target, stop)
        profit = (target - entry) * position['shares']
        print(f"Target ${target}: {r_mult:.1f}R = ${profit:,.2f} profit")
    
    return risk_params

if __name__ == "__main__":
    asyncio.run(main())
