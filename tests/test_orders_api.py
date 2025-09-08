"""Tests for E*TRADE Orders API endpoints."""

import pytest
import json
from unittest.mock import Mock, patch
from mcp_etrade.etrade_client import ETradeClient


class TestOrdersAPI:
    """Test E*TRADE Orders API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a mock E*TRADE client."""
        client = ETradeClient()
        client.oauth = Mock()
        client.oauth.client = Mock()
        return client

    def test_list_orders_success(self, client):
        """Test successful list orders request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "OrdersResponse": {
                "marker": "1234567890",
                "next": "next_marker",
                "Order": [
                    {
                        "orderId": 96,
                        "details": "https://api.etrade.com/v1/accounts/test/orders/96",
                        "orderType": "EQ",
                        "OrderDetail": [
                            {
                                "placedTime": 1609459200000,
                                "executedTime": 1609459260000,
                                "orderValue": 1000.00,
                                "status": "EXECUTED",
                                "orderTerm": "GOOD_FOR_DAY",
                                "priceType": "MARKET",
                                "orderAction": "BUY",
                                "quantity": 10,
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
                ]
            }
        }
        
        client.oauth.client.get.return_value = mock_response
        
        result = client.list_orders("test_account_key")
        
        assert result["OrdersResponse"]["marker"] == "1234567890"
        assert len(result["OrdersResponse"]["Order"]) == 1
        assert result["OrdersResponse"]["Order"][0]["orderId"] == 96
        client.oauth.client.get.assert_called_once()

    def test_list_orders_with_filters(self, client):
        """Test list orders with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"OrdersResponse": {"Order": []}}
        
        client.oauth.client.get.return_value = mock_response
        
        client.list_orders(
            account_id_key="test_account",
            status="OPEN",
            count=50,
            symbol="AAPL",
            security_type="EQ",
            transaction_type="BUY"
        )
        
        call_args = client.oauth.client.get.call_args
        assert "status=OPEN" in call_args[0][0]
        assert "count=50" in call_args[0][0]
        assert "symbol=AAPL" in call_args[0][0]

    def test_preview_order_success(self, client):
        """Test successful preview order request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
                "accountId": "12345678",
                "optionLevelCd": 0,
                "marginLevelCd": "MARGIN_TRADING_ALLOWED",
                "isEmployee": False,
                "commissionMessage": "Commission: $6.95"
            }
        }
        
        client.oauth.client.post.return_value = mock_response
        
        order_request = {
            "orderType": "EQ",
            "clientOrderId": "test_order_123",
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
        
        result = client.preview_order("test_account", order_request)
        
        assert result["PreviewOrderResponse"]["totalOrderValue"] == 1000.00
        assert result["PreviewOrderResponse"]["previewIds"][0]["previewId"] == 123456789
        client.oauth.client.post.assert_called_once()

    def test_place_order_success(self, client):
        """Test successful place order request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "PlaceOrderResponse": {
                "orderType": "EQ",
                "totalOrderValue": 1000.00,
                "totalCommission": 6.95,
                "orderId": 987654321,
                "orderIds": [
                    {
                        "orderId": 987654321,
                        "cashMargin": "CASH"
                    }
                ],
                "placedTime": 1609459200000,
                "accountId": "12345678",
                "dstFlag": True,
                "optionLevelCd": 0,
                "marginLevelCd": "MARGIN_TRADING_ALLOWED",
                "isEmployee": False,
                "commissionMsg": "Commission: $6.95"
            }
        }
        
        client.oauth.client.post.return_value = mock_response
        
        order_request = {
            "orderType": "EQ",
            "clientOrderId": "test_order_123",
            "previewIds": [
                {
                    "previewId": 123456789,
                    "cashMargin": "CASH"
                }
            ],
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
        
        result = client.place_order("test_account", order_request)
        
        assert result["PlaceOrderResponse"]["orderId"] == 987654321
        assert result["PlaceOrderResponse"]["totalOrderValue"] == 1000.00
        client.oauth.client.post.assert_called_once()

    def test_cancel_order_success(self, client):
        """Test successful cancel order request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "CancelOrderResponse": {
                "accountId": "12345678",
                "orderId": 987654321,
                "cancelTime": 1609459200000,
                "Messages": {
                    "Message": [
                        {
                            "description": "Order has been successfully cancelled",
                            "code": 1026,
                            "type": "INFO"
                        }
                    ]
                }
            }
        }
        
        client.oauth.client.put.return_value = mock_response
        
        cancel_request = {
            "CancelOrderRequest": {
                "orderId": 987654321
            }
        }
        
        result = client.cancel_order("test_account", cancel_request)
        
        assert result["CancelOrderResponse"]["orderId"] == 987654321
        assert "successfully cancelled" in result["CancelOrderResponse"]["Messages"]["Message"][0]["description"]
        client.oauth.client.put.assert_called_once()

    def test_preview_changed_order_success(self, client):
        """Test successful preview changed order request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "PreviewOrderResponse": {
                "orderType": "EQ",
                "totalOrderValue": 1500.00,
                "totalCommission": 6.95,
                "previewIds": [
                    {
                        "previewId": 123456790,
                        "cashMargin": "CASH"
                    }
                ],
                "previewTime": 1609459260000,
                "dstFlag": True,
                "accountId": "12345678"
            }
        }
        
        client.oauth.client.post.return_value = mock_response
        
        change_request = {
            "orderType": "EQ",
            "clientOrderId": "test_change_123",
            "order": [
                {
                    "orderAction": "BUY",
                    "quantity": 15,  # Changed quantity
                    "orderTerm": "GOOD_FOR_DAY",
                    "priceType": "LIMIT",
                    "stopPrice": 150.00,
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
        
        result = client.preview_changed_order("test_account", "987654321", change_request)
        
        assert result["PreviewOrderResponse"]["totalOrderValue"] == 1500.00
        assert result["PreviewOrderResponse"]["previewIds"][0]["previewId"] == 123456790
        client.oauth.client.post.assert_called_once()

    def test_place_changed_order_success(self, client):
        """Test successful place changed order request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "PlaceOrderResponse": {
                "orderType": "EQ",
                "totalOrderValue": 1500.00,
                "totalCommission": 6.95,
                "orderId": 987654321,
                "orderIds": [
                    {
                        "orderId": 987654321,
                        "cashMargin": "CASH"
                    }
                ],
                "placedTime": 1609459260000,
                "accountId": "12345678"
            }
        }
        
        client.oauth.client.put.return_value = mock_response
        
        change_request = {
            "orderType": "EQ",
            "clientOrderId": "test_change_123",
            "previewIds": [
                {
                    "previewId": 123456790,
                    "cashMargin": "CASH"
                }
            ],
            "order": [
                {
                    "orderAction": "BUY",
                    "quantity": 15,
                    "orderTerm": "GOOD_FOR_DAY",
                    "priceType": "LIMIT",
                    "stopPrice": 150.00,
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
        
        result = client.place_changed_order("test_account", "987654321", change_request)
        
        assert result["PlaceOrderResponse"]["orderId"] == 987654321
        assert result["PlaceOrderResponse"]["totalOrderValue"] == 1500.00
        client.oauth.client.put.assert_called_once()

    def test_list_orders_error_handling(self, client):
        """Test error handling for list orders."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "Error": {
                "code": 102,
                "message": "Please enter valid account key."
            }
        }
        
        client.oauth.client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            client.list_orders("invalid_account")
        
        assert "400" in str(exc_info.value)

    def test_preview_order_validation(self, client):
        """Test preview order request validation."""
        # Test missing required fields
        invalid_request = {
            "orderType": "EQ"
            # Missing order details
        }
        
        with pytest.raises(ValueError) as exc_info:
            client.preview_order("test_account", invalid_request)
        
        assert "order" in str(exc_info.value).lower()

    def test_place_order_validation(self, client):
        """Test place order request validation."""
        # Test missing previewIds
        invalid_request = {
            "orderType": "EQ",
            "order": [
                {
                    "orderAction": "BUY",
                    "quantity": 10
                }
            ]
            # Missing previewIds
        }
        
        with pytest.raises(ValueError) as exc_info:
            client.place_order("test_account", invalid_request)
        
        assert "previewids" in str(exc_info.value).lower()

    def test_option_order_preview(self, client):
        """Test preview order for options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "PreviewOrderResponse": {
                "orderType": "OPTN",
                "totalOrderValue": 500.00,
                "totalCommission": 6.95,
                "previewIds": [
                    {
                        "previewId": 123456791,
                        "cashMargin": "CASH"
                    }
                ]
            }
        }
        
        client.oauth.client.post.return_value = mock_response
        
        option_request = {
            "orderType": "OPTN",
            "clientOrderId": "option_test_123",
            "order": [
                {
                    "orderAction": "BUY_OPEN",
                    "quantity": 1,
                    "orderTerm": "GOOD_FOR_DAY",
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
        
        result = client.preview_order("test_account", option_request)
        
        assert result["PreviewOrderResponse"]["orderType"] == "OPTN"
        assert result["PreviewOrderResponse"]["totalOrderValue"] == 500.00

    def test_multi_leg_option_order(self, client):
        """Test multi-leg option order preview."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "PreviewOrderResponse": {
                "orderType": "SPREADS",
                "totalOrderValue": 200.00,
                "totalCommission": 6.95,
                "previewIds": [
                    {
                        "previewId": 123456792,
                        "cashMargin": "CASH"
                    }
                ]
            }
        }
        
        client.oauth.client.post.return_value = mock_response
        
        spread_request = {
            "orderType": "SPREADS",
            "clientOrderId": "spread_test_123",
            "order": [
                {
                    "orderAction": "BUY_OPEN",
                    "quantity": 1,
                    "orderTerm": "GOOD_FOR_DAY",
                    "priceType": "NET_DEBIT",
                    "stopPrice": 2.00,
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
                        },
                        {
                            "Product": {
                                "symbol": "AAPL",
                                "securityType": "OPTN",
                                "callPut": "CALL",
                                "expiryYear": 2024,
                                "expiryMonth": 12,
                                "expiryDay": 20,
                                "strikePrice": 155.00
                            }
                        }
                    ]
                }
            ]
        }
        
        result = client.preview_order("test_account", spread_request)
        
        assert result["PreviewOrderResponse"]["orderType"] == "SPREADS"
        assert result["PreviewOrderResponse"]["totalOrderValue"] == 200.00
