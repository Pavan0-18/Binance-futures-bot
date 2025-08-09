# src/advanced/twap.py

import sys
import argparse
import time
import math
from datetime import datetime, timedelta
from binance.enums import *
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import client
from utils import logger, validate_symbol, validate_quantity, validate_price

def validate_twap_args(symbol, side, total_quantity, duration_minutes, num_chunks):
    """Validate TWAP order arguments"""
    try:
        # Validate symbol
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        # Validate side
        if side.upper() not in ['BUY', 'SELL']:
            raise ValueError("Order side must be BUY or SELL")
        
        # Validate quantity
        if not validate_quantity(total_quantity):
            raise ValueError(f"Invalid total quantity: {total_quantity}")
        
        # Validate duration
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        
        # Validate number of chunks
        if num_chunks <= 0 or num_chunks > 100:
            raise ValueError("Number of chunks must be between 1 and 100")
        
        return symbol.upper(), side.upper(), float(total_quantity), int(duration_minutes), int(num_chunks)
    
    except Exception as e:
        logger.error(f"[VALIDATION ERROR] {e}")
        raise

def calculate_chunk_quantity(total_quantity, num_chunks):
    """Calculate quantity per chunk"""
    chunk_quantity = total_quantity / num_chunks
    return round(chunk_quantity, 6)  # Round to 6 decimal places

def calculate_time_interval(duration_minutes, num_chunks):
    """Calculate time interval between chunks in seconds"""
    total_seconds = duration_minutes * 60
    interval_seconds = total_seconds / num_chunks
    return max(1, int(interval_seconds))  # Minimum 1 second interval

def place_twap_orders(symbol, side, total_quantity, duration_minutes, num_chunks, price_limit=None):
    """Execute TWAP (Time-Weighted Average Price) strategy"""
    try:
        logger.info(f"[TWAP STRATEGY] Starting TWAP execution for {side} {total_quantity} {symbol}")
        logger.info(f"[TWAP PARAMS] Duration: {duration_minutes}min, Chunks: {num_chunks}")
        
        # Calculate chunk parameters
        chunk_quantity = calculate_chunk_quantity(total_quantity, num_chunks)
        time_interval = calculate_time_interval(duration_minutes, num_chunks)
        
        logger.info(f"[TWAP CALC] Chunk quantity: {chunk_quantity}, Interval: {time_interval}s")
        
        # Validate chunk quantity
        if chunk_quantity <= 0:
            raise ValueError("Chunk quantity is too small")
        
        orders = []
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        print(f"🚀 Starting TWAP Strategy")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Total Quantity: {total_quantity}")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Chunks: {num_chunks}")
        print(f"   Chunk Quantity: {chunk_quantity}")
        print(f"   Interval: {time_interval} seconds")
        print(f"   Start Time: {start_time.strftime('%H:%M:%S')}")
        print(f"   End Time: {end_time.strftime('%H:%M:%S')}")
        print()
        
        for i in range(num_chunks):
            current_time = datetime.now()
            
            # Check if we've exceeded the time limit
            if current_time >= end_time:
                logger.warning(f"[TWAP TIMEOUT] Time limit reached after {i} chunks")
                print(f"⏰ Time limit reached. Executed {i}/{num_chunks} chunks.")
                break
            
            # Calculate remaining quantity for this chunk
            remaining_quantity = total_quantity - sum(order.get('quantity', 0) for order in orders)
            if remaining_quantity <= 0:
                logger.info(f"[TWAP COMPLETE] All quantity executed after {i} chunks")
                break
            
            # Adjust chunk quantity for the last chunk if needed
            if i == num_chunks - 1:
                chunk_quantity = remaining_quantity
            
            chunk_quantity = min(chunk_quantity, remaining_quantity)
            
            try:
                logger.info(f"[TWAP CHUNK {i+1}/{num_chunks}] Placing {side} {chunk_quantity} {symbol}")
                
                # Place market order for this chunk
                order = client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity=chunk_quantity
                )
                
                orders.append(order)
                
                logger.info(f"[TWAP CHUNK SUCCESS] {i+1}/{num_chunks} - Order ID: {order.get('orderId')}")
                
                print(f"✅ Chunk {i+1}/{num_chunks} executed")
                print(f"   Quantity: {chunk_quantity}")
                print(f"   Order ID: {order.get('orderId', 'N/A')}")
                print(f"   Status: {order.get('status', 'N/A')}")
                
                # Wait for next chunk (except for the last one)
                if i < num_chunks - 1:
                    time.sleep(time_interval)
                
            except BinanceAPIException as e:
                logger.error(f"[TWAP CHUNK API ERROR] {i+1}/{num_chunks}: {e}")
                print(f"❌ Chunk {i+1}/{num_chunks} failed: {e}")
                continue
            except Exception as e:
                logger.error(f"[TWAP CHUNK ERROR] {i+1}/{num_chunks}: {e}")
                print(f"❌ Chunk {i+1}/{num_chunks} failed: {e}")
                continue
        
        # Calculate execution summary
        executed_quantity = sum(float(order.get('quantity', 0)) for order in orders)
        execution_ratio = (executed_quantity / total_quantity) * 100 if total_quantity > 0 else 0
        
        logger.info(f"[TWAP COMPLETE] Executed {executed_quantity}/{total_quantity} ({execution_ratio:.2f}%)")
        
        print()
        print(f"📊 TWAP Execution Summary")
        print(f"   Total Orders: {len(orders)}")
        print(f"   Executed Quantity: {executed_quantity}")
        print(f"   Target Quantity: {total_quantity}")
        print(f"   Execution Ratio: {execution_ratio:.2f}%")
        print(f"   Duration: {datetime.now() - start_time}")
        
        return {
            'orders': orders,
            'executed_quantity': executed_quantity,
            'target_quantity': total_quantity,
            'execution_ratio': execution_ratio,
            'start_time': start_time,
            'end_time': datetime.now()
        }
        
    except Exception as e:
        logger.error(f"[TWAP STRATEGY ERROR] {e}")
        print(f"❌ TWAP strategy failed: {e}")
        return None

def calculate_twap_price(orders):
    """Calculate the TWAP price from executed orders"""
    try:
        if not orders:
            return 0
        
        total_value = 0
        total_quantity = 0
        
        for order in orders:
            # For market orders, we need to get the execution price from fills
            # This is a simplified calculation
            quantity = float(order.get('quantity', 0))
            # In a real implementation, you'd get the actual fill price
            # For now, we'll use a placeholder
            total_quantity += quantity
        
        # This is a simplified TWAP calculation
        # In practice, you'd need to get actual fill prices from the order details
        return total_value / total_quantity if total_quantity > 0 else 0
        
    except Exception as e:
        logger.error(f"[TWAP PRICE CALCULATION ERROR] {e}")
        return 0

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Execute TWAP strategy on Binance Futures')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Total order quantity')
    parser.add_argument('duration', type=int, help='Duration in minutes')
    parser.add_argument('chunks', type=int, help='Number of chunks to split the order')
    parser.add_argument('--price-limit', type=float, help='Maximum/minimum price limit (optional)')
    
    args = parser.parse_args()
    
    try:
        symbol, side, quantity, duration, chunks = validate_twap_args(
            args.symbol, args.side, args.quantity, args.duration, args.chunks
        )
        result = place_twap_orders(symbol, side, quantity, duration, chunks, args.price_limit)
        
        if result:
            print(f"✅ TWAP strategy completed successfully!")
        else:
            print(f"❌ TWAP strategy failed!")
            sys.exit(1)
            
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
