# src/advanced/stop_limit.py

import sys
import argparse
from binance.enums import *
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import client
from utils import logger, validate_symbol, validate_quantity, validate_price

def validate_stop_limit_args(symbol, side, quantity, stop_price, limit_price):
    """Validate stop-limit order arguments"""
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
        
        # Validate prices
        if not validate_price(stop_price):
            raise ValueError(f"Invalid stop price: {stop_price}")
        if not validate_price(limit_price):
            raise ValueError(f"Invalid limit price: {limit_price}")
        
        # Validate price relationship based on side
        if side.upper() == 'BUY':
            if stop_price <= limit_price:
                raise ValueError("For BUY orders: stop price must be higher than limit price")
        else:  # SELL
            if stop_price >= limit_price:
                raise ValueError("For SELL orders: stop price must be lower than limit price")
        
        return symbol.upper(), side.upper(), float(quantity), float(stop_price), float(limit_price)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def place_stop_limit_order(symbol, side, quantity, stop_price, limit_price, time_in_force='GTC'):
    """Place a stop-limit order on Binance Futures"""
    try:
        logger.info(f"[STOP LIMIT ORDER] Attempting to place {side} {quantity} {symbol} @ {limit_price} (stop: {stop_price})")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=FUTURE_ORDER_TYPE_STOP,
            timeInForce=time_in_force,
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price
        )
        
        logger.info(f"[STOP LIMIT ORDER SUCCESS] {side} {quantity} {symbol} @ {limit_price} (stop: {stop_price})")
        logger.info(f"[ORDER DETAILS] {order}")
        
        print(f"✅ Stop-limit order placed successfully!")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Stop Price: {stop_price}")
        print(f"   Limit Price: {limit_price}")
        print(f"   Order ID: {order.get('orderId', 'N/A')}")
        print(f"   Status: {order.get('status', 'N/A')}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"[STOP LIMIT ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[STOP LIMIT ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def place_stop_market_order(symbol, side, quantity, stop_price):
    """Place a stop-market order on Binance Futures"""
    try:
        logger.info(f"[STOP MARKET ORDER] Attempting to place {side} {quantity} {symbol} (stop: {stop_price})")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=FUTURE_ORDER_TYPE_STOP_MARKET,
            quantity=quantity,
            stopPrice=stop_price
        )
        
        logger.info(f"[STOP MARKET ORDER SUCCESS] {side} {quantity} {symbol} (stop: {stop_price})")
        logger.info(f"[ORDER DETAILS] {order}")
        
        print(f"✅ Stop-market order placed successfully!")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Stop Price: {stop_price}")
        print(f"   Order ID: {order.get('orderId', 'N/A')}")
        print(f"   Status: {order.get('status', 'N/A')}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"[STOP MARKET ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[STOP MARKET ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Place stop-limit orders on Binance Futures')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stop-limit order command
    stop_limit_parser = subparsers.add_parser('stop-limit', help='Place a stop-limit order')
    stop_limit_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    stop_limit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    stop_limit_parser.add_argument('quantity', type=float, help='Order quantity')
    stop_limit_parser.add_argument('stop_price', type=float, help='Stop price (trigger price)')
    stop_limit_parser.add_argument('limit_price', type=float, help='Limit price (execution price)')
    stop_limit_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # Stop-market order command
    stop_market_parser = subparsers.add_parser('stop-market', help='Place a stop-market order')
    stop_market_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    stop_market_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    stop_market_parser.add_argument('quantity', type=float, help='Order quantity')
    stop_market_parser.add_argument('stop_price', type=float, help='Stop price (trigger price)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'stop-limit':
            symbol, side, quantity, stop_price, limit_price = validate_stop_limit_args(
                args.symbol, args.side, args.quantity, args.stop_price, args.limit_price
            )
            place_stop_limit_order(symbol, side, quantity, stop_price, limit_price, args.time_in_force)
        elif args.command == 'stop-market':
            symbol, side, quantity, stop_price, _ = validate_stop_limit_args(
                args.symbol, args.side, args.quantity, args.stop_price, args.stop_price
            )
            place_stop_market_order(symbol, side, quantity, stop_price)
        else:
            parser.print_help()
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
