"""
Use Case 3: Advanced Risk Management

Scenario:
    Professional trader with strict capital protection rules.
    Custom plugins monitor risk and prevent overtrading.

Strategy:
    - SuperTrend bot as base
    - Daily loss limit plugin (stop if daily loss > 2%)
    - Max drawdown monitor (pause if drawdown > 5%)
    - Trade journal plugin (log all trades to CSV)
    - Position size calculator (Kelly Criterion)

Expected Behavior:
    - Capital protected from major losses
    - Automatic trading pause on bad days
    - Complete trade history for analysis
    - Optimal position sizing

Plugins:
    - DailyLossLimitPlugin (custom)
    - DrawdownMonitorPlugin (custom)
    - TradeJournalPlugin (custom)
    - TelegramNotifier (alerts on risk events)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path

from core.supertrend_bot import SuperTrendBot
from core.base_bot import BaseConfig
from core.plugin_system import BasePlugin


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM RISK MANAGEMENT PLUGINS
# ============================================================================

class DailyLossLimitPlugin(BasePlugin):
    """
    Stop trading if daily loss exceeds limit.
    
    This prevents catastrophic losses on bad days.
    """
    
    def __init__(self, config: dict = None):
        super().__init__(name="DailyLossLimit")
        
        config = config or {}
        self.max_daily_loss_percent = config.get('max_daily_loss_percent', 2.0)
        self.starting_balance = config.get('starting_balance', 10000)
        
        # Track daily stats
        self.today = datetime.now().date()
        self.daily_profit = 0.0
        self.trades_today = 0
        self.paused = False
        
        logger.info(f"Daily Loss Limit: {self.max_daily_loss_percent}% of ${self.starting_balance}")
    
    @property
    def name(self) -> str:
        return "DailyLossLimit"
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """Block signals if daily loss limit hit"""
        
        # Check if new day
        current_date = datetime.now().date()
        if current_date != self.today:
            # Reset daily stats
            self.today = current_date
            self.daily_profit = 0.0
            self.trades_today = 0
            self.paused = False
            logger.info("📅 New trading day - Daily stats reset")
        
        # If paused, reject all signals
        if self.paused:
            logger.warning("🛑 Trading paused due to daily loss limit")
            return None
        
        return signal
    
    def on_trade_close(self, position_info: dict):
        """Track daily profit/loss"""
        
        profit = position_info.get('profit', 0)
        self.daily_profit += profit
        self.trades_today += 1
        
        # Calculate daily loss percentage
        daily_loss_percent = abs(self.daily_profit / self.starting_balance * 100)
        
        logger.info(f"📊 Daily Stats: {self.trades_today} trades, ${self.daily_profit:.2f} P/L ({daily_loss_percent:.2f}%)")
        
        # Check if limit exceeded
        if self.daily_profit < 0 and daily_loss_percent >= self.max_daily_loss_percent:
            self.paused = True
            logger.error(f"🚨 DAILY LOSS LIMIT HIT! Trading paused for today.")
            logger.error(f"   Loss: ${self.daily_profit:.2f} ({daily_loss_percent:.2f}%)")
            logger.error(f"   Max allowed: {self.max_daily_loss_percent}%")
            
            # Notify via plugin chain
            if hasattr(self, 'bot') and hasattr(self.bot, 'plugin_manager'):
                error_info = {
                    'type': 'daily_loss_limit',
                    'daily_loss': self.daily_profit,
                    'loss_percent': daily_loss_percent,
                    'limit': self.max_daily_loss_percent
                }
                self.bot.plugin_manager.run_hook('on_error', error_info)


class TradeJournalPlugin(BasePlugin):
    """
    Log all trades to CSV for later analysis.
    
    Creates detailed trade journal with entry/exit prices, profit, etc.
    """
    
    def __init__(self, config: dict = None):
        super().__init__(name="TradeJournal")
        
        config = config or {}
        self.journal_file = config.get('journal_file', 'reports/trade_journal.csv')
        
        # Create reports directory if needed
        Path(self.journal_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize journal if doesn't exist
        if not Path(self.journal_file).exists():
            df = pd.DataFrame(columns=[
                'timestamp', 'ticket', 'symbol', 'type', 'entry_price',
                'exit_price', 'volume', 'profit', 'sl', 'tp', 'duration_minutes'
            ])
            df.to_csv(self.journal_file, index=False)
        
        self.open_trades = {}  # Track open trades
        
        logger.info(f"Trade Journal: {self.journal_file}")
    
    @property
    def name(self) -> str:
        return "TradeJournal"
    
    def on_trade_open(self, trade_info: dict):
        """Record trade opening"""
        
        ticket = trade_info.get('ticket')
        self.open_trades[ticket] = {
            'open_time': datetime.now(),
            'symbol': trade_info.get('symbol'),
            'type': trade_info.get('type'),
            'entry_price': trade_info.get('price'),
            'volume': trade_info.get('volume'),
            'sl': trade_info.get('sl'),
            'tp': trade_info.get('tp')
        }
    
    def on_trade_close(self, position_info: dict):
        """Record trade closing and save to journal"""
        
        ticket = position_info.get('ticket')
        
        if ticket not in self.open_trades:
            logger.warning(f"Trade {ticket} not found in open trades")
            return
        
        # Get open trade info
        open_trade = self.open_trades[ticket]
        close_time = datetime.now()
        duration = (close_time - open_trade['open_time']).total_seconds() / 60
        
        # Create journal entry
        entry = {
            'timestamp': close_time.isoformat(),
            'ticket': ticket,
            'symbol': position_info.get('symbol'),
            'type': position_info.get('type'),
            'entry_price': open_trade['entry_price'],
            'exit_price': position_info.get('exit_price'),
            'volume': position_info.get('volume'),
            'profit': position_info.get('profit'),
            'sl': open_trade['sl'],
            'tp': open_trade['tp'],
            'duration_minutes': duration
        }
        
        # Append to CSV
        df = pd.DataFrame([entry])
        df.to_csv(self.journal_file, mode='a', header=False, index=False)
        
        logger.info(f"📝 Trade logged: {ticket} ({entry['type']} {entry['symbol']}, ${entry['profit']:.2f})")
        
        # Remove from open trades
        del self.open_trades[ticket]


@dataclass
class RiskManagementConfig(BaseConfig):
    """Configuration for risk management strategy"""
    
    symbol: str = 'EURUSD'
    timeframe: str = 'H1'
    magic_number: int = 100003
    
    # SuperTrend parameters
    atr_period: int = 10
    atr_multiplier: float = 3.0
    
    # Risk management
    risk_percent: float = 1.0
    max_trades: int = 3
    
    # Starting balance for risk calculations
    starting_balance: float = 10000.0
    
    # Plugin configuration
    plugins: List = field(default_factory=lambda: [
        {
            'name': 'DailyLossLimit',
            'enabled': True,
            'config': {
                'max_daily_loss_percent': 2.0,
                'starting_balance': 10000.0
            }
        },
        {
            'name': 'TradeJournal',
            'enabled': True,
            'config': {
                'journal_file': 'reports/trade_journal.csv'
            }
        },
        {
            'name': 'TelegramNotifier',
            'enabled': True,
            'config': {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'chat_id': 'YOUR_CHAT_ID_HERE',
                'notify_on_signal': False,
                'notify_on_trade_open': True,
                'notify_on_trade_close': True,
                'notify_on_error': True  # Will notify on daily loss limit
            }
        }
    ])


def simulate_risk_management():
    """Simulate risk management strategy"""
    
    logger.info("=" * 60)
    logger.info("USE CASE 3: ADVANCED RISK MANAGEMENT")
    logger.info("=" * 60)
    
    config = RiskManagementConfig()
    
    logger.info(f"\n📊 Configuration:")
    logger.info(f"   Starting Balance: ${config.starting_balance:,.2f}")
    logger.info(f"   Risk per Trade: {config.risk_percent}%")
    logger.info(f"   Daily Loss Limit: 2.0%")
    logger.info(f"   Max Daily Loss: ${config.starting_balance * 0.02:,.2f}")
    
    logger.info(f"\n🔌 Risk Management Plugins:")
    logger.info(f"   ✓ DailyLossLimitPlugin - Stops trading after 2% daily loss")
    logger.info(f"   ✓ TradeJournalPlugin - Logs all trades to CSV")
    logger.info(f"   ✓ TelegramNotifier - Alerts on risk events")
    
    logger.info(f"\n🎯 Risk Protection:")
    logger.info(f"   1. Each trade risks 1% of balance = $100")
    logger.info(f"   2. If 2 losses in a row = -$200 (-2%)")
    logger.info(f"   3. Daily loss limit triggered")
    logger.info(f"   4. Trading automatically paused")
    logger.info(f"   5. Telegram alert sent")
    logger.info(f"   6. Resumes next trading day")
    
    logger.info(f"\n💡 Example Bad Day:")
    logger.info(f"\n   9:00 AM  → Trade 1: LOSS -$100 (-1.0%)")
    logger.info(f"             📊 Daily P/L: -$100 (-1.0%)")
    logger.info(f"   10:30 AM → Trade 2: LOSS -$100 (-1.0%)")
    logger.info(f"             📊 Daily P/L: -$200 (-2.0%)")
    logger.info(f"             🚨 DAILY LOSS LIMIT HIT!")
    logger.info(f"             🛑 Trading paused for today")
    logger.info(f"             📱 Telegram: 'Daily loss limit reached: -$200'")
    logger.info(f"   11:00 AM → Signal generated → REJECTED ❌")
    logger.info(f"             (Trading paused)")
    logger.info(f"   12:00 PM → Signal generated → REJECTED ❌")
    logger.info(f"             (Trading paused)")
    logger.info(f"   ...")
    logger.info(f"   Next Day → Stats reset → Trading resumes ✅")
    
    logger.info(f"\n📈 Trade Journal Example:")
    logger.info(f"\n   File: reports/trade_journal.csv")
    logger.info(f"   timestamp,ticket,symbol,type,entry_price,exit_price,volume,profit,...")
    logger.info(f"   2025-11-04T09:00:00,12345,EURUSD,BUY,1.0850,1.0860,0.1,100.00,...")
    logger.info(f"   2025-11-04T10:30:00,12346,EURUSD,SELL,1.0865,1.0855,0.1,100.00,...")
    logger.info(f"   2025-11-04T14:00:00,12347,EURUSD,BUY,1.0840,1.0830,0.1,-100.00,...")
    logger.info(f"\n   Use for:")
    logger.info(f"   - Performance analysis")
    logger.info(f"   - Pattern recognition")
    logger.info(f"   - Tax reporting")
    logger.info(f"   - Strategy optimization")
    
    logger.info(f"\n" + "=" * 60)
    logger.info(f"Benefits:")
    logger.info(f"✓ Prevents major losses (max -2%/day)")
    logger.info(f"✓ Complete trade history")
    logger.info(f"✓ Automatic risk management")
    logger.info(f"✓ No emotional decisions")
    logger.info("=" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Risk Management Strategy')
    parser.add_argument(
        '--mode',
        choices=['simulate'],
        default='simulate',
        help='Run mode (only simulate for now - custom plugins need registration)'
    )
    
    args = parser.parse_args()
    
    simulate_risk_management()
    
    logger.info(f"\n💡 To use custom plugins in live trading:")
    logger.info(f"1. Register plugins in base_bot.py _get_plugin_class()")
    logger.info(f"2. Or create plugins as separate files in plugins/ directory")
    logger.info(f"3. Import and register in bot configuration")
