"""
Telegram Notifier - Send Alerts and Updates via Telegram
Requires Telegram Bot API token and chat ID
Get token from @BotFather, get chat ID from @userinfobot
"""

import requests
import json
from datetime import datetime
import os


class TelegramNotifier:
    """
    Send messages to Telegram
    
    Setup:
    1. Create bot with @BotFather on Telegram
    2. Get your chat ID from @userinfobot
    3. Set environment variables or config:
       - TELEGRAM_BOT_TOKEN
       - TELEGRAM_CHAT_ID
    
    Usage:
        notifier = TelegramNotifier()
        notifier.send_message("Bot started successfully!")
        notifier.send_trade_alert("BUY", "BTCUSD", 1.0, 45000.0)
    """
    
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token (from @BotFather)
            chat_id: Telegram chat ID (from @userinfobot)
        """
        # Get credentials from args or environment
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')
        
        # Validate
        if not self.bot_token or not self.chat_id:
            raise ValueError(
                "Missing Telegram credentials. "
                "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID "
                "environment variables or pass as arguments."
            )
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if bot token is valid"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            if response.status_code == 200:
                bot_info = response.json()['result']
                print(f" Telegram bot connected: @{bot_info['username']}")
            else:
                raise Exception(f"Invalid bot token: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to connect to Telegram: {e}")
    
    def send_message(self, text, parse_mode='Markdown', disable_notification=False):
        """
        Send text message
        
        Args:
            text: Message text (supports Markdown or HTML)
            parse_mode: 'Markdown' or 'HTML'
            disable_notification: Send silently
        
        Returns:
            bool: True if sent successfully
        """
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                error = response.json().get('description', 'Unknown error')
                print(f" Failed to send message: {error}")
                return False
                
        except Exception as e:
            print(f" Error sending Telegram message: {e}")
            return False
    
    def send_startup_alert(self, bot_name="MT5 Bot"):
        """Send bot startup notification"""
        text = f"""
 *{bot_name} Started*

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 Bot is now running and monitoring markets
        """
        return self.send_message(text.strip())
    
    def send_shutdown_alert(self, bot_name="MT5 Bot", reason="User request"):
        """Send bot shutdown notification"""
        text = f"""
🛑 *{bot_name} Stopped*

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 Reason: {reason}
        """
        return self.send_message(text.strip())
    
    def send_trade_alert(self, order_type, symbol, volume, price, sl=None, tp=None):
        """
        Send trade execution alert
        
        Args:
            order_type: 'BUY' or 'SELL'
            symbol: Trading symbol
            volume: Trade volume (lots)
            price: Entry price
            sl: Stop loss (optional)
            tp: Take profit (optional)
        """
        emoji = "" if order_type == "BUY" else ""
        
        text = f"""
{emoji} *{order_type} Order Executed*

 Symbol: `{symbol}`
 Volume: `{volume}` lots
💵 Price: `{price}`
"""
        
        if sl:
            text += f"🛑 Stop Loss: `{sl}`\n"
        if tp:
            text += f" Take Profit: `{tp}`\n"
        
        text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(text.strip())
    
    def send_close_alert(self, order_type, symbol, volume, entry_price, exit_price, profit):
        """
        Send position close alert
        
        Args:
            order_type: 'BUY' or 'SELL'
            symbol: Trading symbol
            volume: Trade volume
            entry_price: Entry price
            exit_price: Exit price
            profit: Profit/loss amount
        """
        emoji = "" if profit >= 0 else ""
        profit_emoji = "" if profit >= 0 else ""
        
        text = f"""
{emoji} *Position Closed*

 Symbol: `{symbol}`
