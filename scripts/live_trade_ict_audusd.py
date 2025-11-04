"""
Live Trading - AUDUSDm with ICT Bot
Order Blocks + Fair Value Gaps + Market Structure + Dual Orders

Follows QuantumTrader-MT5 architecture:
- Uses BaseTradingBot inheritance
- Dual Orders Strategy (RR 1:1 + Main RR)
- Breakeven SL management
- Proper logging and error handling
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure we're using the venv Python
venv_python = project_root / "venv" / "Scripts" / "python.exe"
if venv_python.exists() and sys.executable != str(venv_python):
    import subprocess
    print(f"Relaunching with venv Python: {venv_python}")
    result = subprocess.run([str(venv_python), __file__], cwd=project_root)
    sys.exit(result.returncode)

import MetaTrader5 as mt5
import time
from datetime import datetime
import logging
import os

from core.ict_bot import ICTBot, ICTConfig

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_audusd_ict.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LiveTrading-ICT')

print("="*80)
print("LIVE TRADING: AUDUSDm - ICT Bot")
print("Order Blocks + Fair Value Gaps + Market Structure")
print("="*80)
print()

# Connect to MT5
if not mt5.initialize():
    logger.error("MT5 initialization failed")
    sys.exit(1)

# Get account info
account_info = mt5.account_info()
if account_info is None:
    logger.error("Failed to get account info")
    mt5.shutdown()
    sys.exit(1)

print(f"Connected to MT5")
print(f"  Account: {account_info.login}")
print(f"  Balance: ${account_info.balance:,.2f}")
print(f"  Equity: ${account_info.equity:,.2f}")
print(f"  Broker: {account_info.company}")
print()

# ICT Bot Configuration
config = ICTConfig(
    symbol='AUDUSDm',
    timeframe=mt5.TIMEFRAME_H1,
    magic_number=234567,  # Different from SuperTrend
    
    # Risk management
    risk_percent=1.0,  # 1% per trade
    rr_ratio=2.0,  # 1:2 risk-reward
    
    # ICT parameters
    lookback_candles=20,
    fvg_min_size=0.0005,  # Minimum FVG size
    
    # Feature flags
    use_order_blocks=True,
    use_fvg=True,
    use_market_structure=True,
    
    # Breakeven management
    move_sl_to_breakeven=True  # From BaseConfig
)

print("Configuration:")
print(f"  Symbol: {config.symbol}")
print(f"  Timeframe: H1")
print(f"  Risk: {config.risk_percent}% per trade")
print(f"  RR Ratio: 1:{config.rr_ratio}")
print(f"  Order Blocks: {'Enabled' if config.use_order_blocks else 'Disabled'}")
print(f"  Fair Value Gaps: {'Enabled' if config.use_fvg else 'Disabled'}")
print(f"  Market Structure: {'Enabled' if config.use_market_structure else 'Disabled'}")
print(f"  Move SL to Breakeven: {'Enabled' if config.move_sl_to_breakeven else 'Disabled'}")
print()

# Initialize ICT Bot
bot = ICTBot(config)
logger.info("ICT Bot initialized and ready")

# Check symbol availability
symbol_info = mt5.symbol_info(config.symbol)
if symbol_info is None:
    logger.error(f"Symbol {config.symbol} not found")
    mt5.shutdown()
    sys.exit(1)

if not symbol_info.visible:
    if not mt5.symbol_select(config.symbol, True):
        logger.error(f"Failed to select {config.symbol}")
        mt5.shutdown()
        sys.exit(1)

print(f"Symbol {config.symbol} ready")
print(f"  Bid: {symbol_info.bid:.5f}")
print(f"  Ask: {symbol_info.ask:.5f}")
print(f"  Spread: {symbol_info.spread} points")
print()

print("="*80)
print("STARTING LIVE TRADING LOOP")
print("="*80)
print("Press Ctrl+C to stop")
print()

# Trading loop
iteration = 0
last_signal_check = None

try:
    while True:
        iteration += 1
        current_time = datetime.now()
        
        # Check every 5 minutes
        if last_signal_check is None or (current_time - last_signal_check).seconds >= 300:
            logger.info(f"Iteration {iteration} - Checking ICT patterns...")
            
            # Get latest market data
            rates = mt5.copy_rates_from_pos(config.symbol, config.timeframe, 0, 100)
            
            if rates is None or len(rates) == 0:
                logger.warning("No market data available, skipping...")
                time.sleep(60)
                continue
            
            import pandas as pd
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calculate indicators
            df = bot.calculate_indicators(df)
            
            # Log current market state
            current_price = df['close'].iloc[-1]
            logger.info(f"Market: {current_price:.5f}")
            
            # Detect patterns
            if hasattr(bot, 'order_blocks') and len(bot.order_blocks) > 0:
                logger.info(f"  Order Blocks: {len(bot.order_blocks)} detected")
            
            # Check for open positions
            positions = mt5.positions_get(symbol=config.symbol, magic=config.magic_number)
            
            if positions is None:
                positions = []
            
            logger.info(f"Open Positions: {len(positions)}")
            
            # If we have open positions, manage them
            if len(positions) > 0:
                for pos in positions:
                    profit = pos.profit
                    pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                    logger.info(f"  Position #{pos.ticket}: {pos_type} @ {pos.price_open:.5f}, P&L: ${profit:.2f}")
            
            # Generate new signal only if no open position
            if len(positions) == 0:
                signal = bot.generate_signal(df)
                
                if signal:
                    logger.info(f"ICT SIGNAL DETECTED!")
                    logger.info(f"  Type: {signal['type']}")
                    logger.info(f"  Price: {signal['price']:.5f}")
                    logger.info(f"  SL: {signal['stop_loss']:.5f}")
                    logger.info(f"  TP: {signal['take_profit']:.5f}")
                    logger.info(f"  Confidence: {signal['confidence']:.1f}%")
                    logger.info(f"  Reason: {signal['reason']}")
                    
                    # Execute trade
                    try:
                        result = bot.execute_trade(signal)
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info(f"Trade executed successfully! Order #{result.order}")
                        else:
                            error_msg = f"Retcode: {result.retcode}" if result else "No result"
                            logger.error(f"Trade failed: {error_msg}")
                    except Exception as e:
                        logger.error(f"Trade execution error: {e}")
                else:
                    logger.info(f"No ICT signal - waiting for setup...")
            
            last_signal_check = current_time
        
        # Show status every iteration
        if iteration % 12 == 0:  # Every hour (5min * 12 = 60min)
            account = mt5.account_info()
            if account:
                logger.info(f"Account Status: Balance=${account.balance:.2f}, Equity=${account.equity:.2f}")
        
        # Wait before next check
        time.sleep(60)  # Check every minute, but signal check every 5 min

except KeyboardInterrupt:
    print()
    print("="*80)
    print("STOPPING LIVE TRADING")
    print("="*80)
    logger.info("User requested stop")
    
    # Show final account state
    account = mt5.account_info()
    if account:
        print(f"Final Balance: ${account.balance:,.2f}")
        print(f"Final Equity: ${account.equity:,.2f}")
    
    # Show open positions
    positions = mt5.positions_get(symbol=config.symbol, magic=config.magic_number)
    if positions and len(positions) > 0:
        print(f"\nYou have {len(positions)} open position(s):")
        for pos in positions:
            pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
            print(f"  #{pos.ticket}: {pos_type} @ {pos.price_open:.5f}, P&L: ${pos.profit:.2f}")
    
    mt5.shutdown()
    print("\nMT5 connection closed")
    print("Goodbye!")

except Exception as e:
    logger.error(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    mt5.shutdown()
