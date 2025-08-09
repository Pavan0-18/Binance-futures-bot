# src/limit_orders.py

import sys
import argparse
from binance.enums import *
from binance.exceptions import BinanceAPIException
from config import client
from utils import logger, validate_symbol, validate_quantity, validate_price

def validate_limit_order_args(symbol, side, quantity, price):
    """Validate limit order arguments"""
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
        
        # Validate price
        if not validate_price(price):
            raise ValueError(f"Invalid price: {price}")
        
        return symbol.upper(), side.upper(), float(quantity), float(price)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def place_limit_order(symbol, side, quantity, price, time_in_force='GTC'):
    """Place a limit order on Binance Futures"""
    try:
        logger.info(f"[LIMIT ORDER] Attempting to place {side} {quantity} {symbol} @ {price}")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=FUTURE_ORDER_TYPE_LIMIT,
            timeInForce=time_in_force,
            quantity=quantity,
            price=price
        )
        
        logger.info(f"[LIMIT ORDER SUCCESS] {side} {quantity} {symbol} @ {price}")
        logger.info(f"[ORDER DETAILS] {order}")
        
        print(f"✅ Limit order placed successfully!")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Price: {price}")
        print(f"   Order ID: {order.get('orderId', 'N/A')}")
        print(f"   Status: {order.get('status', 'N/A')}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"[LIMIT ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[LIMIT ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def cancel_limit_order(symbol, order_id):
    """Cancel a limit order"""
    try:
        logger.info(f"[CANCEL ORDER] Attempting to cancel order {order_id} for {symbol}")
        
        result = client.futures_cancel_order(symbol=symbol, orderId=order_id)
        
        logger.info(f"[CANCEL ORDER SUCCESS] Order {order_id} cancelled")
        logger.info(f"[CANCEL DETAILS] {result}")
        
        print(f"✅ Order cancelled successfully!")
        print(f"   Order ID: {order_id}")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        return result
        
    except BinanceAPIException as e:
        logger.error(f"[CANCEL ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[CANCEL ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def get_open_orders(symbol=None):
    """Get open orders"""
    try:
        logger.info(f"[GET OPEN ORDERS] Retrieving open orders for {symbol or 'all symbols'}")
        
        orders = client.futures_get_open_orders(symbol=symbol)
        
        logger.info(f"[GET OPEN ORDERS SUCCESS] Found {len(orders)} open orders")
        
        if orders:
            print(f"📋 Open Orders ({len(orders)}):")
            for order in orders:
                print(f"   ID: {order.get('orderId')} | {order.get('symbol')} | {order.get('side')} | {order.get('quantity')} @ {order.get('price')} | {order.get('status')}")
        else:
            print("📋 No open orders found")
        
        return orders
        
    except BinanceAPIException as e:
        logger.error(f"[GET OPEN ORDERS API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[GET OPEN ORDERS ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Place limit orders on Binance Futures')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Place order command
    place_parser = subparsers.add_parser('place', help='Place a limit order')
    place_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    place_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    place_parser.add_argument('quantity', type=float, help='Order quantity')
    place_parser.add_argument('price', type=float, help='Order price')
    place_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # Cancel order command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a limit order')
    cancel_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    cancel_parser.add_argument('order_id', help='Order ID to cancel')
    
    # List orders command
    list_parser = subparsers.add_parser('list', help='List open orders')
    list_parser.add_argument('--symbol', help='Trading symbol (optional)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'place':
            symbol, side, quantity, price = validate_limit_order_args(args.symbol, args.side, args.quantity, args.price)
            place_limit_order(symbol, side, quantity, price, args.time_in_force)
        elif args.command == 'cancel':
            cancel_limit_order(args.symbol, args.order_id)
        elif args.command == 'list':
            get_open_orders(args.symbol)
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