📍 Type: {order_type}
 Volume: `{volume}` lots
 Entry: `{entry_price}`
 Exit: `{exit_price}`
{profit_emoji} Profit: `${profit:.2f}`

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return self.send_message(text.strip())
    
    def send_error_alert(self, error_type, message):
        """Send error notification"""
        text = f"""
 *Error Alert*

 Type: {error_type}
 Message: {message}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(text.strip())
    
    def send_daily_summary(self, trades_count, profit, win_rate, balance, equity):
        """
        Send daily trading summary
        
        Args:
            trades_count: Number of trades today
            profit: Total profit/loss
            win_rate: Win rate percentage
            balance: Current balance
            equity: Current equity
        """
        emoji = "" if profit >= 0 else ""
        
        text = f"""
 *Daily Trading Summary*

📅 {datetime.now().strftime('%Y-%m-%d')}

🔢 Trades: `{trades_count}`
{emoji} P&L: `${profit:.2f}`
 Win Rate: `{win_rate:.1f}%`
💵 Balance: `${balance:.2f}`
 Equity: `${equity:.2f}`
        """
        
        return self.send_message(text.strip())
    
    def send_health_alert(self, status, issues=None):
        """
        Send health check alert
        
        Args:
            status: 'PASS', 'WARNING', or 'FAIL'
            issues: List of issue descriptions
        """
        if status == 'PASS':
            emoji = ""
            title = "Health Check: OK"
        elif status == 'WARNING':
            emoji = ""
            title = "Health Check: Warning"
        else:
            emoji = ""
            title = "Health Check: FAILED"
        
        text = f"{emoji} *{title}*\n\n"
        
        if issues:
            text += "Issues:\n"
            for issue in issues:
                text += f"• {issue}\n"
        
        text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(text.strip())
    
    def send_custom_alert(self, title, details, level='INFO'):
        """
        Send custom alert
        
        Args:
            title: Alert title
            details: Alert details (dict or string)
            level: 'INFO', 'WARNING', 'ERROR'
        """
        emoji_map = {
            'INFO': '',
            'WARNING': '',
            'ERROR': ''
        }
        
        emoji = emoji_map.get(level, '')
        text = f"{emoji} *{title}*\n\n"
        
        if isinstance(details, dict):
            for key, value in details.items():
                text += f"• {key}: `{value}`\n"
        else:
            text += str(details)
        
        text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(text.strip())


# Example usage and testing
def test_notifier():
    """Test Telegram notifier"""
    print("="*60)
    print("Testing Telegram Notifier")
    print("="*60)
    
    try:
        # Create notifier (will use environment variables)
        notifier = TelegramNotifier()
        
        # Test 1: Simple message
        print("\n1. Sending simple message...")
        notifier.send_message(" Test message from MT5 Bot!")
        
        # Test 2: Startup alert
        print("2. Sending startup alert...")
        notifier.send_startup_alert("MT5 SuperTrend Bot")
        
        # Test 3: Trade alert
        print("3. Sending trade alert...")
        notifier.send_trade_alert(
            order_type="BUY",
            symbol="BTCUSD",
            volume=0.1,
            price=45000.0,
            sl=44500.0,
            tp=46000.0
        )
        
        # Test 4: Daily summary
        print("4. Sending daily summary...")
        notifier.send_daily_summary(
            trades_count=5,
            profit=125.50,
            win_rate=60.0,
            balance=10125.50,
            equity=10150.25
        )
        
        # Test 5: Health alert
        print("5. Sending health alert...")
        notifier.send_health_alert('WARNING', [
            'High CPU usage: 85%',
            'Low disk space: 500MB remaining'
        ])
        
        print("\n All tests completed!")
        print("Check your Telegram for messages")
        
    except Exception as e:
        print(f"\n Error: {e}")
        print("\nSetup instructions:")
        print("1. Create bot with @BotFather")
        print("2. Get chat ID from @userinfobot")
        print("3. Set environment variables:")
        print("   set TELEGRAM_BOT_TOKEN=your_bot_token")
        print("   set TELEGRAM_CHAT_ID=your_chat_id")


if __name__ == "__main__":
    test_notifier()
