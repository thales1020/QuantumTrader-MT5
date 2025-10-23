#!/usr/bin/env python3
"""
ICT Trading Bot Runner
Inner Circle Trader Strategy
Author: xPOURY4
"""

import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 module not found.")
    print("Please install it using: pip install MetaTrader5")
    sys.exit(1)

from core.ict_bot import ICTBot, ICTConfig


def setup_logging(log_level="INFO", backtest_mode=False):
    """Setup logging configuration"""
    # Different format for backtest (no system timestamp, bar timestamp is in message)
    if backtest_mode:
        log_format = "%(message)s"  # Only show message (bar timestamp already in message)
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(f"logs/ict_bot_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_file="config/config.json"):
    """Load configuration from JSON file"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ICT Trading Bot for MetaTrader 5",
        epilog="Inner Circle Trader Strategy"
    )
    
    parser.add_argument(
        "--account",
        default="demo",
        choices=["demo", "live"],
        help="Account type to use (default: demo)"
    )
    
    parser.add_argument(
        "--symbol",
        default="EURUSD",
        help="Trading symbol (default: EURUSD)"
    )
    
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Update interval in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run backtest instead of live trading"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    return parser.parse_args()


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║               ICT Trading Bot - MT5                       ║
    ║          Inner Circle Trader Strategy                     ║
    ║                                                           ║
    ║  Order Blocks | Fair Value Gaps | Liquidity Sweeps       ║
    ║                                                           ║
    ║  Author: xPOURY4                                          ║
    ║  GitHub: https://github.com/xPOURY4/ML-SuperTrend-MT5     ║
    ║                                                           ║
    ║ ⚠️  EDUCATIONAL PURPOSES ONLY - TRADE AT YOUR OWN RISK    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main function"""
    print_banner()
    
    # Parse arguments
    args = parse_arguments()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
    # Setup logging (different format for backtest mode)
    logger = setup_logging(args.log_level, backtest_mode=args.backtest)
    logger.info("Starting ICT Trading Bot...")
    
    # Load configuration
    try:
        config_data = load_config(args.config)
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Get account credentials
    account_config = config_data["accounts"].get(args.account)
    if not account_config:
        logger.error(f"Account '{args.account}' not found in configuration")
        sys.exit(1)
    
    # Get symbol configuration
    symbol_config = config_data["symbols"].get(args.symbol)
    if not symbol_config or not symbol_config.get("enabled", True):
        logger.error(f"Symbol '{args.symbol}' not found or disabled in configuration")
        sys.exit(1)
    
    # Connect to MT5
    logger.info(f"Connecting to MT5 {args.account} account...")
    
    if not mt5.initialize():
        logger.error("MT5 initialization failed")
        sys.exit(1)
    
    if not mt5.login(account_config["login"], password=account_config["password"], server=account_config["server"]):
        logger.error(f"Login failed: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)
    
    account_info = mt5.account_info()
    logger.info(f"Connected successfully!")
    logger.info(f"Account: {account_info.login}")
    logger.info(f"Balance: {account_info.balance} {account_info.currency}")
    logger.info(f"Leverage: 1:{account_info.leverage}")
    
    # Check if backtest mode
    if args.backtest:
        from datetime import timedelta
        from engines.ict_backtest_engine import ICTBacktestEngine
        
        # Get backtest config
        backtest_config = config_data.get("backtest", {})
        global_settings = config_data.get("global_settings", {})
        
        # Determine date range
        if backtest_config.get("use_date_range", False):
            start_date = datetime.strptime(backtest_config.get("start_date", "2024-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(backtest_config.get("end_date", "2024-12-31"), "%Y-%m-%d")
        else:
            end_date = datetime.now()
            period_days = backtest_config.get("period_days", 30)
            start_date = end_date - timedelta(days=period_days)
        
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
        
        logger.info("="*60)
        logger.info("ICT BACKTEST CONFIGURATION")
        logger.info("="*60)
        logger.info(f"Symbol: {args.symbol}")
        logger.info(f"Timeframe: {symbol_config['timeframe']}")
        logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Initial Balance: ${backtest_config.get('initial_balance', 10000):,.2f}")
        logger.info(f"Risk per Trade: {symbol_config.get('risk_percent', 1.0)}%")
        logger.info(f"RR Ratio: {symbol_config.get('tp_multiplier', 2.0)}/{symbol_config.get('sl_multiplier', 1.0)}")
        logger.info("ICT Components: Order Blocks + FVG + Liquidity Sweeps + Market Structure")
        logger.info("="*60)
        
        # Create bot instance for backtest
        bot_config = ICTConfig(
            symbol=args.symbol,
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
        
        bot = ICTBot(bot_config)
        
        # Create backtest engine
        initial_balance = backtest_config.get("initial_balance", 10000)
        backtest = ICTBacktestEngine(bot, initial_balance=initial_balance)
        
        # Run backtest
        results = backtest.run_backtest(args.symbol, start_date, end_date, timeframe)
        
        # Save results if enabled
        if results and backtest_config.get("save_trades_csv", True):
            import pandas as pd
            
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Save trades to CSV
            trades_df = pd.DataFrame(results['trades'])
            trades_file = reports_dir / f"ict_backtest_{args.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            trades_df.to_csv(trades_file, index=False)
            logger.info(f"Trades saved to: {trades_file}")
            
            # Save equity curve if enabled
            if backtest_config.get("save_equity_curve", True):
                equity_df = pd.DataFrame(results['equity_curve'])
                equity_file = reports_dir / f"ict_equity_{args.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                equity_df.to_csv(equity_file, index=False)
                logger.info(f"Equity curve saved to: {equity_file}")
        
        mt5.shutdown()
        sys.exit(0)
    
    # Create bot configuration for live trading
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    
    bot_config = ICTConfig(
        symbol=args.symbol,
        timeframe=timeframe_map.get(symbol_config["timeframe"], mt5.TIMEFRAME_M15),
        risk_percent=symbol_config.get("risk_percent", 1.0),
        lookback_candles=20,
        fvg_min_size=0.0005,
        liquidity_sweep_pips=5.0,
        rr_ratio=symbol_config.get("tp_multiplier", 2.0) / symbol_config.get("sl_multiplier", 1.0),
        max_positions=config_data["global_settings"].get("max_positions_per_symbol", 1),
        magic_number=123457,
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True
    )
    
    # Create and initialize bot
    bot = ICTBot(bot_config)
    bot.is_connected = True
    
    try:
        logger.info(f"Starting ICT bot for {args.symbol} on {symbol_config['timeframe']} timeframe")
        logger.info(f"Update interval: {args.interval} seconds")
        logger.info("Strategy: Order Blocks + FVG + Liquidity Sweeps + Market Structure")
        logger.info("Press Ctrl+C to stop...")
        
        bot.run(interval_seconds=args.interval)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        mt5.shutdown()
        logger.info("MT5 connection closed")
    
    logger.info("ICT Bot shutdown complete")


if __name__ == "__main__":
    main()
