#!/usr/bin/env python3
"""
Telegram Alert System for ML-SuperTrend Bot
Send notifications to Telegram when trades are opened/closed or errors occur
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional


class TelegramAlert:
    """Telegram notification system"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram bot
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> Optional[Dict]:
        """
        Send message to Telegram
        
        Args:
            message: Message text
            parse_mode: HTML or Markdown
            
        Returns:
            Response JSON or None if failed
        """
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Telegram alert failed: {e}")
            return None
    
    def send_trade_opened(self, trade_info: Dict) -> None:
        """
        Send notification when trade is opened
        
        Args:
            trade_info: Dictionary with trade details
        """
        signal_type = trade_info.get('type', 'UNKNOWN')
        emoji = '' if signal_type == 'BUY' else '' if signal_type == 'SELL' else '⚪'
        
        message = f"""
{emoji} <b>TRADE OPENED</b>

 <b>Symbol:</b> {trade_info.get('symbol', 'N/A')}
{' <b>BUY</b>' if signal_type == 'BUY' else ' <b>SELL</b>'}

 <b>Entry Price:</b> ${trade_info.get('entry', 0):.2f}
🛡️ <b>Stop Loss:</b> ${trade_info.get('sl', 0):.2f}
 <b>Take Profit:</b> ${trade_info.get('tp', 0):.2f}

 <b>Lot Size:</b> {trade_info.get('lot_size', 0):.2f}
💵 <b>Risk Amount:</b> ${trade_info.get('risk_amount', 0):.2f}
 <b>R:R Ratio:</b> {trade_info.get('rr_ratio', 0):.1f}:1

{f" <b>Strategy:</b> {trade_info.get('strategy', 'N/A')}" if 'strategy' in trade_info else ''}
{f" <b>Signal Quality:</b> {trade_info.get('quality', 0):.1f}%" if 'quality' in trade_info else ''}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_trade_closed(self, trade_info: Dict) -> None:
        """
        Send notification when trade is closed
        
        Args:
            trade_info: Dictionary with trade result details
        """
        profit = trade_info.get('profit', 0)
        is_profit = profit > 0
        emoji = '' if is_profit else ''
        
        message = f"""
{emoji} <b>TRADE CLOSED</b>

 <b>Symbol:</b> {trade_info.get('symbol', 'N/A')}
{' BUY' if trade_info.get('type') == 'BUY' else ' SELL'}

{' <b>PROFIT:</b> ' if is_profit else '💸 <b>LOSS:</b> '}<b>${abs(profit):.2f}</b>

 <b>Entry:</b> ${trade_info.get('entry', 0):.2f}
 <b>Exit:</b> ${trade_info.get('exit', 0):.2f}
 <b>Pips:</b> {trade_info.get('pips', 0):.1f}

⏱️ <b>Duration:</b> {trade_info.get('duration', 'N/A')}
 <b>Exit Reason:</b> {trade_info.get('exit_reason', 'N/A')}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_dual_orders_opened(self, order1_info: Dict, order2_info: Dict) -> None:
        """
        Send notification for dual orders
        
        Args:
            order1_info: Order 1 (RR 1:1) details
            order2_info: Order 2 (Main RR) details
        """
        signal_type = order1_info.get('type', 'UNKNOWN')
        emoji = '' if signal_type == 'BUY' else ''
        
        message = f"""
{emoji}{emoji} <b>DUAL ORDERS OPENED</b>

 <b>Symbol:</b> {order1_info.get('symbol', 'N/A')}
{' <b>BUY</b>' if signal_type == 'BUY' else ' <b>SELL</b>'}

 <b>Entry Price:</b> ${order1_info.get('entry', 0):.2f}
🛡️ <b>Stop Loss:</b> ${order1_info.get('sl', 0):.2f}

<b>ORDER 1 (Quick Profit - RR 1:1):</b>
 TP1: ${order1_info.get('tp', 0):.2f}
 Lot: {order1_info.get('lot_size', 0):.2f}
💵 Risk: ${order1_info.get('risk_amount', 0):.2f}

<b>ORDER 2 (Main Target - RR {order2_info.get('rr_ratio', 0):.1f}:1):</b>
 TP2: ${order2_info.get('tp', 0):.2f}
 Lot: {order2_info.get('lot_size', 0):.2f}
💵 Risk: ${order2_info.get('risk_amount', 0):.2f}

 <b>Total Risk:</b> ${order1_info.get('risk_amount', 0) + order2_info.get('risk_amount', 0):.2f}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_error_alert(self, error_msg: str, error_type: str = "ERROR") -> None:
        """
        Send error notification
        
        Args:
            error_msg: Error message
            error_type: Type of error (ERROR, WARNING, CRITICAL)
        """
        emoji = '' if error_type == 'WARNING' else '' if error_type == 'ERROR' else ''
        
        message = f"""
{emoji} <b>{error_type}</b>

