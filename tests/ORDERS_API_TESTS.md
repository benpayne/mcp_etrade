# E*TRADE Orders API Tests

This document describes the comprehensive test suite for the E*TRADE Orders API implementation.

## Overview

The Orders API test suite covers all 6 endpoints from the E*TRADE Orders API v1 specification:

1. **List Orders** (GET) - Retrieve order details for an account
2. **Preview Order** (POST) - Preview an order before placing it
3. **Place Order** (POST) - Submit an order after previewing
4. **Cancel Order** (PUT) - Cancel an existing order
5. **Preview Changed Order** (POST) - Preview modifications to an existing order
6. **Place Changed Order** (PUT) - Submit order modifications

## Test Coverage

### Core Functionality Tests

#### 1. List Orders (`test_list_orders_success`)
- Tests successful retrieval of order list
- Validates response structure with OrdersResponse format
- Verifies order details including orderId, orderType, and OrderDetail arrays
- Confirms proper API endpoint construction

#### 2. List Orders with Filters (`test_list_orders_with_filters`)
- Tests query parameter handling for filtering orders
- Validates URL construction with multiple parameters:
  - `status` (OPEN, EXECUTED, CANCELLED, etc.)
  - `count` (pagination)
  - `symbol` (specific securities)
  - `securityType` (EQ, OPTN, MF, MMF)
  - `transactionType` (BUY, SELL, etc.)

#### 3. Preview Order (`test_preview_order_success`)
- Tests order preview functionality before placement
- Validates PreviewOrderResponse structure
- Confirms preview ID generation for subsequent order placement
- Tests commission calculation and order value estimation

#### 4. Place Order (`test_place_order_success`)
- Tests actual order placement using preview IDs
- Validates PlaceOrderResponse with order confirmation
- Confirms order ID assignment and placement timestamp
- Tests integration with preview workflow

#### 5. Cancel Order (`test_cancel_order_success`)
- Tests order cancellation functionality
- Validates CancelOrderResponse structure
- Confirms cancellation timestamp and status messages
- Tests proper request body formatting

#### 6. Preview Changed Order (`test_preview_changed_order_success`)
- Tests order modification preview
- Validates changed order parameters (quantity, price, etc.)
- Confirms new preview ID generation for modifications
- Tests order change workflow

#### 7. Place Changed Order (`test_place_changed_order_success`)
- Tests submission of order modifications
- Validates successful order change confirmation
- Tests integration with change preview workflow

### Error Handling Tests

#### 8. List Orders Error Handling (`test_list_orders_error_handling`)
- Tests API error response handling (400 status codes)
- Validates error message parsing
- Confirms proper exception raising for invalid account keys

#### 9. Preview Order Validation (`test_preview_order_validation`)
- Tests request validation for missing required fields
- Validates proper error messages for malformed requests
- Confirms client-side validation before API calls

#### 10. Place Order Validation (`test_place_order_validation`)
- Tests validation of preview ID requirement
- Confirms proper error handling for missing preview IDs
- Validates request structure requirements

### Advanced Order Types Tests

#### 11. Option Order Preview (`test_option_order_preview`)
- Tests options order preview functionality
- Validates option-specific parameters:
  - `callPut` (CALL/PUT)
  - `expiryYear`, `expiryMonth`, `expiryDay`
  - `strikePrice`
  - `orderAction` (BUY_OPEN, SELL_CLOSE, etc.)
- Confirms OPTN orderType handling

#### 12. Multi-leg Option Order (`test_multi_leg_option_order`)
- Tests complex option strategies (spreads)
- Validates SPREADS orderType
- Tests multiple instrument legs in single order
- Confirms NET_DEBIT/NET_CREDIT pricing types

## Test Data Structures

### Mock Response Formats

The tests use comprehensive mock responses that match E*TRADE API specifications:

```python
# OrdersResponse format
{
    "OrdersResponse": {
        "marker": "pagination_marker",
        "next": "next_marker", 
        "Order": [
            {
                "orderId": 96,
                "details": "order_details_url",
                "orderType": "EQ",
                "OrderDetail": [...]
            }
        ]
    }
}

# PreviewOrderResponse format
{
    "PreviewOrderResponse": {
        "orderType": "EQ",
        "totalOrderValue": 1000.00,
        "totalCommission": 6.95,
        "previewIds": [
            {
                "previewId": 123456789,
                "cashMargin": "CASH"
            }
        ],
        "previewTime": 1609459200000,
        "dstFlag": True,
        "accountId": "12345678"
    }
}
```

### Order Request Structures

Tests validate proper request formatting for different order types:

```python
# Equity Order
{
    "orderType": "EQ",
    "clientOrderId": "unique_client_id",
    "order": [
        {
            "orderAction": "BUY",
            "quantity": 10,
            "orderTerm": "GOOD_FOR_DAY",
            "priceType": "MARKET",
            "Instrument": [
                {
                    "Product": {
                        "symbol": "AAPL",
                        "securityType": "EQ"
                    }
                }
            ]
        }
    ]
}

# Option Order
{
    "orderType": "OPTN",
    "order": [
        {
            "orderAction": "BUY_OPEN",
            "quantity": 1,
            "priceType": "LIMIT",
            "stopPrice": 5.00,
            "Instrument": [
                {
                    "Product": {
                        "symbol": "AAPL",
                        "securityType": "OPTN",
                        "callPut": "CALL",
                        "expiryYear": 2024,
                        "expiryMonth": 12,
                        "expiryDay": 20,
                        "strikePrice": 150.00
                    }
                }
            ]
        }
    ]
}
```

## API Client Implementation

The tests validate the `ETradeClient` class methods:

- `list_orders()` - GET requests with query parameters
- `preview_order()` - POST requests with order data
- `place_order()` - POST requests with preview IDs
- `cancel_order()` - PUT requests with cancellation data
- `preview_changed_order()` - POST requests for order modifications
- `place_changed_order()` - PUT requests for order changes

## Test Execution

Run all Orders API tests:
```bash
pytest tests/test_orders_api.py -v
```

Run specific test:
```bash
pytest tests/test_orders_api.py::TestOrdersAPI::test_list_orders_success -v
```

## Integration with Existing Test Suite

The Orders API tests integrate seamlessly with the existing 75 tests, bringing the total to 87 tests. All tests pass and maintain compatibility with:

- OAuth authentication tests
- Accounts API tests  
- Option chains tests
- Market data tests
- Configuration tests

## Next Steps

With comprehensive test coverage in place, the Orders API is ready for:

1. Integration into the MCP server tools
2. Real API endpoint testing
3. Production deployment
4. Additional order types and features

The test suite provides a solid foundation for implementing the actual Orders API tools in the MCP server.
