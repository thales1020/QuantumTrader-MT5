"""
Quick Backtest: Deployed Bots
Test ICTBot and SuperTrendBot with historical data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Import deployed versions
from core.ict_bot import ICTBot, ICTConfig
from core.supertrend_bot import SuperTrendBot, SuperTrendConfig
from engines.ict_backtest_engine import ICTBacktestEngine
from engines.backtest_engine import BacktestEngine

print("="*80)
print("📊 BACKTEST: Deployed Bots")
print("="*80)
print()

# Connect to MT5
print("📡 Connecting to MT5...")
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    sys.exit(1)

print("✅ Connected to MT5")
print()

# Backtest parameters
symbol = "AUDUSDm"
timeframe = mt5.TIMEFRAME_H1
start_date = datetime(2025, 9, 1)
end_date = datetime(2025, 10, 23)
initial_balance = 10000.0

print(f"📋 Backtest Configuration:")
print(f"   Symbol: {symbol}")
print(f"   Timeframe: H1")
print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"   Initial Balance: ${initial_balance:,.2f}")
print()

# =============================================================================
# BACKTEST 1: ICTBot
# =============================================================================

print("="*80)
print("BACKTEST 1: ICTBot (Order Blocks + FVG + Market Structure)")
print("="*80)

try:
    # Create ICTBot config
    ict_config = ICTConfig(
        symbol=symbol,
        timeframe=timeframe,
        risk_percent=1.0,
        lookback_candles=20,
        fvg_min_size=0.0005,
        liquidity_sweep_pips=5.0,
        rr_ratio=2.0,
        max_positions=1,
        magic_number=123457,
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True
    )
    
    # Create bot
    ict_bot = ICTBot(ict_config)
    
    # Create backtest engine
    ict_backtest = ICTBacktestEngine(ict_bot, initial_balance=initial_balance)
    
    print("\n🔄 Running ICTBot backtest...")
    print(f"⏱️  This may take a few minutes...")
    print()
    
    # Run backtest
    results = ict_backtest.run_backtest(symbol, start_date, end_date, timeframe)
    
    if results:
        print("\n" + "="*80)
        print("📈 ICTBot BACKTEST RESULTS")
        print("="*80)
        
        print(f"\n💰 Financial Summary:")
        print(f"   Initial Balance:  ${results['initial_balance']:,.2f}")
        print(f"   Final Balance:    ${results['final_balance']:,.2f}")
        print(f"   Total P/L:        ${results['total_profit']:,.2f}")
        print(f"   Return:           {results['return_pct']:.2f}%")
        
        print(f"\n📊 Trade Statistics:")
        print(f"   Total Trades:     {results['total_trades']}")
        print(f"   Winning Trades:   {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"   Losing Trades:    {results['losing_trades']}")
        print(f"   Average Win:      ${results['avg_win']:.2f}")
        print(f"   Average Loss:     ${results['avg_loss']:.2f}")
        print(f"   Profit Factor:    {results['profit_factor']:.2f}")
        
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown:     ${results['max_drawdown']:.2f} ({results['max_drawdown_pct']:.2f}%)")
        print(f"   Sharpe Ratio:     {results.get('sharpe_ratio', 0):.2f}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if results.get('trades'):
            df_trades = pd.DataFrame(results['trades'])
            trades_file = f"reports/ict_backtest_{symbol}_{timestamp}.csv"
            df_trades.to_csv(trades_file, index=False)
            print(f"\n💾 Trades saved to: {trades_file}")
        
        if results.get('equity_curve'):
            df_equity = pd.DataFrame(results['equity_curve'])
            equity_file = f"reports/ict_equity_{symbol}_{timestamp}.csv"
            df_equity.to_csv(equity_file, index=False)
            print(f"💾 Equity curve saved to: {equity_file}")
        
        print("\n✅ ICTBot Backtest Complete")
    else:
        print("\n⚠️  No trades generated during backtest period")
        
except Exception as e:
    print(f"\n❌ ICTBot Backtest Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# BACKTEST 2: SuperTrendBot
# =============================================================================

print("="*80)
print("BACKTEST 2: SuperTrendBot (ML-Optimized Multi-Factor)")
print("="*80)

try:
    # Create SuperTrendBot config
    st_config = SuperTrendConfig(
        symbol=symbol,
        timeframe=timeframe,
        risk_percent=1.0,
        rr_ratio=2.0,  # Risk/reward ratio (BaseConfig parameter)
        max_positions=1,
        # SuperTrend parameters
        atr_period=10,
        min_factor=1.0,
        max_factor=3.0,
        factor_step=0.5,
        # ML optimization
        perf_alpha=10.0,
        cluster_choice='Best',
        # Volume filter
        volume_ma_period=20,
        volume_multiplier=1.2,
        # Trailing stop
        use_trailing=True,
        trail_activation=1.5
    )
    
    # Create bot
    st_bot = SuperTrendBot(st_config)
    
    # Create backtest engine
    st_backtest = BacktestEngine(st_bot, initial_balance=initial_balance)
    
    print("\n🔄 Running SuperTrendBot backtest...")
    print(f"⏱️  This may take a few minutes...")
    print()
    
    # Run backtest
    results = st_backtest.run_backtest(symbol, start_date, end_date, timeframe)
    
    if results:
        print("\n" + "="*80)
        print("📈 SuperTrendBot BACKTEST RESULTS")
        print("="*80)
        
        print(f"\n💰 Financial Summary:")
        print(f"   Initial Balance:  ${results['initial_balance']:,.2f}")
        print(f"   Final Balance:    ${results['final_balance']:,.2f}")
        print(f"   Total P/L:        ${results['total_profit']:,.2f}")
        print(f"   Return:           {results['return_pct']:.2f}%")
        
        print(f"\n📊 Trade Statistics:")
        print(f"   Total Trades:     {results['total_trades']}")
        print(f"   Winning Trades:   {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"   Losing Trades:    {results['losing_trades']}")
        print(f"   Average Win:      ${results['avg_win']:.2f}")
        print(f"   Average Loss:     ${results['avg_loss']:.2f}")
        print(f"   Profit Factor:    {results['profit_factor']:.2f}")
        
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown:     ${results['max_drawdown']:.2f} ({results['max_drawdown_pct']:.2f}%)")
        print(f"   Sharpe Ratio:     {results.get('sharpe_ratio', 0):.2f}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if results.get('trades'):
            df_trades = pd.DataFrame(results['trades'])
            trades_file = f"reports/supertrend_backtest_{symbol}_{timestamp}.csv"
            df_trades.to_csv(trades_file, index=False)
            print(f"\n💾 Trades saved to: {trades_file}")
        
        if results.get('equity_curve'):
            df_equity = pd.DataFrame(results['equity_curve'])
            equity_file = f"reports/supertrend_equity_{symbol}_{timestamp}.csv"
            df_equity.to_csv(equity_file, index=False)
            print(f"💾 Equity curve saved to: {equity_file}")
        
        print("\n✅ SuperTrendBot Backtest Complete")
    else:
        print("\n⚠️  No trades generated during backtest period")
        
except Exception as e:
    print(f"\n❌ SuperTrendBot Backtest Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# COMPARISON
# =============================================================================

print("="*80)
print("📊 BACKTEST COMPARISON SUMMARY")
print("="*80)
print()
print("Both bots tested on same period with same risk parameters")
print(f"Symbol: {symbol}, Timeframe: H1")
print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Initial Balance: ${initial_balance:,.2f}")
print()
print("Review individual results above for detailed comparison")
print()

# Cleanup
mt5.shutdown()
print("✅ MT5 connection closed")
print()
print("="*80)
print("🎉 BACKTEST COMPLETE")
print("="*80)
