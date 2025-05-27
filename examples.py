"""
ML-SuperTrend-MT5 Usage Examples
Educational examples for different trading scenarios
"""

import MetaTrader5 as mt5
from supertrend_bot import SuperTrendBot, Config
from performance_monitor import PerformanceMonitor
from risk_manager import RiskManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example 1: Basic bot setup and run"""
    print("=== Example 1: Basic Usage ===")
    
    # Create configuration
    config = Config(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_M30,
        risk_percent=1.0
    )
    
    # Initialize bot
    bot = SuperTrendBot(config)
    
    # Connect to MT5
    if bot.connect(login=12345678, password="demo_password", server="MetaQuotes-Demo"):
        # Run for 5 cycles
        for i in range(5):
            logger.info(f"Running cycle {i+1}/5")
            bot.run_cycle()
            time.sleep(30)
        
        bot.shutdown()


def example_multi_symbol():
    """Example 2: Trading multiple symbols"""
    print("\n=== Example 2: Multi-Symbol Trading ===")
    
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    bots = []
    
    # Create bot for each symbol
    for symbol in symbols:
        config = Config(
            symbol=symbol,
            timeframe=mt5.TIMEFRAME_H1,
            risk_percent=0.5,  # Lower risk for multiple positions
            cluster_choice="Average"
        )
        
        bot = SuperTrendBot(config)
        if bot.connect(login=12345678, password="demo_password", server="MetaQuotes-Demo"):
            bots.append(bot)
            logger.info(f"Bot initialized for {symbol}")
    
    # Run all bots
    import threading
    threads = []
    
    for bot in bots:
        thread = threading.Thread(target=bot.run, args=(60,))  # 60 second intervals
        thread.start()
        threads.append(thread)
    
    # Wait for all threads
    for thread in threads:
        thread.join()


def example_conservative_strategy():
    """Example 3: Conservative trading approach"""
    print("\n=== Example 3: Conservative Strategy ===")
    
    config = Config(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_H4,  # Higher timeframe
        risk_percent=0.5,            # Lower risk
        cluster_choice="Worst",      # Most conservative cluster
        sl_multiplier=3.0,           # Wider stop loss
        tp_multiplier=2.0,           # Closer take profit
        volume_multiplier=1.5        # Higher volume threshold
    )
    
    bot = SuperTrendBot(config)
    logger.info("Running conservative strategy...")
    # bot.run()


def example_aggressive_strategy():
    """Example 4: Aggressive trading approach"""
    print("\n=== Example 4: Aggressive Strategy ===")
    
    config = Config(
        symbol="GBPUSD",
        timeframe=mt5.TIMEFRAME_M15,  # Lower timeframe
        risk_percent=2.0,             # Higher risk
        cluster_choice="Best",        # Most aggressive cluster
        sl_multiplier=1.5,            # Tighter stop loss
        tp_multiplier=4.0,            # Further take profit
        volume_multiplier=1.0         # Lower volume threshold
    )
    
    bot = SuperTrendBot(config)
    logger.info("Running aggressive strategy...")
    # bot.run()


def example_custom_risk_management():
    """Example 5: Custom risk management"""
    print("\n=== Example 5: Custom Risk Management ===")
    
    # Initialize risk manager
    risk_manager = RiskManager(
        max_daily_loss_percent=3.0,
        max_correlation=0.7
    )
    
    # Check if we can trade
    account_balance = 10000
    if risk_manager.check_daily_loss_limit(account_balance):
        logger.info("Daily loss limit OK, can trade")
    else:
        logger.info("Daily loss limit reached, stopping trading")
    
    # Calculate position size using Kelly Criterion
    win_rate = 55  # 55% win rate
    avg_win = 50   # Average win in pips
    avg_loss = 30  # Average loss in pips
    
    kelly_percent = risk_manager.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    logger.info(f"Recommended risk per trade: {kelly_percent*100:.2f}%")


def example_performance_analysis():
    """Example 6: Performance monitoring and analysis"""
    print("\n=== Example 6: Performance Analysis ===")
    
    # Create sample trade history
    sample_trades = [
        {"symbol": "EURUSD", "profit": 45.50, "entry_time": "2024-01-01 10:00:00", 
         "exit_time": "2024-01-01 14:30:00", "volume": 0.1},
        {"symbol": "EURUSD", "profit": -22.30, "entry_time": "2024-01-02 09:15:00", 
         "exit_time": "2024-01-02 11:45:00", "volume": 0.1},
        {"symbol": "GBPUSD", "profit": 67.80, "entry_time": "2024-01-03 13:00:00", 
         "exit_time": "2024-01-03 16:20:00", "volume": 0.15},
    ]
    
    # Save to file
    import json
    with open('trades.json', 'w') as f:
        json.dump(sample_trades, f)
    
    # Generate report
    monitor = PerformanceMonitor('trades.json')
    monitor.generate_report(days=30)


def example_news_filter():
    """Example 7: Trading with news filter"""
    print("\n=== Example 7: News Filter Example ===")
    
    from news_filter import NewsFilter
    
    # Initialize news filter
    news_filter = NewsFilter()
    
    # Check if it's safe to trade
    symbol = "EURUSD"
    if news_filter.is_news_time(symbol):
        logger.info(f"High impact news event near, avoiding trades on {symbol}")
    else:
        logger.info(f"No major news events, safe to trade {symbol}")


def example_backtest():
    """Example 8: Running a backtest"""
    print("\n=== Example 8: Backtest Example ===")
    
    from datetime import datetime, timedelta
    from backtest_engine import BacktestEngine
    
    # Define backtest parameters
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    # Create strategy configuration
    config = Config(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_H1,
        risk_percent=1.0
    )
    
    # Run backtest
    logger.info(f"Running backtest from {start_date} to {end_date}")
    # backtest = BacktestEngine(strategy=bot.strategy, initial_balance=10000)
    # results = backtest.run_backtest("EURUSD", start_date, end_date, mt5.TIMEFRAME_H1)


def example_optimization():
    """Example 9: Parameter optimization"""
    print("\n=== Example 9: Parameter Optimization ===")
    
    # Define parameter ranges
    param_ranges = {
        'atr_period': [10, 14, 20],
        'sl_multiplier': [1.5, 2.0, 2.5],
        'tp_multiplier': [2.0, 3.0, 4.0],
        'volume_multiplier': [1.0, 1.2, 1.5]
    }
    
    best_params = None
    best_profit_factor = 0
    
    # Grid search (simplified)
    for atr in param_ranges['atr_period']:
        for sl in param_ranges['sl_multiplier']:
            for tp in param_ranges['tp_multiplier']:
                for vol in param_ranges['volume_multiplier']:
                    # Run backtest with these parameters
                    # Calculate profit factor
                    # Update best if better
                    pass
    
    logger.info(f"Best parameters found: {best_params}")


def example_live_monitoring():
    """Example 10: Live monitoring dashboard"""
    print("\n=== Example 10: Live Monitoring ===")
    
    import time
    from datetime import datetime
    
    def monitor_bot_status(bot):
        """Monitor bot status in real-time"""
        while True:
            stats = bot.calculate_statistics()
            positions = mt5.positions_get()
            
            # Clear screen (Windows)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"=== ML-SuperTrend Bot Status ===")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Symbol: {bot.config.symbol}")
            print(f"Timeframe: {bot.config.timeframe}")
            print(f"\n--- Performance ---")
            print(f"Total Trades: {stats['total_trades']}")
            print(f"Win Rate: {stats['win_rate']:.2f}%")
            print(f"Profit Factor: {stats['profit_factor']:.2f}")
            print(f"\n--- Current Positions ---")
            print(f"Open Positions: {len(positions) if positions else 0}")
            
            time.sleep(5)  # Update every 5 seconds


if __name__ == "__main__":
    print("ML-SuperTrend-MT5 Examples")
    print("=" * 50)
    print("\nAvailable examples:")
    print("1. Basic Usage")
    print("2. Multi-Symbol Trading")
    print("3. Conservative Strategy")
    print("4. Aggressive Strategy")
    print("5. Custom Risk Management")
    print("6. Performance Analysis")
    print("7. News Filter")
    print("8. Backtest")
    print("9. Parameter Optimization")
    print("10. Live Monitoring")
    
    choice = input("\nSelect example (1-10): ")
    
    examples = {
        '1': example_basic_usage,
        '2': example_multi_symbol,
        '3': example_conservative_strategy,
        '4': example_aggressive_strategy,
        '5': example_custom_risk_management,
        '6': example_performance_analysis,
        '7': example_news_filter,
        '8': example_backtest,
        '9': example_optimization,
        '10': example_live_monitoring
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice!")