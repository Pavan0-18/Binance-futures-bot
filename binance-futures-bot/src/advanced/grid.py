# src/advanced/grid.py

import sys
import argparse
import time
from datetime import datetime, timedelta
from binance.enums import *
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import client
from utils import logger, validate_symbol, validate_quantity, validate_price

def validate_grid_args(symbol, side, quantity, upper_price, lower_price, grid_levels):
    """Validate grid trading arguments"""
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
        if not validate_price(upper_price):
            raise ValueError(f"Invalid upper price: {upper_price}")
        if not validate_price(lower_price):
            raise ValueError(f"Invalid lower price: {lower_price}")
        
        # Validate price range
        if upper_price <= lower_price:
            raise ValueError("Upper price must be higher than lower price")
        
        # Validate grid levels
        if grid_levels < 2 or grid_levels > 50:
            raise ValueError("Grid levels must be between 2 and 50")
        
        return symbol.upper(), side.upper(), float(quantity), float(upper_price), float(lower_price), int(grid_levels)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def calculate_grid_prices(upper_price, lower_price, grid_levels):
    """Calculate grid price levels"""
    try:
        price_range = upper_price - lower_price
        price_step = price_range / (grid_levels - 1)
        
        grid_prices = []
        for i in range(grid_levels):
            price = lower_price + (i * price_step)
            grid_prices.append(round(price, 2))
        
        logger.info(f"[GRID CALC] Generated {len(grid_prices)} price levels")
        logger.info(f"[GRID PRICES] {grid_prices}")
        
        return grid_prices
        
    except Exception as e:
        logger.error(f"[GRID PRICE CALCULATION ERROR] {e}")
        raise

def calculate_grid_quantities(total_quantity, grid_levels):
    """Calculate quantity per grid level"""
    try:
        quantity_per_level = total_quantity / grid_levels
        return round(quantity_per_level, 6)  # Round to 6 decimal places
        
    except Exception as e:
        logger.error(f"[GRID QUANTITY CALCULATION ERROR] {e}")
        raise

