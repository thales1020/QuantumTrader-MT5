#!/usr/bin/env python3
"""
ML-SuperTrend-MT5 Bot Runner
Main entry point for the trading bot
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

from supertrend_bot import SuperTrendBot, Config
from performance_monitor import PerformanceMonitor


def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_file="config/config.json"):
    """Load configuration from JSON file"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        print(f"Error: Configuration file '{config_file}' not found.")
        print("Please copy config.example.json to config.json and update with your settings.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ML-SuperTrend Trading Bot for MetaTrader 5",
        epilog="For more information, visit: https://github.com/xPOURY4/ML-SuperTrend-MT5"
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
        help="Configuration file path (default: config/config.json)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Update interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode without placing real trades"
    )
    
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run backtest instead of live trading"
    )
    
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Show performance monitor after running"
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
    ║            ML-SuperTrend MT5 Trading Bot                  ║
    ║                                                           ║
    ║  Author: xPOURY4                                          ║
    ║  GitHub: https://github.com/xPOURY4/ML-SuperTrend-MT5    ║
    ║  Twitter: @TheRealPourya                                  ║
    ║                                                           ║
    ║  ⚠️  EDUCATIONAL PURPOSES ONLY - TRADE AT YOUR OWN RISK   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_mt5_connection(login, password, server):
    """Validate MT5 connection"""
    if not mt5.initialize():
        return False, "Failed to initialize MT5"
    
    if not mt5.login(login, password=password, server=server):
        error = mt5.last_error()
        mt5.shutdown()
        return False, f"Login failed: {error}"
    
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        return False, "Failed to get account info"
    
    return True, account_info


def main():
    """Main function"""
    print_banner()
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting ML-SuperTrend Bot...")
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
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
    
    # Validate MT5 connection
    logger.info(f"Connecting to MT5 {args.account} account...")
    success, result = validate_mt5_connection(
        account_config["login"],
        account_config["password"],
        account_config["server"]
    )
    
    if not success:
        logger.error(result)
        sys.exit(1)
    
    account_info = result
    logger.info(f"Connected successfully!")
    logger.info(f"Account: {account_info.login}")
    logger.info(f"Balance: {account_info.balance} {account_info.currency}")
    logger.info(f"Leverage: 1:{account_info.leverage}")
    
    # Create bot configuration
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    
    bot_config = Config(
        symbol=args.symbol,
        timeframe=timeframe_map.get(symbol_config["timeframe"], mt5.TIMEFRAME_M30),
        atr_period=config_data["global_settings"]["atr_period"],
        min_factor=symbol_config["min_factor"],
        max_factor=symbol_config["max_factor"],
        factor_step=symbol_config["factor_step"],
        perf_alpha=config_data["global_settings"]["performance_alpha"],
        cluster_choice=symbol_config["cluster_choice"],
        volume_ma_period=config_data["global_settings"]["volume_ma_period"],
        volume_multiplier=symbol_config["volume_multiplier"],
        sl_multiplier=symbol_config["sl_multiplier"],
        tp_multiplier=symbol_config["tp_multiplier"],
        use_trailing=config_data["global_settings"]["use_trailing_stop"],
        trail_activation=config_data["global_settings"]["trail_activation_atr"],
        risk_percent=symbol_config["risk_percent"],
        max_positions=config_data["global_settings"]["max_positions_per_symbol"]
    )
    
    # Create and initialize bot
    bot = SuperTrendBot(bot_config)
    bot.is_connected = True  # Already connected above
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no real trades will be placed")
        bot.dry_run = True
    
    try:
        # Run bot
        logger.info(f"Starting bot for {args.symbol} on {symbol_config['timeframe']} timeframe")
        logger.info(f"Update interval: {args.interval} seconds")
        logger.info("Press Ctrl+C to stop...")
        
        bot.run(interval_seconds=args.interval)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Cleanup
        mt5.shutdown()
        logger.info("MT5 connection closed")
        
        # Show performance report if requested
        if args.monitor:
            logger.info("Generating performance report...")
            monitor = PerformanceMonitor()
            monitor.generate_report(days=30)
    
    logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()