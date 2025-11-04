"""
Use Case 2: Aggressive Scalping Strategy

Scenario:
    Active trader who wants to capitalize on all opportunities.
    Minimal filters, fast execution, immediate notifications.

Strategy:
    - SuperTrend bot with tight parameters
    - NO RSI filter (trade all signals)
    - NO volume filter (don't miss opportunities)
    - Telegram notifications on EVERY signal and trade

Expected Behavior:
    - Many signals (80-100% of original)
    - Lower win rate (45-55%)
    - More trades = more opportunities
    - Higher risk/reward potential

Configuration:
    - SuperTrend: Tight parameters (atr_multiplier=2.0)
    - Risk: 0.5% per trade (smaller positions, more trades)
    - Telegram: Notify on everything
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dataclasses import dataclass, field
from typing import List
import logging

from core.supertrend_bot import SuperTrendBot
from core.base_bot import BaseConfig


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScalpingConfig(BaseConfig):
    """Configuration for aggressive scalping"""
    
    # Symbol and timeframe
    symbol: str = 'GBPUSD'  # Volatile pair
    timeframe: str = 'M15'   # 15-minute for scalping
    magic_number: int = 100002
    
    # SuperTrend parameters (tight for scalping)
    atr_period: int = 7
    atr_multiplier: float = 2.0  # Tighter stops
    
    # Risk management
    risk_percent: float = 0.5  # Smaller risk per trade
    max_trades: int = 10        # Allow more concurrent trades
    
    # Plugin configuration - Only Telegram
    plugins: List = field(default_factory=lambda: [
        {
            'name': 'TelegramNotifier',
            'enabled': True,
            'config': {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'chat_id': 'YOUR_CHAT_ID_HERE',
                'notify_on_signal': True,         # Notify on every signal
                'notify_on_trade_open': True,     # Notify when trade opens
                'notify_on_trade_close': True,    # Notify when trade closes
                'notify_on_error': True           # Notify on errors
            }
        }
    ])


def simulate_scalping_strategy():
    """Simulate aggressive scalping strategy"""
    
    logger.info("=" * 60)
    logger.info("USE CASE 2: AGGRESSIVE SCALPING STRATEGY")
    logger.info("=" * 60)
    
    config = ScalpingConfig()
    
    logger.info(f"\n📊 Configuration:")
    logger.info(f"   Symbol: {config.symbol} (volatile pair)")
    logger.info(f"   Timeframe: {config.timeframe} (fast scalping)")
    logger.info(f"   Risk: {config.risk_percent}% per trade (smaller positions)")
    logger.info(f"   Max Trades: {config.max_trades} (more opportunities)")
    logger.info(f"   ATR Multiplier: {config.atr_multiplier} (tight stops)")
    
    logger.info(f"\n🔌 Active Plugins:")
    logger.info(f"   ✓ TelegramNotifier (all notifications enabled)")
    logger.info(f"   ✗ RSI Filter (disabled - trade all signals)")
    logger.info(f"   ✗ Volume Filter (disabled - don't miss trades)")
    
    logger.info(f"\n📈 Expected Results:")
    logger.info(f"   - Signal Count: HIGH (trade most signals)")
    logger.info(f"   - Win Rate: 45-55% (more trades = lower accuracy)")
    logger.info(f"   - Trade Frequency: 20-50 trades/day")
    logger.info(f"   - Risk Reward: 1:1.5 to 1:2")
    
    logger.info(f"\n🎯 Trading Logic:")
    logger.info(f"   1. SuperTrend generates signal → Trade immediately")
    logger.info(f"   2. NO filters (maximize opportunities)")
    logger.info(f"   3. Telegram alert sent instantly")
    logger.info(f"   4. Small position size (0.5% risk)")
    logger.info(f"   5. Tight stops (ATR x2.0)")
    
    logger.info(f"\n💡 Example Day:")
    logger.info(f"\n   8:00 AM  → BUY signal → Trade opened")
    logger.info(f"            📱 Telegram: '🟢 BUY GBPUSD @ 1.2650'")
    logger.info(f"   8:15 AM  → TP hit → +15 pips")
    logger.info(f"            📱 Telegram: '✅ BUY closed, Profit: $15'")
    logger.info(f"   8:30 AM  → SELL signal → Trade opened")
    logger.info(f"            📱 Telegram: '🔴 SELL GBPUSD @ 1.2645'")
    logger.info(f"   8:45 AM  → SL hit → -10 pips")
    logger.info(f"            📱 Telegram: '❌ SELL closed, Loss: -$10'")
    logger.info(f"   9:00 AM  → BUY signal → Trade opened...")
    logger.info(f"   ... continues throughout the day")
    logger.info(f"\n   End of Day: 25 trades, 13 wins, 12 losses, +50 pips net")
    
    logger.info(f"\n⚡ Speed Comparison:")
    logger.info(f"\n   Conservative Strategy (Use Case 1):")
    logger.info(f"   - 100 SuperTrend signals")
    logger.info(f"   → 15 pass RSI filter")
    logger.info(f"   → 10 pass volume filter")
    logger.info(f"   = 10 trades executed (10% conversion)")
    
    logger.info(f"\n   Scalping Strategy (Use Case 2):")
    logger.info(f"   - 100 SuperTrend signals")
    logger.info(f"   → NO filters")
    logger.info(f"   = 95 trades executed (95% conversion)")
    logger.info(f"   Note: 5% may be skipped due to max_trades limit")
    
    logger.info(f"\n🎰 Risk Profile:")
    logger.info(f"   - Higher frequency = Higher risk")
    logger.info(f"   - More screen time required")
    logger.info(f"   - More commissions/spreads")
    logger.info(f"   - Good for: Active traders, algorithm trading")
    logger.info(f"   - Not good for: Part-time traders, high stress aversion")
    
    logger.info(f"\n" + "=" * 60)
    logger.info(f"To run with REAL bot:")
    logger.info(f"1. Update Telegram credentials")
    logger.info(f"2. Use demo account first!")
    logger.info(f"3. Monitor actively (high frequency)")
    logger.info("=" * 60)


def run_live_scalping_bot():
    """Run live scalping bot"""
    
    logger.warning("⚠️  SCALPING MODE - HIGH FREQUENCY TRADING!")
    logger.warning("⚠️  This will generate MANY trades - use demo first!")
    
    config = ScalpingConfig()
    
    # Validate configuration
    telegram_plugin = next(
        (p for p in config.plugins if p['name'] == 'TelegramNotifier'),
        None
    )
    
    if telegram_plugin:
        if 'YOUR_BOT_TOKEN' in telegram_plugin['config'].get('bot_token', ''):
            logger.error("❌ Configure Telegram bot_token first!")
            return
    
    try:
        logger.info("Creating SuperTrend scalping bot...")
        bot = SuperTrendBot(config)
        
        logger.info("Connecting to MT5...")
        if not bot.connect():
            logger.error("Failed to connect to MT5")
            return
        
        logger.info("✅ Connected to MT5")
        logger.info(f"✅ Scalping mode active on {config.symbol} {config.timeframe}")
        logger.info(f"📱 Telegram notifications enabled for all events")
        
        logger.info("\n🚀 Starting aggressive scalping bot...")
        logger.info("⚡ HIGH FREQUENCY MODE - Monitor closely!")
        logger.info("Press Ctrl+C to stop\n")
        
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopping scalping bot...")
        if 'bot' in locals():
            bot.shutdown()
        logger.info("✅ Bot stopped")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggressive Scalping Strategy')
    parser.add_argument(
        '--mode',
        choices=['simulate', 'live'],
        default='simulate',
        help='Run mode: simulate (demo) or live (real trading)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'simulate':
        simulate_scalping_strategy()
    else:
        run_live_scalping_bot()