def place_grid_orders(symbol, side, total_quantity, upper_price, lower_price, grid_levels):
    """Execute grid trading strategy"""
    try:
        logger.info(f"[GRID STRATEGY] Starting grid trading for {side} {total_quantity} {symbol}")
        logger.info(f"[GRID PARAMS] Upper: {upper_price}, Lower: {lower_price}, Levels: {grid_levels}")
        
        # Calculate grid parameters
        grid_prices = calculate_grid_prices(upper_price, lower_price, grid_levels)
        quantity_per_level = calculate_grid_quantities(total_quantity, grid_levels)
        
        logger.info(f"[GRID CALC] Quantity per level: {quantity_per_level}")
        
        # Validate quantity per level
        if quantity_per_level <= 0:
            raise ValueError("Quantity per grid level is too small")
        
        orders = []
        
        print(f"🌐 Starting Grid Trading Strategy")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Total Quantity: {total_quantity}")
        print(f"   Price Range: {lower_price} - {upper_price}")
        print(f"   Grid Levels: {grid_levels}")
        print(f"   Quantity per Level: {quantity_per_level}")
        print(f"   Start Time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Place orders at each grid level
        for i, price in enumerate(grid_prices):
            try:
                logger.info(f"[GRID LEVEL {i+1}/{grid_levels}] Placing {side} {quantity_per_level} {symbol} @ {price}")
                
                # Place limit order at this grid level
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    timeInForce='GTC',
                    quantity=quantity_per_level,
                    price=price
                )
                
                orders.append({
                    'order': order,
                    'level': i + 1,
                    'price': price,
                    'quantity': quantity_per_level
                })
                
                logger.info(f"[GRID LEVEL SUCCESS] {i+1}/{grid_levels} - Order ID: {order.get('orderId')}")
                
                print(f"✅ Grid Level {i+1}/{grid_levels} placed")
                print(f"   Price: {price}")
                print(f"   Quantity: {quantity_per_level}")
                print(f"   Order ID: {order.get('orderId', 'N/A')}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except BinanceAPIException as e:
                logger.error(f"[GRID LEVEL API ERROR] {i+1}/{grid_levels}: {e}")
                print(f"❌ Grid Level {i+1}/{grid_levels} failed: {e}")
                continue
            except Exception as e:
                logger.error(f"[GRID LEVEL ERROR] {i+1}/{grid_levels}: {e}")
                print(f"❌ Grid Level {i+1}/{grid_levels} failed: {e}")
                continue
        
        # Calculate execution summary
        successful_orders = len(orders)
        total_placed_quantity = successful_orders * quantity_per_level
        placement_ratio = (successful_orders / grid_levels) * 100
        
        logger.info(f"[GRID COMPLETE] Placed {successful_orders}/{grid_levels} orders ({placement_ratio:.2f}%)")
        
        print()
        print(f"📊 Grid Trading Summary")
        print(f"   Total Levels: {grid_levels}")
        print(f"   Successful Orders: {successful_orders}")
        print(f"   Placement Ratio: {placement_ratio:.2f}%")
        print(f"   Total Quantity Placed: {total_placed_quantity}")
        print(f"   Price Range: {grid_prices[0]} - {grid_prices[-1]}")
        
        return {
            'orders': orders,
            'grid_prices': grid_prices,
            'successful_orders': successful_orders,
            'total_levels': grid_levels,
            'placement_ratio': placement_ratio,
            'total_quantity': total_placed_quantity
        }
        
    except Exception as e:
        logger.error(f"[GRID STRATEGY ERROR] {e}")
        print(f"❌ Grid strategy failed: {e}")
        return None

def monitor_grid_orders(symbol, order_ids, duration_minutes=60):
    """Monitor grid orders and provide status updates"""
    try:
        logger.info(f"[GRID MONITOR] Starting monitoring for {len(order_ids)} orders")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        print(f"👀 Monitoring Grid Orders")
        print(f"   Symbol: {symbol}")
        print(f"   Orders: {len(order_ids)}")
        print(f"   Duration: {duration_minutes} minutes")
        print()
        
        while datetime.now() < end_time:
            filled_orders = 0
            pending_orders = 0
            
            for order_id in order_ids:
                try:
                    order = client.futures_get_order(symbol=symbol, orderId=order_id)
                    status = order.get('status', 'UNKNOWN')
                    
                    if status == 'FILLED':
                        filled_orders += 1
                    elif status in ['NEW', 'PARTIALLY_FILLED']:
                        pending_orders += 1
                        
                except BinanceAPIException as e:
                    logger.error(f"[GRID MONITOR ERROR] Order {order_id}: {e}")
                    continue
            
            print(f"📈 Status Update: {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Filled: {filled_orders}")
            print(f"   Pending: {pending_orders}")
            print(f"   Total: {len(order_ids)}")
            print()
            
            # Wait 30 seconds before next check
            time.sleep(30)
        
        logger.info(f"[GRID MONITOR] Monitoring completed")
        print(f"✅ Grid monitoring completed")
        
    except Exception as e:
        logger.error(f"[GRID MONITOR ERROR] {e}")
        print(f"❌ Grid monitoring failed: {e}")

def cancel_grid_orders(symbol, order_ids):
    """Cancel all grid orders"""
    try:
        logger.info(f"[GRID CANCEL] Attempting to cancel {len(order_ids)} grid orders")
        
        cancelled_orders = []
        for order_id in order_ids:
            try:
                result = client.futures_cancel_order(symbol=symbol, orderId=order_id)
                cancelled_orders.append(result)
                logger.info(f"[GRID CANCEL SUCCESS] Order {order_id} cancelled")
            except BinanceAPIException as e:
                logger.error(f"[GRID CANCEL FAILED] Order {order_id}: {e}")
        
        if cancelled_orders:
            print(f"✅ {len(cancelled_orders)} grid orders cancelled successfully")
        else:
            print("❌ No grid orders were cancelled")
        
        return cancelled_orders
        
    except Exception as e:
        logger.error(f"[GRID CANCEL ERROR] {e}")
        print(f"❌ Error cancelling grid orders: {e}")
        return None

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Execute grid trading strategy on Binance Futures')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Place grid orders command
    place_parser = subparsers.add_parser('place', help='Place grid orders')
    place_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    place_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    place_parser.add_argument('quantity', type=float, help='Total order quantity')
    place_parser.add_argument('upper_price', type=float, help='Upper price limit')
    place_parser.add_argument('lower_price', type=float, help='Lower price limit')
    place_parser.add_argument('levels', type=int, help='Number of grid levels')
    
    # Monitor grid orders command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor grid orders')
    monitor_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    monitor_parser.add_argument('order_ids', nargs='+', help='Order IDs to monitor')
    monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in minutes')
    
    # Cancel grid orders command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel grid orders')
    cancel_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    cancel_parser.add_argument('order_ids', nargs='+', help='Order IDs to cancel')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'place':
            symbol, side, quantity, upper_price, lower_price, levels = validate_grid_args(
                args.symbol, args.side, args.quantity, args.upper_price, args.lower_price, args.levels
            )
            result = place_grid_orders(symbol, side, quantity, upper_price, lower_price, levels)
            
            if result:
                print(f"✅ Grid strategy completed successfully!")
            else:
                print(f"❌ Grid strategy failed!")
                sys.exit(1)
                
        elif args.command == 'monitor':
            monitor_grid_orders(args.symbol, args.order_ids, args.duration)
            
        elif args.command == 'cancel':
            cancel_grid_orders(args.symbol, args.order_ids)
            
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
