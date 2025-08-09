# src/market_orders.py

import sys
import argparse
from binance.enums import *
from binance.exceptions import BinanceAPIException
from config import client
from utils import logger, validate_symbol, validate_quantity

def validate_market_order_args(symbol, side, quantity):
    """Validate market order arguments"""
    try:
        # Validate symbol
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        # Validate side
        if side.upper() not in ['BUY', 'SELL']:
            raise ValueError("Order side must be BUY or SELL")
        
        # Validate quantity
        if not validate_quantity(quantity):
            raise ValueError(f"Invalid quantity: {quantity}")
        
        return symbol.upper(), side.upper(), float(quantity)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def place_market_order(symbol, side, quantity):
    """Place a market order on Binance Futures"""
    try:
        logger.info(f"[MARKET ORDER] Attempting to place {side} {quantity} {symbol}")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )
        
        logger.info(f"[MARKET ORDER SUCCESS] {side} {quantity} {symbol}")
        logger.info(f"[ORDER DETAILS] {order}")
        
        print(f"✅ Market order placed successfully!")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Order ID: {order.get('orderId', 'N/A')}")
        print(f"   Status: {order.get('status', 'N/A')}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"[MARKET ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[MARKET ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Place market orders on Binance Futures')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    
    args = parser.parse_args()
    
    try:
        symbol, side, quantity = validate_market_order_args(args.symbol, args.side, args.quantity)
        place_market_order(symbol, side, quantity)
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
