"""
Telegram Notification Plugin Example

This plugin sends trading notifications to Telegram including:
- Trade entry/exit alerts
- Daily performance summaries
- Risk warnings (daily loss limit, drawdown)
- System status updates
- Custom alerts

Hook Usage:
- after_trade: Send trade entry notification
- on_position_close: Send trade exit notification
- daily_start: Send daily startup message
- daily_end: Send daily performance summary
- on_error: Send error alerts

Requirements:
    pip install python-telegram-bot

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.plugin_system import BasePlugin
from typing import Dict, Optional
from datetime import datetime
import logging
import asyncio


class TelegramNotifier(BasePlugin):
    """
    Telegram Notification Plugin
    
    Features:
    - Real-time trade alerts
    - Daily performance reports
    - Risk warnings
    - Custom message formatting
    - Error notifications
    - Emoji indicators for clarity
    
    Configuration:
        {
            'bot_token': 'YOUR_BOT_TOKEN',     # Get from @BotFather
            'chat_id': 'YOUR_CHAT_ID',         # Your Telegram chat ID
            'notify_trades': True,              # Send trade alerts
            'notify_daily': True,               # Send daily summaries
            'notify_errors': True,              # Send error alerts
            'notify_risk_warnings': True,       # Send risk warnings
            'use_emojis': True,                 # Use emojis in messages
        }
    
    Note:
        This is a simplified example. In production, use:
        - python-telegram-bot library for async
        - Proper error handling
        - Message queuing to avoid rate limits
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Telegram configuration
        self.bot_token = config.get('bot_token', '')
        self.chat_id = config.get('chat_id', '')
        
        # Notification settings
        self.notify_trades = config.get('notify_trades', True)
        self.notify_daily = config.get('notify_daily', True)
        self.notify_errors = config.get('notify_errors', True)
        self.notify_risk_warnings = config.get('notify_risk_warnings', True)
        self.use_emojis = config.get('use_emojis', True)
        
        # Bot instance (would use python-telegram-bot in production)
        self.bot = None
        
        # Message queue (to avoid rate limits)
        self.message_queue = []
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize bot if credentials provided
        if self.bot_token and self.chat_id:
            self._initialize_bot()
        else:
            self.logger.warning("Telegram credentials not provided - running in demo mode")
    
    def get_name(self) -> str:
        return "TelegramNotifier"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def _initialize_bot(self):
        """Initialize Telegram bot (simplified for example)"""
        try:
            # In production, use:
            # from telegram import Bot
            # self.bot = Bot(token=self.bot_token)
            
            self.logger.info("Telegram bot initialized")
            self.logger.info(f"Chat ID: {self.chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {e}")
    
    def _get_emoji(self, type: str) -> str:
        """Get emoji for message type"""
        if not self.use_emojis:
            return ''
        
        emojis = {
            'buy': '🟢',
            'sell': '🔴',
            'profit': '💰',
            'loss': '📉',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️',
            'daily': '📊',
            'start': '🚀',
            'stop': '🛑',
        }
        
        return emojis.get(type, '')
    
    def send_message(self, message: str, silent: bool = False):
        """
        Send message to Telegram
        
        Args:
            message: Message text
            silent: Send without notification sound
        """
        if not self.bot_token or not self.chat_id:
            # Demo mode - just log
            self.logger.info(f"[Telegram Demo] {message}")
            return
        
        try:
            # In production, use:
            # asyncio.run(self.bot.send_message(
            #     chat_id=self.chat_id,
            #     text=message,
            #     parse_mode='HTML',
            #     disable_notification=silent
            # ))
            
            # For demo - just log
            self.logger.info(f"[Telegram] {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
    
    def format_trade_entry_message(self, context: Dict) -> str:
        """Format trade entry notification"""
        trade_type = context.get('type', 'UNKNOWN')
        symbol = context.get('symbol', 'UNKNOWN')
        price = context.get('price', 0)
        size = context.get('position_size', 0)
        sl = context.get('stop_loss', 0)
        tp = context.get('take_profit', 0)
        
        emoji = self._get_emoji('buy' if trade_type == 'BUY' else 'sell')
        
        message = f"""
{emoji} <b>TRADE OPENED</b>

<b>Symbol:</b> {symbol}
<b>Type:</b> {trade_type}
<b>Entry Price:</b> {price:.5f}
<b>Position Size:</b> {size:.2f} lots

<b>Stop Loss:</b> {sl:.5f}
<b>Take Profit:</b> {tp:.5f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
        """.strip()
        
        return message
    
    def format_trade_exit_message(self, context: Dict) -> str:
        """Format trade exit notification"""
        symbol = context.get('symbol', 'UNKNOWN')
        profit = context.get('profit', 0)
        exit_price = context.get('price', 0)
        exit_reason = context.get('exit_reason', 'unknown')
        duration = context.get('duration_minutes', 0)
        
        emoji = self._get_emoji('profit' if profit > 0 else 'loss')
        
        result = "PROFIT" if profit > 0 else "LOSS" if profit < 0 else "BREAK EVEN"
        
        message = f"""
{emoji} <b>TRADE CLOSED - {result}</b>

<b>Symbol:</b> {symbol}
<b>Exit Price:</b> {exit_price:.5f}
<b>Profit/Loss:</b> ${profit:+.2f}

<b>Exit Reason:</b> {exit_reason}
<b>Duration:</b> {duration:.0f} minutes

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
        """.strip()
        
        return message
    
    def format_daily_summary(self, context: Dict) -> str:
        """Format daily performance summary"""
        trades = context.get('daily_trades', 0)
        profit = context.get('daily_profit', 0)
        win_rate = context.get('daily_win_rate', 0)
        
        emoji = self._get_emoji('daily')
        profit_emoji = self._get_emoji('profit' if profit > 0 else 'loss')
        
        message = f"""
{emoji} <b>DAILY PERFORMANCE SUMMARY</b>

<b>Trades Today:</b> {trades}
<b>Win Rate:</b> {win_rate:.1f}%
{profit_emoji} <b>Total P&L:</b> ${profit:+.2f}

<i>Date: {datetime.now().strftime('%Y-%m-%d')}</i>
        """.strip()
        
        return message
    
    def format_risk_warning(self, warning_type: str, details: Dict) -> str:
        """Format risk warning message"""
        emoji = self._get_emoji('warning')
        
        if warning_type == 'daily_loss_limit':
            message = f"""
{emoji} <b>RISK WARNING: DAILY LOSS LIMIT</b>

Your daily loss limit has been reached.
Trading has been stopped for today.

<b>Daily Loss:</b> ${details.get('daily_loss', 0):.2f}
<b>Limit:</b> {details.get('limit_percent', 0)}%

<i>Time: {datetime.now().strftime('%H:%M:%S')}</i>
            """.strip()
        
        elif warning_type == 'max_drawdown':
            message = f"""
{emoji} <b>RISK WARNING: MAX DRAWDOWN</b>

Maximum drawdown limit exceeded.
Please review your strategy.

<b>Current Drawdown:</b> {details.get('drawdown_percent', 0):.2f}%
<b>Limit:</b> {details.get('limit_percent', 0)}%

<i>Time: {datetime.now().strftime('%H:%M:%S')}</i>
            """.strip()
        
        else:
            message = f"""
{emoji} <b>RISK WARNING</b>

Type: {warning_type}
Details: {details}

<i>Time: {datetime.now().strftime('%H:%M:%S')}</i>
            """.strip()
        
        return message
    
    def format_error_message(self, error: str, context: Dict) -> str:
        """Format error notification"""
        emoji = self._get_emoji('error')
        
        message = f"""
{emoji} <b>ERROR ALERT</b>

<b>Error:</b> {error}

<b>Context:</b>
{self._format_dict(context)}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
        """.strip()
        
        return message
    
    def _format_dict(self, data: Dict, indent: int = 0) -> str:
        """Format dictionary for readable display"""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
    
    def notify_trade_entry(self, context: Dict):
        """Send trade entry notification"""
        if not self.notify_trades:
            return
        
        message = self.format_trade_entry_message(context)
        self.send_message(message)
    
    def notify_trade_exit(self, context: Dict):
        """Send trade exit notification"""
        if not self.notify_trades:
            return
        
        message = self.format_trade_exit_message(context)
        self.send_message(message)
    
    def notify_daily_performance(self, context: Dict):
        """Send daily performance summary"""
        if not self.notify_daily:
            return
        
        message = self.format_daily_summary(context)
        self.send_message(message)
    
    def notify_risk_warning(self, warning_type: str, details: Dict):
        """Send risk warning"""
        if not self.notify_risk_warnings:
            return
        
        message = self.format_risk_warning(warning_type, details)
        self.send_message(message, silent=False)  # Important - don't silence
    
    def notify_error(self, error: str, context: Dict):
        """Send error notification"""
        if not self.notify_errors:
            return
        
        message = self.format_error_message(error, context)
        self.send_message(message, silent=False)
    
    def after_trade(self, context: Dict) -> Dict:
        """Hook: Send trade entry notification"""
        self.notify_trade_entry(context)
        return context
    
    def on_position_close(self, context: Dict) -> Dict:
        """Hook: Send trade exit notification"""
        self.notify_trade_exit(context)
        return context
    
    def daily_start(self, context: Dict) -> Dict:
        """Hook: Send daily startup message"""
        emoji = self._get_emoji('start')
        
        message = f"""
{emoji} <b>BOT STARTED</b>

Trading bot is now active.

<i>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
        """.strip()
        
        self.send_message(message, silent=True)
        return context
    
    def daily_end(self, context: Dict) -> Dict:
        """Hook: Send daily summary"""
        self.notify_daily_performance(context)
        return context
    
    def on_error(self, context: Dict) -> Dict:
        """Hook: Send error notification"""
        error = context.get('error', 'Unknown error')
        self.notify_error(error, context)
        return context


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'bot_token': '',  # Add your bot token for real usage
        'chat_id': '',    # Add your chat ID for real usage
        'notify_trades': True,
        'notify_daily': True,
        'notify_errors': True,
        'notify_risk_warnings': True,
        'use_emojis': True,
    }
    
    # Initialize plugin
    notifier = TelegramNotifier(config)
    
    print("\n" + "=" * 60)
    print(f"Plugin: {notifier.get_name()} v{notifier.get_version()}")
    print("=" * 60)
    print("\nRunning in DEMO mode (no bot token provided)")
    print("Messages will be logged instead of sent to Telegram\n")
    
    # Simulate trade entry
    print("Simulating trade entry...")
    notifier.after_trade({
        'type': 'BUY',
        'symbol': 'EURUSD',
        'price': 1.10000,
        'position_size': 0.1,
        'stop_loss': 1.09500,
        'take_profit': 1.10500,
    })
    
    print("\nSimulating trade exit (profit)...")
    notifier.on_position_close({
        'symbol': 'EURUSD',
        'price': 1.10300,
        'profit': 30.00,
        'exit_reason': 'take_profit',
        'duration_minutes': 45,
    })
    
    print("\nSimulating daily summary...")
    notifier.daily_end({
        'daily_trades': 5,
        'daily_profit': 125.50,
        'daily_win_rate': 80.0,
    })
    
    print("\nSimulating risk warning...")
    notifier.notify_risk_warning('daily_loss_limit', {
        'daily_loss': 200.00,
        'limit_percent': 2.0,
    })
    
    print("\n" + "=" * 60)
    print("\nTo use with real Telegram:")
    print("1. Create bot with @BotFather")
    print("2. Get your bot token")
    print("3. Get your chat ID (use @userinfobot)")
    print("4. Update config with token and chat_id")
    print("5. Install: pip install python-telegram-bot")
    print("=" * 60 + "\n")
