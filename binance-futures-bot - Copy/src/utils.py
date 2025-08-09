import logging
import re
from typing import Union

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic symbol validation (e.g., BTCUSDT, ETHUSDT)
    symbol_pattern = r'^[A-Z0-9]{2,20}$'
    return bool(re.match(symbol_pattern, symbol.upper()))

def validate_quantity(quantity: Union[str, float, int]) -> bool:
    """Validate order quantity"""
    try:
        qty = float(quantity)
        return qty > 0
    except (ValueError, TypeError):
        return False

def validate_price(price: Union[str, float, int]) -> bool:
    """Validate order price"""
    try:
        price_val = float(price)
        return price_val > 0
    except (ValueError, TypeError):
        return False

def validate_percentage(percentage: Union[str, float, int]) -> bool:
    """Validate percentage value (0-100)"""
    try:
        pct = float(percentage)
        return 0 <= pct <= 100
    except (ValueError, TypeError):
        return False

def format_quantity(quantity: float, symbol: str = None) -> float:
    """Format quantity to appropriate decimal places"""
    # For most crypto pairs, 6 decimal places is sufficient
    return round(quantity, 6)

def format_price(price: float, symbol: str = None) -> float:
    """Format price to appropriate decimal places"""
    # For most crypto pairs, 2 decimal places is sufficient
    return round(price, 2)

def calculate_position_size(account_balance: float, risk_percentage: float, entry_price: float, stop_loss_price: float) -> float:
    """Calculate position size based on risk management"""
    try:
        risk_amount = account_balance * (risk_percentage / 100)
        price_difference = abs(entry_price - stop_loss_price)
        
        if price_difference == 0:
            return 0
        
        position_size = risk_amount / price_difference
        return format_quantity(position_size)
    except Exception as e:
        logger.error(f"[POSITION SIZE CALCULATION ERROR] {e}")
        return 0

def log_trade_summary(symbol: str, side: str, quantity: float, price: float, order_id: str = None):
    """Log a comprehensive trade summary"""
    logger.info(f"[TRADE SUMMARY] {side} {quantity} {symbol} @ {price}")
    if order_id:
        logger.info(f"[ORDER ID] {order_id}")
    
    # Calculate estimated value
    estimated_value = quantity * price
    logger.info(f"[ESTIMATED VALUE] ${estimated_value:.2f}")

def validate_time_in_force(time_in_force: str) -> bool:
    """Validate time in force parameter"""
    valid_options = ['GTC', 'IOC', 'FOK']
    return time_in_force.upper() in valid_options

def validate_order_type(order_type: str) -> bool:
    """Validate order type"""
    valid_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
    return order_type.upper() in valid_types
