# E*TRADE MCP Server

A comprehensive Model Context Protocol (MCP) server for E*TRADE integration with OAuth authentication, account management, risk calculations, watch lists, and trading guardrails.

## Features

### 🔐 **OAuth Authentication**
- Complete E*TRADE OAuth 1.0a flow
- Token management and renewal
- Secure credential handling

### 💰 **Account Management**
- Account balance retrieval
- Transaction history
- Portfolio viewing
- Real-time account data

### 📊 **Risk Management**
- R-multiple risk calculations
- Daily loss tracking
- Position sizing guardrails
- Risk validation before orders

### 📋 **Watch Lists**
- Create, read, update, delete watch lists
- Symbol management
- Independent from portfolio positions

### 📈 **Market Data**
- Option chains with expiration dates
- Real-time quotes
- Security lookup by company name

### 🚨 **Alerts**
- Price alerts management
- Alert notifications
- Custom alert conditions

## Installation

### Prerequisites
- Python 3.11+
- E*TRADE developer account with API keys

### Install via UVX (Recommended)
```bash
uvx --from git+https://github.com/davdunc/mcp_etrade.git mcp_etrade
```

### Install via pip
```bash
pip install git+https://github.com/davdunc/mcp_etrade.git
```

### Development Install
```bash
git clone https://github.com/davdunc/mcp_etrade.git
cd mcp_etrade
pip install -e .
```

## Configuration

Set your E*TRADE API credentials:

```bash
export ETRADE_OAUTH_CONSUMER_KEY="your_consumer_key"
export ETRADE_OAUTH_CONSUMER_SECRET="your_consumer_secret"
```

## Usage

### Standalone Server
```bash
python -m mcp_etrade.server
```

### With Colosseum Framework
Add to `~/.config/colosseum/mcp.json`:

```json
{
  "etrade": {
    "type": "etrade",
    "command": "uvx",
    "args": ["--from", "git+https://github.com/davdunc/mcp_etrade.git", "mcp_etrade"],
    "env": {
      "ETRADE_OAUTH_CONSUMER_KEY": "${ETRADE_OAUTH_CONSUMER_KEY}",
      "ETRADE_OAUTH_CONSUMER_SECRET": "${ETRADE_OAUTH_CONSUMER_SECRET}"
    }
  }
}
```

## Available Tools

### Authentication
- `get_request_token` - Start OAuth flow
- `get_authorization_url` - Get user authorization URL
- `get_access_token` - Complete OAuth flow
- `renew_access_token` - Refresh tokens
- `revoke_access_token` - Revoke access

### Account Management
- `get_account_balance` - Get account balance and details
- `list_transactions` - List account transactions
- `get_transaction_details` - Get specific transaction details
- `view_portfolio` - View portfolio positions

### Risk Management
- `calculate_risk_parameters` - Calculate R-multiple risk parameters
- `validate_order_risk` - Validate order against risk limits
- `get_daily_risk_status` - Get current daily risk utilization
- `record_actual_loss` - Record actual trading losses

### Watch Lists
- `create_watch_list` - Create new watch list
- `get_watch_lists` - Get all watch lists
- `update_watch_list` - Update existing watch list
- `delete_watch_list` - Delete watch list

### Market Data
- `get_option_chains` - Get option chains for symbols
- `get_option_expire_dates` - Get option expiration dates
- `get_quotes` - Get real-time quotes
- `lookup_product` - Search securities by company name

### Alerts
- `list_alerts` - List price alerts
- `delete_alerts` - Delete alerts
- `get_alert_details` - Get alert details

## Risk Management

The server includes comprehensive risk management features:

- **Daily Risk Limits**: Configurable percentage of account balance
- **Position Size Limits**: Maximum 50% of account per order
- **Loss Tracking**: Both potential and actual loss tracking
- **Validation**: Pre-order risk validation with detailed messages

Example risk validation:
```python
# Validate order before placement
result = await call_tool("validate_order_risk", {
    "account_id": "your_account",
    "order_value": 1000.00,
    "risk_amount": 50.00,
    "risk_percentage": 1.0
})
```

## Testing

Run the comprehensive test suite:

```bash
pytest
```

**Test Coverage:**
- 105 passing tests
- OAuth authentication flows
- Account management operations
- Risk calculation accuracy
- Watch list CRUD operations
- Market data retrieval
- Alert management

## Architecture

- **Clean JSON Output**: Structured responses for agent consumption
- **Comprehensive Error Handling**: Graceful failure modes
- **Mock Data Support**: Full functionality without live API calls
- **Modular Design**: Separate concerns for OAuth, risk, data, etc.

## Integration

Designed for integration with:
- **Colosseum**: Multi-agent trading framework
- **LangChain**: Agent tooling and orchestration
- **MCP Clients**: Any MCP-compatible system

## License

GNU General Public License v3.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/davdunc/mcp_etrade/issues
- Documentation: See inline code documentation
