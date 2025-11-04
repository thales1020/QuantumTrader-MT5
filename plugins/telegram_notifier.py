"""
Telegram Notifier Plugin

Sends trading notifications via Telegram.
Notifies when trades open/close and when errors occur.
"""

import logging
from typing import Optional, Dict, Any
import requests

from core.plugin_system import BasePlugin

logger = logging.getLogger(__name__)


class TelegramNotifierPlugin(BasePlugin):
    """
    Send Telegram notifications for trading events.
    
    Configuration:
        bot_token: Telegram bot token from @BotFather
        chat_id: Your Telegram chat ID (get from @userinfobot)
        notify_on_signal: Notify when signal is generated (default: False)
        notify_on_open: Notify when trade opens (default: True)
        notify_on_close: Notify when trade closes (default: True)
        notify_on_error: Notify on errors (default: True)
    
    Setup:
        1. Create bot with @BotFather on Telegram
        2. Get your chat ID from @userinfobot
        3. Configure plugin with bot_token and chat_id
    
    Example:
        >>> plugin = TelegramNotifierPlugin(
        ...     bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        ...     chat_id="123456789"
        ... )
        >>> bot.plugin_manager.register(plugin)
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize Telegram Notifier Plugin.
        
        Args:
            config: Configuration dict with keys:
                - bot_token: Telegram bot token
                - chat_id: Telegram chat ID
                - notify_on_signal: Notify on signal (default: False)
                - notify_on_trade_open: Notify on trade open (default: True)
                - notify_on_trade_close: Notify on trade close (default: True)
                - notify_on_error: Notify on error (default: True)
        """
        super().__init__(name="TelegramNotifier")
        
        config = config or {}
        self.bot_token = config.get('bot_token', '')
        self.chat_id = config.get('chat_id', '')
        self.notify_on_signal = config.get('notify_on_signal', False)
        self.notify_on_open = config.get('notify_on_trade_open', True)
        self.notify_on_close = config.get('notify_on_trade_close', True)
        self.notify_on_error = config.get('notify_on_error', True)
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot_token or chat_id not configured. Notifications disabled.")
            self.enabled = False
            return
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        logger.info("Telegram Notifier configured")
        
        # Test connection
        self._test_connection()
    
    @property
    def name(self) -> str:
        return "TelegramNotifier"
    
    def _test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            if response.status_code == 200:
                bot_info = response.json()['result']
                logger.info(f"Connected to Telegram bot: @{bot_info['username']}")
                return True
            else:
                logger.error(f"Failed to connect to Telegram: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to Telegram.
        
        Args:
            message: Message text
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully
        """
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug("Telegram message sent successfully")
                return True
            else:
                error = response.json().get('description', 'Unknown error')
                logger.error(f"Failed to send Telegram message: {error}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def on_signal(self, signal: Optional[Dict], df) -> Optional[Dict]:
        """
        Notify when signal is generated (if enabled).
        
        Note: This is called BEFORE trade execution.
        """
        if signal and self.notify_on_signal:
            message = f"""
🔔 <b>Signal Generated</b>

Type: {signal.get('type', 'Unknown')}
Price: {signal.get('price', 0):.5f}
SL: {signal.get('stop_loss', 0):.5f}
TP: {signal.get('take_profit', 0):.5f}
"""
            if 'confidence' in signal:
                message += f"Confidence: {signal['confidence']:.1f}%\n"
            
            self._send_message(message.strip())
        
        return signal
    
    def on_trade_open(self, trade_info: Dict[str, Any]) -> None:
        """Notify when trade is opened"""
        if not self.notify_on_open:
            return
        
        emoji = "🟢" if trade_info.get('type') == 'BUY' else "🔴"
        
        message = f"""
{emoji} <b>Trade Opened</b>

Symbol: {trade_info.get('symbol', 'N/A')}
Type: <b>{trade_info.get('type', 'N/A')}</b>
Ticket: #{trade_info.get('ticket', 'N/A')}

Entry: {trade_info.get('price', 0):.5f}
SL: {trade_info.get('sl', 0):.5f}
TP: {trade_info.get('tp', 0):.5f}
"""
        
        if 'volume' in trade_info:
            message += f"Volume: {trade_info['volume']:.2f} lots\n"
        
        self._send_message(message.strip())
    
    def on_trade_close(self, trade_info: Dict[str, Any]) -> None:
        """Notify when trade is closed"""
        if not self.notify_on_close:
            return
        
        profit = trade_info.get('profit', 0)
        emoji = "✅" if profit > 0 else "❌" if profit < 0 else "➖"
        
        message = f"""
{emoji} <b>Trade Closed</b>

Ticket: #{trade_info.get('ticket', 'N/A')}
Symbol: {trade_info.get('symbol', 'N/A')}

Entry: {trade_info.get('entry_price', 0):.5f}
Exit: {trade_info.get('exit_price', 0):.5f}

<b>Profit: ${profit:.2f}</b>
"""
        
        if 'duration' in trade_info:
            message += f"Duration: {trade_info['duration']}\n"
        
        self._send_message(message.strip())
    
    def on_error(self, error: Exception) -> None:
        """Notify on errors (if enabled)"""
        if not self.notify_on_error:
            return
        
        message = f"""
⚠️ <b>Error Alert</b>

Plugin: {self.name}
Error: {str(error)}
Type: {type(error).__name__}
"""
        
        self._send_message(message.strip())
    
    def on_shutdown(self) -> None:
        """Send shutdown notification"""
        message = """
🛑 <b>Bot Shutdown</b>

Trading bot has been stopped.
"""
        self._send_message(message.strip())
