"""
Trade Analytics Plugin Example

This plugin tracks and analyzes trading performance including:
- Win rate and profit factor
- Average win/loss ratio
- Best/worst trades
- Time-based analytics (best hours, days)
- Symbol performance
- Export reports to JSON/CSV

Hook Usage:
- after_trade: Record trade entry
- on_position_close: Calculate trade metrics
- daily_end: Generate daily report
- weekly_end: Generate weekly summary

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.plugin_system import BasePlugin
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging


class TradeAnalytics(BasePlugin):
    """
    Trade Analytics Plugin
    
    Features:
    - Real-time performance tracking
    - Win rate and profit factor calculation
    - Best/worst trade identification
    - Time-based performance analysis
    - Symbol-specific metrics
    - Export to JSON/CSV
    
    Configuration:
        {
            'track_time_performance': True,  # Analyze by hour/day
            'track_symbol_performance': True,  # Per-symbol stats
            'export_daily_report': True,     # Auto-export daily
            'report_path': './reports/',     # Export directory
            'keep_history_days': 90          # How long to keep data
        }
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Configuration
        self.track_time_performance = config.get('track_time_performance', True)
        self.track_symbol_performance = config.get('track_symbol_performance', True)
        self.export_daily_report = config.get('export_daily_report', True)
        self.report_path = config.get('report_path', './reports/')
        self.keep_history_days = config.get('keep_history_days', 90)
        
        # Trade storage
        self.trades = []  # All completed trades
        self.open_trades = {}  # Currently open trades
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.break_even_trades = 0
        
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        
        # Best/worst tracking
        self.best_trade = None
        self.worst_trade = None
        self.largest_win = 0.0
        self.largest_loss = 0.0
        
        # Time-based analytics
        self.trades_by_hour = defaultdict(list)
        self.trades_by_day = defaultdict(list)
        self.trades_by_symbol = defaultdict(list)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Trade Analytics initialized")
    
    def get_name(self) -> str:
        return "TradeAnalytics"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def record_trade_entry(self, context: Dict):
        """Record when a trade is opened"""
        trade_id = context.get('ticket', f"trade_{len(self.open_trades)}")
        
        trade_data = {
            'ticket': trade_id,
            'symbol': context.get('symbol'),
            'type': context.get('type'),  # 'BUY' or 'SELL'
            'entry_price': context.get('price'),
            'entry_time': datetime.now(),
            'position_size': context.get('position_size'),
            'stop_loss': context.get('stop_loss'),
            'take_profit': context.get('take_profit'),
        }
        
        self.open_trades[trade_id] = trade_data
        
        self.logger.info(f"Trade entry recorded: {trade_id} - {trade_data['symbol']}")
    
    def record_trade_exit(self, context: Dict):
        """Record when a trade is closed and calculate metrics"""
        trade_id = context.get('ticket')
        
        if trade_id not in self.open_trades:
            self.logger.warning(f"Trade {trade_id} not found in open trades")
            return
        
        # Get entry data
        entry_data = self.open_trades.pop(trade_id)
        
        # Calculate trade results
        exit_price = context.get('price')
        profit = context.get('profit', 0)
        
        # Complete trade record
        trade_record = {
            **entry_data,
            'exit_price': exit_price,
            'exit_time': datetime.now(),
            'profit': profit,
            'profit_pct': (profit / context.get('account_balance', 1)) * 100,
            'duration_minutes': (datetime.now() - entry_data['entry_time']).seconds / 60,
            'exit_reason': context.get('exit_reason', 'unknown'),
        }
        
        # Add to trades list
        self.trades.append(trade_record)
        
        # Update metrics
        self.update_metrics(trade_record)
        
        # Track by time/symbol if enabled
        if self.track_time_performance:
            hour = trade_record['entry_time'].hour
            day = trade_record['entry_time'].strftime('%A')
            self.trades_by_hour[hour].append(trade_record)
            self.trades_by_day[day].append(trade_record)
        
        if self.track_symbol_performance:
            symbol = trade_record['symbol']
            self.trades_by_symbol[symbol].append(trade_record)
        
        self.logger.info(
            f"Trade closed: {trade_id} - "
            f"Profit: ${profit:.2f} ({trade_record['profit_pct']:.2f}%)"
        )
    
    def update_metrics(self, trade: Dict):
        """Update performance metrics with new trade"""
        self.total_trades += 1
        profit = trade['profit']
        
        # Categorize trade
        if profit > 0:
            self.winning_trades += 1
            self.gross_profit += profit
            
            # Update best trade
            if profit > self.largest_win:
                self.largest_win = profit
                self.best_trade = trade
        
        elif profit < 0:
            self.losing_trades += 1
            self.gross_loss += abs(profit)
            
            # Update worst trade
            if profit < self.largest_loss:
                self.largest_loss = profit
                self.worst_trade = trade
        
        else:
            self.break_even_trades += 1
        
        # Update totals
        self.total_profit += profit
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        
        return (self.winning_trades / self.total_trades) * 100
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if self.gross_loss == 0:
            return float('inf') if self.gross_profit > 0 else 0.0
        
        return self.gross_profit / self.gross_loss
    
    def calculate_average_win(self) -> float:
        """Calculate average winning trade"""
        if self.winning_trades == 0:
            return 0.0
        
        return self.gross_profit / self.winning_trades
    
    def calculate_average_loss(self) -> float:
        """Calculate average losing trade"""
        if self.losing_trades == 0:
            return 0.0
        
        return self.gross_loss / self.losing_trades
    
    def calculate_expectancy(self) -> float:
        """
        Calculate expectancy (average profit per trade)
        
        Formula: (Win% × Avg Win) - (Loss% × Avg Loss)
        """
        if self.total_trades == 0:
            return 0.0
        
        win_rate = self.calculate_win_rate() / 100
        loss_rate = (self.losing_trades / self.total_trades)
        
        avg_win = self.calculate_average_win()
        avg_loss = self.calculate_average_loss()
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        
        return expectancy
    
    def get_best_trading_hours(self, top_n: int = 3) -> List[Dict]:
        """Get best performing hours"""
        if not self.track_time_performance:
            return []
        
        hour_performance = []
        
        for hour, trades in self.trades_by_hour.items():
            total_profit = sum(t['profit'] for t in trades)
            win_rate = (sum(1 for t in trades if t['profit'] > 0) / len(trades)) * 100 if trades else 0
            
            hour_performance.append({
                'hour': hour,
                'trades': len(trades),
                'profit': total_profit,
                'win_rate': win_rate,
            })
        
        # Sort by profit
        hour_performance.sort(key=lambda x: x['profit'], reverse=True)
        
        return hour_performance[:top_n]
    
    def get_best_trading_days(self) -> List[Dict]:
        """Get best performing days of week"""
        if not self.track_time_performance:
            return []
        
        day_performance = []
        
        for day, trades in self.trades_by_day.items():
            total_profit = sum(t['profit'] for t in trades)
            win_rate = (sum(1 for t in trades if t['profit'] > 0) / len(trades)) * 100 if trades else 0
            
            day_performance.append({
                'day': day,
                'trades': len(trades),
                'profit': total_profit,
                'win_rate': win_rate,
            })
        
        # Sort by profit
        day_performance.sort(key=lambda x: x['profit'], reverse=True)
        
        return day_performance
    
    def get_symbol_performance(self) -> List[Dict]:
        """Get performance by symbol"""
        if not self.track_symbol_performance:
            return []
        
        symbol_perf = []
        
        for symbol, trades in self.trades_by_symbol.items():
            total_profit = sum(t['profit'] for t in trades)
            win_rate = (sum(1 for t in trades if t['profit'] > 0) / len(trades)) * 100 if trades else 0
            
            symbol_perf.append({
                'symbol': symbol,
                'trades': len(trades),
                'profit': total_profit,
                'win_rate': win_rate,
            })
        
        # Sort by profit
        symbol_perf.sort(key=lambda x: x['profit'], reverse=True)
        
        return symbol_perf
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive performance summary"""
        return {
            'overview': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'break_even_trades': self.break_even_trades,
                'win_rate': round(self.calculate_win_rate(), 2),
                'total_profit': round(self.total_profit, 2),
            },
            'metrics': {
                'profit_factor': round(self.calculate_profit_factor(), 2),
                'average_win': round(self.calculate_average_win(), 2),
                'average_loss': round(self.calculate_average_loss(), 2),
                'expectancy': round(self.calculate_expectancy(), 2),
                'largest_win': round(self.largest_win, 2),
                'largest_loss': round(self.largest_loss, 2),
            },
            'best_hours': self.get_best_trading_hours(3),
            'day_performance': self.get_best_trading_days(),
            'symbol_performance': self.get_symbol_performance(),
        }
    
    def export_report(self, filename: Optional[str] = None):
        """Export analytics report to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.report_path}/analytics_{timestamp}.json"
        
        report = self.generate_summary_report()
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Report exported to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
    
    def after_trade(self, context: Dict) -> Dict:
        """Hook: Record trade entry"""
        self.record_trade_entry(context)
        return context
    
    def on_position_close(self, context: Dict) -> Dict:
        """Hook: Record trade exit and update analytics"""
        self.record_trade_exit(context)
        return context
    
    def daily_end(self, context: Dict) -> Dict:
        """Hook: Generate daily report"""
        if self.export_daily_report:
            self.export_report()
        
        # Print daily summary
        summary = self.generate_summary_report()
        
        self.logger.info("=" * 60)
        self.logger.info("DAILY PERFORMANCE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Trades: {summary['overview']['total_trades']}")
        self.logger.info(f"Win Rate: {summary['overview']['win_rate']}%")
        self.logger.info(f"Total Profit: ${summary['overview']['total_profit']}")
        self.logger.info(f"Profit Factor: {summary['metrics']['profit_factor']}")
        self.logger.info("=" * 60)
        
        return context
    
    def get_status(self) -> Dict:
        """Get current analytics status"""
        return {
            'total_trades': self.total_trades,
            'win_rate': round(self.calculate_win_rate(), 2),
            'profit_factor': round(self.calculate_profit_factor(), 2),
            'total_profit': round(self.total_profit, 2),
            'open_positions': len(self.open_trades),
        }


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'track_time_performance': True,
        'track_symbol_performance': True,
        'export_daily_report': False,  # Don't export in example
        'report_path': './reports/',
    }
    
    # Initialize plugin
    analytics = TradeAnalytics(config)
    
    print("\n" + "=" * 60)
    print(f"Plugin: {analytics.get_name()} v{analytics.get_version()}")
    print("=" * 60)
    
    # Simulate some trades
    print("\nSimulating trades...")
    
    # Trade 1: Winner
    analytics.after_trade({
        'ticket': 'T001',
        'symbol': 'EURUSD',
        'type': 'BUY',
        'price': 1.1000,
        'position_size': 0.1,
        'stop_loss': 1.0950,
        'take_profit': 1.1100,
    })
    
    analytics.on_position_close({
        'ticket': 'T001',
        'price': 1.1050,
        'profit': 50.00,
        'account_balance': 10000,
        'exit_reason': 'take_profit',
    })
    
    # Trade 2: Loser
    analytics.after_trade({
        'ticket': 'T002',
        'symbol': 'GBPUSD',
        'type': 'SELL',
        'price': 1.2500,
        'position_size': 0.1,
        'stop_loss': 1.2550,
        'take_profit': 1.2400,
    })
    
    analytics.on_position_close({
        'ticket': 'T002',
        'price': 1.2540,
        'profit': -40.00,
        'account_balance': 10000,
        'exit_reason': 'stop_loss',
    })
    
    # Generate report
    print("\nGenerating performance report...")
    print("-" * 60)
    
    report = analytics.generate_summary_report()
    
    print("\nOverview:")
    for key, value in report['overview'].items():
        print(f"  {key}: {value}")
    
    print("\nMetrics:")
    for key, value in report['metrics'].items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60 + "\n")
