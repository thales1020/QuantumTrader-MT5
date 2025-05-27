# 🚀 Quick Start Guide

Get up and running with ML-SuperTrend-MT5 in 5 minutes!

## Prerequisites Checklist

- [ ] Windows OS (MT5 Python API requirement)
- [ ] Python 3.8 or higher installed
- [ ] MetaTrader 5 terminal installed
- [ ] Demo account credentials from your broker

## Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
cd ML-SuperTrend-MT5

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (2 minutes)

1. Copy the example configuration:
```bash
copy config\config.example.json config\config.json
```

2. Edit `config\config.json` with your MT5 credentials:
```json
{
    "accounts": {
        "demo": {
            "login": YOUR_DEMO_LOGIN,
            "password": "YOUR_DEMO_PASSWORD",
            "server": "YOUR_BROKER_SERVER"
        }
    }
}
```

## Step 3: Run the Bot (1 minute)

### Basic Run
```bash
python run_bot.py
```

### With Options
```bash
# Run on specific symbol
python run_bot.py --symbol GBPUSD

# Run in dry mode (no real trades)
python run_bot.py --dry-run

# Run with performance monitoring
python run_bot.py --monitor

# Run with debug logging
python run_bot.py --log-level DEBUG
```

## Common Broker Servers

| Broker | Demo Server Name |
|--------|------------------|
| IC Markets | ICMarketsSC-Demo |
| XM | XMGlobal-Demo 3 |
| Pepperstone | Pepperstone-Demo |
| FXCM | FXCM-USDDemo01 |
| Admiral Markets | AdmiralMarkets-Demo |

## First Time Setup Tips

1. **Enable Algo Trading in MT5**:
   - Tools → Options → Expert Advisors
   - Check "Allow automated trading"

2. **Start with Conservative Settings**:
   ```json
   {
       "risk_percent": 0.5,
       "cluster_choice": "Average"
   }
   ```

3. **Test Connection First**:
   ```python
   import MetaTrader5 as mt5
   mt5.initialize()
   print(mt5.version())
   ```

## Troubleshooting

### "MT5 initialization failed"
- Make sure MT5 terminal is running
- Check if it's the correct architecture (32/64 bit)

### "Login failed"
- Verify credentials in config.json
- Check server name is exact (case-sensitive)
- Ensure account is not expired

### "No module named 'MetaTrader5'"
```bash
pip uninstall MetaTrader5
pip install MetaTrader5 --no-cache-dir
```

## Next Steps

1. 📊 Monitor your first trades in demo
2. 📈 Check performance reports in `reports/` folder
3. 🔧 Fine-tune parameters based on results
4. 📚 Read the full documentation

## Need Help?

- 📖 Full Documentation: [README.md](README.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/xPOURY4/ML-SuperTrend-MT5/issues)
- 🐦 Twitter: [@TheRealPourya](https://twitter.com/TheRealPourya)

---

**Remember**: Always test thoroughly on demo before going live! 🎯