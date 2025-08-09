# config.py
import os
from dotenv import load_dotenv

load_dotenv()

USE_BINANCE_API = False  # Change to True if you want real API
USE_TESTNET = True  # Set to False for live trading

# Mock Binance client for offline testing
class MockBinanceClient:
    def futures_create_order(self, **kwargs):
        return {
            "symbol": kwargs.get("symbol"),
            "side": kwargs.get("side"),
            "type": kwargs.get("type"),
            "price": kwargs.get("price", "MARKET"),
            "quantity": kwargs.get("quantity"),
            "status": "FILLED",
            "orderId": 123456,
            "clientOrderId": "mock_order"
        }
    
    def futures_get_order(self, symbol, orderId):
        return {
            "symbol": symbol,
            "orderId": orderId,
            "status": "FILLED"
        }
    
    def futures_cancel_order(self, symbol, orderId):
        return {
            "symbol": symbol,
            "orderId": orderId,
            "status": "CANCELED"
        }
    
    def futures_get_open_orders(self, symbol=None):
        return []
    
    def futures_get_account(self):
        return {"totalWalletBalance": "1000.00", "totalUnrealizedProfit": "0.00"}
    
    def futures_get_exchange_info(self):
        return {"symbols": [{"symbol": "BTCUSDT", "status": "TRADING"}]}

# Conditional client setup
if USE_BINANCE_API:
    from binance.client import Client
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    client = Client(api_key, api_secret, testnet=USE_TESTNET)
else:
    client = MockBinanceClient()
