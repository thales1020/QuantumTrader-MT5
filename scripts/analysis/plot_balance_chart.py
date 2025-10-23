#!/usr/bin/env python3
"""
Balance Chart Plotter from Log Files
Vẽ biểu đồ balance progression từ ICT/SuperTrend bot log
Author: xPOURY4
"""

import re
import argparse
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict
import pandas as pd


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
            # Get initial balance from config
            if 'Initial Balance:' in line and initial_balance is None:
                match = re.search(r'Initial Balance: \$?([\d,]+\.?\d*)', line)
                if match:
                    initial_balance = float(match.group(1).replace(',', ''))
                    # Add initial balance at start
                    # Try to get start date from log
                    date_match = re.search(r'Period: (\d{4}-\d{2}-\d{2})', line)
                    if date_match:
                        start_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                    else:
                        # Use log timestamp
                        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                        if timestamp_match:
                            start_date = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d')
                        else:
                            start_date = datetime.now()
                    
                    self.balance_data.append({
                        'timestamp': start_date,
                        'balance': initial_balance
                    })
            
            # Parse CLOSE lines with balance (backtest format)
            if '[CLOSE]' in line and 'Balance:' in line:
                # Extract timestamp and balance
                timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                balance_match = re.search(r'Balance: \$([\d,]+\.?\d*)', line)
                
                if timestamp_match and balance_match:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    balance = float(balance_match.group(1).replace(',', ''))
                    
                    self.balance_data.append({
                        'timestamp': timestamp,
                        'balance': balance
                    })
            
            # Parse live bot format (alternative format)
            elif 'Balance:' in line and 'Equity:' in line and '[CLOSE]' not in line:
                # Format: "        Profit: $145.50 | Balance: $10,145.50 | Equity: $10,145.50"
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                balance_match = re.search(r'Balance: \$([\d,]+\.?\d*)', line)
                
                if timestamp_match and balance_match:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    balance = float(balance_match.group(1).replace(',', ''))
                    
                    self.balance_data.append({
                        'timestamp': timestamp,
                        'balance': balance
                    })
        
        if not self.balance_data:
            print("❌ Không tìm thấy dữ liệu balance trong log file!")
            return False
        
        print(f"✅ Tìm thấy {len(self.balance_data)} điểm balance")
        return True
    
    def plot_chart(self, output_file: str = None, show: bool = True):
        """Vẽ biểu đồ balance"""
        if not self.balance_data:
            print("❌ Không có dữ liệu để vẽ!")
            return
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(self.balance_data)
        df = df.sort_values('timestamp')
        
        # Calculate statistics
        initial_balance = df['balance'].iloc[0]
        final_balance = df['balance'].iloc[-1]
        max_balance = df['balance'].max()
        min_balance = df['balance'].min()
        total_return = ((final_balance - initial_balance) / initial_balance * 100)
        
        # Calculate drawdown
        df['running_max'] = df['balance'].cummax()
        df['drawdown'] = ((df['balance'] - df['running_max']) / df['running_max'] * 100)
        max_drawdown = df['drawdown'].min()
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle('📊 Trading Balance & Drawdown Analysis', fontsize=16, fontweight='bold')
        
        # ===== PLOT 1: Balance Chart =====
        ax1.plot(df['timestamp'], df['balance'], 
                color='#2E86DE', linewidth=2, label='Balance', marker='o', markersize=3)
        
        # Add horizontal lines
        ax1.axhline(y=initial_balance, color='gray', linestyle='--', alpha=0.5, label=f'Initial: ${initial_balance:,.0f}')
        ax1.axhline(y=max_balance, color='green', linestyle=':', alpha=0.3, label=f'Peak: ${max_balance:,.0f}')
        ax1.axhline(y=min_balance, color='red', linestyle=':', alpha=0.3, label=f'Trough: ${min_balance:,.0f}')
        
        # Fill area
        ax1.fill_between(df['timestamp'], df['balance'], initial_balance, 
                        where=(df['balance'] >= initial_balance), 
                        color='green', alpha=0.1, label='Profit Zone')
        ax1.fill_between(df['timestamp'], df['balance'], initial_balance,
                        where=(df['balance'] < initial_balance),
                        color='red', alpha=0.1, label='Loss Zone')
        
        # Formatting
        ax1.set_ylabel('Balance ($)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='best', fontsize=9)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add stats text box
        stats_text = f'Return: {total_return:+.2f}%\nMax DD: {max_drawdown:.2f}%\nTrades: {len(df)}'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # ===== PLOT 2: Drawdown Chart =====
        ax2.fill_between(df['timestamp'], df['drawdown'], 0, 
                        color='red', alpha=0.3)
        ax2.plot(df['timestamp'], df['drawdown'], 
                color='darkred', linewidth=1.5, label='Drawdown %')
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.axhline(y=max_drawdown, color='red', linestyle='--', alpha=0.5, 
                   label=f'Max DD: {max_drawdown:.2f}%')
        
        ax2.set_ylabel('Drawdown (%)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='best', fontsize=9)
        
        # ===== Format X-axis: Monthly ticks =====
        # Determine date range
        date_range = (df['timestamp'].max() - df['timestamp'].min()).days
        
        if date_range > 180:  # > 6 months
            # Show every month
            ax2.xaxis.set_major_locator(mdates.MonthLocator())
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        elif date_range > 60:  # > 2 months
            # Show every 2 weeks
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        else:
            # Show every week
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Save to file
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Chart saved: {output_file}")
        
        # Show plot
        if show:
            plt.show()
        else:
            plt.close()
    
    def print_summary(self):
        """In tóm tắt thống kê"""
        if not self.balance_data:
            return
        
        df = pd.DataFrame(self.balance_data)
        df = df.sort_values('timestamp')
        
        initial_balance = df['balance'].iloc[0]
        final_balance = df['balance'].iloc[-1]
        max_balance = df['balance'].max()
        min_balance = df['balance'].min()
        
        # Calculate returns
        total_return = ((final_balance - initial_balance) / initial_balance * 100)
        
        # Calculate drawdown
        df['running_max'] = df['balance'].cummax()
        df['drawdown'] = ((df['balance'] - df['running_max']) / df['running_max'] * 100)
        max_drawdown = df['drawdown'].min()
        
        # Time period
        start_date = df['timestamp'].iloc[0]
        end_date = df['timestamp'].iloc[-1]
        days = (end_date - start_date).days
        
        print("\n" + "="*60)
        print("📊 BALANCE SUMMARY")
        print("="*60)
        print(f"Period        : {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({days} days)")
        print(f"Data Points   : {len(df)} trades")
        print(f"")
        print(f"Initial       : ${initial_balance:,.2f}")
        print(f"Final         : ${final_balance:,.2f}")
        print(f"Peak          : ${max_balance:,.2f}")
        print(f"Trough        : ${min_balance:,.2f}")
        print(f"")
        print(f"Total Return  : {total_return:+.2f}%")
        print(f"Max Drawdown  : {max_drawdown:.2f}%")
        print(f"")
        
        # Monthly returns if data spans multiple months
        if days > 30:
            df['month'] = df['timestamp'].dt.to_period('M')
            monthly = df.groupby('month')['balance'].agg(['first', 'last'])
            monthly['return'] = ((monthly['last'] - monthly['first']) / monthly['first'] * 100)
            
            print("📅 MONTHLY RETURNS:")
            for month, row in monthly.iterrows():
                print(f"   {month}: {row['return']:+.2f}% (${row['first']:,.0f} → ${row['last']:,.0f})")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Vẽ biểu đồ balance từ log file')
    parser.add_argument('--log', required=True, help='Path to log file')
    parser.add_argument('--output', '-o', help='Output image file (PNG/PDF)')
    parser.add_argument('--no-show', action='store_true', help='Không hiển thị chart (chỉ save)')
    parser.add_argument('--summary', '-s', action='store_true', help='Chỉ in summary, không vẽ chart')
    
    args = parser.parse_args()
    
    # Check if log file exists
    if not Path(args.log).exists():
        print(f"❌ Log file not found: {args.log}")
        print("\n📁 Available log files:")
        for log_file in Path('logs').glob('*.log'):
            print(f"   - {log_file}")
        return
    
    # Create plotter
    plotter = BalanceChartPlotter(args.log)
    
    # Parse log
    if not plotter.parse_log():
        return
    
    # Print summary
    plotter.print_summary()
    
    # Plot chart
    if not args.summary:
        # Auto-generate output filename if not specified
        if args.output:
            output_file = args.output
        else:
            log_name = Path(args.log).stem
            output_file = f"reports/balance_chart_{log_name}.png"
            Path("reports").mkdir(exist_ok=True)
        
        plotter.plot_chart(output_file=output_file, show=not args.no_show)


if __name__ == "__main__":
    main()
