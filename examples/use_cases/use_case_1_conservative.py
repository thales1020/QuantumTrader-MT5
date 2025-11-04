"""
Use Case 1: Conservative Trading Strategy

Scenario:
    A risk-averse trader who wants to trade only the highest probability setups.
    Multiple filters ensure only the best signals are executed.

Strategy:
    - SuperTrend bot as base strategy
    - RSI filter: Only trade extreme oversold/overbought
    - Volume filter: Require 2x average volume
    - Telegram notifications on trades only

Expected Behavior:
    - Fewer signals (10-20% of original)
    - Higher win rate (60-70%)
    - Lower drawdown
    - Peace of mind (only quality trades)

Configuration:
    - RSI: period=14, oversold=25, overbought=75 (stricter than default)
    - Volume: multiplier=2.0 (2x average)
    - Telegram: Only trade notifications (no signals)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dataclasses import dataclass, field
from typing import List
import logging

from core.supertrend_bot import SuperTrendBot
from core.base_bot import BaseConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConservativeConfig(BaseConfig):
    """Configuration for conservative trading"""
    
    # Symbol and timeframe
    symbol: str = 'EURUSD'
    timeframe: str = 'H1'
    magic_number: int = 100001
    
    # SuperTrend parameters (default)
    atr_period: int = 10
    atr_multiplier: float = 3.0
    
    # Risk management
    risk_percent: float = 1.0  # Conservative 1% per trade
    max_trades: int = 3
    
    # Plugin configuration
    plugins: List = field(default_factory=lambda: [
        {
            'name': 'RSIFilter',
            'enabled': True,
            'config': {
                'period': 14,
                'oversold': 25,      # Stricter: only extreme oversold
                'overbought': 75,    # Stricter: only extreme overbought
                'boost_confidence': True
            }
        },
        {
            'name': 'VolumeFilter',
            'enabled': True,
            'config': {
                'multiplier': 2.0,   # Require 2x average volume
                'period': 20,
                'boost_confidence': True
            }
        },
        {
            'name': 'TelegramNotifier',
            'enabled': True,
            'config': {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'chat_id': 'YOUR_CHAT_ID_HERE',
                'notify_on_signal': False,        # Don't notify on signals
                'notify_on_trade_open': True,     # Notify when trade opens
                'notify_on_trade_close': True,    # Notify when trade closes
                'notify_on_error': True           # Notify on errors
            }
        }
    ])


def simulate_conservative_trading():
    """
    Simulate conservative trading strategy.
    
    This demonstration shows:
    1. How plugins filter signals
    2. How multiple plugins work together
    3. Expected reduction in signal count
    """
    
    logger.info("=" * 60)
    logger.info("USE CASE 1: CONSERVATIVE TRADING STRATEGY")
    logger.info("=" * 60)
    
    # Create configuration
    config = ConservativeConfig()
    
    logger.info(f"\n📊 Configuration:")
    logger.info(f"   Symbol: {config.symbol}")
    logger.info(f"   Timeframe: {config.timeframe}")
    logger.info(f"   Risk: {config.risk_percent}% per trade")
    logger.info(f"   Max Trades: {config.max_trades}")
    
    logger.info(f"\n🔌 Active Plugins:")
    for plugin in config.plugins:
        if plugin['enabled']:
            logger.info(f"   ✓ {plugin['name']}")
            if 'config' in plugin:
                for key, value in plugin['config'].items():
                    if key not in ['bot_token', 'chat_id']:
                        logger.info(f"      - {key}: {value}")
    
    logger.info(f"\n📈 Expected Results:")
    logger.info(f"   - Signal Reduction: 80-90% (only best setups)")
    logger.info(f"   - Win Rate: 60-70% (higher quality)")
    logger.info(f"   - Drawdown: Lower (fewer bad trades)")
    logger.info(f"   - Confidence Boost: +10 to +35 per signal")
    
    logger.info(f"\n🎯 Filter Logic:")
    logger.info(f"   1. SuperTrend generates BUY signal")
    logger.info(f"   2. RSI Filter: Accept only if RSI < 25")
    logger.info(f"      - If RSI = 20 → +10 confidence")
    logger.info(f"      - If RSI = 15 → +15 confidence")
    logger.info(f"   3. Volume Filter: Accept only if volume > 2x avg")
    logger.info(f"      - If volume = 2.5x → +10 confidence")
    logger.info(f"      - If volume = 3x → +20 confidence")
    logger.info(f"   4. If BOTH pass → Signal executed with boosted confidence")
    logger.info(f"   5. Telegram notification sent")
    
    logger.info(f"\n💡 Example Scenarios:")
    logger.info(f"\n   Scenario A: Rejected Signal")
    logger.info(f"   - SuperTrend: BUY signal, confidence=70")
    logger.info(f"   - RSI: 45 (neutral) → REJECTED ❌")
    logger.info(f"   - Result: No trade")
    
    logger.info(f"\n   Scenario B: Accepted Signal")
    logger.info(f"   - SuperTrend: BUY signal, confidence=70")
    logger.info(f"   - RSI: 20 (oversold) → PASS ✓ (+15 confidence)")
    logger.info(f"   - Volume: 2.8x average → PASS ✓ (+10 confidence)")
    logger.info(f"   - Final confidence: 95")
    logger.info(f"   - Result: Trade executed! 🚀")
    logger.info(f"   - Telegram: '🟢 BUY EURUSD opened...'")
    
    logger.info(f"\n" + "=" * 60)
    logger.info(f"To run with REAL bot:")
    logger.info(f"1. Update Telegram bot_token and chat_id")
    logger.info(f"2. Configure MT5 connection")
    logger.info(f"3. Run: python -m examples.use_cases.use_case_1_conservative")
    logger.info("=" * 60)


def run_live_conservative_bot():
    """
    Run live conservative trading bot.
    
    WARNING: This requires MT5 connection and will trade real money!
    """
    
    logger.warning("⚠️  LIVE TRADING MODE - This will execute real trades!")
    logger.warning("⚠️  Make sure MT5 is running and configured correctly")
    
    # Create configuration
    config = ConservativeConfig()
    
    # Validate Telegram configuration
    telegram_plugin = next(
        (p for p in config.plugins if p['name'] == 'TelegramNotifier'),
        None
    )
    
    if telegram_plugin:
        if 'YOUR_BOT_TOKEN' in telegram_plugin['config'].get('bot_token', ''):
            logger.error("❌ Please configure Telegram bot_token first!")
            logger.info("Get token from @BotFather on Telegram")
            return
        
        if 'YOUR_CHAT_ID' in telegram_plugin['config'].get('chat_id', ''):
            logger.error("❌ Please configure Telegram chat_id first!")
            logger.info("Get chat_id from @userinfobot on Telegram")
            return
    
    try:
        # Create bot
        logger.info("Creating SuperTrend bot with conservative strategy...")
        bot = SuperTrendBot(config)
        
        # Connect to MT5
        logger.info("Connecting to MT5...")
        if not bot.connect():
            logger.error("Failed to connect to MT5")
            return
        
        logger.info("✅ Connected to MT5")
        logger.info(f"✅ {len(config.plugins)} plugins loaded")
        
        # Start trading
        logger.info("\n🚀 Starting conservative trading bot...")
        logger.info("Press Ctrl+C to stop\n")
        
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopping bot...")
        if 'bot' in locals():
            bot.shutdown()
        logger.info("✅ Bot stopped safely")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Conservative Trading Strategy')
    parser.add_argument(
        '--mode',
        choices=['simulate', 'live'],
        default='simulate',
        help='Run mode: simulate (demo) or live (real trading)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'simulate':
        simulate_conservative_trading()
    else:
        run_live_conservative_bot()
