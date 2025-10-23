#!/usr/bin/env python3
"""
Backtest All Symbols with SuperTrend Bot
Compare SuperTrend performance across multiple symbols
Author: xPOURY4
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

from core.supertrend_bot import SuperTrendBot, Config
from engines.backtest_engine import BacktestEngine


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
    """Run backtest for a single symbol with SuperTrend bot"""
    print("\n" + "="*70)
    print(f"BACKTESTING SUPERTREND: {symbol_name}")
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
    
    # Determine date range
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
    print(f"RR Ratio: {symbol_config.get('tp_multiplier', 3.0)}/{symbol_config.get('sl_multiplier', 2.0)}")
    print()
    
    # Create bot config
    bot_config = Config(
        symbol=symbol_name,
        timeframe=timeframe,
        risk_percent=symbol_config.get("risk_percent", 1.0),
        atr_period=10,
        min_factor=1.0,
        max_factor=5.0,
        factor_step=0.5,
        perf_alpha=10.0,
        cluster_choice=symbol_config.get("cluster_choice", "Best"),
        volume_ma_period=20,
        volume_multiplier=symbol_config.get("volume_multiplier", 1.2),
        sl_multiplier=symbol_config.get("sl_multiplier", 2.0),
        tp_multiplier=symbol_config.get("tp_multiplier", 3.0),
        use_trailing=symbol_config.get("use_trailing", True),
        trail_activation=1.5,
        max_positions=1,
        magic_number=123456
    )
    
    # Create bot and backtest engine
    bot = SuperTrendBot(bot_config)
    engine = BacktestEngine(
        bot=bot,
        initial_balance=backtest_config.get('initial_balance', 10000)
    )
    
    # Run backtest
    start_time = time.time()
    
    try:
        result = engine.run_backtest(
            symbol=symbol_name,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
        
        execution_time = time.time() - start_time
        
        if result is None:
            print(f"❌ Backtest failed for {symbol_name}")
            return None
        
        # Calculate additional metrics
        initial_balance = result['initial_balance']
        final_balance = result['final_balance']
        total_pnl = final_balance - initial_balance
        total_return = (total_pnl / initial_balance) * 100 if initial_balance > 0 else 0
        
        # Print results
        print("\n" + "-"*70)
        print("BACKTEST RESULTS")
        print("-"*70)
        print(f"Total Trades: {result['total_trades']}")
        print(f"Win Rate: {result['win_rate']:.2f}%")
        print(f"Profit Factor: {result['profit_factor']:.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Total P&L: ${total_pnl:.2f}")
        print(f"Max Drawdown: {abs(result['max_drawdown']):.2f}%")
        print(f"Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
        print(f"Initial Balance: ${initial_balance:,.2f}")
        print(f"Final Balance: ${final_balance:,.2f}")
        print(f"Execution Time: {execution_time:.2f}s")
        print("-"*70)
        
        # Add metadata and calculated fields
        result['symbol'] = symbol_name
        result['timeframe'] = symbol_config['timeframe']
        result['execution_time'] = execution_time
        result['total_pnl'] = total_pnl
        result['total_return'] = total_return
        
        return result
        
    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python backtest_all_symbols_supertrend.py <account_type>")
        print("Example: python backtest_all_symbols_supertrend.py demo")
        sys.exit(1)
    
    account_type = sys.argv[1]
    
    # Load configuration
    try:
        full_config = load_config()
    except FileNotFoundError:
        print("Error: config/config.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json: {e}")
        sys.exit(1)
    
    if account_type not in full_config['accounts']:
        print(f"Error: Account type '{account_type}' not found in config")
        print(f"Available accounts: {list(full_config['accounts'].keys())}")
        sys.exit(1)
    
    account_config = full_config['accounts'][account_type]
    backtest_config = full_config.get('backtest', {})
    symbols_config = full_config.get('symbols', {})
    
    # Connect to MT5
    print("="*70)
    print("SUPERTREND BOT - MULTI-SYMBOL BACKTEST")
    print("="*70)
    print(f"Account: {account_type}")
    print(f"Server: {account_config['server']}")
    print()
    
    if not connect_mt5(account_config):
        sys.exit(1)
    
    print(f"✓ Connected to MT5: {account_config['server']}")
    print()
    
    # Filter enabled symbols
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
            print(f"❌ Error backtesting {symbol_name}: {e}")
            failed_symbols.append(symbol_name)
            import traceback
            traceback.print_exc()
    
    total_elapsed = time.time() - total_start_time
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - ALL SYMBOLS (SUPERTREND BOT)")
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
        print(f"{'Symbol':<12} {'TF':<5} {'Trades':<7} {'Win%':<7} {'PF':<7} {'Return%':<9} {'Profit$':<10} {'DD%':<7} {'Sharpe':<8} {'Time(s)':<8}")
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
            sharpe = r.get('sharpe_ratio', 0)
            exec_time = r.get('execution_time', 0)
            
            print(f"{symbol:<12} {tf:<5} {trades:<7} {win_rate:<7.2f} {pf:<7.2f} {ret:<9.2f} ${profit:<9.2f} {dd:<7.2f} {sharpe:<8.2f} {exec_time:<8.2f}")
        
        # Best performers
        print("\n" + "="*70)
        print("TOP PERFORMERS (SUPERTREND BOT)")
        print("="*70)
        
        best_return = max(results_sorted, key=lambda x: x.get('total_return', 0))
        best_pf = max(results_sorted, key=lambda x: x.get('profit_factor', 0))
        best_wr = max(results_sorted, key=lambda x: x.get('win_rate', 0))
        best_sharpe = max(results_sorted, key=lambda x: x.get('sharpe_ratio', 0))
        
        print(f"Best Return: {best_return['symbol']} ({best_return.get('total_return', 0):.2f}%)")
        print(f"Best Profit Factor: {best_pf['symbol']} ({best_pf.get('profit_factor', 0):.2f})")
        print(f"Best Win Rate: {best_wr['symbol']} ({best_wr.get('win_rate', 0):.2f}%)")
        print(f"Best Sharpe Ratio: {best_sharpe['symbol']} ({best_sharpe.get('sharpe_ratio', 0):.2f})")
        
        # Aggregate statistics
        print("\n" + "="*70)
        print("AGGREGATE STATISTICS")
        print("="*70)
        
        total_trades_all = sum(r.get('total_trades', 0) for r in results)
        avg_win_rate = sum(r.get('win_rate', 0) * r.get('total_trades', 0) for r in results) / total_trades_all if total_trades_all > 0 else 0
        avg_pf = sum(r.get('profit_factor', 0) for r in results) / len(results) if results else 0
        total_profit = sum(r.get('total_pnl', 0) for r in results)
        avg_return = sum(r.get('total_return', 0) for r in results) / len(results) if results else 0
        
        print(f"Total Trades Across All Symbols: {total_trades_all}")
        print(f"Average Win Rate: {avg_win_rate:.2f}%")
        print(f"Average Profit Factor: {avg_pf:.2f}")
        print(f"Total Profit: ${total_profit:,.2f}")
        print(f"Average Return: {avg_return:.2f}%")
        
        # Performance distribution
        profitable = sum(1 for r in results if r.get('total_return', 0) > 0)
        unprofitable = len(results) - profitable
        
        print(f"\nPerformance Distribution:")
        print(f"  Profitable Symbols: {profitable} ({profitable/len(results)*100:.1f}%)")
        print(f"  Unprofitable Symbols: {unprofitable} ({unprofitable/len(results)*100:.1f}%)")
    
    mt5.shutdown()
    
    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    main()
