# E*TRADE Account Balance Tool

A comprehensive tool for checking your E*TRADE account balance using the mcp_etrade server.

## Features

✅ **Account Balance Verification** - Get real-time account balance information  
✅ **Mock Data Support** - Works without credentials for testing  
✅ **Formatted Display** - Clean, readable balance information  
✅ **Error Handling** - Graceful handling of authentication issues  
✅ **Flexible Account IDs** - Support for any account ID  

## Quick Start

### Basic Usage (Demo Mode)
```bash
cd /home/davdunc/src/mcp_servers/mcp_etrade
source .venv/bin/activate
python balance_tool.py
```

### With Custom Account ID
```bash
python balance_tool.py "your_account_id_here"
```

### With Real E*TRADE Credentials
```bash
export ETRADE_OAUTH_CONSUMER_KEY='your_consumer_key'
export ETRADE_OAUTH_CONSUMER_SECRET='your_consumer_secret'
python balance_tool.py "your_real_account_id"
```

## Sample Output

```
E*TRADE Account Balance Tool
========================================
✅ OAuth credentials configured (Key: ABC12345...)
Using account ID: demo_account_123

==================================================
📊 E*TRADE ACCOUNT BALANCE
==================================================
Account ID:    demo_account_123
Account Type:  PDT_ACCOUNT
Description:   Individual Brokerage Account
Authenticated: ✅ Yes

💰 CASH BALANCES
------------------------------
Money Market Balance:    $   10,000.00
Funds for Open Orders:  $        0.00

📈 COMPUTED BALANCES
------------------------------
Total Account Balance:   $   10,000.00
Cash Balance:            $   10,000.00
Available for Investment:$   10,000.00
Available for Withdrawal:$   10,000.00

🎯 SUMMARY
------------------------------
Total Portfolio Value:   $   10,000.00
Available Cash:          $   10,000.00

✅ This is live account data from E*TRADE
```

## How It Works

1. **Credential Check** - Verifies if OAuth credentials are configured
2. **MCP Server Call** - Uses the `get_account_balance` tool from mcp_etrade
3. **Data Parsing** - Processes the JSON response from E*TRADE API
4. **Formatted Display** - Shows balance information in a readable format

## Balance Information Displayed

### Account Details
- Account ID and type
- Account description
- Authentication status

### Cash Balances
- Money Market Balance
- Funds reserved for open orders

### Computed Balances
- Total account balance
- Available cash balance
- Cash available for investment
- Cash available for withdrawal

## Error Handling

The tool handles common scenarios:

- **No OAuth Credentials** - Falls back to mock data with clear instructions
- **Invalid Account ID** - Shows appropriate error messages
- **API Errors** - Displays E*TRADE API error responses
- **Network Issues** - Graceful handling of connection problems

## Integration with mcp_etrade

This tool leverages the existing `get_account_balance` tool from the mcp_etrade server:

```python
# Uses the existing MCP tool
result = await call_tool("get_account_balance", {"account_id": account_id})
```

## Next Steps for Real Data

To use with actual E*TRADE data:

1. **Get OAuth Credentials**
   - Register at [developer.etrade.com](https://developer.etrade.com)
   - Create an application to get consumer key/secret

2. **Set Environment Variables**
   ```bash
   export ETRADE_OAUTH_CONSUMER_KEY='your_key'
   export ETRADE_OAUTH_CONSUMER_SECRET='your_secret'
   ```

3. **Complete OAuth Flow**
   - Use mcp_etrade OAuth tools to get access tokens
   - Follow the authentication workflow

4. **Use Real Account ID**
   - Get your account ID from E*TRADE
   - Pass it to the balance tool

## Files

- `balance_tool.py` - Main comprehensive balance checker
- `demo_balance.py` - Simple demo version
- `check_balance.py` - Basic balance checker
- `test_balance.py` - Development/testing version

## Dependencies

- mcp_etrade server (existing)
- Python 3.7+
- asyncio support
- JSON parsing

The tool uses the existing mcp_etrade infrastructure, so no additional dependencies are required.
