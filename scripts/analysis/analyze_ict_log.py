#!/usr/bin/env python3
"""
ICT Bot Log Analyzer
Phân tích log file và tạo báo cáo thống kê
Author: xPOURY4
"""

import re
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict
import json


class ICTLogAnalyzer:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.trades = []
        self.signals = []
        self.errors = []
        
    def parse_log(self):
        """Parse log file và extract thông tin"""
        print(f"📖 Đọc log file: {self.log_file}")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_position = None
        
        for line in lines:
            # Parse OPEN positions (cả 2 formats)
            if '[OPEN]' in line:
                open_match = re.search(
                    r'\[OPEN\] (BUY|SELL) at ([\d.]+), SL: ([\d.]+), TP: ([\d.]+), Size: ([\d.]+), Conditions: (\d+)',
                    line
                )
                if open_match:
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else None
                    
                    current_position = {
                        'timestamp': timestamp,
                        'type': open_match.group(1),
                        'entry_price': float(open_match.group(2)),
                        'sl': float(open_match.group(3)),
                        'tp': float(open_match.group(4)),
                        'size': float(open_match.group(5)),
                        'conditions': int(open_match.group(6))
                    }
            
            # Parse CLOSE positions - Live Bot Format (with Position #)
            elif '[CLOSE]' in line and 'Position #' in line:
                close_match = re.search(
                    r'\[CLOSE\] Position #(\d+) - (.*)',
                    line
                )
                if close_match and current_position:
                    ticket = close_match.group(1)
                    reason = close_match.group(2)
                    current_position['ticket'] = ticket
                    current_position['reason'] = reason
            
            # Parse CLOSE positions - Backtest Format (with P&L directly)
            elif '[CLOSE]' in line and 'P&L:' in line:
                close_match = re.search(
                    r'\[CLOSE\] (BUY|SELL) at ([\d.]+), P&L: \$([\d.-]+) \(([\d.-]+) pips\) - (.*)',
                    line
                )
                if close_match:
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    
                    # Create trade from backtest format
                    trade = {
                        'timestamp': timestamp_match.group(1) if timestamp_match else None,
                        'type': close_match.group(1),
                        'close_price': float(close_match.group(2)),
                        'profit': float(close_match.group(3)),
                        'pips': float(close_match.group(4)),
                        'reason': close_match.group(5),
                        'ticket': 'BT_' + str(len(self.trades) + 1)
                    }
                    
                    # Match with current_position if exists
                    if current_position:
                        trade.update({
                            'entry_price': current_position['entry_price'],
                            'sl': current_position['sl'],
                            'tp': current_position['tp'],
                            'size': current_position['size'],
                            'conditions': current_position['conditions']
                        })
                        current_position = None
                    
                    self.trades.append(trade)
            
            # Parse profit/balance line (Live Bot format)
            elif 'Profit:' in line and 'Balance:' in line:
                profit_match = re.search(
                    r'Profit: \$([\d.-]+) \| Balance: \$([\d.]+) \| Equity: \$([\d.]+)',
                    line
                )
                if profit_match and current_position:
                    current_position['profit'] = float(profit_match.group(1))
                    current_position['balance'] = float(profit_match.group(2))
                    current_position['equity'] = float(profit_match.group(3))
            
            # Parse win rate line (Live Bot format)
            elif 'Win Rate:' in line and current_position and 'profit' in current_position:
                stats_match = re.search(
                    r'Total: (\d+) trades \| Win: (\d+) \| Loss: (\d+) \| Win Rate: ([\d.]+)%',
                    line
                )
                if stats_match:
                    current_position['total_trades_at_close'] = int(stats_match.group(1))
                    current_position['wins_at_close'] = int(stats_match.group(2))
                    current_position['losses_at_close'] = int(stats_match.group(3))
                    current_position['win_rate_at_close'] = float(stats_match.group(4))
                    
                    # Add to trades list
                    self.trades.append(current_position)
                    current_position = None
            
            # Parse signals
            elif '[ANALYZING]' in line:
                signal_match = re.search(
                    r'\[ANALYZING\] Signal detected: (BUY|SELL), Conditions: (\d+)',
                    line
                )
                if signal_match:
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    self.signals.append({
                        'timestamp': timestamp_match.group(1) if timestamp_match else None,
                        'type': signal_match.group(1),
                        'conditions': int(signal_match.group(2))
                    })
            
            # Parse errors
            elif 'ERROR' in line or 'FAILED' in line.upper():
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                self.errors.append({
                    'timestamp': timestamp_match.group(1) if timestamp_match else None,
                    'message': line.strip()
                })
        
        print(f"✅ Tìm thấy: {len(self.trades)} trades, {len(self.signals)} signals, {len(self.errors)} errors")
    
    def calculate_statistics(self) -> Dict:
        """Tính toán thống kê từ trades"""
        if not self.trades:
            return {}
        
        df = pd.DataFrame(self.trades)
        
        total_trades = len(df)
        winning_trades = len(df[df['profit'] > 0])
        losing_trades = len(df[df['profit'] < 0])
        breakeven_trades = len(df[df['profit'] == 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = df['profit'].sum()
        gross_profit = df[df['profit'] > 0]['profit'].sum() if winning_trades > 0 else 0
        gross_loss = abs(df[df['profit'] < 0]['profit'].sum()) if losing_trades > 0 else 0
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        avg_win = df[df['profit'] > 0]['profit'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['profit'] < 0]['profit'].mean() if losing_trades > 0 else 0
        
        max_win = df['profit'].max() if total_trades > 0 else 0
        max_loss = df['profit'].min() if total_trades > 0 else 0
        
        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for profit in df['profit']:
            if profit > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            elif profit < 0:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        # Trading hours analysis
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        best_hour = df.groupby('hour')['profit'].sum().idxmax() if total_trades > 0 else None
        worst_hour = df.groupby('hour')['profit'].sum().idxmin() if total_trades > 0 else None
        
        # Trade type analysis
        buy_trades = df[df['type'] == 'BUY']
        sell_trades = df[df['type'] == 'SELL']
        
        buy_win_rate = (len(buy_trades[buy_trades['profit'] > 0]) / len(buy_trades) * 100) if len(buy_trades) > 0 else 0
        sell_win_rate = (len(sell_trades[sell_trades['profit'] > 0]) / len(sell_trades) * 100) if len(sell_trades) > 0 else 0
        
        # Balance progression
        if 'balance' in df.columns:
            initial_balance = df['balance'].iloc[0] - df['profit'].iloc[0] if total_trades > 0 else 0
            final_balance = df['balance'].iloc[-1] if total_trades > 0 else 0
        else:
            # For backtest, calculate cumulative balance
            initial_balance = 10000.0  # Default backtest initial balance
            df['cumulative_profit'] = df['profit'].cumsum()
            df['balance'] = initial_balance + df['cumulative_profit']
            final_balance = df['balance'].iloc[-1] if total_trades > 0 else initial_balance
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_win': max_win,
            'max_loss': max_loss,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'best_hour': best_hour,
            'worst_hour': worst_hour,
            'buy_trades': len(buy_trades),
            'buy_win_rate': buy_win_rate,
            'sell_trades': len(sell_trades),
            'sell_win_rate': sell_win_rate,
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_return': ((final_balance - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
        }
    
    def generate_report(self, output_format='console'):
        """Tạo báo cáo thống kê"""
        stats = self.calculate_statistics()
        
        if not stats:
            print("❌ Không có dữ liệu để phân tích!")
            return
        
        # Console report
        if output_format in ['console', 'all']:
            self._print_console_report(stats)
        
        # CSV report
        if output_format in ['csv', 'all']:
            self._save_csv_report()
        
        # JSON report
        if output_format in ['json', 'all']:
            self._save_json_report(stats)
        
        # HTML report
        if output_format in ['html', 'all']:
            self._save_html_report(stats)
    
    def _print_console_report(self, stats: Dict):
        """In báo cáo ra console"""
        print("\n" + "="*80)
        print("📊 ICT BOT - BÁO CÁO THỐNG KÊ TRADING")
        print("="*80)
        
        print(f"\n📈 TỔNG QUAN:")
        print(f"   Tổng số trades      : {stats['total_trades']}")
        print(f"   Trades thắng        : {stats['winning_trades']} ({stats['win_rate']:.2f}%)")
        print(f"   Trades thua         : {stats['losing_trades']} ({100-stats['win_rate']:.2f}%)")
        print(f"   Trades hòa          : {stats['breakeven_trades']}")
        
        print(f"\n💰 LỢI NHUẬN:")
        print(f"   Tổng P/L            : ${stats['total_profit']:,.2f}")
        print(f"   Gross Profit        : ${stats['gross_profit']:,.2f}")
        print(f"   Gross Loss          : ${stats['gross_loss']:,.2f}")
        print(f"   Profit Factor       : {stats['profit_factor']:.2f}")
        
        print(f"\n📊 TRUNG BÌNH:")
        print(f"   Avg Win             : ${stats['avg_win']:,.2f}")
        print(f"   Avg Loss            : ${stats['avg_loss']:,.2f}")
        print(f"   Win/Loss Ratio      : {abs(stats['avg_win']/stats['avg_loss']):.2f}" if stats['avg_loss'] != 0 else "N/A")
        
        print(f"\n🎯 RECORDS:")
        print(f"   Max Win             : ${stats['max_win']:,.2f}")
        print(f"   Max Loss            : ${stats['max_loss']:,.2f}")
        print(f"   Max Consecutive Wins : {stats['max_consecutive_wins']}")
        print(f"   Max Consecutive Loss : {stats['max_consecutive_losses']}")
        
        print(f"\n📅 PHÂN TÍCH THEO GIỜ:")
        print(f"   Giờ tốt nhất        : {stats['best_hour']}:00")
        print(f"   Giờ tệ nhất         : {stats['worst_hour']}:00")
        
        print(f"\n🔄 PHÂN TÍCH THEO LOẠI:")
        print(f"   BUY Trades          : {stats['buy_trades']} ({stats['buy_win_rate']:.2f}% win rate)")
        print(f"   SELL Trades         : {stats['sell_trades']} ({stats['sell_win_rate']:.2f}% win rate)")
        
        print(f"\n💵 BALANCE:")
        print(f"   Initial Balance     : ${stats['initial_balance']:,.2f}")
        print(f"   Final Balance       : ${stats['final_balance']:,.2f}")
        print(f"   Total Return        : {stats['total_return']:.2f}%")
        
        print(f"\n⚠️  ERRORS/WARNINGS:")
        print(f"   Tổng số errors      : {len(self.errors)}")
        
        print(f"\n🎯 SIGNALS:")
        print(f"   Tổng số signals     : {len(self.signals)}")
        print(f"   Signals → Trades    : {(len(self.trades)/len(self.signals)*100):.2f}%" if self.signals else "N/A")
        
        print("\n" + "="*80)
    
    def _save_csv_report(self):
        """Lưu trades vào CSV"""
        if not self.trades:
            return
        
        df = pd.DataFrame(self.trades)
        output_file = f"reports/ict_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Path("reports").mkdir(exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"✅ CSV report saved: {output_file}")
    
    def _save_json_report(self, stats: Dict):
        """Lưu stats vào JSON"""
        output_file = f"reports/ict_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path("reports").mkdir(exist_ok=True)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'log_file': self.log_file,
            'statistics': stats,
            'trades': self.trades,
            'signals_count': len(self.signals),
            'errors_count': len(self.errors)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON report saved: {output_file}")
    
    def _save_html_report(self, stats: Dict):
        """Tạo báo cáo HTML"""
        output_file = f"reports/ict_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        Path("reports").mkdir(exist_ok=True)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ICT Bot Trading Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .stat-label {{ font-size: 14px; color: #7f8c8d; text-transform: uppercase; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #2c3e50; margin-top: 5px; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 ICT Bot Trading Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📈 Tổng Quan</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Trades</div>
                <div class="stat-value">{stats['total_trades']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value {'positive' if stats['win_rate'] > 50 else 'negative'}">{stats['win_rate']:.2f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Profit Factor</div>
                <div class="stat-value {'positive' if stats['profit_factor'] > 1 else 'negative'}">{stats['profit_factor']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Net P/L</div>
                <div class="stat-value {'positive' if stats['total_profit'] > 0 else 'negative'}">${stats['total_profit']:,.2f}</div>
            </div>
        </div>
        
        <h2>💰 Chi Tiết Lợi Nhuận</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Gross Profit</td><td class="positive">${stats['gross_profit']:,.2f}</td></tr>
            <tr><td>Gross Loss</td><td class="negative">${stats['gross_loss']:,.2f}</td></tr>
            <tr><td>Average Win</td><td>${stats['avg_win']:,.2f}</td></tr>
            <tr><td>Average Loss</td><td>${stats['avg_loss']:,.2f}</td></tr>
            <tr><td>Max Win</td><td>${stats['max_win']:,.2f}</td></tr>
            <tr><td>Max Loss</td><td>${stats['max_loss']:,.2f}</td></tr>
        </table>
        
        <h2>🔄 Phân Tích Theo Loại</h2>
        <table>
            <tr><th>Type</th><th>Trades</th><th>Win Rate</th></tr>
            <tr><td>BUY</td><td>{stats['buy_trades']}</td><td>{stats['buy_win_rate']:.2f}%</td></tr>
            <tr><td>SELL</td><td>{stats['sell_trades']}</td><td>{stats['sell_win_rate']:.2f}%</td></tr>
        </table>
        
        <h2>💵 Balance</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Initial Balance</td><td>${stats['initial_balance']:,.2f}</td></tr>
            <tr><td>Final Balance</td><td>${stats['final_balance']:,.2f}</td></tr>
            <tr><td>Total Return</td><td class="{'positive' if stats['total_return'] > 0 else 'negative'}">{stats['total_return']:.2f}%</td></tr>
        </table>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML report saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Phân tích ICT Bot log file')
    parser.add_argument('--log', default='logs/ict_bot_20251016.log', help='Path to log file')
    parser.add_argument('--format', choices=['console', 'csv', 'json', 'html', 'all'], 
                       default='all', help='Output format')
    
    args = parser.parse_args()
    
    # Check if log file exists
    if not Path(args.log).exists():
        print(f"❌ Log file not found: {args.log}")
        print("📁 Available log files:")
        for log_file in Path('logs').glob('ict_bot_*.log'):
            print(f"   - {log_file}")
        return
    
    # Analyze log
    analyzer = ICTLogAnalyzer(args.log)
    analyzer.parse_log()
    analyzer.generate_report(output_format=args.format)


if __name__ == "__main__":
    main()
