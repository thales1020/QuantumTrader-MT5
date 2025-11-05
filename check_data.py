import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

# Check last 30 days
end = datetime.now()
start = end - timedelta(days=30)

rates = mt5.copy_rates_range('EURUSDm', mt5.TIMEFRAME_H1, start, end)

if rates is not None and len(rates) > 0:
    print(f"✅ Data available: {len(rates)} bars")
    print(f"   From: {datetime.fromtimestamp(rates[0][0])}")
    print(f"   To:   {datetime.fromtimestamp(rates[-1][0])}")
    
    # Check 2024 data
    start_2024 = datetime(2024, 1, 1)
    end_2024 = datetime(2024, 12, 31)
    rates_2024 = mt5.copy_rates_range('EURUSDm', mt5.TIMEFRAME_H1, start_2024, end_2024)
    count_2024 = len(rates_2024) if rates_2024 is not None else 0
    print(f"\n2024 data: {count_2024} bars")
    
    # Check 2025 data
    start_2025 = datetime(2025, 1, 1)
    end_2025 = datetime.now()
    rates_2025 = mt5.copy_rates_range('EURUSDm', mt5.TIMEFRAME_H1, start_2025, end_2025)
    count_2025 = len(rates_2025) if rates_2025 is not None else 0
    print(f"2025 data: {count_2025} bars")
else:
    print("❌ No data available")

mt5.shutdown()
