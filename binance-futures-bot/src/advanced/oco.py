# src/advanced/oco.py

import sys
import argparse
from binance.enums import *
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import client
from utils import logger, validate_symbol, validate_quantity, validate_price

def validate_oco_args(symbol, side, quantity, price, stop_price, stop_limit_price):
    """Validate OCO order arguments"""
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
        if not validate_price(price):
            raise ValueError(f"Invalid limit price: {price}")
        if not validate_price(stop_price):
            raise ValueError(f"Invalid stop price: {stop_price}")
        if not validate_price(stop_limit_price):
            raise ValueError(f"Invalid stop limit price: {stop_limit_price}")
        
        # Validate price relationships based on side
        if side.upper() == 'SELL':
            # For SELL orders: stop_price < price < stop_limit_price
            if not (stop_price < price < stop_limit_price):
                raise ValueError("For SELL orders: stop_price < limit_price < stop_limit_price")
        else:  # BUY
            # For BUY orders: stop_limit_price < price < stop_price
            if not (stop_limit_price < price < stop_price):
                raise ValueError("For BUY orders: stop_limit_price < limit_price < stop_price")
        
        return symbol.upper(), side.upper(), float(quantity), float(price), float(stop_price), float(stop_limit_price)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def place_oco_order(symbol, side, quantity, price, stop_price, stop_limit_price, time_in_force='GTC'):
    """Place an OCO (One-Cancels-the-Other) order on Binance Futures"""
    try:
        logger.info(f"[OCO ORDER] Attempting to place {side} {quantity} {symbol}")
        logger.info(f"[OCO DETAILS] Limit: {price}, Stop: {stop_price}, Stop Limit: {stop_limit_price}")
        
        # Note: OCO orders are not directly supported in Binance Futures API
        # We'll implement this by placing two separate orders and managing them
        logger.warning("[OCO ORDER] OCO orders not directly supported in Binance Futures. Using alternative approach.")
        
        # Place limit order
        limit_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL if side == "SELL" else SIDE_BUY,
            type=FUTURE_ORDER_TYPE_LIMIT,
            timeInForce=time_in_force,
            quantity=quantity,
            price=price
        )
        
        # Place stop-limit order
        stop_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL if side == "SELL" else SIDE_BUY,
            type=FUTURE_ORDER_TYPE_STOP,
            timeInForce=time_in_force,
            quantity=quantity,
            price=stop_limit_price,
            stopPrice=stop_price
        )
        
        logger.info(f"[OCO ORDER SUCCESS] {side} {quantity} {symbol}")
        logger.info(f"[LIMIT ORDER DETAILS] {limit_order}")
        logger.info(f"[STOP ORDER DETAILS] {stop_order}")
        
        print(f"✅ OCO order placed successfully!")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Limit Price: {price}")
        print(f"   Stop Price: {stop_price}")
        print(f"   Stop Limit Price: {stop_limit_price}")
        print(f"   Limit Order ID: {limit_order.get('orderId', 'N/A')}")
        print(f"   Stop Order ID: {stop_order.get('orderId', 'N/A')}")
        
        return {
            'limit_order': limit_order,
            'stop_order': stop_order,
            'symbol': symbol,
            'side': side,
            'quantity': quantity
        }
        
    except BinanceAPIException as e:
        logger.error(f"[OCO ORDER API ERROR] {e}")
        print(f"❌ Binance API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"[OCO ORDER ERROR] {e}")
        print(f"❌ Unknown error: {e}")
        return None

def cancel_oco_orders(symbol, order_ids):
    """Cancel OCO orders"""
    try:
        logger.info(f"[CANCEL OCO ORDERS] Attempting to cancel orders {order_ids} for {symbol}")
        
        cancelled_orders = []
        for order_id in order_ids:
            try:
                result = client.futures_cancel_order(symbol=symbol, orderId=order_id)
                cancelled_orders.append(result)
                logger.info(f"[CANCEL SUCCESS] Order {order_id} cancelled")
            except BinanceAPIException as e:
                logger.error(f"[CANCEL FAILED] Order {order_id}: {e}")
        
        if cancelled_orders:
            print(f"✅ {len(cancelled_orders)} orders cancelled successfully")
            for order in cancelled_orders:
                print(f"   Order ID: {order.get('orderId')} - Status: {order.get('status')}")
        else:
            print("❌ No orders were cancelled")
        
        return cancelled_orders
        
    except Exception as e:
        logger.error(f"[CANCEL OCO ORDERS ERROR] {e}")
        print(f"❌ Error cancelling orders: {e}")
        return None

def get_oco_order_status(symbol, order_ids):
    """Get status of OCO orders"""
    try:
        logger.info(f"[GET OCO STATUS] Checking status of orders {order_ids} for {symbol}")
        
        order_statuses = []
        for order_id in order_ids:
            try:
                order = client.futures_get_order(symbol=symbol, orderId=order_id)
                order_statuses.append(order)
                logger.info(f"[ORDER STATUS] {order_id}: {order.get('status')}")
            except BinanceAPIException as e:
                logger.error(f"[GET ORDER FAILED] {order_id}: {e}")
        
        if order_statuses:
            print(f"📋 OCO Order Status ({len(order_statuses)} orders):")
            for order in order_statuses:
                print(f"   ID: {order.get('orderId')} | {order.get('symbol')} | {order.get('side')} | {order.get('quantity')} @ {order.get('price')} | {order.get('status')}")
        else:
            print("📋 No order status information available")
        
        return order_statuses
        
    except Exception as e:
        logger.error(f"[GET OCO STATUS ERROR] {e}")
        print(f"❌ Error getting order status: {e}")
        return None

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Place OCO orders on Binance Futures')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Place OCO order command
    place_parser = subparsers.add_parser('place', help='Place an OCO order')
    place_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    place_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    place_parser.add_argument('quantity', type=float, help='Order quantity')
    place_parser.add_argument('price', type=float, help='Limit price')
    place_parser.add_argument('stop_price', type=float, help='Stop price')
    place_parser.add_argument('stop_limit_price', type=float, help='Stop limit price')
    place_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # Cancel OCO orders command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel OCO orders')
    cancel_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    cancel_parser.add_argument('order_ids', nargs='+', help='Order IDs to cancel')
    
    # Get OCO status command
    status_parser = subparsers.add_parser('status', help='Get OCO order status')
    status_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    status_parser.add_argument('order_ids', nargs='+', help='Order IDs to check')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'place':
            symbol, side, quantity, price, stop_price, stop_limit_price = validate_oco_args(
                args.symbol, args.side, args.quantity, args.price, args.stop_price, args.stop_limit_price
            )
            place_oco_order(symbol, side, quantity, price, stop_price, stop_limit_price, args.time_in_force)
        elif args.command == 'cancel':
            cancel_oco_orders(args.symbol, args.order_ids)
        elif args.command == 'status':
            get_oco_order_status(args.symbol, args.order_ids)
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
