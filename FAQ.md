# ❓ Frequently Asked Questions (FAQ)

## General Questions

### Q: What is ML-SuperTrend-MT5?
**A:** ML-SuperTrend-MT5 is an advanced trading bot that uses Machine Learning (K-means clustering) to optimize the traditional SuperTrend indicator parameters dynamically. It's designed for MetaTrader 5 and written in Python.

### Q: Is this bot profitable?
**A:** Past performance is not indicative of future results. The bot shows positive results in backtesting (55-60% win rate on M30 timeframe), but real trading involves risks. Always test thoroughly on demo accounts first.

### Q: Can I use this for real money trading?
**A:** While the bot is functional, it's published for EDUCATIONAL PURPOSES. If you choose to use it with real money, you do so at your own risk. We recommend extensive testing on demo accounts first.

### Q: What markets does it support?
**A:** The bot works with any instrument available in MT5:
- Forex pairs (EUR/USD, GBP/USD, etc.)
- Indices (US500, DAX, etc.)
- Commodities (Gold, Oil, etc.)
- Cryptocurrencies (if your broker offers them)

## Technical Questions

### Q: Why does it only work on Windows?
**A:** The MetaTrader5 Python API is only available for Windows. This is a limitation from MetaQuotes, not our bot.

### Q: Can I run multiple instances?
**A:** Yes! You can run multiple instances for different symbols or accounts. Each instance should have a unique `magic_number` in the configuration.

### Q: How much RAM/CPU does it need?
**A:** Minimal requirements:
- RAM: 2GB (4GB recommended)
- CPU: Any modern processor
- Disk: 100MB for the bot + logs

### Q: Can I modify the strategy?
**A:** Absolutely! The code is open source. Feel free to modify, improve, and share your enhancements with the community.

## Installation Issues

### Q: "ModuleNotFoundError: No module named 'talib'"
**A:** TA-Lib requires special installation:
```bash
# Download the .whl file for your Python version from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.24‑cp39‑cp39‑win_amd64.whl
```

### Q: "MT5 initialization failed"
**A:** Common solutions:
1. Ensure MT5 terminal is running
2. Enable "Algo Trading" in MT5 settings
3. Check if you're using the correct MT5 version (32/64 bit)
4. Run Python as Administrator

### Q: "Login failed"
**A:** Check:
1. Credentials are correct (case-sensitive)
2. Server name is exact (get from broker)
3. Account is not expired
4. Internet connection is stable

## Configuration Questions

### Q: What's the best timeframe?
**A:** Based on our testing:
- **M30**: Best balance (55-60% win rate)
- **H1**: Higher win rate (58-63%) but fewer signals
- **M15**: More signals but lower win rate (52-57%)

### Q: What's the optimal risk percentage?
**A:** Depends on your risk tolerance:
- **Conservative**: 0.5-1%
- **Moderate**: 1-2%
- **Aggressive**: 2-3%
- Never risk more than you can afford to lose!

### Q: Should I use "Best", "Average", or "Worst" cluster?
**A:** 
- **Best**: Most aggressive, highest potential returns and risks
- **Average**: Balanced approach (recommended for beginners)
- **Worst**: Most conservative, lower drawdown but fewer profits

## Performance Questions

### Q: Why am I getting different results than shown?
**A:** Results vary due to:
- Broker differences (spread, commission)
- Market conditions
- Execution timing
- Slippage
- Your specific configuration

### Q: How can I improve performance?
**A:** Tips:
1. Trade during high liquidity sessions
2. Avoid major news events
3. Use appropriate position sizing
4. Monitor and adjust parameters regularly
5. Consider multiple timeframe analysis

### Q: What's the expected drawdown?
**A:** Historical maximum drawdowns:
- M30: 10-15%
- H1: 8-12%
- H4: 5-10%

## Trading Questions

### Q: Can I use it 24/7?
**A:** Yes, but consider:
- Some sessions have better performance
- Weekend gaps can cause issues
- News events affect performance
- Monitor regularly even if automated

### Q: How many trades per day?
**A:** Depends on timeframe and market:
- M15: 2-5 trades/day
- M30: 1-3 trades/day
- H1: 3-5 trades/week
- H4: 1-2 trades/week

### Q: Can I trade multiple pairs?
**A:** Yes! But remember:
- Reduce risk per trade
- Watch correlation between pairs
- Monitor total exposure
- Ensure sufficient margin

## Troubleshooting

### Q: Bot stops after a few hours
**A:** Common causes:
1. Connection timeout - check internet stability
2. Memory leak - restart periodically
3. MT5 disconnection - check terminal
4. Check logs for specific errors

### Q: No trades being placed
**A:** Check:
1. Market is open
2. Sufficient margin
3. Volume filter settings
4. Spread is normal
5. No existing positions at max limit

### Q: Getting slippage
**A:** Solutions:
1. Increase `deviation` parameter
2. Trade during high liquidity
3. Use VPS closer to broker
4. Avoid news times

## Advanced Questions

### Q: Can I add my own indicators?
**A:** Yes! Add them in the `calculate_supertrends()` method. The clustering algorithm will adapt to any performance metric you provide.

### Q: How does the ML clustering work?
**A:** The bot:
1. Tests multiple ATR multipliers
2. Measures performance of each
3. Groups them into 3 clusters using K-means
4. Selects optimal parameters from chosen cluster

### Q: Can I change from 3 clusters?
**A:** Yes, modify the K-means initialization, but 3 clusters (Best/Average/Worst) provides good intuitive control.

## Support

### Q: Where can I get help?
**A:** 
- GitHub Issues: [Report bugs or request features](https://github.com/xPOURY4/ML-SuperTrend-MT5/issues)
- Twitter: [@TheRealPourya](https://twitter.com/TheRealPourya)
- Read the documentation thoroughly

### Q: Can I contribute?
**A:** Yes! We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Q: Is there a Discord/Telegram group?
**A:** Not officially, but the community may create one. Check GitHub discussions.

---

**Remember**: Trading involves substantial risk. Never trade with money you cannot afford to lose. This software is provided as-is for educational purposes.