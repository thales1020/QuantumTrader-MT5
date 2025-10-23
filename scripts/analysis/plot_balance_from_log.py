#!/usr/bin/env python3
"""
Plot Balance Chart from ICT Bot Log
Vẽ biểu đồ balance progression từ log file
Author: xPOURY4
"""

import re
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict


class BalanceChartPlotter:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.balance_data = []
        
    def parse_log(self):
        """Parse log file và extract balance data"""
        print(f"📖 Đọc log file: {self.log_file}")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        initial_balance = None
        
        for line in lines:
            # Extract initial balance
            if 'Initial Balance:' in line:
                match = re.search(r'Initial Balance: \$?([\d,]+\.?\d*)', line)
                if match:
                    initial_balance = float(match.group(1).replace(',', ''))
                    # Add initial balance at start
                    if not self.balance_data:
                        # Try to get start date from log
                        date_match = re.search(r'Period: (\d{4}-\d{2}-\d{2})', line.split('Initial Balance')[0])
                        if date_match:
                            start_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                        else:
                            start_date = datetime.now()
                        
                        self.balance_data.append({
                            'time': start_date,
                            'balance': initial_balance,
                            'type': 'INITIAL'
                        })
            
            # Extract balance from CLOSE lines
            if '[CLOSE]' in line and 'Balance:' in line:
                # Parse timestamp
                time_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                # Parse balance
                balance_match = re.search(r'Balance: \$([\d,]+\.?\d*)', line)
                
                if time_match and balance_match:
                    timestamp = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                    balance = float(balance_match.group(1).replace(',', ''))
                    
                    # Determine if win or loss
                    profit_match = re.search(r'P&L: \$([\d.-]+)', line)
                    trade_type = 'WIN' if profit_match and float(profit_match.group(1)) > 0 else 'LOSS'
                    
                    self.balance_data.append({
                        'time': timestamp,
                        'balance': balance,
                        'type': trade_type
                    })
        
        print(f"✅ Tìm thấy {len(self.balance_data)} balance records")
        return len(self.balance_data) > 0
    
    def plot_balance_chart(self, output_file: str = None):
        """Vẽ biểu đồ balance progression"""
        if not self.balance_data:
            print("❌ Không có dữ liệu balance để vẽ!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.balance_data)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Calculate statistics
        initial_balance = df['balance'].iloc[0]
        final_balance = df['balance'].iloc[-1]
        total_return = ((final_balance - initial_balance) / initial_balance) * 100
        max_balance = df['balance'].max()
        min_balance = df['balance'].min()
        
        # Calculate drawdown
        df['peak'] = df['balance'].cummax()
        df['drawdown'] = ((df['balance'] - df['peak']) / df['peak']) * 100
        max_drawdown = df['drawdown'].min()
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[3, 1])
        fig.suptitle('ICT Bot Balance Progression', fontsize=16, fontweight='bold')
        
        # Plot 1: Balance curve
        ax1.plot(df['time'], df['balance'], linewidth=2, color='#2E86AB', label='Balance')
        ax1.fill_between(df['time'], initial_balance, df['balance'], 
                         where=(df['balance'] >= initial_balance), 
                         color='#27AE60', alpha=0.3, label='Profit Zone')
        ax1.fill_between(df['time'], initial_balance, df['balance'], 
                         where=(df['balance'] < initial_balance), 
                         color='#E74C3C', alpha=0.3, label='Loss Zone')
        
        # Mark wins and losses
        wins = df[df['type'] == 'WIN']
        losses = df[df['type'] == 'LOSS']
        
        ax1.scatter(wins['time'], wins['balance'], color='#27AE60', s=30, alpha=0.6, 
                   marker='^', label='Win Trades', zorder=5)
        ax1.scatter(losses['time'], losses['balance'], color='#E74C3C', s=30, alpha=0.6, 
                   marker='v', label='Loss Trades', zorder=5)
        
        # Initial balance line
        ax1.axhline(y=initial_balance, color='gray', linestyle='--', linewidth=1, 
                   alpha=0.7, label=f'Initial: ${initial_balance:,.0f}')
        
        # Formatting
        ax1.set_ylabel('Balance ($)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='upper left', framealpha=0.9)
        
        # Format x-axis with monthly ticks
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_minor_locator(mdates.WeekdayLocator())
        
        # Rotate x-axis labels
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add statistics text box
        stats_text = (
            f'Initial Balance: ${initial_balance:,.2f}\n'
            f'Final Balance: ${final_balance:,.2f}\n'
            f'Total Return: {total_return:+.2f}%\n'
            f'Max Balance: ${max_balance:,.2f}\n'
            f'Min Balance: ${min_balance:,.2f}\n'
            f'Max Drawdown: {max_drawdown:.2f}%\n'
            f'Total Trades: {len(df) - 1}'
        )
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
                verticalalignment='top', bbox=props, family='monospace')
        
        # Plot 2: Drawdown
        ax2.fill_between(df['time'], 0, df['drawdown'], color='#E74C3C', alpha=0.5)
        ax2.plot(df['time'], df['drawdown'], linewidth=1.5, color='#C0392B')
        ax2.set_ylabel('Drawdown (%)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
        
        # Format x-axis for drawdown plot
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_minor_locator(mdates.WeekdayLocator())
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Biểu đồ đã lưu: {output_file}")
        else:
            plt.show()
        
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Vẽ biểu đồ balance từ ICT Bot log')
    parser.add_argument('--log', default='logs/ict_bot_20251016.log', 
                       help='Path to log file')
    parser.add_argument('--output', default=None, 
                       help='Output file path (default: statistic/balance_chart_YYYYMMDD_HHMMSS.png)')
    
    args = parser.parse_args()
    
    # Check if log file exists
    if not Path(args.log).exists():
        print(f"❌ Log file not found: {args.log}")
        print("📁 Available log files:")
        for log_file in Path('logs').glob('ict_bot_*.log'):
            print(f"   - {log_file}")
        return
    
    # Default output path
    if args.output is None:
        Path('statistic').mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'statistic/balance_chart_{timestamp}.png'
    
    # Parse and plot
    plotter = BalanceChartPlotter(args.log)
    
    if plotter.parse_log():
        plotter.plot_balance_chart(args.output)
    else:
        print("❌ Không tìm thấy dữ liệu balance trong log file!")


if __name__ == "__main__":
    main()