{error_msg}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_bot_started(self, bot_info: Dict) -> None:
        """
        Send notification when bot starts
        
        Args:
            bot_info: Bot configuration info
        """
        message = f"""
🤖 <b>BOT STARTED</b>

 <b>Symbol:</b> {bot_info.get('symbol', 'N/A')}
⏱️ <b>Timeframe:</b> {bot_info.get('timeframe', 'N/A')}
 <b>Strategy:</b> {bot_info.get('strategy', 'N/A')}
 <b>Account Balance:</b> ${bot_info.get('balance', 0):.2f}
 <b>Risk per Trade:</b> {bot_info.get('risk_percent', 0):.2f}%
 <b>R:R Ratio:</b> {bot_info.get('rr_ratio', 0):.1f}:1

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_bot_stopped(self, reason: str = "Manual stop") -> None:
        """
        Send notification when bot stops
        
        Args:
            reason: Reason for stopping
        """
        message = f"""
🛑 <b>BOT STOPPED</b>

 <b>Reason:</b> {reason}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.send_message(message.strip())
    
    def send_daily_report(self, stats: Dict) -> None:
        """
        Send daily performance report
        
        Args:
            stats: Daily statistics
        """
        pnl = stats.get('pnl', 0)
        is_profit = pnl > 0
        emoji = '' if is_profit else ''
        
        message = f"""
{emoji} <b>DAILY PERFORMANCE REPORT</b>

 <b>P&L:</b> ${pnl:.2f} ({'+' if is_profit else ''}{stats.get('pnl_percent', 0):.2f}%)
 <b>Win Rate:</b> {stats.get('win_rate', 0):.1f}%
 <b>Profit Factor:</b> {stats.get('profit_factor', 0):.2f}

 <b>Total Trades:</b> {stats.get('total_trades', 0)}
 <b>Wins:</b> {stats.get('wins', 0)}
 <b>Losses:</b> {stats.get('losses', 0)}

💵 <b>Avg Win:</b> ${stats.get('avg_win', 0):.2f}
💸 <b>Avg Loss:</b> ${stats.get('avg_loss', 0):.2f}

 <b>Current Balance:</b> ${stats.get('balance', 0):.2f}
 <b>Max Drawdown:</b> {stats.get('max_dd', 0):.2f}%

⏰ <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}
        """
        
        self.send_message(message.strip())
    
    def send_weekly_report(self, stats: Dict) -> None:
        """
        Send weekly performance report
        
        Args:
            stats: Weekly statistics
        """
        message = f"""
 <b>WEEKLY PERFORMANCE REPORT</b>

 <b>Week P&L:</b> ${stats.get('pnl', 0):.2f}
 <b>Return:</b> {stats.get('return_percent', 0):.2f}%
 <b>Win Rate:</b> {stats.get('win_rate', 0):.1f}%

 <b>Total Trades:</b> {stats.get('total_trades', 0)}
 <b>Wins:</b> {stats.get('wins', 0)}
 <b>Losses:</b> {stats.get('losses', 0)}

 <b>Best Day:</b> ${stats.get('best_day', 0):.2f}
 <b>Worst Day:</b> ${stats.get('worst_day', 0):.2f}

💵 <b>Current Balance:</b> ${stats.get('balance', 0):.2f}
 <b>Max DD (Week):</b> {stats.get('max_dd', 0):.2f}%

⏰ <b>Week:</b> {stats.get('week_label', 'N/A')}
        """
        
        self.send_message(message.strip())


# Example usage and setup instructions
if __name__ == "__main__":
    print("""
    ============================================
    TELEGRAM ALERT SETUP INSTRUCTIONS
    ============================================
    
    1. Create Telegram Bot:
       - Open Telegram and chat with @BotFather
       - Send: /newbot
       - Follow instructions to create bot
       - Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
    
    2. Get Your Chat ID:
       - Start a chat with your bot
       - Send any message to it
       - Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
       - Find "chat":{"id":YOUR_CHAT_ID} in the response
       - Copy the chat ID number
    
    3. Add to config.json:
       {
           "telegram": {
               "enabled": true,
               "bot_token": "YOUR_BOT_TOKEN",
               "chat_id": "YOUR_CHAT_ID"
           }
       }
    
    4. Test:
    """)
    
    # Example test
    BOT_TOKEN = input("Enter your bot token: ")
    CHAT_ID = input("Enter your chat ID: ")
    
    alert = TelegramAlert(BOT_TOKEN, CHAT_ID)
    
    # Test message
    print("\nSending test message...")
    result = alert.send_message(" <b>Telegram Alert System Connected!</b>\n\nYour bot is ready to send notifications.")
    
    if result:
        print(" Success! Check your Telegram.")
    else:
        print(" Failed. Check your credentials.")
