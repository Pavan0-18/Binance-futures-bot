# Binance Futures Order Bot

A comprehensive CLI-based trading bot for Binance USDT-M Futures that supports multiple order types with robust logging, validation, and documentation.

## 🚀 Features

### Core Orders (Mandatory)
- ✅ **Market Orders** - Immediate execution at current market price
- ✅ **Limit Orders** - Execution at specified price with time-in-force options

### Advanced Orders (Bonus - Higher Priority)
- ✅ **Stop-Limit Orders** - Trigger limit orders when stop price is hit
- ✅ **OCO (One-Cancels-the-Other)** - Place take-profit and stop-loss simultaneously
- ✅ **TWAP (Time-Weighted Average Price)** - Split large orders into smaller chunks over time
- ✅ **Grid Orders** - Automated buy-low/sell-high within a price range

### Validation & Logging
- ✅ **Comprehensive Input Validation** - Symbol, quantity, price thresholds
- ✅ **Structured Logging** - All actions logged with timestamps and error traces
- ✅ **Error Handling** - Robust error handling with detailed error messages

## 📁 Project Structure

```
binance-futures-bot/
├── src/
│   ├── config.py              # Configuration and API client setup
│   ├── utils.py               # Validation functions and logging
│   ├── market_orders.py       # Market order implementation
│   ├── limit_orders.py        # Limit order implementation
│   └── advanced/              # Advanced order strategies
│       ├── stop_limit.py      # Stop-limit orders
│       ├── oco.py            # OCO (One-Cancels-the-Other) orders
│       ├── twap.py           # TWAP strategy
│       └── grid.py           # Grid trading strategy
├── bot.log                   # Structured log file
├── env_template.txt          # Environment variables template
└── README.md                # This file
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install python-binance python-dotenv
```

### 2. Create API Credentials

1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create a new API key
3. **Enable "Futures Trading" permissions**
4. **Add your IP address to the whitelist**

### 3. Configure Environment

1. Copy `env_template.txt` to `.env`:
   ```bash
   cp env_template.txt .env
   ```

2. Edit `.env` with your actual credentials:
   ```
   API_KEY=your_actual_api_key_here
   API_SECRET=your_actual_api_secret_here
   ```

### 4. Test Setup

```bash
python -c "from src.config import client; print('✅ API connection successful')"
```

## 📖 Usage

### Market Orders

```bash
# Place a market buy order
python src/market_orders.py BTCUSDT BUY 0.001

# Place a market sell order
python src/market_orders.py ETHUSDT SELL 0.01
```

### Limit Orders

```bash
# Place a limit buy order
python src/limit_orders.py place BTCUSDT BUY 0.001 45000

# Place a limit sell order with custom time-in-force
python src/limit_orders.py place ETHUSDT SELL 0.01 3000 --time-in-force IOC

# List open orders
python src/limit_orders.py list

# Cancel a specific order
python src/limit_orders.py cancel BTCUSDT 123456789
```

### Stop-Limit Orders

```bash
# Place a stop-limit buy order (stop: 44000, limit: 44500)
python src/advanced/stop_limit.py stop-limit BTCUSDT BUY 0.001 44000 44500

# Place a stop-market sell order
python src/advanced/stop_limit.py stop-market ETHUSDT SELL 0.01 3200
```

### OCO (One-Cancels-the-Other) Orders

```bash
# Place an OCO order (limit: 46000, stop: 44000, stop-limit: 43500)
python src/advanced/oco.py place BTCUSDT SELL 0.001 46000 44000 43500

# Check OCO order status
python src/advanced/oco.py status BTCUSDT 123456789 123456790

# Cancel OCO orders
python src/advanced/oco.py cancel BTCUSDT 123456789 123456790
```

### TWAP (Time-Weighted Average Price) Strategy

```bash
# Execute TWAP strategy (1 BTC over 60 minutes in 10 chunks)
python src/advanced/twap.py BTCUSDT BUY 1.0 60 10

# Execute TWAP with price limit
python src/advanced/twap.py ETHUSDT SELL 10.0 30 5 --price-limit 3000
```

### Grid Trading Strategy

```bash
# Place grid orders (price range: 44000-46000, 10 levels)
python src/advanced/grid.py place BTCUSDT BUY 0.1 46000 44000 10

# Monitor grid orders
python src/advanced/grid.py monitor BTCUSDT 123456789 123456790 --duration 120

# Cancel grid orders
python src/advanced/grid.py cancel BTCUSDT 123456789 123456790
```

## 🔧 Configuration

### API Settings

Edit `src/config.py` to configure:

```python
USE_BINANCE_API = True    # Set to True for real API, False for mock
USE_TESTNET = True        # Set to True for testnet, False for live trading
```

### Logging

Logs are automatically saved to `bot.log` with:
- Timestamps
- Log levels (INFO, ERROR, WARNING)
- Structured message format
- API calls and responses
- Error traces

## 🛡️ Safety Features

- **Input Validation** - All parameters validated before API calls
- **Error Handling** - Comprehensive error handling with detailed messages
- **Rate Limiting** - Built-in delays to respect API rate limits
- **Testnet Support** - Safe testing environment available
- **Mock Mode** - Offline testing without real API calls

## 📊 Logging Examples

```
2024-01-15 10:30:15,123 - INFO - [MARKET ORDER] Attempting to place BUY 0.001 BTCUSDT
2024-01-15 10:30:15,456 - INFO - [MARKET ORDER SUCCESS] BUY 0.001 BTCUSDT
2024-01-15 10:30:15,789 - INFO - [ORDER DETAILS] {'orderId': 123456789, 'status': 'FILLED'}
```

## ⚠️ Important Notes

- **Testnet First** - Always test with testnet before live trading
- **Small Amounts** - Start with small quantities for testing
- **API Permissions** - Ensure your API key has futures trading permissions
- **IP Whitelist** - Add your IP to the API key whitelist
- **Risk Management** - Implement proper risk management strategies

## 🐛 Troubleshooting

### Common Issues

1. **API Error -2015**: Invalid API key, IP, or permissions
   - Check API credentials in `.env`
   - Verify IP is whitelisted
   - Ensure futures trading permissions are enabled

2. **Import Errors**: Missing dependencies
   - Run `pip install python-binance python-dotenv`

3. **Validation Errors**: Invalid parameters
   - Check symbol format (e.g., BTCUSDT)
   - Verify quantity is positive
   - Ensure prices are valid

## 📈 Advanced Features

### Risk Management
- Position size calculation based on account balance
- Percentage-based risk management
- Stop-loss and take-profit automation

### Order Management
- Order status monitoring
- Bulk order cancellation
- Order history tracking

### Strategy Automation
- Grid trading with dynamic price levels
- TWAP execution with configurable intervals
- OCO order management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## ⚖️ Disclaimer

This bot is for educational and demonstration purposes only. Trading cryptocurrencies involves significant risk. Always:
- Test thoroughly before live trading
- Start with small amounts
- Implement proper risk management
- Never invest more than you can afford to lose

---

**Built with ❤️ for the Binance Futures Trading Community**
