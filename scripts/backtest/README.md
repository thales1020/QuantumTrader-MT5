#  Backtest Scripts

Scripts để chạy backtest cho các chiến lược khác nhau.

## Files

- **backtest_all_symbols.py** - Backtest tất cả symbols
- **backtest_all_symbols_supertrend.py** - Backtest SuperTrend strategy

## Usage

```bash
# Backtest all symbols
python scripts/backtest/backtest_all_symbols.py

# Backtest SuperTrend strategy
python scripts/backtest/backtest_all_symbols_supertrend.py
```

## Output

Results saved to `reports/` folder:
- CSV files với trade history
- JSON files với summary statistics
- Equity curves
