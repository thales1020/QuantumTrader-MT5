#!/usr/bin/env python3
"""
Backtest All Symbols
Format output to match SMC-style reporting while using the non-SMC ICT bot/engine
Author: xPOURY4 (adapted)
"""

import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 module not found.")
    print("Please install it using: pip install MetaTrader5")
    sys.exit(1)

from core.ict_bot import ICTBot, Config
from engines.ict_backtest_engine import ICTBacktestEngine


def load_config():
    """Load configuration from config.json"""
    config_path = Path('config/config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def connect_mt5(account_config):
    """Connect to MT5 account"""
    if not mt5.initialize():
        print("MT5 initialization failed")
        return False

    if not mt5.login(
        account_config['login'],
        password=account_config['password'],
        server=account_config['server']
    ):
        print(f"Login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False

    return True


def run_symbol_backtest(symbol_name, symbol_config, backtest_config):
    """Run backtest for a single symbol following run_ict_bot.py structure"""
    print("\n" + "="*70)
    print(f"BACKTESTING: {symbol_name}")
    print("="*70)

    # Map timeframe
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }

    timeframe = timeframe_map.get(symbol_config["timeframe"], mt5.TIMEFRAME_M15)

    # Determine date range (same as run_ict_bot.py)
    if backtest_config.get("use_date_range", False):
        start_date = datetime.strptime(backtest_config.get("start_date", "2025-01-01"), "%Y-%m-%d")
        end_date = datetime.strptime(backtest_config.get("end_date", "2025-10-01"), "%Y-%m-%d")
    else:
        end_date = datetime.now()
        period_days = backtest_config.get("period_days", 30)
        start_date = end_date - timedelta(days=period_days)

    print(f"Symbol: {symbol_name}")
    print(f"Timeframe: {symbol_config['timeframe']}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Initial Balance: ${backtest_config.get('initial_balance', 10000):,.2f}")
    print(f"Risk per Trade: {symbol_config.get('risk_percent', 1.0)}%")
    print(f"RR Ratio: {symbol_config.get('tp_multiplier', 2.0)}/{symbol_config.get('sl_multiplier', 1.0)}")
    print()

    # Create bot config
    bot_config = Config(
        symbol=symbol_name,
        timeframe=timeframe,
        risk_percent=symbol_config.get("risk_percent", 1.0),
        lookback_candles=20,
        fvg_min_size=0.0005,
        liquidity_sweep_pips=5.0,
        rr_ratio=symbol_config.get("tp_multiplier", 2.0) / symbol_config.get("sl_multiplier", 1.0),
        max_positions=1,
        magic_number=123457,
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True
    )

    # Create bot instance
    bot = ICTBot(bot_config)

    # Create backtest engine
    initial_balance = backtest_config.get("initial_balance", 10000)
    engine = ICTBacktestEngine(bot, initial_balance=initial_balance)

    # Run backtest
    start_time = time.time()

    result = engine.run_backtest(
        symbol=symbol_name,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe
    )

    elapsed_time = time.time() - start_time

    if result:
        print()
        print("="*70)
        print(f"RESULTS: {symbol_name}")
        print("="*70)
        print(f"Execution Time: {elapsed_time:.2f}s ({elapsed_time/60:.2f} min)")
        print(f"Total Trades: {result.get('total_trades', 0)}")
        print(f"Winning Trades: {result.get('winning_trades', 0)}")
        print(f"Losing Trades: {result.get('losing_trades', 0)}")
        print(f"Win Rate: {result.get('win_rate', 0):.2f}%")
        print(f"Profit Factor: {result.get('profit_factor', 0):.2f}")
        print(f"Total Return: {result.get('total_return', 0):.2f}%")
        print(f"Max Drawdown: {result.get('max_drawdown', 0):.2f}%")
        print(f"Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
        print()
        # SMC-like metrics (placeholders)
        print("SMC METRICS:")
        print(f"Average Signal Quality: {result.get('avg_signal_quality', 0):.1f}%")
        print(f"High Quality (\u226570%) WR: {result.get('high_quality_wr', 0):.1f}%")
        print(f"SMC Signals WR: {result.get('smc_signals_wr', 0):.1f}%")
        print()
        print(f"Initial Balance: ${result.get('initial_balance', 0):,.2f}")
        print(f"Final Balance: ${result.get('final_balance', 0):,.2f}")

        # Calculate P&L
        initial = result.get('initial_balance', 0)
        final = result.get('final_balance', 0)
        total_pnl = final - initial
        print(f"Total P&L: ${total_pnl:,.2f}")

        # Add to result for summary
        result['total_pnl'] = total_pnl
        result['execution_time'] = elapsed_time
        result['symbol'] = symbol_name
        result['timeframe'] = symbol_config['timeframe']
    else:
        print(f"\u274c Backtest failed for {symbol_name}")

    return result


def main():
    print("="*70)
    print("BACKTEST ALL SYMBOLS")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load config
    config_data = load_config()

    # Get account config
    account_name = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if account_name not in config_data['accounts']:
        print(f"Error: Account '{account_name}' not found in config")
        sys.exit(1)

    account_config = config_data['accounts'][account_name]
    backtest_config = config_data.get('backtest', {})

    # Connect to MT5
    print(f"Connecting to {account_config['server']}...")
    if not connect_mt5(account_config):
        sys.exit(1)

    account_info = mt5.account_info()
    print(f" Connected successfully")
    print(f"  Account: {account_info.login}")
    print(f"  Balance: {account_info.balance} {account_info.currency}")
    print()

    # Get enabled symbols
    symbols_config = config_data.get('symbols', {})
    enabled_symbols = {
        name: cfg for name, cfg in symbols_config.items()
        if cfg.get('enabled', False)
    }

    if not enabled_symbols:
        print("No enabled symbols found in config")
        mt5.shutdown()
        sys.exit(1)

    print(f"Found {len(enabled_symbols)} enabled symbols:")
    for symbol in enabled_symbols.keys():
        print(f"  - {symbol}")
    print()

    # Run backtests
    results = []
    failed_symbols = []

    total_start_time = time.time()

    for i, (symbol_name, symbol_config) in enumerate(enabled_symbols.items(), 1):
        print(f"\n[{i}/{len(enabled_symbols)}] Processing {symbol_name}...")

        try:
            result = run_symbol_backtest(
                symbol_name,
                symbol_config,
                backtest_config
            )

            if result:
                results.append(result)
            else:
                failed_symbols.append(symbol_name)

        except Exception as e:
            print(f"\u274c Error backtesting {symbol_name}: {e}")
            failed_symbols.append(symbol_name)
            import traceback
            traceback.print_exc()

    total_elapsed = time.time() - total_start_time

    # Summary
    print("\n" + "="*70)
    print("SUMMARY - ALL SYMBOLS")
    print("="*70)
    print(f"Total Execution Time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} min)")
    print(f"Symbols Tested: {len(enabled_symbols)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(failed_symbols)}")

    if failed_symbols:
        print(f"\nFailed symbols: {', '.join(failed_symbols)}")

    if results:
        print("\n" + "-"*70)
        print("PERFORMANCE COMPARISON")
        print("-"*70)
        print(f"{'Symbol':<12} {'TF':<5} {'Trades':<7} {'Win%':<7} {'PF':<7} {'Return%':<9} {'Profit$':<10} {'DD%':<7} {'Quality':<8} {'Time(s)':<8}")
        print("-"*70)

        # Sort by return
        results_sorted = sorted(results, key=lambda x: x.get('total_return', 0), reverse=True)

        for r in results_sorted:
            symbol = r.get('symbol', 'N/A')
            tf = r.get('timeframe', 'N/A')
            trades = r.get('total_trades', 0)
            win_rate = r.get('win_rate', 0)
            pf = r.get('profit_factor', 0)
            ret = r.get('total_return', 0)
            profit = r.get('total_pnl', 0)
            dd = abs(r.get('max_drawdown', 0))  # Absolute value for better readability
            quality = r.get('avg_signal_quality', 0)
            exec_time = r.get('execution_time', 0)

            print(f"{symbol:<12} {tf:<5} {trades:<7} {win_rate:<7.2f} {pf:<7.2f} {ret:<9.2f} ${profit:<9.2f} {dd:<7.2f} {quality:<8.1f} {exec_time:<8.2f}")

        # Best performers
        print("\n" + "="*70)
        print("TOP PERFORMERS")
        print("="*70)

        best_return = max(results_sorted, key=lambda x: x.get('total_return', 0))
        best_pf = max(results_sorted, key=lambda x: x.get('profit_factor', 0))
        best_wr = max(results_sorted, key=lambda x: x.get('win_rate', 0))
        best_quality = max(results_sorted, key=lambda x: x.get('avg_signal_quality', 0))

        print(f"Best Return: {best_return['symbol']} ({best_return.get('total_return', 0):.2f}%)")
        print(f"Best Profit Factor: {best_pf['symbol']} ({best_pf.get('profit_factor', 0):.2f})")
        print(f"Best Win Rate: {best_wr['symbol']} ({best_wr.get('win_rate', 0):.2f}%)")
        print(f"Best Signal Quality: {best_quality['symbol']} ({best_quality.get('avg_signal_quality', 0):.1f}%)")

        # SMC-like Stats Summary (aggregated placeholders)
        print("\n" + "="*70)
        print("SMC LIBRARY STATISTICS")
        print("="*70)

        total_trades_all = sum(r.get('total_trades', 0) for r in results)
        avg_quality_all = sum(r.get('avg_signal_quality', 0) * r.get('total_trades', 0) for r in results) / total_trades_all if total_trades_all > 0 else 0

        print(f"Total Trades Across All Symbols: {total_trades_all}")
        print(f"Average Signal Quality: {avg_quality_all:.1f}%")

        # Quality breakdown
        high_q_trades = sum(r.get('quality_buckets', {}).get('high', 0) for r in results)
        med_q_trades = sum(r.get('quality_buckets', {}).get('medium', 0) for r in results)
        low_q_trades = sum(r.get('quality_buckets', {}).get('low', 0) for r in results)

        if total_trades_all > 0:
            print(f"\nQuality Distribution:")
            print(f"  High (\u226570%): {high_q_trades} ({high_q_trades/total_trades_all*100:.1f}%)")
            print(f"  Medium (50-69%): {med_q_trades} ({med_q_trades/total_trades_all*100:.1f}%)")
            print(f"  Low (<50%): {low_q_trades} ({low_q_trades/total_trades_all*100:.1f}%)")

    mt5.shutdown()

    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    main()
